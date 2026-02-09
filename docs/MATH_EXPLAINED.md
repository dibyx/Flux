# The Math Behind flux GPU - Explained for College Students

**No boring theory - just the math you actually need to understand GPUs**

---

## Introduction

Hey! So you want to understand the math that makes flux GPU work? Good news: **it's not rocket science**. 

Most of it is stuff you already know:
- Basic algebra (y = mx + b)
- Multiplying numbers
- Comparing which number is bigger
- Converting 2D coordinates to memory addresses

Let's dive in with **actual examples** you can code up yourself.

---

## 1. SIMD: Do the Same Thing to 4 Numbers at Once

### The Problem

You have two lists of numbers and want to add them:
```
A = [1, 2, 3, 4]
B = [5, 6, 7, 8]
C = ?  # Should be [6, 8, 10, 12]
```

### The "Normal" Way (CPU)
```python
C = []
for i in range(4):
    C.append(A[i] + B[i])
# Took 4 loops!
```

### The GPU Way (SIMD)
```python
# Do all 4 additions AT THE SAME TIME
C = [A[0]+B[0], A[1]+B[1], A[2]+B[2], A[3]+B[3]]
# Happens in ONE clock cycle!
```

### The Math

**SIMD = Single Instruction, Multiple Data**

One `ADD` instruction does **4 additions** in parallel:
```
ADD R3, R1, R2

Internally:
  R3[0] = R1[0] + R2[0]  ─┐
  R3[1] = R1[1] + R2[1]  ─┤ All happen
  R3[2] = R1[2] + R2[2]  ─┤ at the same time
  R3[3] = R1[3] + R2[3]  ─┘
```

**Why this matters**: 4× faster than doing them one at a time!

### Try It Yourself

```python
import struct

# flux GPU ALU simulation
def simd_add(a_vec, b_vec):
    """Add two 4-element vectors in parallel"""
    return [a_vec[i] + b_vec[i] for i in range(4)]

# Example
A = [1.0, 2.5, 3.7, 4.2]
B = [0.5, 1.5, 2.3, 3.8]
C = simd_add(A, B)
print(f"Result: {C}")  # [1.5, 4.0, 6.0, 8.0]
```

**Quiz**: If you add 1 million numbers on a CPU (1 at a time), and a GPU does 4 at a time, how much faster is the GPU?
<details>
<summary>Answer</summary>
4× faster! (1 million ÷ 4 = 250,000 operations)
</details>

---

## 2. Triangle Rasterization: The Edge Function

### The Problem

You have a triangle with vertices at:
```
V0 = (100, 100)
V1 = (400, 100)
V2 = (250, 300)
```

**Question**: Is the pixel at (200, 150) inside the triangle?

### The Wrong Way (Brute Force)

```python
# Check EVERY pixel on screen (640×480 = 307,200 pixels!)
for y in range(480):
    for x in range(640):
        if inside_triangle(x, y, V0, V1, V2):
            draw_pixel(x, y)
# This is SLOW!
```

### The Smart Way: Edge Function

**Key Insight**: A point is inside a triangle if it's on the **same side** of all 3 edges.

#### Step 1: Define an Edge

An edge from `V0 = (x0, y0)` to `V1 = (x1, y1)` divides the plane in two:

```
        V1 (x1, y1)
          ●
         /
        /  ← Points on left have f(P) > 0
       /
      /  ← Points on right have f(P) < 0
     ●
    V0 (x0, y0)
```

#### Step 2: The Edge Function Formula

For a point `P = (x, y)`:

```
f(P) = (y0 - y1) × x + (x1 - x0) × y + x0×y1 - x1×y0
```

**If f(P) > 0**: P is on the left  
**If f(P) < 0**: P is on the right  
**If f(P) = 0**: P is exactly on the line

#### Step 3: Inside Test

P is inside triangle if **all 3 edge functions have the same sign**:

```python
def edge_function(v0, v1, p):
    """Calculate edge function for point p"""
    x0, y0 = v0
    x1, y1 = v1
    px, py = p
    
    return (y0 - y1) * px + (x1 - x0) * py + x0*y1 - x1*y0

def inside_triangle(p, v0, v1, v2):
    """Check if point p is inside triangle"""
    e0 = edge_function(v0, v1, p)
    e1 = edge_function(v1, v2, p)
    e2 = edge_function(v2, v0, p)
    
    # All same sign? (all >= 0 or all <= 0)
    return (e0 >= 0 and e1 >= 0 and e2 >= 0) or \
           (e0 <= 0 and e1 <= 0 and e2 <= 0)
```

