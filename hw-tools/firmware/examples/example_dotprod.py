#!/usr/bin/env python3
"""
Example: Matrix Multiplication on flux GPU
Demonstrates chaining multiple operations
"""

import sys
sys.path.append('../../')
from hw_tools.firmware.firmware_driver import FluxGPU

def main():
    print("=== flux GPU Dot Product Demo ===\n")
    
    gpu = FluxGPU(interface='simulation')
    
    # Load program
    gpu.load_program('../../sw-toolchain/examples/dotprod.hex')
    
    # Setup vectors
    print("--- Input Vectors ---")
    A = [1.0, 2.0, 3.0, 4.0]
    B = [5.0, 6.0, 7.0, 8.0]
    
    gpu.write_memory(0x1000, A)
    gpu.write_memory(0x2000, B)
    
    gpu.set_register(0, 10, [0x1000, 0, 0, 0])
    gpu.set_register(0, 11, [0x2000, 0, 0, 0])
    gpu.set_register(0, 12, [0x3000, 0, 0, 0])
    
    print(f"A = {A}")
    print(f"B = {B}")
    
    # Execute
    print("\n--- Computing A · B ---")
    gpu.start_execution()
    
    # Read element-wise products
    products = gpu.read_memory(0x3000, 4)
    print(f"\nElement-wise products: {products}")
    
    # Manual sum (GPU doesn't have reduce yet)
    dot_product = sum(products)
    expected = sum(a*b for a, b in zip(A, B))
    
    print(f"\nDot product (sum): {dot_product}")
    print(f"Expected: {expected}")
    
    assert abs(dot_product - expected) < 0.001, "FAIL!"
    print("\n✓ Test PASSED!")

if __name__ == "__main__":
    main()
