# flux GPU - Extensions & Future Work

**Ideas for extending and improving the flux GPU**

---

## Overview

Since you're working **without hardware**, these extensions focus on what you can implement and test in **simulation**. All changes can be validated using the Python simulator before any FPGA work.

---

## Easy Extensions (1-2 hours each)

### 1. Add More Instructions

**Goal**: Expand the ISA with useful operations

**New Instructions to Add**:
```
MAD  (Multiply-Add): rd = rs1 * rs2 + rd
MIN  (Minimum): rd = min(rs1, rs2)
MAX  (Maximum): rd = max(rs1, rs2)
AND  (Bitwise AND): rd = rs1 & rs2
OR   (Bitwise OR): rd = rs1 | rs2
XOR  (Bitwise XOR): rd = rs1 ^ rs2
SHL  (Shift Left): rd = rs1 << rs2
SHR  (Shift Right): rd = rs1 >> rs2
```

**Files to Modify**:
1. `meta/specs/isa.md` - Document new opcodes
2. `rtl/src/shader_core/instruction_decoder.sv` - Add decode logic
3. `rtl/src/shader_core/simd_alu.sv` - Implement operations
4. `sw-toolchain/asm/assembler.py` - Add assembly support
5. `sw-toolchain/sim/simulator.py` - Add simulation support

**Example** (MAD instruction):

```systemverilog
// In simd_alu.sv
ALU_MAD: begin
    r0 = $shortrealtobits($bitstoshortreal(a0) * $bitstoshortreal(b0) + $bitstoshortreal(result[31:0]));
    r1 = $shortrealtobits($bitstoshortreal(a1) * $bitstoshortreal(b1) + $bitstoshortreal(result[63:32]));
    // ... lanes 2, 3
    result <= {r3, r2, r1, r0};
end
```

**Test**:
```python
# In simulator
def test_mad():
    sim = FluxSimulator()
    sim.write_reg(0, 1, [2.0, 3.0, 4.0, 5.0])  # R1
    sim.write_reg(0, 2, [3.0, 4.0, 5.0, 6.0])  # R2
    sim.write_reg(0, 3, [1.0, 1.0, 1.0, 1.0])  # R3
    sim.execute_instruction(0, encode_mad(3, 1, 2))
    result = sim.read_reg(0, 3)
    assert result == [7.0, 13.0, 21.0, 31.0]  # 2*3+1, 3*4+1, ...
```

**Benefit**: More powerful compute capabilities

---

### 2. Dot Product Instruction

**Goal**: Hardware-accelerated vector dot product

**New Instruction**:
```
DOT rd, rs1, rs2
# rd[0] = rs1[0]*rs2[0] + rs1[1]*rs2[1] + rs1[2]*rs2[2] + rs1[3]*rs2[3]
# rd[1:3] = 0
```

**Implementation**:
```systemverilog
ALU_DOT: begin
    real sum;
    sum = $bitstoshortreal(a0) * $bitstoshortreal(b0) +
          $bitstoshortreal(a1) * $bitstoshortreal(b1) +
          $bitstoshortreal(a2) * $bitstoshortreal(b2) +
          $bitstoshortreal(a3) * $bitstoshortreal(b3);
    r0 = $shortrealtobits(sum);
    result <= {96'b0, r0};  // Only lane 0 has result
end
```

**Use Case**: ML matrix multiplication, physics simulations

---

### 3. Integer ALU Path

**Goal**: Support integer operations alongside FP32

**Add**:
- Integer add/sub/mul
- Comparison operations (SLTI, SLTU)
- Useful for loop counters, array indexing

**Implementation**:
```systemverilog
wire op_is_integer = (alu_op == ALU_ADDI) || (alu_op == ALU_SUBI);

always @(*) begin
    if (op_is_integer) begin
        // Integer path
        result_lane[0] = $signed(a0) + $signed(b0);
    end else begin
        // FP32 path (existing)
        result_lane[0] = $shortrealtobits($bitstoshortreal(a0) + $bitstoshortreal(b0));
    end
end
```

