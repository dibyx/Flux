#!/usr/bin/env python3
"""
Example: Run Vector Addition on flux GPU
"""

import sys
sys.path.append('../../')
from hw_tools.firmware.firmware_driver import FluxGPU

def main():
    print("=== flux GPU Vector Addition Demo ===\n")
    
    # Initialize GPU (simulation mode for now)
    gpu = FluxGPU(interface='simulation')
    
    # Load the vector addition program
    gpu.load_program('../../sw-toolchain/examples/vecadd.hex')
    
    # Setup input data
    print("\n--- Setting up data ---")
    
    # Arrays: A = [10, 20, 30, 40], B = [1, 2, 3, 4]
    A = [10.0, 20.0, 30.0, 40.0]
    B = [1.0, 2.0, 3.0, 4.0]
    
    # Write to memory
    gpu.write_memory(0x1000, A)  # Array A at 0x1000
    gpu.write_memory(0x2000, B)  # Array B at 0x2000
    
    # Set register pointers
    gpu.set_register(0, 10, [0x1000, 0, 0, 0])  # R10 = &A
    gpu.set_register(0, 11, [0x2000, 0, 0, 0])  # R11 = &B
    gpu.set_register(0, 12, [0x3000, 0, 0, 0])  # R12 = &C (output)
    
    print(f"Array A: {A}")
    print(f"Array B: {B}")
    
    # Execute
    print("\n--- Executing on GPU ---")
    gpu.start_execution(thread_mask=0x01)
    
    # Read results
    print("\n--- Results ---")
    C = gpu.read_memory(0x3000, 4)
    print(f"Array C (A+B): {C}")
    
    # Verify
    expected = [a + b for a, b in zip(A, B)]
    assert C == expected, f"FAIL: Expected {expected}, got {C}"
    print("\n✓ Test PASSED!")
    
    # Show registers
    gpu.dump_registers(thread_id=0)

if __name__ == "__main__":
    main()
