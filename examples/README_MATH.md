# flux GPU - Math Examples

**Runnable Python code demonstrating all GPU math concepts**

---

## Quick Start

### Basic Demo (No Dependencies)

```bash
python math_demo.py
```

This will show you:
1. ✅ SIMD operations (4× speedup)
2. ✅ Edge function algorithm
3. ✅ Bounding box optimization
4. ✅ Triangle rasterization
5. ✅ Memory addressing (2D → 1D)
6. ✅ Floating-point representation
7. ✅ Instruction encoding
8. ✅ Performance calculations
9. ✅ Complete GPU simulation

**No external libraries needed!** Pure Python.

### Visual Demo (Requires matplotlib)

```bash
# Install matplotlib first
pip install matplotlib

# Run visual demo
python visual_demo.py
```

This creates beautiful visualizations:
- 📊 Edge function heatmaps
- 📊 Step-by-step rasterization
- 📊 Multi-triangle scenes

**Generates PNG images you can share!**

---

## What's Inside

### math_demo.py

**Complete, working examples** of all GPU math:

```python
# Example: Test if point is inside triangle
V0 = (100, 100)
V1 = (400, 100)
V2 = (250, 300)
P = (200, 150)

result = inside_triangle(P, V0, V1, V2)
print(f"Inside? {result}")  # True!
```

**All functions are copy-paste ready!**

### visual_demo.py

**3 beautiful visualizations**:

1. **Edge Function Heatmap**
   - Shows positive/negative regions
   - Color-coded by distance
   - All 3 edges + combined result

2. **Rasterization Steps**
   - Step 1: Bounding box
   - Step 2: Pixel testing
   - Step 3: Final filled triangle

3. **Multi-Triangle Scene**
   - Multiple colored triangles
   - Alpha blending
   - Looks like real GPU output!

---

## Example Output

### math_demo.py

```
============================================================
1. SIMD DEMONSTRATION
============================================================

Vector A: [1.0, 2.5, 3.7, 4.2]
Vector B: [0.5, 1.5, 2.3, 3.8]
Result C: [1.5, 4.0, 6.0, 8.0]

✓ All 4 additions happened in ONE operation!

Performance:
  CPU (sequential): 4 operations
  GPU (SIMD):       1 operation
  Speedup:          4×

============================================================
2. EDGE FUNCTION - TRIANGLE RASTERIZATION
============================================================

Triangle vertices:
  V0: (100, 100)
  V1: (400, 100)
  V2: (250, 300)

Testing points:

  Point (200, 150) - Inside (center-top)
    e0 =    15000, e1 =    32500, e2 =    12500
    Result: ✓ INSIDE

  Point (100, 50) - Outside (above)
    e0 =        0, e1 =   -20000, e2 =    45000
    Result: ✗ OUTSIDE

...
```

### visual_demo.py

Generates 3 PNG images showing:
- Edge function behavior
- Pixel-by-pixel rasterization
- Beautiful colored triangles

---

## Interactive Challenges

Try modifying the code:

### Challenge 1: Different Triangles

```python
# In math_demo.py, change these:
V0 = (50, 50)     # Your coordinates
V1 = (300, 80)
V2 = (150, 400)
```

### Challenge 2: More Colors

```python
# In visual_demo.py, add triangles:
triangles = [
    ((100, 100), (400, 100), (250, 300), 0xFF0000, "Red"),
    ((200, 200), (500, 300), (350, 450), 0xFFFF00, "Yellow"),  # Add this!
]
```

### Challenge 3: Performance Testing

```python
# In math_demo.py, test bigger triangles:
triangle_sizes = {
    "Giant (600×400)": 240_000,  # Add this!
}
```

### Challenge 4: Edge Function Math

Try calculating edge function by hand:
```
V0 = (0, 0)
V1 = (100, 0)  
P = (50, 50)

e = (y0 - y1) × px + (x1 - x0) × py + x0×y1 - x1×y0
e = (0 - 0) × 50 + (100 - 0) × 50 + 0×0 - 100×0
e = 0 + 5000 + 0 - 0 = 5000

Positive → point is on the left ✓
```

---

## Code Structure

### math_demo.py Functions