**Benefit**: More versatile for general computing

---

## Medium Extensions (4-8 hours each)

### 4. Instruction Fetch + Program Counter

**Goal**: Fetch instructions from memory automatically

**Current State**: Instructions fed externally  
**Target**: Self-contained execution

**Add**:
```systemverilog
module instruction_fetch (
    input  wire        clk,
    input  wire        rst_n,
    output wire [31:0] pc,           // Program counter
    output wire [31:0] instruction,  // Fetched instruction
    input  wire        branch_taken,
    input  wire [31:0] branch_target
);

reg [31:0] pc_reg;

always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        pc_reg <= 32'h0;
    else if (branch_taken)
        pc_reg <= branch_target;
    else
        pc_reg <= pc_reg + 4;  // Next instruction
end

// Read from instruction memory
assign instruction = imem[pc_reg[15:2]];  // Word-aligned

endmodule
```

**Files**:
- Create `rtl/src/shader_core/instruction_fetch.sv`
- Modify `shader_core.sv` to instantiate
- Add instruction memory (BRAM or array)

**Test**: Load program into memory, watch PC advance

---

### 5. Thread Scheduler (Warp Scheduler)

**Goal**: Implement actual multi-threading

**Concept**: 32 threads share one shader core, round-robin scheduling

**Implementation**:
```systemverilog
module warp_scheduler (
    input  wire        clk,
    input  wire        rst_n,
    output reg  [4:0]  active_thread,  // Which thread is executing
    input  wire [31:0] thread_ready,   // Bitmap of ready threads
    output wire        all_done
);

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        active_thread <= 5'd0;
    end else begin
        // Round-robin scheduling
        if (thread_ready[active_thread]) begin
            // Execute current thread for 1 cycle
            active_thread <= active_thread + 1;
        end else begin
            // Skip to next ready thread
            active_thread <= find_next_ready(active_thread, thread_ready);
        end
    end
end

assign all_done = (thread_ready == 32'h0);

endmodule
```

**Benefit**: True GPU-style parallelism

---

### 6. L1 Cache (16 KB)

**Goal**: Reduce memory access latency

**Design**:
- Direct-mapped or 2-way set-associative
- 64-byte cache lines
- 256 lines = 16 KB

**Implementation**:
```systemverilog
module l1_cache (
    input  wire        clk,
    input  wire [31:0] addr,
    input  wire        read_req,
    output reg  [31:0] data,
    output reg         hit,
    output reg         miss
);

// Cache storage
reg [31:0] cache_data [0:255][0:15];  // 256 lines × 16 words
reg [23:0] cache_tags [0:255];
reg        cache_valid [0:255];

wire [7:0] index = addr[11:4];   // 256 lines
wire [3:0] offset = addr[3:0];   // 16 words per line
wire [23:0] tag = addr[31:8];

always @(posedge clk) begin
    if (read_req) begin
        if (cache_valid[index] && cache_tags[index] == tag) begin
            // HIT
            data <= cache_data[index][offset];
            hit <= 1;
            miss <= 0;
        end else begin
            // MISS - fetch from memory
            miss <= 1;
            hit <= 0;
        end
    end
end

endmodule
```

**Simulation**: Track hit/miss rates

---

## Advanced Extensions (10+ hours each)

### 7. LLVM Backend (C Compiler)

**Goal**: Write C code, compile to flux assembly

**Approach**:
- Study LLVM backend tutorial
- Define flux target in LLVM
- Map C operations to ISA

**Example**:
```c
// test.c
void vector_add(float* a, float* b, float* c, int n) {
    for (int i = 0; i < n; i += 4) {
        // SIMD load
        vec4 va = load_vec4(&a[i]);
        vec4 vb = load_vec4(&b[i]);
        // SIMD add
        vec4 vc = va + vb;
        // SIMD store
        store_vec4(&c[i], vc);
    }
}
```

**Compile**:
```bash
llvm-flux test.c -o test.s
```

**Resources**:
- LLVM Backend Tutorial
- RISC-V LLVM backend (reference)

