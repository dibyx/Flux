#!/usr/bin/env python3
"""
flux GPU Math Examples - Interactive Version
Run this to see all the math concepts in action!
"""

import struct
import time

# =============================================================================
# 1. SIMD - Do 4 Things at Once
# =============================================================================

def simd_add(a_vec, b_vec):
    """Add two 4-element vectors (SIMD style)"""
    return [a_vec[i] + b_vec[i] for i in range(4)]

def simd_demo():
    print("="*60)
    print("1. SIMD DEMONSTRATION")
    print("="*60)
    
    A = [1.0, 2.5, 3.7, 4.2]
    B = [0.5, 1.5, 2.3, 3.8]
    
    print(f"\nVector A: {A}")
    print(f"Vector B: {B}")
    
    # Single instruction, multiple data
    C = simd_add(A, B)
    
    print(f"Result C: {C}")
    print("\n✓ All 4 additions happened in ONE operation!")
    
    # Performance comparison
    print("\nPerformance:")
    print(f"  CPU (sequential): 4 operations")
    print(f"  GPU (SIMD):       1 operation")
    print(f"  Speedup:          4×")

# =============================================================================
# 2. Edge Function - Triangle Inside Test
# =============================================================================

def edge_function(v0, v1, p):
    """
    Calculate edge function for point p and edge v0→v1
    Returns:
        > 0: point is on the left
        < 0: point is on the right
        = 0: point is on the line
    """
    x0, y0 = v0
    x1, y1 = v1
    px, py = p
    
    return (y0 - y1) * px + (x1 - x0) * py + x0*y1 - x1*y0

def inside_triangle(p, v0, v1, v2):
    """Check if point p is inside triangle v0-v1-v2"""
    e0 = edge_function(v0, v1, p)
    e1 = edge_function(v1, v2, p)
    e2 = edge_function(v2, v0, p)
    
    # All same sign?
    return (e0 >= 0 and e1 >= 0 and e2 >= 0) or \
           (e0 <= 0 and e1 <= 0 and e2 <= 0)

def edge_function_demo():
    print("\n" + "="*60)
    print("2. EDGE FUNCTION - TRIANGLE RASTERIZATION")
    print("="*60)
    
    # Triangle vertices
    V0 = (100, 100)
    V1 = (400, 100)
    V2 = (250, 300)
    
    print(f"\nTriangle vertices:")
    print(f"  V0: {V0}")
    print(f"  V1: {V1}")
    print(f"  V2: {V2}")
    
    # Test points
    test_points = [
        ((200, 150), "Inside (center-top)"),
        ((250, 200), "Inside (center)"),
        ((100, 50), "Outside (above)"),
        ((500, 200), "Outside (right)"),
        ((150, 350), "Outside (below)"),
    ]
    
    print("\nTesting points:")
    for point, description in test_points:
        e0 = edge_function(V0, V1, point)
        e1 = edge_function(V1, V2, point)
        e2 = edge_function(V2, V0, point)
        inside = inside_triangle(point, V0, V1, V2)
        
        print(f"\n  Point {point} - {description}")
        print(f"    e0 = {e0:8.0f}, e1 = {e1:8.0f}, e2 = {e2:8.0f}")
        print(f"    Result: {'✓ INSIDE' if inside else '✗ OUTSIDE'}")

# =============================================================================
# 3. Bounding Box Optimization
# =============================================================================

def get_bounding_box(v0, v1, v2, screen_width=640, screen_height=480):
    """Find bounding box for triangle, clamped to screen"""
    xs = [v0[0], v1[0], v2[0]]
    ys = [v0[1], v1[1], v2[1]]
    
    min_x = max(0, min(xs))
    max_x = min(screen_width - 1, max(xs))
    min_y = max(0, min(ys))
    max_y = min(screen_height - 1, max(ys))
    
    return (min_x, max_x, min_y, max_y)