```python
# SIMD
simd_add(a_vec, b_vec)          # Add 4 numbers at once

# Triangle rasterization
edge_function(v0, v1, p)         # Calculate edge function
inside_triangle(p, v0, v1, v2)   # Inside test
get_bounding_box(v0, v1, v2)     # Optimization

# Full rasterizer
class Framebuffer:               # Pixel storage
    set_pixel(x, y, color)
    get_pixel(x, y)

rasterize_triangle(fb, v0, v1, v2, color)

# Memory
pixel_to_address(x, y, width)    # 2D → 1D
address_to_pixel(addr, width)    # 1D → 2D

# Floating-point
float_to_bits(f)                 # See the binary
bits_to_float(b)                 # Convert back

# Instructions
encode_r_type(...)               # Encode ADD, SUB, MUL
encode_i_type(...)               # Encode ADDI, LOAD

# Complete GPU
class SimpleGPU:
    draw_triangle(v0, v1, v2, color)
```

### visual_demo.py Functions

```python
visualize_edge_function(v0, v1, v2)     # Heatmap
visualize_rasterization_steps(v0, v1, v2)  # Step-by-step
visualize_scene(triangles)               # Multi-triangle
```

---

## Learning Path

**For beginners**, run in this order:

1. **math_demo.py** - See all math concepts
   ```bash
   python math_demo.py > output.txt
   # Read output.txt to understand each concept
   ```

2. **Read the code** - Understand how it works
   - Start with `simd_add()` (simplest)
   - Then `edge_function()` (core algorithm)
   - Finally `rasterize_triangle()` (complete)

3. **visual_demo.py** - See it visually
   ```bash
   python visual_demo.py
   # Study the generated PNG images
   ```

4. **Modify and experiment**
   - Change triangle coordinates
   - Add more triangles
   - Try different colors
   - Break things and fix them!

---

## Understanding the Output

### SIMD Example

```
Vector A: [1.0, 2.5, 3.7, 4.2]
Vector B: [0.5, 1.5, 2.3, 3.8]
Result C: [1.5, 4.0, 6.0, 8.0]
```

**What happened**:
- Lane 0: 1.0 + 0.5 = 1.5 ✓
- Lane 1: 2.5 + 1.5 = 4.0 ✓
- Lane 2: 3.7 + 2.3 = 6.0 ✓
- Lane 3: 4.2 + 3.8 = 8.0 ✓

All 4 additions in **one operation**!

### Edge Function Example

```
Point (200, 150) - Inside
  e0 = 15000, e1 = 32500, e2 = 12500
```

**What this means**:
- All three values are **positive**
- Point is on the **same side** of all 3 edges
- Therefore, point is **INSIDE** the triangle ✓

### Performance Example

```
Small (100×100) (10,000 cycles):
  Time:       200.0 μs
  Throughput: 5000 triangles/second
```

**Translation**:
- 10,000 clock cycles to rasterize
- At 50 MHz: 200 microseconds
- Can draw 5,000 triangles per second
- That's **83 FPS** if each frame has 60 triangles!

---

## Tips & Tricks

### Performance

**Fast testing**: Comment out print statements
```python
def rasterize_triangle(fb, v0, v1, v2, color):
    # print(f"Rasterizing...")  # Comment out for speed
    ...
```

### Debugging

**Add visualization**:
```python
# See intermediate values
def edge_function(v0, v1, p):
    result = (y0 - y1) * px + (x1 - x0) * py + x0*y1 - x1*y0
    print(f"Edge: v0={v0}, v1={v1}, p={p} → {result}")  # Debug
    return result
```

### Experimentation

**Try extreme cases**:
```python
# Degenerate triangle (line)
V0 = (100, 100)
V1 = (200, 100)  
V2 = (300, 100)  # All on same line!

# What happens?
```

---

## Further Exploration

After mastering these examples:

1. **Optimize the code**
   - Use NumPy for faster arrays
   - Parallelize with multiprocessing
   - Profile with cProfile

2. **Add features**
   - Z-buffer (depth testing)
   - Texture mapping
   - Antialiasing

3. **Compare to real GPU**
   - Time your Python code
   - vs flux GPU simulator
   - vs actual GPU (if you have hardware)

4. **Build something cool**
   - Draw your name in triangles
   - Render a 3D cube
   - Make an animation

---

## Questions?

**"Why is my output different?"**
- Check Python version (need 3.7+)
- Check triangle coordinates (typo?)
- Try the exact examples first

**"Can I use this in my project?"**
- Yes! All code is open-source
- Apache 2.0 license (very permissive)
- Credit appreciated but not required

**"How do I make it faster?"**
- Use NumPy instead of lists
- Remove print statements
- Run with `python -O` (optimized)

**"Can I visualize without matplotlib?"**
- Yes! Use asterisks in terminal:
  ```python
  for y in range(height):
      for x in range(width):
          print('█' if framebuffer[y][x] else ' ', end='')
      print()
  ```

---

**Now go experiment! Break things, fix them, and learn! 🚀**
