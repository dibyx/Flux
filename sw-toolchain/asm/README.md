# flux Assembler README

## Overview

The **flux assembler** converts assembly language programs into machine code for the flux GPU.

## Usage

```bash
python assembler.py <input.s> [output_base]
```

### Examples

```bash
# Assemble vector addition
cd flux/sw-toolchain/asm
python assembler.py ../examples/vecadd.s

# Outputs:
# - vecadd.bin (binary machine code)
# - vecadd.hex (hex format for simulation)
```

## Assembly Language Syntax

### Registers
- `R0` - `R31`: General-purpose registers
- `R0` is hardwired to zero

### Instructions

**Arithmetic (R-type)**:
```assembly
ADD R3, R1, R2    # R3 = R1 + R2
SUB R3, R1, R2    # R3 = R1 - R2
MUL R3, R1, R2    # R3 = R1 * R2
DIV R3, R1, R2    # R3 = R1 / R2
```

**Immediate (I-type)**:
```assembly
ADDI R7, R6, 100  # R7 = R6 + 100
LI R5, 42         # R5 = 42 (pseudo: ADDI R5, R0, 42)
```

**Memory (M-type)**:
```assembly
LOAD R5, 16(R4)   # R5 = MEM[R4 + 16]
STORE R3, 0(R12)  # MEM[R12 + 0] = R3
```

**Control Flow**:
```assembly
BEQ R1, R0, label # if (R1 == 0) goto label
BNE R1, R2, label # if (R1 != R2) goto label
JAL label         # R31 = PC+4; PC = label
```

**Special**:
```assembly
NOP               # No operation
HALT              # Stop execution
```

### Labels

```assembly
main:
    ADD R1, R2, R3
loop:
    ADDI R1, R1, 1
    BNE R1, R10, loop
```

### Comments

```assembly
# This is a comment
ADD R1, R2, R3  # R1 = R2 + R3
```

## Output Formats

### Binary (.bin)
- Little-endian 32-bit words
- Ready to load into instruction memory

### Hex (.hex)
- One hex word per line
- For use with RTL simulators (`$readmemh`)

## Examples

See `../examples/` for sample programs:
- `vecadd.s` - Vector addition
- `dotprod.s` - Dot product
- `loop.s` - Loop with branches
- `conditional.s` - If-else statement

## Implementation Notes

The assembler performs **two passes**:

1. **First pass**: Collect labels and their addresses
2. **Second pass**: Resolve label references and generate machine code

### Immediate Encoding
- I-type: 12-bit sign-extended immediate
- Negative values: Use two's complement

### Branch Offsets
- Relative to PC
- Automatically calculated from labels
- Byte-addressed (address / 4 for instruction offset)

---

See [ISA Specification](../../docs/specs/isa.md) for complete instruction encoding details.
