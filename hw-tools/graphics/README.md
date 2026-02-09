# flux GPU Graphics System

**Hardware-accelerated triangle rasterization with VGA output**

---

## Overview

The flux GPU graphics pipeline can draw triangles to a 640×480 framebuffer and display them on a VGA monitor.

**Components**:
- VGA timing generator (640×480 @ 60Hz)
- VGA controller with framebuffer interface
- Dual-port framebuffer (307,200 pixels, RGB888)
- Triangle rasterizer (edge function algorithm)
- Graphics top module (integration)

---

## Quick Start

### Python Demo

```bash
cd hw-tools/graphics

# Simulation mode
python triangle_demo.py simulation

# FPGA mode (with VGA monitor connected)
python triangle_demo.py uart
```

### Assembly Demo

```bash
cd hw-tools/graphics

# Assemble
python ../../sw-toolchain/asm/assembler.py triangle_demo.s

# Simulate (won't show graphics, but verifies logic)
python ../../sw-toolchain/sim/simulator.py triangle_demo.hex
```

---

## Hardware Specifications

### VGA Timing

| Parameter | Value |
|-----------|-------|
| Resolution | 640 × 480 |
| Refresh rate | 60 Hz |
| Pixel clock | 25.175 MHz |
| H-sync polarity | Negative |
| V-sync polarity | Negative |

**Timing Details**:
- Horizontal: 800 total (640 visible, 16 front, 96 sync, 48 back)
- Vertical: 525 total (480 visible, 10 front, 2 sync, 33 back)

### Framebuffer

| Specification | Value |
|---------------|-------|
| Size | 640 × 480 pixels |
| Color depth | 24-bit RGB888 |
| Total memory | ~900 KB (307,200 × 24 bits) |
| Type | Dual-port BRAM |
| Ports | Write (rasterizer), Read (VGA) |

### Rasterizer

**Algorithm**: Edge function (half-space test)

**Process**:
1. Calculate bounding box of triangle
2. Iterate through each pixel in bounding box
3. Test if pixel is inside triangle using edge functions
4. Write pixel to framebuffer if inside

**Performance**: 
- Simple triangle (~100×100): ~10,000 pixels = ~200 μs @ 50 MHz
- Complex triangle (~400×400): ~160,000 pixels = ~3.2 ms

---

## API

### Python (Firmware Driver)

```python
from firmware_driver import FluxGPU

gpu = FluxGPU(interface='uart')  # or 'simulation'

# Draw triangle
gpu.write_memory(0x5000, [v0_x])  # Vertex 0 X
gpu.write_memory(0x5004, [v0_y])  # Vertex 0 Y
gpu.write_memory(0x5008, [v1_x])  # Vertex 1 X
gpu.write_memory(0x500C, [v1_y])  # Vertex 1 Y
gpu.write_memory(0x5010, [v2_x])  # Vertex 2 X
gpu.write_memory(0x5014, [v2_y])  # Vertex 2 Y
gpu.write_memory(0x5018, [color]) # RGB888 color
gpu.write_memory(0x5020, [1.0])   # Start rasterization

# Wait for completion
while gpu.read_memory(0x5024, 1)[0] != 0:
    time.sleep(0.01)
```

### Assembly

```assembly
# Set vertex coordinates
LI R10, 100      # V0 X
LI R11, 200      # V0 Y
LI R12, 500      # V1 X
LI R13, 200      # V1 Y
LI R14, 300      # V2 X
LI R15, 400      # V2 Y
LI R16, 0xFF0000 # Red color

# Write to graphics registers
STORE R10, 0x5000  # V0 X
STORE R11, 0x5004  # V0 Y
# ... (repeat for all vertices and color)

# Start rasterization
LI R20, 1
STORE R20, 0x5020

# Wait for completion
wait:
    LOAD R21, 0x5024
    BNE R21, R0, wait

HALT
```

---

## Memory Map

| Address | Register | Description |
|---------|----------|-------------|
| 0x5000 | V0_X | Vertex 0 X coordinate (0-639) |
| 0x5004 | V0_Y | Vertex 0 Y coordinate (0-479) |
| 0x5008 | V1_X | Vertex 1 X coordinate |
| 0x500C | V1_Y | Vertex 1 Y coordinate |
| 0x5010 | V2_X | Vertex 2 X coordinate |
| 0x5014 | V2_Y | Vertex 2 Y coordinate |
| 0x5018 | COLOR | RGB888 color (0xRRGGBB) |
| 0x5020 | START | Write 1 to start rasterization |
| 0x5024 | BUSY | Read-only: 1 if busy, 0 if done |
| 0x5030 | CLEAR_START | Write 1 to clear screen |
| 0x5034 | CLEAR_COLOR | Color for clear operation |