---

### 8. Texture Mapping

**Goal**: Sample textures during rasterization

**Add**:
- Texture memory (separate from framebuffer)
- UV coordinate interpolation
- Bilinear filtering

**RTL Changes**:
```systemverilog
module texture_sampler (
    input  wire [9:0]  u, v,        // Texture coordinates
    input  wire [31:0] tex_addr,    // Texture base address
    output wire [23:0] color        // Sampled color
);

// Bilinear interpolation
wire [7:0] u_frac = u[7:0];
wire [7:0] v_frac = v[7:0];
wire [9:0] u_int = u[9:8];
wire [9:0] v_int = v[9:8];

// Fetch 4 texels
wire [23:0] c00 = tex_mem[tex_addr + v_int*256 + u_int];
wire [23:0] c01 = tex_mem[tex_addr + v_int*256 + u_int + 1];
wire [23:0] c10 = tex_mem[tex_addr + (v_int+1)*256 + u_int];
wire [23:0] c11 = tex_mem[tex_addr + (v_int+1)*256 + u_int + 1];

// Interpolate
assign color = lerp2d(c00, c01, c10, c11, u_frac, v_frac);

endmodule
```

**Test in Simulation**: Render textured triangle

---

### 9. Z-Buffer (Depth Testing)

**Goal**: Correct occlusion for 3D scenes

**Add**:
- Depth buffer (same size as framebuffer)
- Depth comparison during rasterization
- Z-value interpolation

**Algorithm**:
```
For each pixel in triangle:
    z_new = interpolate_depth(v0.z, v1.z, v2.z, px, py)
    if z_new < z_buffer[px, py]:
        framebuffer[px, py] = color
        z_buffer[px, py] = z_new
```

**RTL**:
```systemverilog
// Add to rasterizer
wire [15:0] z_interpolated = interpolate_z(v0_z, v1_z, v2_z, curr_x, curr_y);
wire [15:0] z_current = z_buffer[fb_addr];

if (inside && (z_interpolated < z_current)) begin
    fb_write <= 1;
    fb_data <= color;
    z_buffer[fb_addr] <= z_interpolated;
end
```

**Benefit**: Real 3D graphics

---

## Simulation-Only Extensions

### 10. Advanced Simulator Features

**Goal**: Make simulator more useful for development

**Add**:
1. **Graphical Output**:
   ```python
   import matplotlib.pyplot as plt
   
   def visualize_framebuffer(sim):
       pixels = sim.read_framebuffer()
       img = np.array(pixels).reshape(480, 640, 3)
       plt.imshow(img)
       plt.show()
   ```

2. **Performance Profiler**:
   ```python
   class Profiler:
       def __init__(self, sim):
           self.sim = sim
           self.instr_counts = {}
       
       def profile(self, instructions):
           for pc, instr in instructions:
               opcode = decode_opcode(instr)
               self.instr_counts[opcode] = self.instr_counts.get(opcode, 0) + 1
   ```

3. **Waveform Viewer**:
   - Log all signal changes
   - Export to VCD format
   - View in GTKWave

4. **Debugger**:
   ```python
   class Debugger:
       def __init__(self, sim):
           self.breakpoints = set()
       
       def set_breakpoint(self, addr):
           self.breakpoints.add(addr)
       
       def step(self):
           # Execute one instruction
           # Check breakpoints
           # Print registers
   ```

---

### 11. Benchmark Suite

**Goal**: Standard tests for performance comparison

**Benchmarks to Add**:
1. **Vector Add** (memory bandwidth)
2. **Matrix Multiply** (compute throughput)
3. **Mandelbrot Set** (FP32 performance)
4. **Ray-Triangle Intersection** (graphics)
5. **FFT** (mixed operations)

