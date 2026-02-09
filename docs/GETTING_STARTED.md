# Getting Started with flux GPU

**Your first 30 minutes with flux - from zero to rendering triangles!**

---

## Step 1: Run the Math Demo (5 minutes)

**No installation needed!** Pure Python.

```bash
cd d:\Flux\flux
python examples\math_demo.py
```

**You'll see:**
- ✅ SIMD operations (4× speedup demo)
- ✅ Edge function algorithm (how triangles work)
- ✅ Triangle rasterization (actual GPU work)
- ✅ Performance calculations (FPS, throughput)
- ✅ Complete GPU simulation

**This shows you ALL the math behind the GPU!**

---

## Step 2: Try the Visual Demo (10 minutes)

Install matplotlib (one time):
```bash
pip install matplotlib
```

Run the visual demo:
```bash
python examples\visual_demo.py
```

**Generates 3 beautiful images:**
1. `edge_function_visualization.png` - See the math in color!
2. `rasterization_steps.png` - Step-by-step triangle drawing
3. `triangle_scene.png` - Multiple colored triangles

Open the images and study them!

---

## Step 3: Write Your First Assembly Program (10 minutes)

Create `my_first_program.s`:
```assembly
# Add two numbers
LI R1, 100        # Load 100 into R1
LI R2, 42         # Load 42 into R2
ADD R3, R1, R2    # R3 = R1 + R2 = 142
STORE R3, 0       # Store result at address 0
HALT
```

Assemble it:
```bash
python sw-toolchain\asm\assembler.py my_first_program.s
```

Run it:
```bash
python sw-toolchain\sim\simulator.py my_first_program.hex
```

**You just programmed a GPU!** 🎉

---

## Step 4: Draw a Triangle (5 minutes)

Create `my_triangle.py`:
```python
import sys
sys.path.append('hw-tools/firmware')
from firmware_driver import FluxGPU

# Create GPU (simulation mode)
gpu = FluxGPU(interface='simulation')

# Draw a red triangle
gpu.draw_triangle(
    v0=(100, 200),   # Bottom-left
    v1=(500, 200),   # Bottom-right
    v2=(300, 400),   # Top
    color=0xFF0000   # Red
)

print("✓ Triangle drawn!")
```

Run it:
```bash
python my_triangle.py
```

---

## What Next?

### Learn the Concepts (Read These)

1. **[Math Explained](file:///d:/Flux/flux/docs/MATH_EXPLAINED.md)** - All GPU math with examples
2. **[GPU Fundamentals](file:///d:/Flux/flux/docs/theory/gpu_fundamentals.md)** - How GPUs work
3. **[ISA Specification](file:///d:/Flux/flux/meta/specs/isa.md)** - All instructions

### Build Something

**Easy Projects:**
- Draw your initials in triangles
- Vector addition (add 1000 numbers)
- Matrix operations

**Medium Projects:**
- Mandelbrot set renderer
- 3D cube (project to 2D triangles)
- Simple physics simulation

**Hard Projects:**
- Ray tracer
- Particle system
- Add new instructions to the ISA

### Study the Hardware

**RTL Tour** (if you know Verilog):
1. `rtl/src/shader_core/shader_core.sv` - Main compute unit
2. `rtl/src/raster/rasterizer.sv` - Triangle drawing
3. `rtl/src/video/vga_controller.sv` - Display output

**Run Tests**:
```bash
cd rtl/test
pytest test_shader_core.py -v
```

---

## Common Questions

**Q: I don't know assembly. Can I still use flux?**  
A: Yes! Start with the Python examples (`math_demo.py`, `my_triangle.py`). Assembly is optional.

**Q: Do I need an FPGA board?**  
A: No! Everything works in simulation. FPGA is optional for hardware testing.

**Q: What if I get stuck?**  
A: Read the docs! We have 9,000+ lines covering everything from atoms to applications.

**Q: Can I modify flux?**  
A: Absolutely! It's 100% open-source. Fork it, break it, improve it!

---

## Quick Reference

### Important Files

```
flux/
├── examples/
│   ├── math_demo.py        ← Start here!
│   ├── visual_demo.py      ← See the visuals
│   ├── vecadd.s            ← Assembly example
│   └── README_MATH.md      ← Math examples guide
│
├── docs/
│   ├── MATH_EXPLAINED.md   ← All GPU math (read this!)
│   ├── EXTENSIONS.md       ← 18 ideas for improvements
│   └── theory/             ← Architecture deep-dives
│
├── sw-toolchain/
│   ├── asm/assembler.py    ← Assembly → Machine code
│   └── sim/simulator.py    ← Run programs
│
└── hw-tools/
    ├── firmware/           ← GPU control API
    └── graphics/           ← Triangle demos
```

### Cheat Sheet

**Assemble program:**
```bash
python sw-toolchain\asm\assembler.py program.s
```

**Run program:**
```bash
python sw-toolchain\sim\simulator.py program.hex
```

**Draw triangle:**
```python
from firmware_driver import FluxGPU
gpu = FluxGPU(interface='simulation')
gpu.draw_triangle(v0, v1, v2, color)
```

**See math:**
```bash
python examples\math_demo.py
```

**Visualize:**
```bash
python examples\visual_demo.py
```

---

## Learning Paths

### "I want to learn GPU programming"
1. Read MATH_EXPLAINED.md
2. Run math_demo.py
3. Write assembly programs
4. Study GPU fundamentals doc
5. Read ISA specification
6. Build projects!

### "I want to learn hardware design"
1. Read logic gates tutorial
2. Study GPU fundamentals
3. Read shader core RTL
4. Run Cocotb tests
5. Modify hardware
6. Synthesize for FPGA

### "I'm teaching a class"
1. Read beginner learning path (8-week course)
2. Use education index (all materials)
3. Assign hands-on projects
4. Show visual demos
5. Have students modify flux

### "I just want to see it work"
1. Run math_demo.py (2 minutes)
2. Run visual_demo.py (3 minutes)
3. Done! You've seen a working GPU.

---

## Next Steps

After this getting started guide:

**Beginner → Intermediate:**
- [8-Week Learning Path](file:///d:/Flux/flux/docs/tutorials/beginner_learning_path.md)
- [Education Index](file:///d:/Flux/flux/docs/EDUCATION_INDEX.md)

**Intermediate → Advanced:**
- [Extensions Guide](file:///d:/Flux/flux/docs/EXTENSIONS.md)
- [FPGA Testing](file:///d:/Flux/flux/hw-tools/fpga/TESTING.md)

**Complete Reference:**
- [Final Report](file:///d:/Flux/flux/FINAL_REPORT.md)
- [Project Summary](file:///d:/Flux/flux/PROJECT_SUMMARY.md)

---

**Ready? Let's start!** 🚀

```bash
python examples\math_demo.py
```