def bounding_box_demo():
    print("\n" + "="*60)
    print("3. BOUNDING BOX OPTIMIZATION")
    print("="*60)
    
    V0 = (100, 100)
    V1 = (400, 100)
    V2 = (250, 300)
    
    min_x, max_x, min_y, max_y = get_bounding_box(V0, V1, V2)
    
    bbox_width = max_x - min_x + 1
    bbox_height = max_y - min_y + 1
    bbox_pixels = bbox_width * bbox_height
    screen_pixels = 640 * 480
    
    print(f"\nBounding box: ({min_x}, {min_y}) to ({max_x}, {max_y})")
    print(f"Size: {bbox_width} × {bbox_height} = {bbox_pixels:,} pixels")
    print(f"\nFull screen: 640 × 480 = {screen_pixels:,} pixels")
    print(f"Speedup: {screen_pixels / bbox_pixels:.1f}×")
    print(f"Pixels saved: {screen_pixels - bbox_pixels:,} ({(1 - bbox_pixels/screen_pixels)*100:.1f}%)")

# =============================================================================
# 4. Triangle Rasterization (Complete)
# =============================================================================

class Framebuffer:
    """Simple framebuffer for demonstration"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
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
        return 0
    
    def count_pixels(self, color):
        """Count how many pixels have this color"""
        return sum(1 for p in self.pixels if p == color)

def rasterize_triangle(framebuffer, v0, v1, v2, color):
    """Rasterize triangle to framebuffer"""
    min_x, max_x, min_y, max_y = get_bounding_box(v0, v1, v2, 
                                                   framebuffer.width, 
                                                   framebuffer.height)
    
    pixels_tested = 0
    pixels_drawn = 0
    
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            pixels_tested += 1
            if inside_triangle((x, y), v0, v1, v2):
                framebuffer.set_pixel(x, y, color)
                pixels_drawn += 1
    
    return pixels_tested, pixels_drawn

def rasterization_demo():
    print("\n" + "="*60)
    print("4. TRIANGLE RASTERIZATION")
    print("="*60)
    
    # Create framebuffer
    fb = Framebuffer(640, 480)
    
    # Triangle
    V0 = (100, 100)
    V1 = (400, 100)
    V2 = (250, 300)
    color = 0xFF0000  # Red
    
    print(f"\nRasterizing triangle...")
    print(f"  Vertices: {V0}, {V1}, {V2}")
    print(f"  Color: 0x{color:06X}")
    
    # Rasterize
    start = time.time()
    tested, drawn = rasterize_triangle(fb, V0, V1, V2, color)
    elapsed = time.time() - start
    
    print(f"\nResults:")
    print(f"  Pixels tested: {tested:,}")
    print(f"  Pixels drawn: {drawn:,}")
    print(f"  Fill rate: {drawn/tested*100:.1f}%")
    print(f"  Time: {elapsed*1000:.2f} ms (Python)")
    
    # Verify
    red_pixels = fb.count_pixels(color)
    print(f"\nVerification:")
    print(f"  Red pixels in framebuffer: {red_pixels:,}")
    print(f"  Match: {'✓' if red_pixels == drawn else '✗'}")

# =============================================================================
# 5. Memory Addressing (2D → 1D)
# =============================================================================

def pixel_to_address(x, y, width):
    """Convert 2D pixel coordinate to 1D memory address"""
    return y * width + x

def address_to_pixel(addr, width):
    """Convert 1D memory address to 2D pixel coordinate"""
    y = addr // width
    x = addr % width
    return (x, y)

def memory_addressing_demo():
    print("\n" + "="*60)
    print("5. MEMORY ADDRESSING (2D → 1D)")
    print("="*60)
    
    width = 640
    
    test_coords = [
        (0, 0),       # Top-left
        (639, 0),     # Top-right
        (0, 479),     # Bottom-left
        (639, 479),   # Bottom-right
        (100, 200),   # Random
    ]
    
    print(f"\nFramebuffer width: {width}")
    print("\nCoordinate → Address conversions:")
    
    for x, y in test_coords:
        addr = pixel_to_address(x, y, width)
        back_x, back_y = address_to_pixel(addr, width)
        
        print(f"  ({x:3d}, {y:3d}) → address {addr:6d} → ({back_x:3d}, {back_y:3d}) {'✓' if (x,y)==(back_x,back_y) else '✗'}")

# =============================================================================
# 6. Floating-Point Representation
# =============================================================================

def float_to_bits(f):
    """Convert float to 32-bit integer representation"""
    return struct.unpack('>I', struct.pack('>f', f))[0]

def bits_to_float(b):
    """Convert 32-bit integer to float"""
    return struct.unpack('>f', struct.pack('>I', b))[0]

def fp_demo():
    print("\n" + "="*60)
    print("6. FLOATING-POINT REPRESENTATION (IEEE 754)")
    print("="*60)
    
    test_floats = [3.14, -2.5, 0.0, 1.0, 42.0]
    
    print("\nFloat → Binary representation:")
    for f in test_floats:
        bits = float_to_bits(f)
        
        # Extract components
        sign = (bits >> 31) & 1
        exponent = (bits >> 23) & 0xFF
        mantissa = bits & 0x7FFFFF
        
        print(f"\n  {f:8.2f} = 0x{bits:08X}")
        print(f"    Sign:     {sign} ({'positive' if sign == 0 else 'negative'})")
        print(f"    Exponent: {exponent} (biased)")
        print(f"    Mantissa: 0x{mantissa:06X}")
        
        # Verify
        back = bits_to_float(bits)
        print(f"    Verify:   {back} {'✓' if abs(back - f) < 1e-6 else '✗'}")

# =============================================================================
# 7. Instruction Encoding
# =============================================================================

def encode_r_type(opcode, rd, rs1, rs2, funct3, funct7):
    """Encode R-type instruction (e.g., ADD, SUB, MUL)"""
    instr = 0
    instr |= (opcode & 0x7F)        # Bits 0-6
    instr |= (rd & 0x1F) << 7       # Bits 7-11
    instr |= (funct3 & 0x7) << 12   # Bits 12-14
    instr |= (rs1 & 0x1F) << 15     # Bits 15-19
    instr |= (rs2 & 0x1F) << 20     # Bits 20-24
    instr |= (funct7 & 0x7F) << 25  # Bits 25-31
    return instr

def encode_i_type(opcode, rd, rs1, funct3, imm):
    """Encode I-type instruction (e.g., ADDI, LOAD)"""
    instr = 0
    instr |= (opcode & 0x7F)
    instr |= (rd & 0x1F) << 7
    instr |= (funct3 & 0x7) << 12
    instr |= (rs1 & 0x1F) << 15
    instr |= (imm & 0xFFF) << 20
    return instr

def instruction_encoding_demo():
    print("\n" + "="*60)
    print("7. INSTRUCTION ENCODING")
    print("="*60)
    
    # Examples
    instructions = [
        ("ADD R3, R1, R2", encode_r_type(0b0110011, 3, 1, 2, 0b000, 0b0000000)),
        ("SUB R5, R4, R3", encode_r_type(0b0110011, 5, 4, 3, 0b000, 0b0100000)),
        ("ADDI R7, R6, 100", encode_i_type(0b0010011, 7, 6, 0b000, 100)),
    ]
    
    print("\nAssembly → Machine Code:")
    for asm, machine_code in instructions:
        print(f"  {asm:20s} = 0x{machine_code:08X} = {bin(machine_code)}")

# =============================================================================
# 8. Performance Calculations
# =============================================================================

def performance_demo():
    print("\n" + "="*60)
    print("8. PERFORMANCE CALCULATIONS")
    print("="*60)
    
    clock_freq = 50_000_000  # 50 MHz
    
    triangle_sizes = {
        "Tiny (50×50)": 2_500,
        "Small (100×100)": 10_000,
        "Medium (200×200)": 40_000,
        "Large (400×400)": 160_000,
    }
    
    print(f"\nClock frequency: {clock_freq/1e6:.0f} MHz")
    print("\nTriangle rasterization performance:")
    
    for name, cycles in triangle_sizes.items():
        time_us = (cycles / clock_freq) * 1e6
        time_ms = time_us / 1000
        triangles_per_sec = clock_freq / cycles
        fps_100_tri = triangles_per_sec / 100
        
        print(f"\n  {name} ({cycles:,} cycles):")
        print(f"    Time:       {time_us:7.1f} μs ({time_ms:.2f} ms)")
        print(f"    Throughput: {triangles_per_sec:7.0f} triangles/second")
        print(f"    FPS (100 tri/frame): {fps_100_tri:5.1f}")

# =============================================================================
# 9. Complete GPU Simulation
# =============================================================================

class SimpleGPU:
    """Simple GPU simulator demonstrating all concepts"""
    def __init__(self, width=640, height=480):
        self.framebuffer = Framebuffer(width, height)
        self.cycles = 0
        self.clock_freq = 50_000_000  # 50 MHz
    
    def draw_triangle(self, v0, v1, v2, color, verbose=True):
        """Draw a triangle with full statistics"""
        if verbose:
            print(f"\n--- Drawing Triangle ---")
            print(f"Vertices: {v0}, {v1}, {v2}")
            print(f"Color: 0x{color:06X}")
        
        # Reset cycle counter
        start_cycles = self.cycles
        
        # Rasterize
        tested, drawn = rasterize_triangle(self.framebuffer, v0, v1, v2, color)
        self.cycles += tested  # Each pixel test = 1 cycle (simplified)
        
        cycles_used = self.cycles - start_cycles
        time_us = (cycles_used / self.clock_freq) * 1e6
        
        if verbose:
            print(f"\nStatistics:")
            print(f"  Pixels tested: {tested:,}")
            print(f"  Pixels drawn: {drawn:,}")
            print(f"  Fill rate: {drawn/tested*100:.1f}%")
            print(f"  Cycles: {cycles_used:,}")
            print(f"  Time @ 50 MHz: {time_us:.1f} μs")
        
        return drawn

def gpu_demo():
    print("\n" + "="*60)
    print("9. COMPLETE GPU SIMULATION")
    print("="*60)
    
    gpu = SimpleGPU()
    
    # Draw multiple triangles
    triangles = [
        ((100, 100), (400, 100), (250, 300), 0xFF0000, "Red"),
        ((200, 150), (500, 200), (300, 400), 0x00FF00, "Green"),
        ((50, 200), (150, 400), (400, 350), 0x0000FF, "Blue"),
    ]
    
    print("\nDrawing scene with 3 triangles...")
    total_pixels = 0
    
    for i, (v0, v1, v2, color, name) in enumerate(triangles, 1):
        print(f"\n  Triangle {i} ({name}):")
        pixels = gpu.draw_triangle(v0, v1, v2, color, verbose=False)
        total_pixels += pixels
        print(f"    Drew {pixels:,} pixels")
    
    print(f"\nScene complete!")
    print(f"  Total pixels drawn: {total_pixels:,}")
    print(f"  Total cycles: {gpu.cycles:,}")
    print(f"  Time @ 50 MHz: {(gpu.cycles / gpu.clock_freq) * 1e3:.2f} ms")

# =============================================================================
# Main Program
# =============================================================================

def main():
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  flux GPU - Math & Algorithms Interactive Demo".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60 + "\n")
    
    # Run all demos
    simd_demo()
    edge_function_demo()
    bounding_box_demo()
    rasterization_demo()
    memory_addressing_demo()
    fp_demo()
    instruction_encoding_demo()
    performance_demo()
    gpu_demo()
    
    # Final message
    print("\n" + "="*60)
    print("ALL DEMOS COMPLETE!")
    print("="*60)
    print("\nNow you've seen all the math behind flux GPU in action!")
    print("Try modifying the code and experimenting! 🚀")
    print("")

if __name__ == "__main__":
    main()
