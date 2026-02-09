# flux Firmware README

**Complete firmware system for programming and controlling the flux GPU**

---

## Overview

The firmware layer provides high-level APIs to:
- Load programs into GPU memory
- Initialize registers and data
- Start execution
- Read results
- Debug programs

---

## Components

### 1. **firmware_driver.py**
Main driver class (`FluxGPU`) with methods for all GPU operations.

**Interfaces**:
- `simulation`: Software simulator (default, fastest)
- `uart`: Hardware via USB-UART
- `pcie`: Hardware via PCIe (future)

### 2. **firmware_guide.md**
Detailed documentation on:
- Boot process
- Command protocol
- UART packet format
- Debugging techniques

### 3. **examples/**
Working demos:
- `example_vecadd.py` - Vector addition
- `example_dotprod.py` - Dot product
- `README.md` - Usage guide

---

## Quick Start

### Run Example (Simulation)

```bash
cd hw-tools/firmware/examples
python example_vecadd.py
```

**Output**:
```
=== flux GPU Vector Addition Demo ===
✓ Loaded 5 instructions
Array A: [10.0, 20.0, 30.0, 40.0]
Array B: [1.0, 2.0, 3.0, 4.0]
Array C (A+B): [11.0, 22.0, 33.0, 44.0]
✓ Test PASSED!
```

---

## API Reference

### Initialize GPU

```python
from firmware_driver import FluxGPU

gpu = FluxGPU(interface='simulation')
```

### Load Program

```python
gpu.load_program('path/to/program.hex')
```

### Write Memory

```python
# Write array to memory
gpu.write_memory(0x1000, [1.0, 2.0, 3.0, 4.0])
```

### Set Registers

```python
# Set register (4-wide SIMD)
gpu.set_register(thread_id=0, reg_id=10, value=[0x1000, 0, 0, 0])
```

### Execute

```python
# Run thread 0
gpu.start_execution(thread_mask=0x01)
```

### Read Results

```python
# Read memory
result = gpu.read_memory(0x3000, count=4)

# Read register
r3 = gpu.get_register(thread_id=0, reg_id=3)
```

### Debug

```python
# Dump all registers
gpu.dump_registers(thread_id=0, show_all=True)

# Dump memory range
gpu.dump_memory(0x1000, count=16)
```

---

## Hardware Mode (FPGA)

### Requirements

1. **ULX3S board** programmed with flux bitstream
2. **USB-UART cable** connected to FPGA
3. **Python pyserial**: `pip install pyserial`

### Usage

```python
gpu = FluxGPU(interface='uart')  # Change interface
# ... rest is identical to simulation ...
```

### UART Protocol

**Packet Format**:
```
[START] [CMD] [LENGTH] [DATA...] [CHECKSUM]
  0xAA   1B      2B      N bytes     1B
```

**Commands**:
- `0x80`: LOAD_PROG - Load program
- `0x90`: WRITE_MEM - Write memory
- `0xC0`: READ_MEM - Read memory
- `0xA0`: WRITE_REG - Write register
- `0xA1`: READ_REG - Read register
- `0xB0`: START - Start execution
- `0xB1`: HALT_CHECK - Check if halted

See `firmware_guide.md` for protocol details.

---

## Complete Workflow Example

```python
#!/usr/bin/env python3
from firmware_driver import run_program

# This function does everything:
# 1. Assembles the .s file
# 2. Loads to GPU
# 3. Initializes data
# 4. Executes
# 5. Shows results

gpu = run_program('my_program.s', interface='simulation')

# Check specific outputs
result = gpu.read_memory(0x3000, 4)
print(f"Result: {result}")
```

---

## Files

| File | Lines | Purpose |
|------|-------|---------|
| `firmware_driver.py` | 400 | Main API |
| `firmware_guide.md` | 500 | Protocol docs |
| `examples/example_vecadd.py` | 50 | Vector add demo |
| `examples/example_dotprod.py` | 50 | Dot product demo |
| `examples/README.md` | 100 | Examples guide |

**Total**: ~1,100 lines

---

## Common Patterns

### Pattern: Batch Operations

```python
# Load multiple arrays efficiently
arrays = {
    0x1000: [1, 2, 3, 4],
    0x2000: [5, 6, 7, 8],
    0x3000: [9, 10, 11, 12]
}

for addr, data in arrays.items():
    gpu.write_memory(addr, data)
```

### Pattern: Verify Results

```python
def verify(got, expected, tolerance=1e-6):
    assert len(got) == len(expected)
    for i, (g, e) in enumerate(zip(got, expected)):
        assert abs(g - e) < tolerance, f"Fail at {i}"
    print("✓ Pass")

result = gpu.read_memory(0x3000, 4)
verify(result, [11, 22, 33, 44])
```

### Pattern: Performance Test

```python
import time

start = time.time()
gpu.start_execution()
elapsed = time.time() - start

instr_count = 100  # from assembler
ipc = instr_count / elapsed if elapsed > 0 else float('inf')

print(f"Time: {elapsed*1000:.2f} ms")
print(f"IPC: {ipc:.0f} instructions/sec")
```

---

## Troubleshooting

### Problem: Program doesn't execute

**Check**:
1. Program loaded? (`gpu.load_program(...)`)
2. Registers initialized? (R10, R11, R12 for vecadd)
3. HALT instruction present?

**Debug**:
```python
gpu.dump_registers(0, show_all=True)
```

### Problem: Wrong results

**Check**:
1. Input data written correctly?
2. Output address correct?

**Debug**:
```python
# Verify inputs
A = gpu.read_memory(0x1000, 4)
print(f"Array A: {A}")
```

### Problem: UART communication fails

**Check**:
1. Correct port: `/dev/ttyUSB0` (Linux) or `COM3` (Windows)
2. Baud rate: 115200
3. Cable connected?

**Fix**:
```python
# Try different port
gpu = FluxGPU(interface='uart')
gpu.port = serial.Serial('COM4', 115200)  # Windows
```

---

## Next Steps

1. **Run all examples**: Test each demo
2. **Write custom program**: Try your own assembly
3. **Port to FPGA**: Test on real hardware
4. **Extend protocol**: Add new commands
5. **Build debugger**: Interactive stepping

---

## See Also

- [Firmware Guide](firmware_guide.md) - Protocol details
- [Assembler](../../sw-toolchain/asm/) - Write programs
- [Simulator](../../sw-toolchain/sim/) - Test programs
- [ISA Spec](../../docs/specs/isa.md) - Instruction reference

---

**flux firmware**: Bridge between software and hardware 🔗
