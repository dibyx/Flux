# flux Firmware Examples

Complete working examples demonstrating GPU programming.

---

## Quick Start

```bash
cd hw-tools/firmware/examples

# Run vector addition
python example_vecadd.py

# Run dot product
python example_dotprod.py

# Custom program
python example_custom.py
```

---

## Example 1: Vector Addition

**File**: `example_vecadd.py`

```python
# Initialize GPU
gpu = FluxGPU(interface='simulation')

# Load program
gpu.load_program('vecadd.hex')

# Setup data
gpu.write_memory(0x1000, [10, 20, 30, 40])  # A
gpu.write_memory(0x2000, [1, 2, 3, 4])      # B

# Point registers to arrays
gpu.set_register(0, 10, [0x1000, 0, 0, 0])
gpu.set_register(0, 11, [0x2000, 0, 0, 0])
gpu.set_register(0, 12, [0x3000, 0, 0, 0])

# Execute
gpu.start_execution()

# Read results
C = gpu.read_memory(0x3000, 4)
# C = [11, 22, 33, 44]
```

---

## Example 2: Dot Product

**File**: `example_dotprod.py`

Computes A·B = A[0]×B[0] + A[1]×B[1] + A[2]×B[2] + A[3]×B[3]

**Output**:
```
A = [1, 2, 3, 4]
B = [5, 6, 7, 8]
Products = [5, 12, 21, 32]
Dot = 70 ✓
```

---

## Example 3: Custom Program

**File**: `example_custom.py`

Write your own assembly, assemble it, and run!

```python
# 1. Write assembly
code = """
LI R1, 42
LI R2, 8
MUL R3, R1, R2  # R3 = 336
HALT
"""

with open('my_program.s', 'w') as f:
    f.write(code)

# 2. Assemble & run
from firmware_driver import run_program
gpu = run_program('my_program.s')

# 3. Check result
r3 = gpu.get_register(0, 3)
print(f"R3 = {r3[0]}")  # Should be 336
```

---

## Running on Hardware (FPGA)

**Requirements**:
- ULX3S board programmed with flux bitstream
- USB-UART cable connected

**Steps**:
```python
# Change interface to 'uart'
gpu = FluxGPU(interface='uart')

# Rest is identical!
gpu.load_program('vecadd.hex')
# ... same code ...
gpu.start_execution()
```

**UART Protocol**: See `firmware_guide.md` for packet format

---

## Common Patterns

### Pattern 1: Initialize Array

```python
def init_array(gpu, addr, values):
    """Helper to write array to memory"""
    gpu.write_memory(addr, values)
    return addr
```

### Pattern 2: Verify Results

```python
def check_result(got, expected, tolerance=1e-6):
    """Compare floating point results"""
    for i, (g, e) in enumerate(zip(got, expected)):
        diff = abs(g - e)
        assert diff < tolerance, f"Mismatch at {i}: {g} vs {e}"
    print("✓ All checks passed")
```

### Pattern 3: Benchmark

```python
import time

start = time.time()
gpu.start_execution()
elapsed = time.time() - start

print(f"Execution time: {elapsed*1000:.2f} ms")
```

---

## Debugging

### Enable Verbose Mode

```python
# In firmware_driver.py
gpu.start_execution(thread_mask=0x01)

# For simulation mode, modify:
sim.run(thread=0, verbose=True)  # Shows each instruction
```

### Dump Everything

```python
# After execution
gpu.dump_registers(thread_id=0, show_all=True)
gpu.dump_memory(0x0000, count=256)  # All memory
```

### Trace Execution

Add print statements to simulator:

```python
# In simulator.py execute_instruction()
print(f"PC={self.pc[thread]:04x} INSTR={instr:08x} ...")
```

---

## Next Steps

1. **Write your own program**: Start with simple arithmetic
2. **Profile performance**: Measure instruction count
3. **Port to FPGA**: Run on real hardware!
4. **Extend ISA**: Add new instructions (reduce, shuffle, etc.)

---

See `firmware_guide.md` for low-level protocol details.
