# flux GPU - Quick Reference Card

**One-page guide to the complete flux GPU platform**

---

## 📁 Project Structure

```
flux/
├── docs/                       # 8,000+ lines documentation
│   ├── fundamentals/          # Physics, gates, materials (3k lines)
│   ├── theory/                # GPU architecture (2k lines)
│   ├── setup/                 # Installation guides (1.5k lines)
│   ├── tutorials/             # 8-week course (600 lines)
│   └── specs/                 # ISA specification (500 lines)
├── rtl/src/shader_core/       # 450 lines SystemVerilog
│   ├── instruction_decoder.sv
│   ├── simd_alu.sv
│   ├── register_file.sv
│   └── shader_core.sv
├── sw-toolchain/              # 1,300+ lines Python
│   ├── asm/                   # Assembler (300 lines)
│   ├── sim/                   # Simulator (350 lines)
│   └── examples/              # 4 assembly programs
├── hw-tools/
│   ├── fpga/                  # Synthesis scripts (Yosys, nextpnr)
│   └── firmware/              # GPU driver (400 lines) + examples
└── meta/
    ├── roadmap.md             # Progress tracking
    └── LEGAL.md               # Licensing
```

---

## 🚀 Quick Start Commands

### Write & Run Assembly

```bash
# 1. Write program
cat > test.s << EOF
LI R1, 42
ADDI R2, R1, 8
HALT
EOF

# 2. Assemble
python sw-toolchain/asm/assembler.py test.s

# 3. Simulate
python sw-toolchain/sim/simulator.py test.hex
```

### Use Firmware API

```python
from hw_tools.firmware.firmware_driver import FluxGPU

gpu = FluxGPU(interface='simulation')
gpu.load_program('program.hex')
gpu.write_memory(0x1000, [1.0, 2.0, 3.0, 4.0])
gpu.start_execution()
result = gpu.read_memory(0x3000, 4)
```

### Synthesize for FPGA

```bash
cd hw-tools/fpga
make all          # Synthesize + P&R + bitstream
make report       # Resource usage
make prog         # Program ULX3S (if connected)
```

---

## 📚 Learning Paths

### For Complete Beginners
→ [`docs/tutorials/beginner_learning_path.md`](docs/tutorials/beginner_learning_path.md)
- 8-week structured course
- No prerequisites

### For Programmers
1. ISA Spec: `docs/specs/isa.md`
2. Write assembly: `sw-toolchain/examples/`
3. Use assembler & simulator

### For Hardware Engineers
1. GPU Theory: `docs/theory/gpu_fundamentals.md`
2. Study RTL: `rtl/src/shader_core/*.sv`
3. FPGA synthesis: `hw-tools/fpga/`

### For Students (Any Major)
1. Education Index: `docs/EDUCATION_INDEX.md`
2. Choose path by background (CS/EE/Chem)
3. Follow structured materials

---

## 🔧 Key Features

### ISA (Instruction Set)
- **12 instructions**: ADD, SUB, MUL, DIV, ADDI, LI, LOAD, STORE, BEQ, BNE, JAL, HALT
- **Encoding**: RISC-V-inspired 32-bit
- **SIMD**: 4-wide FP32 (128-bit registers)

### Hardware
- **Shader Core**: Decoder + ALU + RegFile
- **FPGA**: 8k LUTs @ 50 MHz (ULX3S)
- **Verified**: All Cocotb tests passing ✓

### Software
- **Assembler**: Full ISA support, binary output
- **Simulator**: 1000× faster than RTL
- **Firmware**: Complete API (sim/UART/PCIe)

---

## 📖 Documentation Map

| Topic | File | Lines |
|-------|------|-------|
| **Getting Started** | `docs/setup/quick_start.md` | 279 |
| **GPU Basics** | `docs/theory/gpu_fundamentals.md` | 322 |
| **Transistors** | `docs/fundamentals/semiconductor_physics.md` | 1000+ |
| **Logic Gates** | `docs/fundamentals/logic_gates_tutorial.md` | 1000+ |
| **Materials** | `docs/fundamentals/materials_science.md` | 1000+ |
| **ISA Reference** | `docs/specs/isa.md` | 500+ |
| **Toolchain Setup** | `docs/setup/toolchain_guide.md` | 402 |
| **FPGA Build** | `docs/setup/fpga_build.md` | 160 |
| **Firmware** | `hw-tools/firmware/firmware_guide.md` | 500+ |
| **8-Week Course** | `docs/tutorials/beginner_learning_path.md` | 600+ |

---

## 🎯 Common Tasks

### Task: Run Vector Addition

```bash
cd sw-toolchain/asm
python assembler.py ../examples/vecadd.s
cd ../sim
python simulator.py ../examples/vecadd.hex
# Output: [6.0, 8.0, 10.0, 12.0]
```

### Task: Debug Assembly Program

```python
# Add --verbose to see each instruction
python simulator.py program.hex --verbose

# Or dump registers
sim.dump_registers(thread_id=0, show_all=True)
```

### Task: Check FPGA Resources

```bash
cd hw-tools/fpga
make all
make report
# Shows: LUTs, FFs, BRAMs
```

### Task: Write Custom Assembly

```assembly
# my_program.s
LI R1, 10       # R1 = 10
LI R2, 20       # R2 = 20
ADD R3, R1, R2  # R3 = R1 + R2 = 30
HALT
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| **"Command not found"** | Add `python` before script name |
| **Assembly errors** | Check syntax vs `docs/specs/isa.md` |
| **Wrong results** | Verify inputs with `dump_memory()` |
| **Synthesis fails** | Check file paths in `synth.ys` |
| **UART timeout** | Verify port: `/dev/ttyUSB0` or `COM3` |

---

## 📊 Specifications

### Hardware

| Spec | Value |
|------|-------|
| Cores | 1 shader core |
| SIMD Width | 4 (FP32) |
| Threads | 32 |
| Registers | 32 × 128-bit per thread |
| Memory | 64 KB (simulation) |
| Frequency | 50 MHz (target) |
| FPGA | ULX3S (ECP5 LFE5U-85F) |
| Resource | ~8k LUTs (9%) |

### Software

| Component | Language | Lines |
|-----------|----------|-------|
| Assembler | Python | 300 |
| Simulator | Python | 350 |
| Firmware | Python | 400 |
| RTL | SystemVerilog | 450 |
| Docs | Markdown | 8,000+ |

---

## 🔗 External Resources

**Online Simulators**:
- Logic gates: [LogicBruno](https://logibruno.web.app/)
- Build computer: [NandGame](https://nandgame.com/)
- Verilog practice: [HDLBits](https://hdlbits.01xz.net/)

**Videos**:
- "How Transistors Work" - Ben Eater
- "From Sand to Silicon" - Intel
- "Chip Manufacturing" - ASML

**Books**:
- "Digital Design" - Harris & Harris
- "Computer Architecture" - Patterson & Hennessy

---

## 📝 License

- **Hardware**: CERN-OHL-S (open hardware)
- **Software**: Apache 2.0 (permissive)
- **Docs**: CC-BY-SA 4.0 (attribution)

---

## 📈 Project Stats

- **Total Lines**: ~10,000
- **Files**: 50+
- **Phases**: 5 complete
- **Status**: Educational prototype ready ✅

---

**Print this card for quick reference!** 📄

For complete docs: See `docs/EDUCATION_INDEX.md`
