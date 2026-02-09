#!/usr/bin/env python3
"""
GPU Firmware Driver - Load and Execute Programs on flux GPU

This module provides high-level functions to program and control
the flux GPU via UART or simulation interface.
"""

import struct
import time
import sys

class FluxGPU:
    """
    Main driver class for flux GPU
    """
    
    def __init__(self, interface='simulation'):
        """
        Initialize GPU driver
        
        Args:
            interface: 'simulation', 'uart', or 'pcie'
        """
        self.interface = interface
        self.halted = False
        
        if interface == 'uart':
            import serial
            self.port = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        elif interface == 'simulation':
            # For software simulator
            self.memory = bytearray(64 * 1024)
            self.registers = [[[0.0]*4 for _ in range(32)] for _ in range(32)]
            self.instructions = []
            self.pc = 0
        
        print(f"✓ flux GPU initialized ({interface} mode)")
    
    def load_program(self, hex_file):
        """Load program from .hex file into instruction memory"""
        instructions = []
        
        with open(hex_file, 'r') as f:
            for line in f:
                instr = int(line.strip(), 16)
                instructions.append(instr)
        
        if self.interface == 'simulation':
            self.instructions = instructions
        else:
            # Send to hardware via UART/PCIe
            self._send_program(instructions)
        
        print(f"✓ Loaded {len(instructions)} instructions from {hex_file}")
        return len(instructions)
    
    def set_register(self, thread_id, reg_id, value):
        """
        Set register value
        
        Args:
            thread_id: Thread ID (0-31)
            reg_id: Register ID (0-31)
            value: List of 4 floats [lane0, lane1, lane2, lane3]
        """
        if len(value) != 4:
            raise ValueError("Register value must be 4 floats (SIMD lanes)")
        
        if self.interface == 'simulation':
            self.registers[thread_id][reg_id] = value
        else:
            self._send_write_register(thread_id, reg_id, value)
        
        print(f"  T{thread_id} R{reg_id} = {value}")
    
    def write_memory(self, addr, data):
        """
        Write data to GPU memory
        
        Args:
            addr: Memory address
            data: List of floats to write
        """
        if self.interface == 'simulation':
            for i, val in enumerate(data):
                offset = addr + i * 4
                packed = struct.pack('f', val)
                self.memory[offset:offset+4] = packed
        else:
            self._send_write_memory(addr, data)
        
        print(f"✓ Wrote {len(data)} values to 0x{addr:04x}")
    
    def read_memory(self, addr, count):
        """
        Read data from GPU memory
        
        Args:
            addr: Start address
            count: Number of floats to read
        
        Returns:
            List of floats
        """
        if self.interface == 'simulation':
            result = []
            for i in range(count):
                offset = addr + i * 4
                raw = self.memory[offset:offset+4]
                val = struct.unpack('f', bytes(raw))[0]
                result.append(val)
            return result
        else:
            return self._send_read_memory(addr, count)
    
    def start_execution(self, thread_mask=0x00000001):
        """
        Start GPU execution
        
        Args:
            thread_mask: Bitmap of threads to execute (bit 0 = thread 0)
        """
        if self.interface == 'simulation':
            # Use software simulator
            from sw_toolchain.sim.simulator import FluxSimulator
            sim = FluxSimulator()
            sim.instructions = self.instructions
            sim.regfile[0] = self.registers[0]
            sim.memory = self.memory
            sim.run(thread=0, verbose=False)
            
            # Copy results back
            self.registers[0] = sim.regfile[0]
            self.memory = sim.memory
            self.halted = sim.halted
        else:
            self._send_start_command(thread_mask)
            self._wait_for_halt()
        
        print("✓ Execution complete")
    
    def get_register(self, thread_id, reg_id):
        """Read register value after execution"""
        if self.interface == 'simulation':
            return self.registers[thread_id][reg_id]
        else:
            return self._send_read_register(thread_id, reg_id)
    
    def dump_registers(self, thread_id=0, show_all=False):
        """Print all non-zero registers"""
        print(f"\n=== Registers (Thread {thread_id}) ===")
        for i in range(32):
            val = self.get_register(thread_id, i)
            if show_all or any(v != 0.0 for v in val):
                print(f"R{i:2d} = [{val[0]:8.2f}, {val[1]:8.2f}, {val[2]:8.2f}, {val[3]:8.2f}]")
    
    def dump_memory(self, addr, count=4):
        """Print memory contents"""
        print(f"\n=== Memory (0x{addr:04x}) ===")
        data = self.read_memory(addr, count)
        for i in range(0, len(data), 4):
            offset = addr + i * 4
            chunk = data[i:i+4]
            if len(chunk) == 4:
                print(f"0x{offset:04x}: [{chunk[0]:8.2f}, {chunk[1]:8.2f}, {chunk[2]:8.2f}, {chunk[3]:8.2f}]")
    
    # === Hardware Communication (UART/PCIe) ===
    
    def _send_program(self, instructions):
        """Send program to hardware"""
        packet = bytearray()
        packet.append(0xAA)  # Start
        packet.append(0x80)  # LOAD_PROG command
        packet.extend(len(instructions).to_bytes(2, 'little'))
        
        for instr in instructions:
            packet.extend(instr.to_bytes(4, 'little'))
        
        checksum = sum(packet[1:]) & 0xFF
        packet.append(checksum)
        
        self.port.write(packet)
        ack = self.port.read(1)
        if ack != b'\x06':
            raise RuntimeError("Failed to load program")
    
    def _send_write_register(self, tid, rid, value):
        """Send write register command"""
        packet = bytearray()
        packet.append(0xAA)
        packet.append(0xA0)  # WRITE_REG
        packet.append(tid)
        packet.append(rid)
        
        for f in value:
            packet.extend(struct.pack('f', f))
        
        checksum = sum(packet[1:]) & 0xFF
        packet.append(checksum)
        self.port.write(packet)
    
    def _send_write_memory(self, addr, data):
        """Send write memory command"""
        packet = bytearray()
        packet.append(0xAA)
        packet.append(0x90)  # WRITE_MEM
        packet.extend(addr.to_bytes(4, 'little'))
        packet.extend(len(data).to_bytes(2, 'little'))
        
        for val in data:
            packet.extend(struct.pack('f', val))
        
        checksum = sum(packet[1:]) & 0xFF
        packet.append(checksum)
        self.port.write(packet)
    
    def _send_read_memory(self, addr, count):
        """Send read memory command"""
        packet = bytearray()
        packet.append(0xAA)
        packet.append(0xC0)  # READ_MEM
        packet.extend(addr.to_bytes(4, 'little'))
        packet.extend(count.to_bytes(2, 'little'))
        
        checksum = sum(packet[1:]) & 0xFF
        packet.append(checksum)
        self.port.write(packet)
        
        # Receive response
        response_len = count * 4
        data = self.port.read(response_len)
        
        result = []
        for i in range(0, len(data), 4):
            val = struct.unpack('f', data[i:i+4])[0]
            result.append(val)
        
        return result
    
    def _send_start_command(self, thread_mask):
        """Send start execution command"""
        packet = bytearray()
        packet.append(0xAA)
        packet.append(0xB0)  # START
        packet.extend(thread_mask.to_bytes(4, 'little'))
        
        checksum = sum(packet[1:]) & 0xFF
        packet.append(checksum)
        self.port.write(packet)
    
    def _wait_for_halt(self, timeout=5.0):
        """Poll for halt signal"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            packet = bytearray([0xAA, 0xB1])  # HALT_CHECK
            packet.append(sum(packet[1:]) & 0xFF)
            self.port.write(packet)
            
            response = self.port.read(1)
            if response == b'\x01':  # Halted
                self.halted = True
                return
            
            time.sleep(0.01)  # 10ms poll
        
        raise TimeoutError("GPU did not halt within timeout")
    
    def close(self):
        """Close connection"""
        if self.interface == 'uart':
            self.port.close()

# === High-Level Helper Functions ===

def run_program(assembly_file, interface='simulation', show_output=True):
    """
    Complete workflow: Assemble → Load → Execute → Show Results
    
    Args:
        assembly_file: Path to .s assembly file
        interface: 'simulation', 'uart', or 'pcie'
        show_output: Print results
    
    Returns:
        FluxGPU object with results
    """
    import os
    
    # Step 1: Assemble
    print(f"\n=== Assembling {assembly_file} ===")
    asm_cmd = f"python sw-toolchain/asm/assembler.py {assembly_file}"
    ret = os.system(asm_cmd)
    if ret != 0:
        raise RuntimeError("Assembly failed")
    
    hex_file = assembly_file.replace('.s', '.hex')
    
    # Step 2: Initialize GPU
    gpu = FluxGPU(interface=interface)
    
    # Step 3: Load program
    print(f"\n=== Loading Program ===")
    gpu.load_program(hex_file)
    
    # Step 4: Setup (example for vector add)
    print(f"\n=== Initializing Data ===")
    gpu.set_register(0, 10, [0x1000, 0, 0, 0])  # &A
    gpu.set_register(0, 11, [0x2000, 0, 0, 0])  # &B
    gpu.set_register(0, 12, [0x3000, 0, 0, 0])  # &C
    
    # Initialize arrays in memory
    gpu.write_memory(0x1000, [1.0, 2.0, 3.0, 4.0])  # A
    gpu.write_memory(0x2000, [5.0, 6.0, 7.0, 8.0])  # B
    
    # Step 5: Execute
    print(f"\n=== Executing ===")
    gpu.start_execution(thread_mask=0x01)
    
    # Step 6: Show results
    if show_output:
        gpu.dump_registers(thread_id=0)
        
        print("\n=== Input A ===")
        gpu.dump_memory(0x1000, count=4)
        
        print("\n=== Input B ===")
        gpu.dump_memory(0x2000, count=4)
        
        print("\n=== Output C ===")
        gpu.dump_memory(0x3000, count=4)
    
    return gpu

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python firmware_driver.py <program.s> [interface]")
        print("  interface: simulation (default), uart, pcie")
        sys.exit(1)
    
    program = sys.argv[1]
    interface = sys.argv[2] if len(sys.argv) > 2 else 'simulation'
    
    gpu = run_program(program, interface=interface)
    print("\n✓ Program complete!")
