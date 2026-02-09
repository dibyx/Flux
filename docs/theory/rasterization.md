# Triangle Rasterization Theory

**Understanding how GPUs draw triangles**

---

## Why Triangles?

Triangles are the fundamental primitive in 3D graphics because:
1. **Simple**: Defined by just 3 points
2. **Always planar**: 3 points always form a flat surface
3. **Fast**: Efficient algorithms exist
4. **Universal**: Any polygon can be decomposed into triangles

---

## Rasterization Overview

**Rasterization** = Converting vector graphics (triangles) to raster graphics (pixels)

```
Input: 3 vertices (x,y coordinates)
Output: Set of pixels inside the triangle
```

---

## Edge Function Algorithm

### The Math

An **edge function** determines which side of a line a point is on.

For an edge from vertex V0 to V1, the edge function at point P is:

```
f(P) = (V1.y - V0.y) * P.x + (V0.x - V1.x) * P.y + V0.x*V1.y - V1.x*V0.y
```

**Sign interpretation**:
- `f(P) > 0`: Point is on the left of the edge
- `f(P) < 0`: Point is on the right of the edge  
- `f(P) = 0`: Point is exactly on the edge

### Inside-Triangle Test

A point P is inside triangle V0-V1-V2 if:

```
f01(P), f12(P), f20(P) all have the SAME sign
```

Where:
- `f01` = edge function for V0→V1
- `f12` = edge function for V1→V2
- `f20` = edge function for V2→V0

**Example**:
```
V0 = (100, 100)
V1 = (300, 100)
V2 = (200, 300)
P  = (200, 150)

f01(P) = (100-100)*200 + (100-300)*150 + 100*100 - 300*100 = -30,000 + 10,000 = -20,000
f12(P) = (300-100)*200 + (300-200)*150 + 300*300 - 200*100 = 40,000 + 15,000 + 90,000 - 20,000 = 125,000
f20(P) = (100-300)*200 + (200-100)*150 + 100*300 - 200*100 = -40,000 + 15,000 + 30,000 - 20,000 = -15,000

NOT all same sign → P is OUTSIDE
```

---

## Bounding Box Optimization

Instead of testing every pixel on screen (640×480 = 307,200), only test pixels in the triangle's bounding box:

```
min_x = min(V0.x, V1.x, V2.x)
max_x = max(V0.x, V1.x, V2.x)
min_y = min(V0.y, V1.y, V2.y)
max_y = max(V0.y, V1.y, V2.y)

for y in range(min_y, max_y+1):
    for x in range(min_x, max_x+1):
        if inside_triangle(x, y):
            draw_pixel(x, y)
```

**Speedup**: 
- Full screen: 307,200 tests
- Small triangle (100×100): ~10,000 tests
- **30× faster!**

---

## Scanline Rasterization

### Step-by-Step Algorithm

```python
def rasterize_triangle(v0, v1, v2, color):
    # 1. Calculate bounding box
    min_x = min(v0.x, v1.x, v2.x)
    max_x = max(v0.x, v1.x, v2.x)
    min_y = min(v0.y, v1.y, v2.y)
    max_y = max(v0.y, v1.y, v2.y)
    
    # 2. Clamp to screen (640×480)
    min_x = max(0, min_x)
    max_x = min(639, max_x)
    min_y = max(0, min_y)
    max_y = min(479, max_y)
    
    # 3. Scan each pix in bounding box
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            # 4. Compute edge functions
            e0 = edge_function(v0, v1, (x, y))
            e1 = edge_function(v1, v2, (x, y))
            e2 = edge_function(v2, v0, (x, y))
            
            # 5. Inside test
            if (e0 >= 0 and e1 >= 0 and e2 >= 0) or \
               (e0 <= 0 and e1 <= 0 and e2 <= 0):
                # 6. Write pixel
                framebuffer[y * 640 + x] = color
```

---

## Hardware Implementation

### flux GPU Rasterizer

**State Machine**:
```
IDLE → CALC_BBOX → RASTER → WRITE_PIX → DONE
                      ↑          |
                      └──────────┘
                      (iterate through bbox)
```

**Key Components**:

1. **Edge Function Module** (`edge_function.sv`):
   - Combinational logic
   - Computes `f(P)` for one edge
   - 22-bit signed output