---

## VGA Wiring

### ULX3S to VGA Connector

**Standard VGA DB-15 connector**:

| VGA Pin | Signal | ULX3S GPIO | Color |
|---------|--------|------------|-------|
| 1 | Red | GP14 | Red wire |
| 2 | Green | GP15 | Green wire |
| 3 | Blue | GP16 | Blue wire |
| 13 | H-Sync | GP17 | Yellow wire |
| 14 | V-Sync | GP18 | Brown wire |
| 5,6,7,8,10 | GND | GND | Black wire |

**Note**: ULX3S outputs 3.3V logic. Most VGA monitors expect 0.7V analog.
You may need:
- Resistor divider (270Ω + 470Ω per channel)
- OR: VGA DAC board (recommended for best quality)

---

## Examples

### Example 1: Single Red Triangle

```python
draw_triangle(
    gpu,
    v0=(100, 200),
    v1=(500, 200),
    v2=(300, 400),
    color=0xFF0000  # Red
)
```

**Output**: Red triangle pointing downward

### Example 2: Three Overlapping Triangles

```python
# Red
draw_triangle(gpu, (100,200), (500,200), (300,400), 0xFF0000)
# Green (overlaps)
draw_triangle(gpu, (200,100), (400,300), (150,450), 0x00FF00)
# Blue
draw_triangle(gpu, (400,100), (600,400), (500,450), 0x0000FF)
```

**Output**: Colorful overlapping triangles

### Example 3: Color Gradient (Manual)

Draw many small triangles with varying colors to simulate gradient.

---

## Limitations

**Current Version**:
- ❌ No perspective correction
- ❌ No texture mapping
- ❌ No Z-buffer (depth testing)
- ❌ No anti-aliasing
- ❌ Solid color only (no interpolation)
- ❌ No backface culling

**Performance**:
- Full-screen triangle: ~3-5 ms to rasterize
- Max triangles/second: ~200-300 (at 50 MHz system clock)
- Frame rate: Limited by rasterization, not VGA output

---

## Troubleshooting

### No VGA Output

1. **Check connections**: Verify all VGA pins are connected
2. **Check clock**: VGA requires 25 MHz pixel clock
3. **Check sync**: Use oscilloscope to verify H-sync and V-sync
4. **Monitor compatibility**: Try different monitor (some don't support VGA)

### Garbled Output

1. **Timing issues**: Verify pixel clock is exactly 25.175 MHz
2. **Framebuffer corruption**: Reset GPU and redraw
3. **Signal integrity**: Use shorter cables, add termination resistors

### Triangle Not Appearing

1. **Coordinates**: Check vertices are within 0-639 (X) and 0-479 (Y)
2. **Color**: Verify color is not 0x000000 (black on black)
3. **Busy flag**: Wait for rasterizer to complete
4. **Framebuffer**: Try clearing screen first

---

## Future Enhancements

1. **Texture Mapping**: Sample textures during rasterization
2. **Z-Buffer**: Depth testing for 3D scenes
3. **Gouraud Shading**: Interpolate colors across triangle
4. **Clipping**: Properly clip triangles at screen edges
5. **Anti-Aliasing**: MSAA or FXAA
6. **HDMI Output**: Replace VGA with digital output

---

## Technical Details

### Rasterizer Algorithm

**Edge Function**:
```
f(x,y) = (y0-y1)*x + (x1-x0)*y + x0*y1 - x1*y0
```

**Inside Test**:
Point (x,y) is inside triangle if all three edge functions have the same sign.

**Optimization**:
- Bounding box reduces pixels to test
- Early rejection for obviously outside pixels
- Pipelined edge function calculation

### Resource Usage

| Module | LUTs | FFs | BRAMs |
|--------|------|-----|-------|
| VGA Timing | 150 | 50 | 0 |
| VGA Controller | 300 | 200 | 0 |
| Framebuffer | 50 | 20 | 48 |
| Rasterizer | 2,000 | 1,200 | 0 |
| **Total Graphics** | **2,500** | **1,470** | **48** |

**Plus Shader Core**: 8,000 LUTs, 12,000 FFs, 32 BRAMs

**Grand Total**: ~10,500 LUTs (~12% of ULX3S), 96 BRAMs (~46%)

---

## See Also

- [VGA Timing Specification](http://www.tinyvga.com/vga-timing/640x480@60Hz)
- [Triangle Rasterization](https://fgiesen.wordpress.com/2013/02/08/triangle-rasterization-in-practice/)
- [Edge Function Tutorial](https://www.scratchapixel.com/lessons/3d-basic-rendering/rasterization-practical-implementation)

---

**flux graphics: Real-time triangle rasterization on FPGA** 🎨
