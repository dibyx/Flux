# Memory Systems: Bandwidth, Caches, and Optimization

## Table of Contents
1. [The Memory Wall Problem](#the-memory-wall-problem)
2. [GPU Memory Hierarchy](#gpu-memory-hierarchy)

![Memory Hierarchy](../diagrams/memory_hierarchy_diagram.png)

**Also available:** [Text version with performance tables](../diagrams/memory_hierarchy_diagram.txt)
3. [Cache Architecture](#cache-architecture)
4. [Memory Access Patterns](#memory-access-patterns)
5. [Bandwidth Optimization](#bandwidth-optimization)

---

## The Memory Wall Problem

### Physics of the Problem

**Moore's Law Mismatch**:
- Transistor count: 2× every 18 months
- Memory bandwidth: ~1.3× every 18 months
- **Result**: Growing gap between compute and memory speed

**Example Calculation**:

**GPU Specs** (Hypothetical):
- 10 TFLOPS (10 trillion FP32 operations/second)
- 500 GB/s memory bandwidth

**Naive Workload** (vector addition: `c[i] = a[i] + b[i]`):
- Each operation: read 8 bytes (2× FP32), write 4 bytes (1× FP32) = 12 bytes/op
- **Bandwidth-limited performance**: 500 GB/s ÷ 12 bytes/op = **41.7 GFLOPS**
- **Actual compute**: 10,000 GFLOPS
- **Utilization**: 0.4% (!!)

**Conclusion**: Without caching/reuse, the GPU is idle 99.6% of the time.

---

## GPU Memory Hierarchy

### Physical Layout

```
┌──────────────────┐
│   Shader Core    │  ← Register File (64KB, <1 cycle)
│                  │  ← Shared Memory (128KB, ~5 cycles)
└────────┬─────────┘
         │
    ┌────▼────┐
    │ L1 Cache│  ← Per-core (128KB, ~30 cycles)
    └────┬────┘
         │
    ┌────▼────┐
    │ L2 Cache│  ← Shared across cores (4-8MB, ~100 cycles)
    └────┬────┘
         │
    ┌────▼────┐
    │  VRAM   │  ← GDDR6/HBM (8-24GB, ~200-400 cycles)
    └─────────┘
```

### Memory Type Details

#### 1. Registers

**Properties**:
- **Size**: 64-256KB per shader core
- **Organization**: 32-bit registers, 32-256 per thread
- **Access**: Single-cycle, no arbitration
- **Scope**: Private to each thread

**Register Pressure**:
- Modern GPU: 65,536 registers per core
- If 2048 threads active, each gets 32 registers
- **Spilling**: If shader uses >32 registers, excess spills to local memory (slow!)

**Implementation (RTL)**:
```systemverilog
// Simplified register file (32 threads × 32 registers)
module register_file (
    input clk,
    input [4:0] thread_id,      // 32 threads
    input [4:0] reg_addr,       // 32 registers
    input [31:0] write_data,
    input write_enable,
    output [31:0] read_data
);
    reg [31:0] regs [0:1023];  // 32 × 32 = 1024 entries
    
    wire [9:0] full_addr = {thread_id, reg_addr};
    
    always @(posedge clk) begin
        if (write_enable)
            regs[full_addr] <= write_data;
    end
    
    assign read_data = regs[full_addr];
endmodule
```

#### 2. Shared Memory (SMEM)

**Properties**:
- **Size**: 64-128KB per shader core
- **Access**: ~5-30 cycles (depends on bank conflicts)
- **Scope**: Shared by all threads in a thread block
- **Programmability**: Explicitly managed by programmer

**Use Cases**:
- Data shared between threads (e.g., tile of matrix in matrix multiply)
- Manual caching of frequently accessed global memory

**Bank Conflicts**:
```
// 32 banks, one per thread in a warp
Bank(address) = address % 32

// Good: Each thread accesses different bank
shared_mem[threadIdx.x]      // No conflicts

// Bad: All threads access same bank
shared_mem[0]                // 32-way conflict → 32× slower
```

#### 3. L1 Cache

**Properties**:
- **Size**: 128-256KB per core
- **Line Size**: 128 bytes
- **Associativity**: 4-8 way set-associative
- **Policy**: LRU replacement
- **Scope**: Per shader core

**L1 Cache Behavior**:
```
Address Breakdown (64-bit):
[Tag: 48 bits][Set: 8 bits][Offset: 6 bits]
                  ↑              ↑
            128 sets      64 bytes/line
```

#### 4. L2 Cache

**Properties**:
- **Size**: 4-8MB (shared across all cores)
- **Line Size**: 128 bytes
- **Bandwidth**: ~2-3 TB/s
- **Purpose**: Reduce VRAM traffic, handle inter-core communication

**Partition**: Often divided into slices (e.g., 16 slices × 512KB each) for bandwidth.

#### 5. VRAM (GDDR6 / HBM)

**GDDR6 Specs**:
- **Capacity**: 8-24GB
- **Bandwidth**: 500-1000 GB/s (multiple channels, 32-bit wide each)
- **Latency**: 200-400 cycles
- **Technology**: High-speed DDR with on-die termination

**HBM2/HBM3 Specs**:
- **Capacity**: 16-48GB
- **Bandwidth**: 1-3 TB/s (2048-bit bus!)
- **Latency**: Similar to GDDR6
- **Advantage**: Massive bandwidth via 3D stacking

---

## Cache Architecture

### Cache Line Fill Sequence

**1. Thread requests address 0x1000**  
**2. Check L1 Cache**:
   - Tag match? → L1 hit, return in ~5 cycles
   - Miss? → proceed to step 3

**3. Check L2 Cache**:
   - Tag match? → L2 hit, return in ~30 cycles, fill L1
   - Miss? → proceed to step 4

**4. Access VRAM**:
   - Read 128-byte cache line from DRAM
   - Latency: ~200 cycles
   - Fill L2 and L1

### Coalescing Logic

**Goal**: Merge multiple thread requests into one memory transaction.

**Example**:
```
Warp of 32 threads, each requests 4 bytes:
Thread 0: address 0x1000
Thread 1: address 0x1004
...
Thread 31: address 0x107C

→ All fall within one 128-byte cache line
→ Coalescer issues 1 transaction instead of 32
→ 32× bandwidth savings!
```

**Implementation Sketch**:
```systemverilog
// Coalescing unit (simplified)
module coalescer (
    input [31:0] addresses [0:31],  // 32 thread addresses
    output [31:0] base_addr,        // Cache-line-aligned base
    output [31:0] mask              // Which threads participate
);
    // Align to 128-byte boundary
    assign base_addr = addresses[0] & ~32'h7F;
    
    // Check if all addresses within same line
    integer i;
    always @(*) begin
        mask = 32'h0;
        for (i = 0; i < 32; i = i + 1) begin
            if ((addresses[i] & ~32'h7F) == base_addr)
                mask[i] = 1'b1;
        end
    end
endmodule
```

---

## Memory Access Patterns

### Pattern 1: Sequential Access (Best)

```c
// Thread i reads element i
float val = data[threadIdx.x];
```

**Result**: Fully coalesced. One 128-byte transaction for 32× FP32 reads.

### Pattern 2: Strided Access (Bad)

```c
// Thread i reads element i*STRIDE
float val = data[threadIdx.x * STRIDE];
```

**Result**:
- STRIDE=1: Coalesced (good)
- STRIDE=2: 2 transactions
- STRIDE=32: 32 transactions (worst case)

### Pattern 3: Random Access (Worst)

```c
float val = data[random_index[threadIdx.x]];
```

**Result**: Up to 32 separate transactions. Cache thrashing likely.

### Pattern 4: Broadcast (Acceptable)

```c
// All threads read same address
float val = data[0];
```

**Result**: Special broadcast path in hardware. Single transaction.

---

## Bandwidth Optimization

### Technique 1: Tiling (Blocking)

**Problem**: Matrix multiply ( C = A × B ) is memory-bound.

**Naive**:
```c
C[i][j] = 0;
for (k = 0; k < N; k++)
    C[i][j] += A[i][k] * B[k][j];
// Arithmetic intensity: 2 FLOPs / 3 loads = 0.67 FLOPs/byte
```

**Tiled** (using shared memory):
```c
// Load tile of A and B into shared memory
__shared__ float As[TILE][TILE];
__shared__ float Bs[TILE][TILE];

for (tile = 0; tile < N/TILE; tile++) {
    // Load tile cooperatively
    As[ty][tx] = A[...];
    Bs[ty][tx] = B[...];
    __syncthreads();
    
    // Compute using shared mem (TILE times reuse)
    for (k = 0; k < TILE; k++)
        Cvalue += As[ty][k] * Bs[k][tx];
    __syncthreads();
}

// Arithmetic intensity: TILE×2 FLOPs / 3 loads
// For TILE=16: 10.7 FLOPs/byte (16× better!)
```

### Technique 2: Memory Compression

**Lossless Compression** (on chip):
- Color compression: DXT/BC formats (4:1 or 6:1)
- Depth compression: Plane equation encoding
- Benefit: Reduces VRAM bandwidth by 2-4×

### Technique 3: Data Reordering

**Z-Order Curve** (for 2D textures):
```
Linear layout:    Z-order layout:
0  1  2  3        0  1  4  5
4  5  6  7   →    2  3  6  7
8  9 10 11        8  9 12 13
12 13 14 15       10 11 14 15
```

**Benefit**: Nearby 2D coordinates map to nearby memory addresses → better cache locality.

---

## Practical Implementation: Memory Controller

### RTL Sketch (Simplified)

```systemverilog
module memory_controller (
    input clk,
    input rst_n,
    
    // Request from L2 cache
    input [63:0] req_addr,
    input req_valid,
    output reg req_ready,
    
    // Response to L2 cache
    output reg [127:0] resp_data,  // 128-byte line
    output reg resp_valid,
    
    // DRAM interface (AXI4)
    output reg [63:0] axi_araddr,
    output reg axi_arvalid,
    input axi_arready,
    // ... (AXI read channel signals)
);

    // State machine: IDLE → REQUEST → WAIT → RESPONSE
    typedef enum {IDLE, REQUEST, WAIT, RESP} state_t;
    state_t state;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
        end else case (state)
            IDLE: begin
                if (req_valid) begin
                    axi_araddr <= req_addr & ~64'h7F;  // Align to 128B
                    axi_arvalid <= 1'b1;
                    state <= REQUEST;
                end
            end
            REQUEST: begin
                if (axi_arready) begin
                    axi_arvalid <= 1'b0;
                    state <= WAIT;
                end
            end
            WAIT: begin
                if (axi_rvalid && axi_rlast) begin
                    resp_data <= axi_rdata;
                    resp_valid <= 1'b1;
                    state <= RESP;
                end
            end
            RESP: begin
                resp_valid <= 1'b0;
                state <= IDLE;
            end
        endcase
    end
endmodule
```

---

## Key Takeaways

1. **Memory is the bottleneck**: Spend 80% of optimization time on memory access patterns.
2. **Coalescing is critical**: Ensure sequential access whenever possible.
3. **Shared memory is your friend**: Use it for data reuse within a block.
4. **Tiling/Blocking**: Essential for compute-intensive kernels (matrix multiply, convolution).
5. **Measure**: Use profilers (nvprof, NCU, AMD uProf) to see actual bandwidth utilization.

**Next**: [Toolchain Setup Guide](../setup/toolchain_guide.md) to start building your GPU.