### Real Example with Numbers

Let's test pixel (200, 150) with our triangle:

```python
V0 = (100, 100)
V1 = (400, 100)
V2 = (250, 300)
P  = (200, 150)

# Edge 0: V0 → V1
e0 = (100 - 100) × 200 + (400 - 100) × 150 + 100×100 - 400×100
   = 0 × 200 + 300 × 150 + 10000 - 40000
   = 0 + 45000 + 10000 - 40000
   = 15000  ✓ positive

# Edge 1: V1 → V2
e1 = (100 - 300) × 200 + (250 - 400) × 150 + 400×300 - 250×100
   = -200 × 200 + (-150) × 150 + 120000 - 25000
   = -40000 - 22500 + 120000 - 25000
   = 32500  ✓ positive

# Edge 2: V2 → V0
e2 = (300 - 100) × 200 + (100 - 250) × 150 + 250×100 - 100×300
   = 200 × 200 + (-150) × 150 + 25000 - 30000
   = 40000 - 22500 + 25000 - 30000
   = 12500  ✓ positive

# All positive? YES! → Point (200, 150) is INSIDE
```

**Try it yourself**:
```python
def test_point():
    V0 = (100, 100)
    V1 = (400, 100)
    V2 = (250, 300)
    
    test_points = [
        (200, 150, True),   # Inside
        (100, 50, False),   # Outside (too high)
        (500, 200, False),  # Outside (too far right)
        (250, 200, True),   # Inside (center)
    ]
    
    for px, py, expected in test_points:
        result = inside_triangle((px, py), V0, V1, V2)
        status = "✓" if result == expected else "✗"
        print(f"{status} Point ({px}, {py}): {result} (expected {expected})")

test_point()
```

### Optimization: Bounding Box

Instead of testing ALL 307,200 pixels, only test pixels in the triangle's bounding box:

```python
def get_bounding_box(v0, v1, v2):
    """Find the smallest rectangle containing the triangle"""
    xs = [v0[0], v1[0], v2[0]]
    ys = [v0[1], v1[1], v2[1]]
    
    min_x = max(0, min(xs))      # Clamp to screen
    max_x = min(639, max(xs))
    min_y = max(0, min(ys))
    max_y = min(479, max(ys))
    
    return (min_x, max_x, min_y, max_y)

V0 = (100, 100)
V1 = (400, 100)
V2 = (250, 300)

min_x, max_x, min_y, max_y = get_bounding_box(V0, V1, V2)
# min_x = 100, max_x = 400, min_y = 100, max_y = 300

# Now only test: (400-100) × (300-100) = 300 × 200 = 60,000 pixels
# vs 640 × 480 = 307,200 pixels
# 5× fewer tests!
```

**Full rasterizer**:
```python
def rasterize_triangle(v0, v1, v2, color):
    """Fill triangle with color"""
    framebuffer = [[0]*640 for _ in range(480)]  # 2D array
    
    min_x, max_x, min_y, max_y = get_bounding_box(v0, v1, v2)
    
    pixels_tested = 0
    pixels_drawn = 0
    
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            pixels_tested += 1
            if inside_triangle((x, y), v0, v1, v2):
                framebuffer[y][x] = color
                pixels_drawn += 1
    
    print(f"Tested {pixels_tested} pixels, drew {pixels_drawn}")
    return framebuffer

# Example
fb = rasterize_triangle((100,100), (400,100), (250,300), 0xFF0000)
# Output: Tested 60000 pixels, drew ~30000
```

---

## 3. VGA Timing: When to Draw Each Pixel

### The Problem

Your monitor expects pixels at **exactly the right time**. Too early or late = garbled image.

### VGA 640×480 @ 60Hz Timing

**Question**: How fast do we send pixels?

#### Math Time!

```
Resolution: 640 × 480 pixels
Refresh rate: 60 Hz (60 times per second)
```

**Step 1**: How many pixels per frame?
```
Visible pixels = 640 × 480 = 307,200 pixels
```

**Step 2**: But VGA also has "blanking" periods (invisible):
```
Horizontal:
  Visible: 640 pixels
  Front porch: 16 pixels
  Sync pulse: 96 pixels
  Back porch: 48 pixels
  Total: 640 + 16 + 96 + 48 = 800 pixels per line

Vertical:
  Visible: 480 lines
  Front porch: 10 lines
  Sync pulse: 2 lines
  Back porch: 33 lines
  Total: 480 + 10 + 2 + 33 = 525 lines per frame

Total pixels per frame = 800 × 525 = 420,000 "pixels"
(including blanking)
```

