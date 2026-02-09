#!/usr/bin/env python3
"""
flux GPU Instruction Simulator
Software model of the shader core for rapid testing
"""

import sys
import struct
from typing import List, Dict

class FluxSimulator:
    def __init__(self, num_threads=32, num_regs=32):
        self.num_threads = num_threads
        self.num_regs = num_regs
        
        # Register file: [thread][reg] = [lane0, lane1, lane2, lane3] (4× FP32)
        self.regfile = [[[0.0] * 4 for _ in range(num_regs)] for _ in range(num_threads)]
        
        # Memory (simplified, 64KB)
        self.memory = bytearray(64 * 1024)
        
        # Program counter per thread
        self.pc = [0] * num_threads
        
        # Execution mask (for divergence)
        self.exec_mask = [True] * num_threads
        
        # Instruction memory
        self.instructions = []
        
        # Halted flag
        self.halted = False
        
        # Statistics
        self.stats = {
            'instructions_executed': 0,
            'memory_reads': 0,
            'memory_writes': 0,
        }
    
    def load_program(self, filename: str):
        """Load program from hex file"""
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    self.instructions.append(int(line, 16))
        print(f"Loaded {len(self.instructions)} instructions")
    
    def load_binary(self, filename: str):
        """Load program from binary file"""
        with open(filename, 'rb') as f:
            data = f.read()
            for i in range(0, len(data), 4):
                word = int.from_bytes(data[i:i+4], byteorder='little')
                self.instructions.append(word)
        print(f"Loaded {len(self.instructions)} instructions")
    
    def decode(self, instr: int) -> Dict:
        """Decode instruction"""
        opcode = instr & 0x7F
        rd = (instr >> 7) & 0x1F
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1F
        rs2 = (instr >> 20) & 0x1F
        funct7 = (instr >> 25) & 0x7F
        
        # I-type immediate (sign-extended)
        imm_i = (instr >> 20)
        if imm_i & 0x800:  # Sign bit
            imm_i |= 0xFFFFF000
        imm_i = struct.unpack('i', struct.pack('I', imm_i & 0xFFFFFFFF))[0]
        
        # S-type immediate
        imm_s = ((instr >> 25) << 5) | ((instr >> 7) & 0x1F)
        if imm_s & 0x800:
            imm_s |= 0xFFFFF000
        imm_s = struct.unpack('i', struct.pack('I', imm_s & 0xFFFFFFFF))[0]
        
        # B-type immediate
        imm_b = (((instr >> 31) & 1) << 12) | (((instr >> 7) & 1) << 11) | \
                (((instr >> 25) & 0x3F) << 5) | (((instr >> 8) & 0xF) << 1)
        if imm_b & 0x1000:
            imm_b |= 0xFFFFE000
        imm_b = struct.unpack('i', struct.pack('I', imm_b & 0xFFFFFFFF))[0]
        
        return {
            'opcode': opcode,
            'rd': rd, 'rs1': rs1, 'rs2': rs2,
            'funct3': funct3, 'funct7': funct7,
            'imm_i': imm_i, 'imm_s': imm_s, 'imm_b': imm_b
        }
    
    def read_reg(self, thread: int, reg: int) -> List[float]:
        """Read register value"""
        if reg == 0:
            return [0.0, 0.0, 0.0, 0.0]  # R0 hardwired to 0
        return self.regfile[thread][reg].copy()
    
    def write_reg(self, thread: int, reg: int, value: List[float]):
        """Write register value"""
        if reg != 0:  # R0 is read-only
            self.regfile[thread][reg] = value.copy()
    
    def read_memory(self, addr: int) -> List[float]:
        """Read 4× FP32 from memory"""
        result = []
        for i in range(4):
            offset = addr + i * 4
            if offset + 4 <= len(self.memory):
                raw = self.memory[offset:offset+4]
                val = struct.unpack('f', bytes(raw))[0]
                result.append(val)
            else:
                result.append(0.0)
        self.stats['memory_reads'] += 1
        return result
    
    def write_memory(self, addr: int, value: List[float]):
        """Write 4× FP32 to memory"""
        for i in range(4):
            offset = addr + i * 4
            if offset + 4 <= len(self.memory):
                raw = struct.pack('f', value[i])
                self.memory[offset:offset+4] = raw
        self.stats['memory_writes'] += 1
    
    def init_memory(self, addr: int, values: List[float]):
        """Initialize memory with test data"""
        for i, val in enumerate(values):
            offset = addr + i * 4
            if offset + 4 <= len(self.memory):
                raw = struct.pack('f', val)
                self.memory[offset:offset+4] = raw
    
    def execute_instruction(self, thread: int, instr: int):
        """Execute single instruction for one thread"""
        d = self.decode(instr)
        
        # R-type instructions
        if d['opcode'] == 0x33:
            rs1_val = self.read_reg(thread, d['rs1'])
            rs2_val = self.read_reg(thread, d['rs2'])
            
            if d['funct3'] == 0 and d['funct7'] == 0:  # ADD
                result = [a + b for a, b in zip(rs1_val, rs2_val)]
            elif d['funct3'] == 0 and d['funct7'] == 0x20:  # SUB
                result = [a - b for a, b in zip(rs1_val, rs2_val)]
            elif d['funct3'] == 0 and d['funct7'] == 0x01:  # MUL
                result = [a * b for a, b in zip(rs1_val, rs2_val)]
            elif d['funct3'] == 4 and d['funct7'] == 0x01:  # DIV
                result = [a / b if b != 0 else 0.0 for a, b in zip(rs1_val, rs2_val)]
            else:
                result = [0.0] * 4
            
            self.write_reg(thread, d['rd'], result)
        
        # I-type (ADDI)
        elif d['opcode'] == 0x13:
            rs1_val = self.read_reg(thread, d['rs1'])
            imm_float = float(d['imm_i'])
            result = [a + imm_float for a in rs1_val]
            self.write_reg(thread, d['rd'], result)
        
        # LOAD
        elif d['opcode'] == 0x03:
            rs1_val = self.read_reg(thread, d['rs1'])
            addr = int(rs1_val[0]) + d['imm_i']  # Use lane 0 for address
            result = self.read_memory(addr)
            self.write_reg(thread, d['rd'], result)
        
        # STORE
        elif d['opcode'] == 0x23:
            rs1_val = self.read_reg(thread, d['rs1'])
            rs2_val = self.read_reg(thread, d['rs2'])
            addr = int(rs1_val[0]) + d['imm_s']
            self.write_memory(addr, rs2_val)
        
        # BEQ
        elif d['opcode'] == 0x63 and d['funct3'] == 0:
            rs1_val = self.read_reg(thread, d['rs1'])[0]  # Compare lane 0
            rs2_val = self.read_reg(thread, d['rs2'])[0]
            if rs1_val == rs2_val:
                self.pc[thread] += d['imm_b'] - 4  # -4 because we auto-increment
        
        # BNE
        elif d['opcode'] == 0x63 and d['funct3'] == 1:
            rs1_val = self.read_reg(thread, d['rs1'])[0]
            rs2_val = self.read_reg(thread, d['rs2'])[0]
            if rs1_val != rs2_val:
                self.pc[thread] += d['imm_b'] - 4
        
        # HALT
        elif d['opcode'] == 0x7F:
            self.halted = True
            return
        
        self.stats['instructions_executed'] += 1
    
    def run(self, thread: int = 0, max_steps: int = 1000, verbose: bool = False):
        """Run simulation for single thread"""
        print(f"\n=== Running thread {thread} ===")
        
        steps = 0
        while not self.halted and steps < max_steps:
            pc_addr = self.pc[thread]
            pc_idx = pc_addr // 4
            
            if pc_idx >= len(self.instructions):
                break
            
            instr = self.instructions[pc_idx]
            
            if verbose:
                print(f"PC={pc_addr:04x} INSTR={instr:08x}", end="")
                
            self.execute_instruction(thread, instr)
            
            if verbose:
                print()
            
            self.pc[thread] += 4
            steps += 1
        
        if self.halted:
            print(f"✓ Program halted after {steps} instructions")
        else:
            print(f"⚠ Reached max steps ({max_steps})")
    
    def print_registers(self, thread: int = 0, show_all: bool = False):
        """Print register contents"""
        print(f"\n=== Registers (Thread {thread}) ===")
        for i in range(self.num_regs):
            val = self.regfile[thread][i]
            if show_all or any(v != 0.0 for v in val):
                print(f"R{i:2d} = [{val[0]:8.2f}, {val[1]:8.2f}, {val[2]:8.2f}, {val[3]:8.2f}]")
    
    def print_memory(self, start: int, count: int = 16):
        """Print memory contents"""
        print(f"\n=== Memory (0x{start:04x} - 0x{start+count*4-1:04x}) ===")
        for i in range(0, count, 4):
            addr = start + i * 4
            values = self.read_memory(addr)
            print(f"0x{addr:04x}: [{values[0]:8.2f}, {values[1]:8.2f}, {values[2]:8.2f}, {values[3]:8.2f}]")
    
    def print_stats(self):
        """Print execution statistics"""
        print("\n=== Statistics ===")
        print(f"Instructions executed: {self.stats['instructions_executed']}")
        print(f"Memory reads:          {self.stats['memory_reads']}")
        print(f"Memory writes:         {self.stats['memory_writes']}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python simulator.py <program.hex> [--verbose]")
        print("   or: python simulator.py <program.bin> [--verbose]")
        sys.exit(1)
    
    program_file = sys.argv[1]
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    
    # Create simulator
    sim = FluxSimulator()
    
    # Load program
    if program_file.endswith('.hex'):
        sim.load_program(program_file)
    elif program_file.endswith('.bin'):
        sim.load_binary(program_file)
    else:
        print("Error: File must be .hex or .bin")
        sys.exit(1)
    
    # Initialize test data (example for vecadd)
    # A = [1.0, 2.0, 3.0, 4.0] at 0x1000
    # B = [5.0, 6.0, 7.0, 8.0] at 0x2000
    sim.init_memory(0x1000, [1.0, 2.0, 3.0, 4.0])
    sim.init_memory(0x2000, [5.0, 6.0, 7.0, 8.0])
    
    # Set base addresses in registers
    sim.write_reg(0, 10, [0x1000, 0, 0, 0])  # R10 = &A
    sim.write_reg(0, 11, [0x2000, 0, 0, 0])  # R11 = &B
    sim.write_reg(0, 12, [0x3000, 0, 0, 0])  # R12 = &C
    
    # Run simulation
    sim.run(thread=0, verbose=verbose)
    
    # Print results
    sim.print_registers(thread=0)
    
    print("\nInput A (0x1000):")
    sim.print_memory(0x1000, count=4)
    
    print("\nInput B (0x2000):")
    sim.print_memory(0x2000, count=4)
    
    print("\nOutput C (0x3000):")
    sim.print_memory(0x3000, count=4)
    
    sim.print_stats()

if __name__ == "__main__":
    main()