**Example Template**:
```python
# benchmarks/vecadd_bench.py
import time

def benchmark_vecadd(size):
    gpu = FluxGPU(interface='simulation')
    
    # Setup
    a = [float(i) for i in range(size)]
    b = [float(i*2) for i in range(size)]
    
    # Execute
    start = time.time()
    gpu.vector_add(a, b, size)
    elapsed = time.time() - start
    
    # Report
    throughput = (size * 4) / elapsed  # bytes/sec
    print(f"Size: {size}, Time: {elapsed:.3f}s, Throughput: {throughput/1e6:.1f} MB/s")

for size in [1000, 10000, 100000]:
    benchmark_vecadd(size)
```

---

### 12. Automated Testing Framework

**Goal**: Continuous validation as you extend

**Setup**:
```python
# tests/test_suite.py
import pytest

class TestISA:
    def test_add(self):
        sim = FluxSimulator()
        # ... test ADD instruction
    
    def test_mul(self):
        # ... test MUL instruction
    
    # Add test for each instruction

class TestGraphics:
    def test_triangle_simple(self):
        # ... render triangle, check output
    
    def test_triangle_offscreen(self):
        # ... test clipping

# Run with:
# pytest tests/ -v
```

**CI/CD** (optional):
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest tests/
```

---

## Learning/Teaching Extensions

### 13. Interactive Tutorials

**Goal**: Jupyter notebooks for learning

**Topics**:
1. **GPU Basics**:
   ```jupyter
   # 01_gpu_intro.ipynb
   from flux import FluxSimulator
   
   ## Lesson 1: Your First GPU Program
   Let's add two numbers using the flux GPU...
   ```

2. **Assembly Programming**:
   - Step-by-step instruction guide
   - Interactive exercises
   - Visual register/memory display

3. **Graphics Pipeline**:
   - Draw triangle step-by-step
   - Visualize rasterization process
   - Interactive vertex manipulation

**Tools**: Jupyter, IPython widgets, matplotlib

---

### 14. Web-based Emulator

**Goal**: Run flux in browser for easy sharing

**Stack**:
- Backend: Python simulator
- Frontend: React + Three.js
- Communication: WebSocket or REST API

**Features**:
1. **Code Editor**: Write assembly in browser
2. **Visualizer**: See registers, memory, framebuffer
3. **Step Debugger**: Execute instruction-by-instruction
4. **Examples**: Pre-loaded demo programs

**Demo**: Share URL, others can run your programs!

---

## Research Extensions

### 15. Novel Scheduling Algorithms

**Experiment**:
- Priority-based thread scheduling
- Workload-aware scheduling
- Compare performance

**Metrics**:
- Thread utilization
- Memory bandwidth efficiency
- Latency hiding effectiveness

---

### 16. Energy Modeling

**Goal**: Estimate power consumption

**Method**:
- Count instruction types
- Weight by energy cost
- Sum total energy

**Example**:
```python
energy_costs = {
    'ADD': 1.0,   # Baseline
    'MUL': 3.5,   # More expensive
    'DIV': 10.0,  # Most expensive
    'LOAD': 2.0,
    'STORE': 2.5
}

total_energy = sum(instr_count[op] * energy_costs[op] 
                   for op in instructions)
```

**Use**: Optimize for power efficiency

---

## Documentation Extensions

### 17. Video Tutorials

**Record**:
1. Setup walkthrough
2. Writing first program
3. Graphics demo
4. Hardware synthesis (simulated)

**Tools**: OBS Studio, Kdenlive

---

### 18. Academic Paper

**Write**: "flux: An Educational GPU Architecture"

**Sections**:
1. Introduction & Motivation
2. Architecture Design
3. Implementation
4. Evaluation
5. Educational Impact

**Target**: Workshop at ISCA, MICRO, or education conference

---

## Summary: What to Start With

**No Hardware? Start Here**:
1. ✅ Add MAD instruction (easy win)
2. ✅ Benchmark suite (measure progress)
3. ✅ Graphical simulator output (see your work!)
4. ✅ Jupyter tutorials (teach others)

**When You Get Hardware**:
1. Test current design
2. Add L1 cache
3. Implement texture mapping
4. Build full demo scene

**All extensions validated in simulation first** - hardware optional! 🚀

---

**Pick what interests you most and start coding!**
