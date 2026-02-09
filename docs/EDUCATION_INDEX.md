# flux Educational Resources Index

**Complete guide to all learning materials**

---

## For Complete Beginners

👉 **Start here**: [Beginner's Learning Path](tutorials/beginner_learning_path.md)
- 8-week structured course
- No prerequisites beyond high school science
- Hands-on exercises and projects

---

## Foundational Knowledge

### 1. **Semiconductor Physics**
📄 [semiconductor_physics.md](fundamentals/semiconductor_physics.md)

**Topics**:
- Atoms to transistors
- Silicon crystals and doping (N-type, P-type)
- MOSFET operation
- Manufacturing process (photolithography, CVD, PVD)
- Modern process nodes (5nm, 3nm)
- Quantum effects at small scales

**Best for**: Understanding WHY chips work at the atomic level

---

### 2. **Logic Gates & Digital Design**
📄 [logic_gates_tutorial.md](fundamentals/logic_gates_tutorial.md)

**Topics**:
- All basic gates (NOT, AND, OR, XOR, NAND, NOR)
- Building adders from gates
- Memory elements (flip-flops, latches)
- Multiplexers and ALU design
- Hands-on exercises with online simulators

**Best for**: Bridging from transistors to digital logic

---

### 3. **Materials Science**
📄 [materials_science.md](fundamentals/materials_science.md)

**Topics**:
- Why different materials? (Si, SiO₂, Cu, HfO₂)
- Chemical properties and reactions
- Deposition techniques (PVD, CVD, ALD)
- Ion implantation and doping
- Purity requirements (99.9999999%)
- Sustainability and environmental impact

**Best for**: Chemistry students and materials engineers

---

## GPU-Specific Theory

### 4. **GPU Fundamentals**
📄 [gpu_fundamentals.md](theory/gpu_fundamentals.md)

**Topics**:
- Why GPUs exist (parallelism for graphics)
- SIMT execution model
- GPU vs CPU architecture
- Memory hierarchy
- Performance metrics

**Best for**: Understanding the big picture

---

### 5. **Graphics Pipeline**
📄 [pipeline_explained.md](theory/pipeline_explained.md)

**Topics**:
- Vertex processing
- Rasterization
- Fragment shading
- Output merging
- Compute shaders

**Best for**: Graphics programmers

---

### 6. **Memory Systems**
📄 [memory_systems.md](theory/memory_systems.md)

**Topics**:
- Memory hierarchy (registers → VRAM)
- Bandwidth optimization
- Caching strategies
- Coalescing
- Tiling techniques

**Best for**: Performance optimization

---

## Practical Guides

### 7. **ISA Specification**
📄 [isa.md](specs/isa.md)

**Topics**:
- Complete instruction set (12 instructions)
- Instruction formats (R/I/S/B-type)
- Encoding examples
- Assembly language syntax
- SIMD execution model

**Best for**: Assembly programmers

---

### 8. **Firmware Programming**
📄 [firmware_guide.md](../hw-tools/firmware/firmware_guide.md)

**Topics**:
- What is firmware?
- Boot process
- Command protocol
- Loading programs to GPU
- Debugging techniques
- Python examples

**Best for**: Low-level system programmers

---

## Setup & Tooling

### 9. **Quick Start**
📄 [quick_start.md](setup/quick_start.md)

**Topics**:
- 15-minute getting started
- Run first simulation
- Assemble first program

**Best for**: Impatient learners! (we've all been there)

---

### 10. **Toolchain Guide**
📄 [toolchain_guide.md](setup/toolchain_guide.md)

**Topics**:
- Installing all tools (Yosys, Verilator, Python)
- HDL simulation setup
- FPGA toolchain
- ASIC flow (OpenLane)

**Best for**: Setting up development environment

---

### 11. **FPGA Build Guide**
📄 [fpga_build.md](setup/fpga_build.md)

**Topics**:
- Synthesizing flux for ULX3S
- Resource usage analysis
- Timing constraints
- Programming the board
- Troubleshooting

**Best for**: FPGA prototyping

---

## Learning Paths by Background

### For Computer Science Students
1. GPU Fundamentals
2. ISA Specification
3. Software Toolchain (assembler/simulator)
4. Assembly programming
5. Firmware basics
6. (Optional) RTL overview

### For Electrical Engineering Students
1. Semiconductor Physics
2. Logic Gates Tutorial
3. Materials Science
4. GPU Fundamentals
5. RTL deep dive
6. FPGA synthesis

### For Chemistry Students
1. Materials Science (start here!)
2. Semiconductor Physics (focus on doping)
3. Manufacturing processes
4. (Optional) GPU overview
5. (Optional) Simple assembly programs

### For Complete Beginners
👉 Follow the [8-week learning path](tutorials/beginner_learning_path.md) which integrates everything!

---

## Interactive Resources

### Online Simulators
- **Logic gates**: [LogicBruno](https://logibruno.web.app/)
- **Build computer**: [NandGame](https://nandgame.com/)
- **Verilog practice**: [HDLBits](https://hdlbits.01xz.net/)

### Videos (Recommended)
- "How Transistors Work" - Ben Eater
- "From Sand to Silicon" - Intel
- "Microchip Manufacturing" - ASML

### Books
- "Digital Design and Computer Architecture" - Harris & Harris
- "Computer Organization and Design" - Patterson & Hennessy
- "CMOS VLSI Design" - Weste & Harris

---

## Quick Reference

| I want to... | Read this |
|--------------|-----------|
| Understand atoms → transistors | [Semiconductor Physics](fundamentals/semiconductor_physics.md) |
| Learn logic gates | [Logic Gates Tutorial](fundamentals/logic_gates_tutorial.md) |
| Understand materials in chips | [Materials Science](fundamentals/materials_science.md) |
| Write assembly programs | [ISA Spec](specs/isa.md) |
| Program the GPU (firmware) | [Firmware Guide](../hw-tools/firmware/firmware_guide.md) |
| Synthesize for FPGA | [FPGA Build](setup/fpga_build.md) |
| Follow structured course | [Beginner Path](tutorials/beginner_learning_path.md) |

---

## Documentation Statistics

| Category | Files | Total Lines |
|----------|-------|-------------|
| Fundamentals | 3 | ~3,000 |
| Theory | 3 | ~2,000 |
| Setup | 3 | ~1,500 |
| Specs | 1 | ~500 |
| Tutorials | 1 | ~600 |
| Firmware | 1 | ~500 |
| **Total** | **12** | **~8,000+** |

**All content**: Free and open-source (CC-BY-SA 4.0)

---

## Contributing

Found a typo? Want to add content?

1. Fork the repo
2. Edit markdown files
3. Submit pull request
4. Help others learn!

**Guidelines**:
- Keep explanations simple
- Add diagrams where possible
- Include hands-on exercises
- Test all code examples

---

## Contact & Support

**Questions?**
- GitHub Issues: Technical problems
- GitHub Discussions: Learning questions
- Discord: Real-time chat (coming soon!)

---

**flux**: Making GPU knowledge accessible to everyone 🌍
