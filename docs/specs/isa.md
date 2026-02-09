# flux ISA Specification v0.1

## Overview

The **flux ISA** is a minimal RISC-style instruction set designed for educational GPU shader execution. It supports:
- 32-bit fixed-width instructions
- SIMD execution (4-wide FP32)
- Load/store architecture
- 32 general-purpose registers per thread

---

## Register Architecture

### General-Purpose Registers
- **R0-R31**: 32× 32-bit registers per thread
- **R0**: Hardwired to 0 (reads always return 0, writes ignored)
- **R31**: Link register (used for function calls)

### Special Registers
- **PC**: Program counter (not directly accessible)
- **EXEC_MASK**: Per-thread execution mask (for divergence)

---

## Instruction Format

All instructions are **32 bits** (4 bytes) with the following formats:

### R-Type (Register-Register ALU)
```
┌────────┬────────┬────────┬────────┬────────┬────────┐
│ opcode │   rd   │  rs1   │  rs2   │ funct3 │ funct7 │
│ [6:0]  │ [11:7] │[19:15] │[24:20] │[14:12] │[31:25] │
└────────┴────────┴────────┴────────┴────────┴────────┘
```

### I-Type (Immediate)
```
┌────────┬────────┬────────┬──────────────┬────────┐
│ opcode │   rd   │  rs1   │   imm[11:0]  │        │
│ [6:0]  │ [11:7] │[19:15] │   [31:20]    │        │
└────────┴────────┴────────┴──────────────┴────────┘
```

### M-Type (Memory)
```
┌────────┬────────┬────────┬──────────────┬────────┐
│ opcode │ rd/rs2 │  rs1   │    offset    │ funct3 │
│ [6:0]  │ [11:7] │[19:15] │   [31:25]    │[14:12] │
└────────┴────────┴────────┴──────────────┴────────┘
```

---

## Instruction Set

### Arithmetic (R-Type)

| Mnemonic | Opcode | Funct3 | Funct7 | Description |
|----------|--------|--------|--------|-------------|
| **ADD**  | 0x33   | 0x0    | 0x00   | rd = rs1 + rs2 |
| **SUB**  | 0x33   | 0x0    | 0x20   | rd = rs1 - rs2 |
| **MUL**  | 0x33   | 0x0    | 0x01   | rd = rs1 × rs2 |
| **DIV**  | 0x33   | 0x4    | 0x01   | rd = rs1 ÷ rs2 |
| **MAD**  | 0x33   | 0x0    | 0x02   | rd = rs1 × rs2 + rd (fused multiply-add) |

### Immediate (I-Type)

| Mnemonic | Opcode | Description |
|----------|--------|-------------|
| **ADDI** | 0x13   | rd = rs1 + sign_ext(imm) |
| **LI**   | 0x13   | rd = sign_ext(imm) (alias: ADDI rd, R0, imm) |

### Memory (M-Type)

| Mnemonic | Opcode | Funct3 | Description |
|----------|--------|--------|-------------|
| **LOAD** | 0x03   | 0x2    | rd = MEM[rs1 + offset] |
| **STORE**| 0x23   | 0x2    | MEM[rs1 + offset] = rs2 |

### Control Flow

| Mnemonic | Opcode | Description |
|----------|--------|-------------|
| **BEQ**  | 0x63   | if (rs1 == rs2) PC += offset |
| **BNE**  | 0x63   | if (rs1 != rs2) PC += offset |
| **JAL**  | 0x6F   | R31 = PC+4; PC += offset |
| **JALR** | 0x67   | R31 = PC+4; PC = rs1 + offset |
| **RET**  | 0x67   | PC = R31 (alias: JALR R0, R31, 0) |

### Special

| Mnemonic | Opcode | Description |
|----------|--------|-------------|
| **NOP**  | 0x13   | No operation (ADDI R0, R0, 0) |
| **HALT** | 0x7F   | Stop execution |

---

## Encoding Examples

### Example 1: ADD R3, R1, R2
```
ADD R3, R1, R2  →  rd=3, rs1=1, rs2=2, opcode=0x33, funct3=0, funct7=0

Binary:
  0000000 00010 00001 000 00011 0110011
  [funct7][rs2 ][rs1 ][f3 ][ rd ][opcode]

Hex: 0x002081B3
```

### Example 2: LOAD R5, 16(R4)
```
LOAD R5, 16(R4)  →  rd=5, rs1=4, offset=16, opcode=0x03, funct3=2

Binary:
  000000010000 00100 010 00101 0000011
  [  offset  ][rs1 ][f3][ rd ][opcode]

Hex: 0x01022283
```

### Example 3: ADDI R7, R6, 100
```
ADDI R7, R6, 100  →  rd=7, rs1=6, imm=100, opcode=0x13

Binary:
  000001100100 00110 000 00111 0010011
  [   imm    ][rs1 ][f3][ rd ][opcode]

Hex: 0x06430393
```

---

## SIMD Execution Model

Each instruction operates on **4-wide FP32 vectors** (128-bit registers).

### Example: Vector Addition
```assembly
# Compute: C[i] = A[i] + B[i] for 4 elements

LOAD  R1, 0(R10)     # R1 = [A[0], A[1], A[2], A[3]]
LOAD  R2, 0(R11)     # R2 = [B[0], B[1], B[2], B[3]]
ADD   R3, R1, R2     # R3 = R1 + R2 (4 parallel adds)
STORE R3, 0(R12)     # Store result
```

