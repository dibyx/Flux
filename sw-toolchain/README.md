# flux Software Toolchain

Complete software development tools for the flux GPU.

---

## Components

### 1. Assembler ([asm/](asm/))

Converts assembly language to machine code.

**Usage**:
```bash
cd asm
python assembler.py ../examples/vecadd.s
# → vecadd.bin, vecadd.hex
```

**Features**:
- Full ISA support (R/I/S/B-type)
- Label resolution
- Binary & hex output formats
- Error reporting

**See**: [asm/README.md](asm/README.md)

---

### 2. Simulator ([sim/](sim/))

Software model for rapid testing.

**Usage**:
```bash
cd sim
python simulator.py ../examples/vecadd.hex
```

**Features**:
- 1000× faster than RTL simulation
- SIMD execution (4-wide FP32)
- Register & memory inspection
- Execution statistics

**See**: [sim/README.md](sim/README.md)

---

### 3. Example Programs ([examples/](examples/))

Sample assembly programs demonstrating the ISA:

| Program | Description |
|---------|-------------|
| [vecadd.s](examples/vecadd.s) | Vector addition (SIMD) |
| [dotprod.s](examples/dotprod.s) | Dot product |
| [loop.s](examples/loop.s) | Loop with branches |
| [conditional.s](examples/conditional.s) | If-else statements |

---

## Quick Start Workflow

### 1. Write Assembly
```assembly
# myprogram.s
LI R1, 10
ADDI R2, R1, 5
HALT
```

### 2. Assemble
```bash
python asm/assembler.py examples/myprogram.s
```

### 3. Simulate
```bash
python sim/simulator.py examples/myprogram.hex --verbose
```

### 4. View Results
Check register values and memory contents in simulator output.

---

## Directory Structure

```
sw-toolchain/
├── asm/
│   ├── assembler.py      # Assembler implementation
│   └── README.md          # Assembler docs
├── sim/
│   ├── simulator.py       # Instruction simulator
│   └── README.md          # Simulator docs
└── examples/
    ├── vecadd.s           # Vector addition
    ├── dotprod.s          # Dot product
    ├── loop.s             # Loop example
    └── conditional.s      # Conditional example
```

---

## Requirements

- **Python 3.7+** (no external dependencies!)
- Standard library only:
  - `struct` (FP32 packing)
  - `sys`, `re` (parsing)

---

## Future Tools

Planned additions:
- **Compiler**: C → flux assembly (LLVM backend)
- **Debugger**: GDB-style interactive debugging
- **Profiler**: Performance analysis
- **Runtime**: Kernel launch and memory management

---

## Integration with Hardware

### Run on RTL Simulation
1. Assemble: `python asm/assembler.py program.s`
2. Load hex file in testbench: `$readmemh("program.hex", imem);`
3. Run: `make test`

### Run on FPGA
1. Assemble to binary: `program.bin`
2. Flash to instruction BRAM
3. Program FPGA: `cd ../../hw-tools/fpga && make prog`

---

See [ISA Specification](../docs/specs/isa.md) for complete instruction reference.