2. **Bounding Box Calculator**:
   - Finds min/max of 3 vertices
   - Clamps to screen bounds

3. **Pixel Iterator**:
   - Nested X/Y counters
   - Increments through bounding box

4. **Inside Tester**:
   - Compares signs of 3 edge functions
   - Generates `inside` signal

5. **Framebuffer Writer**:
   - Calculates address: `y * 640 + x`
   - Writes color if inside

**Performance** (@ 50 MHz system clock):
- Small triangle (100×100): ~200 μs
- Medium (200×200): ~800 μs
- Large (400×400): ~3.2 ms
- **Max triangles/second**: ~300

---

## Advanced Topics

### Barycentric Coordinates

Instead of edge functions, use barycentric coordinates (λ0, λ1, λ2):

```
P = λ0*V0 + λ1*V1 + λ2*V2
where λ0 + λ1 + λ2 = 1
```

**Benefits**:
- Natural for interpolation (colors, texture coords)
- Used in advanced shaders

**flux GPU**: Uses edge functions (simpler hardware)

### Sub-pixel Accuracy

Real GPUs use fixed-point math for sub-pixel precision:
- Store vertices as 28.4 fixed-point (4 fractional bits)
- Allows smooth movement of triangles
- Reduces aliasing artifacts

### Fill Rules

What happens if pixel is exactly on edge?

**Top-left rule**: Pixel belongs to triangle if:
- On top edge, OR
- On left edge

Prevents holes and double-fills when triangles share edges.

### Incremental Calculation

Instead of recalculating edge function for every pixel:

```
e(x+1, y) = e(x, y) + (V1.y - V0.y)
e(x, y+1) = e(x, y) + (V0.x - V1.x)
```

Add instead of multiply → faster!

---

## Comparison to CPU Rasterization

| Aspect | CPU | GPU (flux) |
|--------|-----|------------|
| Algorithm | Same (edge function) | Same |
| Parallelism | 1 triangle at a time | 1 triangle (multi-core: many) |
| Speed | ~1 ms/triangle (Python) | ~200 μs (FPGA) |
| Optimization | Loop unrolling, SIMD | Pipelined, dedicated HW |

**GPU Advantage**: Dedicated hardware, no instruction fetch overhead

---

## Rasterization in flux GPU

### Implementation Highlights

**File**: `rtl/src/raster/rasterizer.sv` (180 lines)

**Key Features**:
- ✅ Edge function algorithm
- ✅ Bounding box optimization
- ✅ Screen clipping
- ✅ Solid color fill
- ✅ State machine with done signal

**Missing Features** (future work):
- ❌ Texture mapping
- ❌ Color interpolation (Gouraud shading)
- ❌ Perspective-correct interpolation
- ❌ Anti-aliasing

### Example Usage

```systemverilog
rasterizer rast (
    .clk(clk_50mhz),
    .rst_n(rst_n),
    .v0_x(10'd100), .v0_y(10'd200),  // Vertex 0
    .v1_x(10'd500), .v1_y(10'd200),  // Vertex 1
    .v2_x(10'd300), .v2_y(10'd400),  // Vertex 2
    .color(24'hFF0000),              // Red
    .start(start_signal),
    .busy(rast_busy),
    .done(rast_done),
    .fb_addr(fb_write_addr),
    .fb_data(fb_write_data),
    .fb_write(fb_write_enable)
);
```

---

## Further Reading

**Papers**:
- "A Parallel Algorithm for Polygon Rasterization" (Juan Pineda, 1988)
- "Triangle Scan Conversion" (Chris Hecker, Game Developer Magazine)

**Online Resources**:
- [Scratchapixel - Rasterization](https://www.scratchapixel.com/lessons/3d-basic-rendering/rasterization-practical-implementation)
- [Fabian Giesen's Blog](https://fgiesen.wordpress.com/2013/02/08/triangle-rasterization-in-practice/)

**Books**:
- "Fundamentals of Computer Graphics" - Shirley & Mars chner
- "Real-Time Rendering" - Akenine-Möller et al.

---

**Next**: Study [VGA output](vga_timing.md) to display rasterized triangles on screen