**Hardware executes**: 
- 4 parallel FP32 adders
- All operations SIMD (Single Instruction, Multiple Data)

---

## Thread Execution & Divergence

### Warp Execution
- **Warp size**: 32 threads
- All threads execute same instruction (lockstep)
- Each thread has own register file

### Branch Divergence
```assembly
        BEQ R1, R0, label_a   # If R1==0, goto label_a
        # Path 1: R1 != 0
        ADD R3, R3, R1
        JAL label_end
label_a:
        # Path 2: R1 == 0
        MUL R3, R3, R2
label_end:
        STORE R3, 0(R4)
```

**Hardware behavior**:
1. Evaluate condition for all 32 threads
2. Execute Path 1 with threads where condition is false (mask others)
3. Execute Path 2 with threads where condition is true (mask others)
4. Reconverge at `label_end`

**Performance**: Divergent branches serialize execution (2× slowdown in this case).

---

## Memory Model

### Address Space
- **Global Memory**: Shared by all threads (VRAM)
- **Shared Memory**: Per thread-block (fast, explicit)
- **Registers**: Per-thread (fastest)

### Memory Layout (for LOAD/STORE)
- Addresses are **byte-addressed**
- All loads/stores are **4-byte aligned** (FP32)
- Unaligned access → undefined behavior (for simplicity)

### Coalescing
Hardware coalesces adjacent thread accesses:
```assembly
# Thread i loads from address base + i*4
LOAD R1, (R10)   # R10 = base + threadIdx * 4

# If threads 0-31 access consecutive addresses:
# → 1 memory transaction (128 bytes)
# Otherwise: up to 32 transactions (slow!)
```

---

## Assembly Examples

### Example 1: Dot Product (4 elements)
```assembly
# Compute: dot = A[0]*B[0] + A[1]*B[1] + A[2]*B[2] + A[3]*B[3]

LOAD  R1, 0(R10)     # R1 = A (4 elements)
LOAD  R2, 0(R11)     # R2 = B (4 elements)
MUL   R3, R1, R2     # R3 = A * B (element-wise)

# Horizontal sum (reduce)
# TODO: Need SHUFFLE or explicit reduce instructions
# For now, assume R3[0] contains partial sum
STORE R3, 0(R12)
```

### Example 2: Conditional (if-else)
```assembly
# if (x > 0) y = x + 1; else y = x - 1;

LOAD  R1, 0(R10)     # R1 = x
BEQ   R1, R0, else_branch
# if-branch (x != 0, assuming x>0 simplification)
ADDI  R2, R1, 1
JAL   end_if
else_branch:
ADDI  R2, R1, -1
end_if:
STORE R2, 0(R11)     # Store y
```

### Example 3: Loop (vector add 128 elements)
```assembly
# for (i = 0; i < 128; i += 4) C[i] = A[i] + B[i]

        ADDI  R10, R0, 0      # i = 0
loop:
        LOAD  R1, 0(R20)      # R1 = A[i] (R20 = &A[i])
        LOAD  R2, 0(R21)      # R2 = B[i]
        ADD   R3, R1, R2
        STORE R3, 0(R22)      # C[i] = R3
        
        ADDI  R20, R20, 16    # Advance A pointer (4 floats * 4 bytes)
        ADDI  R21, R21, 16    # Advance B pointer
        ADDI  R22, R22, 16    # Advance C pointer
        ADDI  R10, R10, 4     # i += 4
        
        ADDI  R11, R0, 128    # R11 = 128
        BNE   R10, R11, loop  # if (i != 128) goto loop
        
        HALT
```

---

## Future Extensions (Not Implemented Yet)

- **Texture sampling**: `TEX rd, rs1, rs2` (sample texture at UV coords)
- **Atomics**: `ATOMIC_ADD`, `ATOMIC_CAS`
- **Shuffle**: Inter-lane data movement
- **Transcendentals**: `SIN`, `COS`, `EXP`, `LOG`, `SQRT`, `RSQRT`
- **FP16 / INT operations**: Mixed-precision support

---

## Implementation Notes

### Minimal Implementation (Phase 2)
For the initial shader core, implement:
- ✅ ADD, SUB, MUL (R-type)
- ✅ ADDI, LI (I-type)
- ✅ LOAD, STORE (M-type)
- ✅ NOP, HALT

**Skip for now**: Branches (BEQ/BNE/JAL), DIV, MAD

### Decoder Logic
```systemverilog
always_comb begin
    case (opcode)
        7'b0110011: begin  // R-type
            case (funct3)
                3'b000: alu_op = (funct7[5]) ? SUB : ADD;
                3'b000: alu_op = (funct7[0]) ? MUL : ADD;
                // ...
            endcase
        end
        7'b0010011: alu_op = ADDI;  // I-type
        7'b0000011: mem_op = LOAD;
        7'b0100011: mem_op = STORE;
        // ...
    endcase
end
```

---

## References
- **RISC-V ISA**: Inspired by RV32I encoding
- **NVIDIA PTX**: SIMD execution model
- **AMD GCN ISA**: Wave execution concepts

**Document Version**: 0.1 (2026-02-08)