**Step 3**: Pixel clock calculation
```
Frames per second: 60
Pixels per frame: 420,000
Pixel clock = 60 × 420,000 = 25,200,000 Hz = 25.2 MHz
```

**In practice**: Standard VGA uses **25.175 MHz** (very close!)

### Generating Sync Signals

**H-Sync** (horizontal sync):
```python
def generate_hsync(pixel_x):
    """Generate horizontal sync signal"""
    # Active for pixels 656-751 (96 pixels wide)
    if 656 <= pixel_x < 752:
        return 0  # Active LOW
    else:
        return 1  # Inactive HIGH

# Test
for x in [0, 640, 656, 750, 751, 799]:
    print(f"x={x:3d}: hsync={generate_hsync(x)}")
```

**V-Sync** (vertical sync):
```python
def generate_vsync(line_y):
    """Generate vertical sync signal"""
    # Active for lines 490-491 (2 lines)
    if 490 <= line_y < 492:
        return 0  # Active LOW
    else:
        return 1  # Inactive HIGH
```

### Display Enable

Only output color during visible area:

```python
def is_visible(x, y):
    """Check if pixel is in visible area"""
    return (0 <= x < 640) and (0 <= y < 480)

# Pixel output logic
def get_pixel_color(x, y, framebuffer):
    if is_visible(x, y):
        return framebuffer[y][x]  # Show actual color
    else:
        return 0x000000  # Black during blanking
```

---

## 4. Memory Addressing: 2D → 1D

### The Problem

Framebuffer is a **1D array** in hardware, but pixels are **2D** (x, y).

How do you convert?

### The Formula

```
address = y × width + x
```

**Example** (640×480 display):
```
Pixel at (10, 5):
  address = 5 × 640 + 10 = 3210

Pixel at (639, 479):
  address = 479 × 640 + 639 = 306,559
  (last pixel)
```

### Why This Works

Think of the framebuffer as rows stacked:

```
Row 0: [pixel 0, pixel 1, ..., pixel 639]
Row 1: [pixel 640, pixel 641, ..., pixel 1279]
Row 2: [pixel 1280, pixel 1281, ..., pixel 1919]
...
Row y: [pixel y×640, pixel y×640+1, ..., pixel y×640+639]
```

To get pixel at (x, y):
1. Skip past `y` complete rows: `y × 640`
2. Add `x` offset within row: `+ x`
3. Final address: `y × 640 + x`

### Python Example

```python
class Framebuffer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # 1D array (what hardware uses)
        self.pixels = [0] * (width * height)
    
    def set_pixel(self, x, y, color):
        """Set pixel at (x, y) to color"""
        if 0 <= x < self.width and 0 <= y < self.height:
            address = y * self.width + x
            self.pixels[address] = color
    
    def get_pixel(self, x, y):
        """Get pixel color at (x, y)"""
        if 0 <= x < self.width and 0 <= y < self.height:
            address = y * self.width + x
            return self.pixels[address]
        return 0  # Black if out of bounds

# Usage
fb = Framebuffer(640, 480)
fb.set_pixel(100, 200, 0xFF0000)  # Red pixel
print(f"Pixel (100, 200) = 0x{fb.get_pixel(100, 200):06X}")
print(f"Stored at address: {200 * 640 + 100}")
```

### Optimization for Hardware

Multiplying by 640 in hardware is expensive. Trick: use bit shifts!

```
640 = 512 + 128 = 2^9 + 2^7
```

So:
```
y × 640 = y × (2^9 + 2^7)
        = (y << 9) + (y << 7)
```

**In Verilog** (flux GPU uses this):
```systemverilog
wire [18:0] addr_y_512 = {pixel_y, 9'b0};       // y × 512 (left shift 9)
wire [18:0] addr_y_128 = {2'b0, pixel_y, 7'b0}; // y × 128 (left shift 7)
wire [18:0] address = addr_y_512 + addr_y_128 + pixel_x;
```

**No multiplication needed!** Just shifts and adds.

---

## 5. Floating-Point Math: How GPU Adds 3.14 + 2.71

### IEEE 754 FP32 Format

Every float is stored as 32 bits:

```
Sign (1 bit) | Exponent (8 bits) | Mantissa (23 bits)
```

**Example**: 3.14 in binary

```
3.14 in binary ≈ 11.001000111...

Normalized: 1.1001000111... × 2^1

Sign: 0 (positive)
Exponent: 1 + 127 = 128 = 10000000 (biased)
Mantissa: 10010001110101110000101
          (implicit 1. not stored)

Full 32 bits:
0 10000000 10010001110101110000101
```

