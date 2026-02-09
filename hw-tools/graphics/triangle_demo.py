#!/usr/bin/env python3
"""
Triangle Demo - Python Firmware
Draws a colored triangle using the flux GPU graphics pipeline
"""

import sys
sys.path.append('../../')
from hw_tools.firmware.firmware_driver import FluxGPU

def draw_triangle(gpu, v0, v1, v2, color):
    """
    Draw a triangle to the framebuffer
    
    Args:
        gpu: FluxGPU instance
        v0, v1, v2: Tuples of (x, y) coordinates
        color: 24-bit RGB color (0xRRGGBB)
    """
    print(f"Drawing triangle:")
    print(f"  V0: {v0}")
    print(f"  V1: {v1}")
    print(f"  V2: {v2}")
    print(f"  Color: 0x{color:06X}")
    
    # Write vertex coordinates to GPU registers
    # Memory-mapped registers starting at 0x5000
    gpu.write_memory(0x5000, [float(v0[0])])  # V0 X
    gpu.write_memory(0x5004, [float(v0[1])])  # V0 Y
    gpu.write_memory(0x5008, [float(v1[0])])  # V1 X
    gpu.write_memory(0x500C, [float(v1[1])])  # V1 Y
    gpu.write_memory(0x5010, [float(v2[0])])  # V2 X
    gpu.write_memory(0x5014, [float(v2[1])])  # V2 Y
    gpu.write_memory(0x5018, [float(color)])  # Color
    
    # Trigger rasterization
    gpu.write_memory(0x5020, [1.0])  # Start bit
    
    # Wait for completion (poll busy flag)
    import time
    timeout = 5.0  # 5 second timeout
    start_time = time.time()
    
    while True:
        busy = gpu.read_memory(0x5024, 1)[0]
        if busy == 0.0:
            break
        if time.time() - start_time > timeout:
            print("⚠️  Timeout waiting for rasterization")
            return False
        time.sleep(0.01)  # 10ms poll interval
    
    print("✓ Triangle rasterized!")
    return True

def main():
    print("=== flux GPU Triangle Demo ===\n")
    
    # Initialize GPU
    # For simulation, use 'simulation'
    # For FPGA with UART, use 'uart'
    interface = 'simulation'
    if len(sys.argv) > 1:
        interface = sys.argv[1]
    
    gpu = FluxGPU(interface=interface)
    
    # Example 1: Red triangle
    print("\n--- Drawing Red Triangle ---")
    success = draw_triangle(
        gpu,
        v0=(100, 200),
        v1=(500, 200),
        v2=(300, 400),
        color=0xFF0000  # Red
    )
    
    if not success:
        return 1
    
    # Example 2: Green triangle (overlapping)
    print("\n--- Drawing Green Triangle ---")
    draw_triangle(
        gpu,
        v0=(200, 100),
        v1=(400, 300),
        v2=(150, 450),
        color=0x00FF00  # Green
    )
    
    # Example 3: Blue triangle
    print("\n--- Drawing Blue Triangle ---")
    draw_triangle(
        gpu,
        v0=(400, 100),
        v1=(600, 400),
        v2=(500, 450),
        color=0x0000FF  # Blue
    )
    
    print("\n✓ Demo complete!")
    print(f"\nIf running on FPGA ({interface}), check your VGA monitor for output.")
    print("Expected: Three overlapping colored triangles (red, green, blue)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
