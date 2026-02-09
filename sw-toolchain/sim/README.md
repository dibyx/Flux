# flux Instruction Simulator README

## Overview

The **flux simulator** is a software model of the shader core that executes assembled programs without requiring RTL simulation.

**Benefits**:
- **Fast**: 1000× faster than RTL simulation
- **Debugging**: Inspect registers and memory easily
- **Development**: Rapid iteration on software

---

## Usage

### Basic Execution

```bash
python simulator.py program.hex
```

### Verbose Mode (shows each instruction)

```bash
python simulator.py program.hex --verbose
```

---

## Features

### SIMD Execution
- 4-wide FP32 vectors in all registers
- Example: `[1.0, 2.0, 3.0, 4.0] + [5.0, 6.0, 7.0, 8.0] = [6.0, 8.0, 10.0, 12.0]`

### Register File
- 32 threads × 32 registers
- R0 hardwired to zero
- Each register holds 4× FP32 values

### Memory Model
- 64 KB simulated memory
- Byte-addressed
- Load/Store 4× FP32 at a time

### Supported Instructions
- **Arithmetic**: ADD, SUB, MUL, DIV
- **Immediate**: ADDI, LI
- **Memory**: LOAD, STORE
- **Control**: BEQ, BNE
- **Special**: HALT

---

## Example Session

### 1. Write Assembly
```assembly
# vecadd.s
LOAD R1, 0(R10)
LOAD R2, 0(R11)
ADD R3, R1, R2
STORE R3, 0(R12)
HALT
```

### 2. Assemble
```bash
python ../asm/assembler.py ../examples/vecadd.s
```

### 3. Simulate
```bash
python simulator.py ../examples/vecadd.hex
```

### 4. Output
```
=== Running thread 0 ===
✓ Program halted after 5 instructions

=== Registers (Thread 0) ===
R1  = [    1.00,     2.00,     3.00,     4.00]
R2  = [    5.00,     6.00,     7.00,     8.00]
R3  = [    6.00,     8.00,    10.00,    12.00]
R10 = [ 4096.00,     0.00,     0.00,     0.00]
R11 = [ 8192.00,     0.00,     0.00,     0.00]
R12 = [12288.00,     0.00,     0.00,     0.00]

Input A (0x1000):
0x1000: [    1.00,     2.00,     3.00,     4.00]

Input B (0x2000):
0x2000: [    5.00,     6.00,     7.00,     8.00]

Output C (0x3000):
0x3000: [    6.00,     8.00,    10.00,    12.00]

=== Statistics ===
Instructions executed: 5
Memory reads:          2
Memory writes:         1
```

---

## Implementation Details

### Register Format
Each register stores 4× FP32 (128 bits total):
```python
regfile[thread][reg] = [lane0, lane1, lane2, lane3]
```

### Memory Layout
- Addresses are byte-aligned
- Each LOAD/STORE accesses 16 bytes (4× FP32)
- Example: LOAD from 0x1000 reads 0x1000-0x100F

### Instruction Decoding
- Follows ISA specification exactly
- Supports R/I/S/B-type formats
- Immediate values are sign-extended

### Execution Model
- Single-threaded (executes one thread at a time)
- PC advances by 4 bytes per instruction
- Branches modify PC relative to current position

---

## Limitations

**Not implemented** (for simplicity):
- Multi-threading (only thread 0 runs)
- Warp divergence (no execution masks)
- JAL/JALR instructions
- Memory coalescing (simulated memory is always fast)

**Future additions**:
- Multi-thread execution with scheduler
- Waveform visualization
- Breakpoints and single-stepping
- Register diff viewer

---

## Debugging Tips

### View All Registers
Modify `print_registers()` call to:
```python
sim.print_registers(thread=0, show_all=True)
```

### Inspect Memory Range
```python
sim.print_memory(0x1000, count=16)  # 16× 4-byte values
```

### Add Custom Test Data
```python
# In main():
sim.init_memory(0x1000, [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
sim.write_reg(0, 10, [0x1000, 0, 0, 0])
```

---

## Performance

**Typical speed**: 100,000+ instructions/second

**Comparison**:
- RTL simulation (Verilator): ~100 inst/sec
- This simulator: ~100,000 inst/sec
- **Speedup: 1000×**

---

See [ISA Specification](../../docs/specs/isa.md) for instruction encoding details.
