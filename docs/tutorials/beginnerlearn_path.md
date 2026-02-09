# Beginner's Learning Path for flux GPU

**A structured 8-week course for college students with no prior hardware experience**

---

## Course Overview

**Goal**: Understand GPUs from atoms to applications

**Prerequisites**: 
- Basic programming (Python or C)
- High school physics & chemistry
- Enthusiasm to learn!

**Time commitment**: ~10 hours/week

---

## Week 1: Foundations - From Sand to Silicon

### Learning Objectives
- Understand atoms, electrons, and semiconductors
- Learn how transistors work
- See how geometry affects chip design

### Materials
📖 **Read**:
- [Semiconductor Physics](../fundamentals/semiconductor_physics.md) - Sections 1-3
- Focus on: Silicon atoms, doping, MOSFET basics

🎥 **Watch**:
- "How Transistors Work" (Ben Eater): [YouTube](https://www.youtube.com/watch?v=IcrBqCFLHIY)
- "From Sand to Silicon": [YouTube](https://www.youtube.com/watch?v=_VMYPLXnd7E)

### Hands-On Activities
1. **Draw a MOSFET**: Paper sketch with labels
2. **Calculate doping**: If 1 cm³ has 10²² Si atoms, how many dopants for 10¹⁶/cm³?
3. **Quiz yourself**: Can you explain N-type vs P-type to a friend?

### Assessment
**Project**: Write a 1-page report explaining why silicon (not copper or carbon) is used for chips.

**Expected time**: 8-10 hours

---

## Week 2: Logic Gates - Building Blocks

### Learning Objectives
- Understand all basic logic gates
- Build an adder from gates
- See connection to transistors

### Materials
📖 **Read**:
- [Logic Gates Tutorial](../fundamentals/logic_gates_tutorial.md) - Complete
- Pay extra attention to the half-adder example

🎮 **Interactive**:
- Play [NandGame](https://nandgame.com/) - Levels 1-10
- Build computer from NAND gates (seriously, it's fun!)

### Hands-On Activities
1. **Truth tables**: Create for all 6 basic gates
2. **Build full adder**: Use online simulator ([LogicBruno](https://logibruno.web.app/))
3. **Count transistors**: How many in a 32-bit adder?

### Programming Exercise
```python
# Simulate gates in Python
def NAND(a, b):
    return not (a and b)

def XOR(a, b):
    # Build using only NAND gates
    # Your code here!
    pass

# Test
assert XOR(0, 0) == 0
assert XOR(0, 1) == 1
assert XOR(1, 1) == 0
```

**Expected time**: 10-12 hours

---

## Week 3: Materials & Manufacturing

### Learning Objectives
- Understand chip fabrication process
- Learn about different materials (Si, Cu, HfO₂)
- Appreciate purity requirements

### Materials
📖 **Read**:
- [Materials Science](../fundamentals/materials_science.md) - Sections 1-5
- Skip quantum effects for now (come back later!)

🎥 **Watch**:
- "How Microchips Are Made" (Intel): [YouTube](https://www.youtube.com/watch?v=d9SWNLZvA8g)
- "Inside a Clean Room" tour

### Virtual Lab
- Explore [ChipTown](https://www.youtube.com/watch?v=35jWSQXXQgY) animation (ASML)
- Write down each step: Deposition → Lithography → Etching

### Assessment
**Lab Report**: Choose one material (Cu, SiO₂, or HfO₂) and explain:
1. Its properties (melting point, conductivity, etc.)
2. Why it's used in GPUs
3. How it's deposited (PVD, CVD, etc.)

**Expected time**: 8-10 hours

---

## Week 4: GPU Architecture Overview

### Learning Objectives
- Understand GPU vs CPU differences
- Learn SIMT execution model
- See big picture of GPU components

### Materials
📖 **Read**:
- [GPU Fundamentals](../theory/gpu_fundamentals.md) - Complete
- [Pipeline Explained](../theory/pipeline_explained.md) - Sections 1-2

📊 **Study Diagrams**:
- GPU Architecture Overview (printed large!)
- Trace data flow from memory → shader → output

### Discussion Questions
1. Why parallel processing for graphics?
2. What is a "thread" in GPU context?
3. How does SIMT differ from SIMD?

### Mini-Project
**Compare**: Create a table comparing:
- CPU (your laptop)
- GPU (any modern card)

| Feature | CPU | GPU |
|---------|-----|-----|
| Cores | 8 | ??? |
| Threads | 16 | ??? |
| Clock Speed | 3 GHz | ??? |
| Memory BW | 50 GB/s | ??? |

Use Google to fill in GPU specs!

**Expected time**: 10 hours

---

## Week 5: ISA & Assembly Programming

### Learning Objectives
- Understand Instruction Set Architecture
- Write simple assembly programs
- Use the flux assembler

### Materials
📖 **Read**:
- [ISA Specification](../specs/isa.md) - Sections 1-4
- Focus on instruction formats and encoding

🛠️ **Setup Environment**:
```bash
# Install Python (if needed)
# Navigate to flux directory
cd flux/sw-toolchain/asm
python assembler.py --help
```

### Programming Exercises

**Exercise 1**: Hello World (GPU style)
```assembly
# Initialize R1 with value 42
LI R1, 42
HALT
```
Assemble and verify output!

**Exercise 2**: Add two numbers
```assembly
LI R1, 10
LI R2, 20
ADD R3, R1, R2  # R3 should be 30
HALT
```

**Exercise 3**: Vector addition (use existing example)
```bash
python assembler.py ../examples/vecadd.s
# Study the output
```

**Challenge**: Modify `vecadd.s` to multiply instead of add

### Assessment
**Program**: Write assembly to compute:
```
result = (A + B) * C
Where A=2, B=3, C=4
Expected: 20
```

**Expected time**: 12-14 hours

---

## Week 6: Simulation & Verification

### Learning Objectives
- Run programs in the simulator
- Debug assembly code
- Understand register flow

### Materials
📖 **Read**:
- [Simulator README](../sw-toolchain/sim/README.md)
- Study the implementation (optional but valuable!)

### Hands-On Labs

**Lab 1**: Run and trace
```bash
python sim/simulator.py examples/vecadd.hex --verbose
# Study each instruction step-by-step
```

**Lab 2**: Debugging
- Write buggy program (infinite loop!)
- See how simulator times out
- Fix the bug

**Lab 3**: Performance analysis
```bash
python sim/simulator.py examples/loop.s
# How many instructions executed?
# How many memory accesses?
# Calculate IPC
```

### Project
**Benchmark Suite**: Create 5 test programs:
1. Arithmetic (add, sub, mul, div)
2. Memory (load/store)
3. Branches (if-else)
4. Loops
5. Complex (combine all)

Run each, collect statistics, compare!

**Expected time**: 12 hours

---

## Week 7: RTL & Hardware Design

### Learning Objectives
- Read SystemVerilog code
- Understand hardware modules
- See gates → RTL connection

### Materials
📖 **Study Code**:
```
rtl/src/shader_core/
├── instruction_decoder.sv  ← Start here (simplest)
├── simd_alu.sv            ← Then this
├── register_file.sv       ← Memory element
└── shader_core.sv         ← Integration
```

**Read each file top-to-bottom**, write comments explaining what you understand.

🎥 **Watch**:
- "Introduction to SystemVerilog" (Nandland)
- "Hardware Description Languages" (MIT 6.111)

### Exercises

**Exercise 1**: Annotate code
```systemverilog
// instruction_decoder.sv line 20
assign opcode = instruction[6:0];
// YOUR EXPLANATION: _______________
```

**Exercise 2**: Trace signal
Pick one signal (e.g., `alu_op`), trace it from decoder → ALU → result

**Exercise 3**: Modify RTL (advanced)
Add a new instruction: `INC R1` (increment by 1)
- Update decoder
- Update ALU
- Test with assembler + simulator

**Expected time**: 14-16 hours

---

## Week 8: FPGA Synthesis & Final Project

### Learning Objectives
- Synthesize RTL to FPGA
- Understand resource usage
- Complete end-to-end workflow

### Materials
📖 **Read**:
- [FPGA Build Guide](../setup/fpga_build.md)
- [Toolchain Setup](../setup/toolchain_guide.md) - FPGA section

### Setup (if you have ULX3S board)
```bash
# Install tools
sudo apt install yosys nextpnr-ecp5

# Synthesize
cd hw-tools/fpga
make all
```

**No board?** Use simulation instead:
```bash
cd rtl/test
make
# Run Verilator simulation
```

### Final Project Options

**Option A: Software** (Recommended for beginners)
- Write 3 complex assembly programs
- Benchmark on simulator
- Document performance
- Report: 5 pages + code

**Option B: Hardware** (If you know Verilog)
- Add new instruction to ISA
- Modify RTL
- Update assembler
- Verify with tests
- Report: Implementation details

**Option C: Theory** (Research-oriented)
- Deep dive into one topic (memory hierarchy, rasterization, etc.)
- Compare flux to real GPUs (NVIDIA, AMD)
- Propose improvements
- Report: 10 pages

### Presentation
- 10-minute video explaining your project
- Live demo (simulator or FPGA)
- Code walkthrough

**Expected time**: 20+ hours

---

## Post-Course: What's Next?

### Advanced Topics
1. **Memory Hierarchy**: Implement L1 cache
2. **Parallel Execution**: Multi-core shader
3. **Graphics Pipeline**: Add rasterizer
4. **Compiler**: LLVM backend for flux
5. **ASIC**: Explore OpenLane flow

### Career Paths
- **Hardware Engineer**: RTL design, verification
- **GPU Architect**: Performance optimization
- **Driver Developer**: Software/hardware interface
- **Research**: Novel GPU architectures

### Resources
**Communities**:
- [Reddit r/FPGA](https://reddit.com/r/FPGA)
- Discord: Hardware dev servers
- Stack Overflow: FPGA/Verilog tags

**Further Learning**:
- "Computer Architecture" by Hennessy & Patterson
- MIT 6.004 (Computation Structures)
- UC Berkeley CS152 (Computer Architecture)

---

## Assessment Rubric

| Week | Deliverable | Weight |
|------|-------------|--------|
| 1 | MOSFET report | 5% |
| 2 | Gate exercises | 10% |
| 3 | Materials lab | 10% |
| 4 | GPU comparison | 10% |
| 5 | Assembly programs | 15% |
| 6 | Benchmark suite | 15% |
| 7 | RTL annotations | 10% |
| 8 | Final project | 25% |

**Total**: 100%

**Grading Scale**:
- A: 90-100% (Excellent understanding)
- B: 80-89% (Good progress)
- C: 70-79% (Satisfactory)
- D: 60-69% (Needs improvement)

---

## Tips for Success

1. **Start early**: Don't cram hardware learning
2. **Ask questions**: Use forums, Discord,GitHub issues
3. **Draw diagrams**: Visualize everything
4. **Code daily**: Even 30 minutes helps
5. **Collaborate**: Study groups are powerful
6. **Be curious**: Follow tangents if interesting!

---

## Common Pitfalls

❌ **Skipping fundamentals**: Don't jump to RTL without understanding gates  
❌ **Not testing code**: Always verify assembly with simulator  
❌ **Ignoring errors**: Synthesis warnings matter!  
❌ **Passive learning**: Hardware requires hands-on practice  

✅ **Fix**: Do every exercise, type every command yourself

---

## Support Resources

**Stuck? Try these**:
1. Re-read the markdown docs (seriously!)
2. Search error messages online
3. Ask on [GitHub Discussions](https://github.com/your-org/flux/discussions)
4. Email: flux-edu@example.com
5. Office hours: TBD

---

**Good luck on your GPU journey!** 🚀

Remember: Every expert was once a beginner. The flux GPU is designed for YOUR success.

---

**Course developed for**: Computer Engineering, Electrical Engineering, and Computer Science students at the undergraduate level (years 2-4).

**License**: CC-BY-SA 4.0 (free to use, modify, and share with attribution)