### Addition Algorithm

```python
def fp_add(a, b):
    """Simplified FP32 addition"""
    # 1. Extract components
    sign_a, exp_a, mant_a = extract_fp(a)
    sign_b, exp_b, mant_b = extract_fp(b)
    
    # 2. Align exponents (shift smaller one)
    if exp_a > exp_b:
        mant_b >>= (exp_a - exp_b)
        exp_result = exp_a
    else:
        mant_a >>= (exp_b - exp_a)
        exp_result = exp_b
    
    # 3. Add mantissas
    mant_result = mant_a + mant_b
    
    # 4. Normalize result
    while mant_result >= 2.0:
        mant_result /= 2
        exp_result += 1
    
    # 5. Pack result
    return pack_fp(0, exp_result, mant_result)
```

**In flux GPU**: Hardware does this in **1 clock cycle** for **4 numbers** simultaneously!

### Try It

```python
import struct

def float_to_bits(f):
    """Convert float to 32-bit integer"""
    return struct.unpack('>I', struct.pack('>f', f))[0]

def bits_to_float(b):
    """Convert 32-bit integer to float"""
    return struct.unpack('>f', struct.pack('>I', b))[0]

# Example
f = 3.14
bits = float_to_bits(f)
print(f"3.14 as bits: 0x{bits:08X}")
print(f"Binary: {bin(bits)}")

# Verify
back = bits_to_float(bits)
print(f"Back to float: {back}")
```

---

## 6. Instruction Encoding: How Assembly Becomes Binary

### The Problem

Assembly:
```assembly
ADD R3, R1, R2
```

Must become a 32-bit number that hardware understands.

### R-Type Instruction Format

```
| opcode | rd  | funct3 | rs1 | rs2 | funct7 |
| 7 bits | 5   | 3      | 5   | 5   | 7      |
```

**For ADD**:
- opcode = `0110011` (arithmetic)
- funct3 = `000` (ADD)
- funct7 = `0000000` (ADD, not SUB)
- rd = R3 = `00011`
- rs1 = R1 = `00001`
- rs2 = R2 = `00010`

**Full encoding**:
```
0000000 | 00010 | 00001 | 000 | 00011 | 0110011
funct7  | rs2   | rs1   | f3  | rd    | opcode
```

As one 32-bit number:
```
0000000 00010 00001 000 00011 0110011
= 0x002080B3
```

### Python Encoder

```python
def encode_r_type(opcode, rd, rs1, rs2, funct3, funct7):
    """Encode R-type instruction"""
    instr = 0
    instr |= (opcode & 0x7F)        # Bits 0-6
    instr |= (rd & 0x1F) << 7       # Bits 7-11
    instr |= (funct3 & 0x7) << 12   # Bits 12-14
    instr |= (rs1 & 0x1F) << 15     # Bits 15-19
    instr |= (rs2 & 0x1F) << 20     # Bits 20-24
    instr |= (funct7 & 0x7F) << 25  # Bits 25-31
    return instr

# ADD R3, R1, R2
add_instr = encode_r_type(
    opcode=0b0110011,  # Arithmetic
    rd=3,              # R3
    rs1=1,             # R1
    rs2=2,             # R2
    funct3=0b000,      # ADD
    funct7=0b0000000   # ADD
)

print(f"ADD R3, R1, R2 = 0x{add_instr:08X}")
```

### I-Type (Immediate) Example

```assembly
ADDI R7, R6, 100
```

Format:
```
| immediate | rs1 | funct3 | rd  | opcode |
| 12 bits   | 5   | 3      | 5   | 7      |
```

```python
def encode_i_type(opcode, rd, rs1, funct3, imm):
    """Encode I-type instruction"""
    instr = 0
    instr |= (opcode & 0x7F)
    instr |= (rd & 0x1F) << 7
    instr |= (funct3 & 0x7) << 12
    instr |= (rs1 & 0x1F) << 15
    instr |= (imm & 0xFFF) << 20  # 12-bit immediate
    return instr

# ADDI R7, R6, 100
addi_instr = encode_i_type(
    opcode=0b0010011,  # I-type arithmetic
    rd=7,
    rs1=6,
    funct3=0b000,
    imm=100
)

print(f"ADDI R7, R6, 100 = 0x{addi_instr:08X}")
```

---

## 7. Performance Math: How Fast Is It?

### Clock Cycles vs Real Time

```
Time = Cycles × Clock Period

Clock Period = 1 / Frequency
```

