#!/usr/bin/env python3
"""
flux GPU Assembler
Converts assembly language to machine code for the flux ISA
"""

import sys
import re
from typing import List, Dict, Tuple

class FluxAssembler:
    def __init__(self):
        # Instruction encoding lookup
        self.opcodes = {
            'ADD': 0x33, 'SUB': 0x33, 'MUL': 0x33, 'DIV': 0x33,
            'ADDI': 0x13, 'LI': 0x13,
            'LOAD': 0x03, 'STORE': 0x23,
            'BEQ': 0x63, 'BNE': 0x63,
            'JAL': 0x6F, 'JALR': 0x67,
            'NOP': 0x13, 'HALT': 0x7F
        }
        
        self.funct3 = {
            'ADD': 0x0, 'SUB': 0x0, 'MUL': 0x0, 'DIV': 0x4,
            'ADDI': 0x0,
            'LOAD': 0x2, 'STORE': 0x2,
            'BEQ': 0x0, 'BNE': 0x1,
        }
        
        self.funct7 = {
            'ADD': 0x00, 'SUB': 0x20, 'MUL': 0x01, 'DIV': 0x01,
        }
        
        self.labels = {}  # Label name -> address
        self.instructions = []  # List of (address, instruction_str)
        
    def parse_register(self, reg_str: str) -> int:
        """Parse register name (R0-R31) to number"""
        reg_str = reg_str.strip().upper()
        if reg_str.startswith('R'):
            return int(reg_str[1:])
        raise ValueError(f"Invalid register: {reg_str}")
    
    def parse_immediate(self, imm_str: str) -> int:
        """Parse immediate value (decimal or hex)"""
        imm_str = imm_str.strip()
        if imm_str.startswith('0x') or imm_str.startswith('0X'):
            return int(imm_str, 16)
        elif imm_str.startswith('-'):
            val = int(imm_str)
            # Sign extend to 12 bits for I-type
            if val < 0:
                return (1 << 12) + val
            return val
        else:
            return int(imm_str)
    
    def encode_r_type(self, mnemonic: str, rd: int, rs1: int, rs2: int) -> int:
        """Encode R-type instruction"""
        opcode = self.opcodes[mnemonic]
        funct3_val = self.funct3[mnemonic]
        funct7_val = self.funct7[mnemonic]
        
        instr = opcode | (rd << 7) | (funct3_val << 12) | (rs1 << 15) | (rs2 << 20) | (funct7_val << 25)
        return instr
    
    def encode_i_type(self, mnemonic: str, rd: int, rs1: int, imm: int) -> int:
        """Encode I-type instruction"""
        opcode = self.opcodes[mnemonic]
        funct3_val = self.funct3.get(mnemonic, 0)
        
        # Mask immediate to 12 bits
        imm = imm & 0xFFF
        
        instr = opcode | (rd << 7) | (funct3_val << 12) | (rs1 << 15) | (imm << 20)
        return instr
    
    def encode_s_type(self, mnemonic: str, rs2: int, rs1: int, offset: int) -> int:
        """Encode S-type instruction (STORE)"""
        opcode = self.opcodes[mnemonic]
        funct3_val = self.funct3[mnemonic]
        
        # Split immediate into imm[4:0] and imm[11:5]
        imm_low = offset & 0x1F
        imm_high = (offset >> 5) & 0x7F
        
        instr = opcode | (imm_low << 7) | (funct3_val << 12) | (rs1 << 15) | (rs2 << 20) | (imm_high << 25)
        return instr
    
    def encode_b_type(self, mnemonic: str, rs1: int, rs2: int, offset: int) -> int:
        """Encode B-type instruction (branches)"""
        opcode = self.opcodes[mnemonic]
        funct3_val = self.funct3[mnemonic]
        
        # B-type immediate encoding (complicated!)
        # imm[12|10:5|4:1|11]
        imm12 = (offset >> 12) & 1
        imm11 = (offset >> 11) & 1
        imm_10_5 = (offset >> 5) & 0x3F
        imm_4_1 = (offset >> 1) & 0xF
        
        instr = opcode | (imm11 << 7) | (imm_4_1 << 8) | (funct3_val << 12) | (rs1 << 15) | (rs2 << 20) | (imm_10_5 << 25) | (imm12 << 31)
        return instr
    
    def assemble_line(self, line: str, addr: int) -> Tuple[int, str]:
        """Assemble a single line of assembly"""
        # Remove comments
        if '#' in line:
            line = line[:line.index('#')]
        
        line = line.strip()
        if not line:
            return None, ""
        
        # Check for label
        if ':' in line:
            label, rest = line.split(':', 1)
            self.labels[label.strip()] = addr
            line = rest.strip()
            if not line:
                return None, ""
        
        # Parse instruction
        parts = re.split(r'[,\s()]+', line)
        parts = [p for p in parts if p]  # Remove empty strings
        
        if not parts:
            return None, ""
        
        mnemonic = parts[0].upper()
        
        # Handle different instruction formats
        if mnemonic in ['ADD', 'SUB', 'MUL', 'DIV']:
            # R-type: ADD R3, R1, R2
            rd = self.parse_register(parts[1])
            rs1 = self.parse_register(parts[2])
            rs2 = self.parse_register(parts[3])
            return self.encode_r_type(mnemonic, rd, rs1, rs2), line
        
        elif mnemonic == 'ADDI':
            # I-type: ADDI R7, R6, 100
            rd = self.parse_register(parts[1])
            rs1 = self.parse_register(parts[2])
            imm = self.parse_immediate(parts[3])
            return self.encode_i_type(mnemonic, rd, rs1, imm), line
        
        elif mnemonic == 'LI':
            # Pseudo: LI R7, 100 -> ADDI R7, R0, 100
            rd = self.parse_register(parts[1])
            imm = self.parse_immediate(parts[2])
            return self.encode_i_type('ADDI', rd, 0, imm), line
        
        elif mnemonic == 'LOAD':
            # M-type: LOAD R5, 16(R4) or LOAD R5, offset, R4
            rd = self.parse_register(parts[1])
            if '(' in line:
                # Format: offset(base)
                offset = self.parse_immediate(parts[2])
                rs1 = self.parse_register(parts[3])
            else:
                # Format: rd, offset, rs1
                offset = self.parse_immediate(parts[2])
                rs1 = self.parse_register(parts[3])
            return self.encode_i_type('LOAD', rd, rs1, offset), line
        
        elif mnemonic == 'STORE':
            # M-type: STORE R3, 0(R12) or STORE R3, offset, R12
            rs2 = self.parse_register(parts[1])
            if '(' in line:
                offset = self.parse_immediate(parts[2])
                rs1 = self.parse_register(parts[3])
            else:
                offset = self.parse_immediate(parts[2])
                rs1 = self.parse_register(parts[3])
            return self.encode_s_type('STORE', rs2, rs1, offset), line
        
        elif mnemonic in ['BEQ', 'BNE']:
            # B-type: BEQ R1, R0, label
            rs1 = self.parse_register(parts[1])
            rs2 = self.parse_register(parts[2])
            # Label will be resolved in second pass
            return (mnemonic, rs1, rs2, parts[3]), line
        
        elif mnemonic == 'NOP':
            # NOP: ADDI R0, R0, 0
            return self.encode_i_type('ADDI', 0, 0, 0), line
        
        elif mnemonic == 'HALT':
            return 0x7F, line
        
        else:
            raise ValueError(f"Unknown instruction: {mnemonic}")
    
    def assemble(self, source: str) -> List[int]:
        """Assemble source code and return list of machine code words"""
        lines = source.split('\n')
        
        # First pass: collect labels
        addr = 0
        for line in lines:
            result, orig = self.assemble_line(line, addr)
            if result is not None:
                self.instructions.append((addr, result, orig))
                addr += 4  # Each instruction is 4 bytes
        
        # Second pass: resolve labels and generate final code
        machine_code = []
        for addr, instr, orig in self.instructions:
            if isinstance(instr, tuple):
                # Branch instruction with label
                mnemonic, rs1, rs2, label = instr
                target_addr = self.labels.get(label)
                if target_addr is None:
                    raise ValueError(f"Undefined label: {label}")
                offset = target_addr - addr
                instr = self.encode_b_type(mnemonic, rs1, rs2, offset)
            
            machine_code.append(instr)
            print(f"0x{addr:08x}: 0x{instr:08x}  # {orig}")
        
        return machine_code
    
    def write_binary(self, machine_code: List[int], filename: str):
        """Write machine code to binary file"""
        with open(filename, 'wb') as f:
            for word in machine_code:
                # Write as little-endian 32-bit words
                f.write(word.to_bytes(4, byteorder='little'))
    
    def write_hex(self, machine_code: List[int], filename: str):
        """Write machine code to hex file (for simulation)"""
        with open(filename, 'w') as f:
            for word in machine_code:
                f.write(f"{word:08x}\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python assembler.py <input.s> [output.bin]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_base = sys.argv[2] if len(sys.argv) > 2 else input_file.rsplit('.', 1)[0]
    
    with open(input_file, 'r') as f:
        source = f.read()
    
    assembler = FluxAssembler()
    
    print(f"Assembling {input_file}...")
    print("=" * 60)
    
    try:
        machine_code = assembler.assemble(source)
        
        print("=" * 60)
        print(f"✓ Assembly successful: {len(machine_code)} instructions")
        
        # Write outputs
        assembler.write_binary(machine_code, f"{output_base}.bin")
        assembler.write_hex(machine_code, f"{output_base}.hex")
        
        print(f"✓ Binary written to: {output_base}.bin")
        print(f"✓ Hex written to: {output_base}.hex")
        
    except Exception as e:
        print(f"✗ Assembly failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