**Example**:
```
Rasterize triangle = 10,000 cycles
Clock frequency = 50 MHz

Time = 10,000 × (1 / 50,000,000)
     = 10,000 / 50,000,000
     = 0.0002 seconds
     = 0.2 milliseconds
     = 200 microseconds
```

### Throughput Calculation

```python
def calculate_throughput():
    """How many triangles per second?"""
    clock_freq = 50_000_000  # 50 MHz
    
    # Different triangle sizes
    triangles_sizes = {
        "small (100×100)": 10_000,
        "medium (200×200)": 40_000,
        "large (400×400)": 160_000,
    }
    
    for name, cycles in triangles_sizes.items():
        time_per_tri = cycles / clock_freq
        triangles_per_sec = clock_freq / cycles
        fps_100_tri = triangles_per_sec / 100
        
        print(f"\n{name}:")
        print(f"  Time: {time_per_tri*1e6:.1f} μs")
        print(f"  Throughput: {triangles_per_sec:.0f} tri/sec")
        print(f"  FPS (100 tri/frame): {fps_100_tri:.1f}")

calculate_throughput()
```

Output:
```
small (100×100):
  Time: 200.0 μs
  Throughput: 5000 tri/sec
  FPS (100 tri/frame): 50.0

medium (200×200):
  Time: 800.0 μs
  Throughput: 1250 tri/sec
  FPS (100 tri/frame): 12.5

large (400×400):
  Time: 3200.0 μs
  Throughput: 312 tri/sec
  FPS (100 tri/frame): 3.1
```

---

## 8. Putting It All Together: Full Example

Let's render a triangle from start to finish:

```python
class SimpleGPU:
    def __init__(self):
        self.framebuffer = Framebuffer(640, 480)
        self.cycles = 0
    
    def draw_triangle(self, v0, v1, v2, color):
        """Complete triangle rasterization"""
        print(f"\n--- Rasterizing Triangle ---")
        print(f"V0: {v0}, V1: {v1}, V2: {v2}")
        print(f"Color: 0x{color:06X}")
        
        # Step 1: Calculate bounding box
        min_x, max_x, min_y, max_y = get_bounding_box(v0, v1, v2)
        bbox_pixels = (max_x - min_x + 1) * (max_y - min_y + 1)
        print(f"\nBounding box: ({min_x},{min_y}) to ({max_x},{max_y})")
        print(f"Will test {bbox_pixels} pixels")
        
        pixels_drawn = 0
        
        # Step 2: Scan bounding box
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                self.cycles += 1  # Count operations
                
                # Step 3: Inside test
                if inside_triangle((x, y), v0, v1, v2):
                    # Step 4: Write to framebuffer
                    self.framebuffer.set_pixel(x, y, color)
                    pixels_drawn += 1
        
        print(f"\nResults:")
        print(f"  Pixels tested: {bbox_pixels}")
        print(f"  Pixels drawn: {pixels_drawn}")
        print(f"  Fill rate: {pixels_drawn/bbox_pixels*100:.1f}%")
        print(f"  Cycles: {self.cycles}")
        
        # Performance
        clock_freq = 50_000_000
        time_us = (self.cycles / clock_freq) * 1e6
        print(f"  Time @ 50 MHz: {time_us:.1f} μs")

# Run it!
gpu = SimpleGPU()
gpu.draw_triangle(
    v0=(100, 100),
    v1=(400, 100),
    v2=(250, 300),
    color=0xFF0000  # Red
)
```

---

## Summary: The Math You Actually Need

| Concept | Math | Used For |
|---------|------|----------|
| **SIMD** | Parallel addition | 4× speedup |
| **Edge Function** | Line equation | Inside-triangle test |
| **Bounding Box** | min/max | Skip pixels outside |
| **2D → 1D** | `y × width + x` | Memory addressing |
| **Bit Shifts** | `<<` and `>>` | Fast multiply/divide by 2^n |
| **FP32** | IEEE 754 | Decimal numbers |
| **Clock Math** | `time = cycles / freq` | Performance analysis |

**None of this requires calculus, differential equations, or advanced math!**

It's all stuff you learned in high school:
- Multiplication
- Comparing numbers  
- Coordinate geometry
- Binary arithmetic

---

## Challenges for You

**Challenge 1**: Modify the edge function to work with negative coordinates.

**Challenge 2**: Optimize `y × 640` using only shifts and adds (hint: 640 = 512 + 128).

**Challenge 3**: Write a function to draw a filled circle using a similar bounding box + inside test approach.

**Challenge 4**: Calculate how many FPS you could get if each frame has 1,000 triangles.

---

**Now go code! The math is just a tool - the fun part is building stuff with it.** 🚀
