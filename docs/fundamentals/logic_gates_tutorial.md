# Logic Gates & Digital Design Tutorial

**Hands-on introduction to building digital circuits**

---

## Prerequisites
None! Start from zero knowledge.

---

## Part 1: What is a Logic Gate?

**Definition**: A circuit that performs a logical operation on one or more inputs and produces a single output.

**Key concept**: Everything in computers is built from these!

---

## Basic Gates

### NOT Gate (Inverter)

**Function**: Flips the input
```
Input → ●─┤o├─● → Output
        NOT

Truth Table:
 In | Out
----+----
 0  |  1   ← Flip
 1  |  0   ← Flip
```

**Real-world**: Light switch (ON→OFF, OFF→ON)

### AND Gate

**Function**: Output is 1 only if BOTH inputs are 1
```
A ─┬─●
   │   AND  → Output
B ─┴─●

Truth Table:
 A | B | Out
---+---+----
 0 | 0 |  0
 0 | 1 |  0
 1 | 0 |  0
 1 | 1 |  1  ← Only TRUE here
```

**Real-world**: Door with 2 locks (need BOTH keys)

### OR Gate

**Function**: Output is 1 if AT LEAST ONE input is 1
```
A ─┬─●
   │   OR  → Output
B ─┴─●

Truth Table:
 A | B | Out
---+---+----
 0 | 0 |  0
 0 | 1 |  1  ← One is enough
 1 | 0 |  1  ← One is enough
 1 | 1 |  1
```

**Real-world**: Light with 2 switches (either works)

### XOR Gate (Exclusive OR)

**Function**: Output is 1 if inputs are DIFFERENT
```
A ─┬─⊕
   │   XOR  → Output
B ─┴─⊕

Truth Table:
 A | B | Out
---+---+----
 0 | 0 |  0
 0 | 1 |  1  ← Different
 1 | 0 |  1  ← Different
 1 | 1 |  0  ← Same
```

**Real-world**: Toggle switch (flips state)

---

## Part 2: Building an Adder

### Half Adder (adds 2 bits)

**Problem**: Add A + B, produce Sum and Carry

```
Example: 1 + 1 in binary
  1
+ 1
---
 10  ← Sum=0, Carry=1
```

**Circuit**:
```
A ─┬─⊕─ Sum
   │  
B ─┼─⊕
   │
   └─AND─ Carry
```

**How it works**:
- Sum = A XOR B (1 if different)
- Carry = A AND B (1 if both 1)

**Truth Table**:
| A | B | Sum | Carry |
|---|---|-----|-------|
| 0 | 0 |  0  |   0   |
| 0 | 1 |  1  |   0   |
| 1 | 0 |  1  |   0   |
| 1 | 1 |  0  |   1   | ← 1+1=2 (10 in binary)

### Full Adder (adds 3 bits)

**Problem**: Add A + B + Carry_in (for chaining)

**Circuit**: 2 half-adders + OR
```
A ──┬─────────⊕─┬─ Sum
    │          │ 
B ──┼───⊕─────┼─⊕
    │         │
C_in┴─AND──┬──┘
           │
        OR─┴── Carry_out
```

**Example**: 1 + 1 + 1
```
  1
  1
+ 1 (carry from previous)
---
 11  → Sum=1, Carry=1
```

---

## Part 3: Multi-bit Adder

### 4-bit Ripple Adder

Add two 4-bit numbers: A[3:0] + B[3:0]

```
   A3 B3    A2 B2    A1 B1    A0 B0
    │ │      │ │      │ │      │ │
    ▼ ▼      ▼ ▼      ▼ ▼      ▼ ▼
   ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐
C3◄┤ FA  │◄─┤ FA  │◄─┤ FA  │◄─┤ HA  │◄ 0
   └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘
      │        │        │        │
      S3       S2       S1       S0
      
Result: S[3:0], Carry C3
```

**Example**: 5 + 6 = 11
```
Binary:
  0101  (5)
+ 0110  (6)
------
  1011  (11)
```

**Problem**: "Ripple" delay
- Bit 3 waits for bit 2
- Bit 2 waits for bit 1
- Slow for large numbers!

**Solution**: Carry Look-ahead Adder (advanced topic)

---

## Part 4: Memory Elements

### SR Latch (Set-Reset)

**Function**: Stores 1 bit

```
S (Set)   ─┬─NOR─┬─┐
           │     │ │ Q (Output)
R (Reset) ─┴─NOR─┴─┘
             ↑
           Feedback loop!
```

**Operation**:
- S=1, R=0 → Q=1 (Set)
- S=0, R=1 → Q=0 (Reset)
- S=0, R=0 → Q=previous (Hold)
- S=1, R=1 → **Forbidden** (unstable)

**Key idea**: Feedback creates memory!

### D Flip-Flop (with Clock)

**Function**: Stores input value on clock edge

```
D (Data) ───┐
            │  DFF  ├─ Q
CLK (Clock)─┘       

Timing diagram:
CLK  ┐ ┌─┐ ┌─┐ ┌─┐
     └─┘ └─┘ └─┘ └─┘
D    0 1 1 0 1 0 ...
Q    - 0─1───0─1─...  ← Changes on rising edge
```

**Use in GPU**: Register file (32 threads × 32 regs × 128 bits = millions of flip-flops!)

---

## Part 5: Multiplexer (Data Selector)

### 2:1 Multiplexer

**Function**: Select between 2 inputs

```
D0 ──┐
     ├─●─ Output
D1 ──┘ 
      ▲
      │
    Select (S)
    
If S=0 → Output = D0
If S=1 → Output = D1
```

**Circuit**:
```
D0 ─AND─┐
        │
    S  NOT    OR── Output
        │     │
D1 ─AND─┘

When S=0: Top AND enabled, bottom disabled
```

**Use in GPU**: Operand selection (immediate vs register)

---

## Part 6: Building Our ALU

### Simple 2-bit ALU

**Operations**:
- Op=00: ADD
- Op=01: SUB
- Op=10: AND
- Op=11: OR

**Circuit**:
```
      A B         A B         A B
      │ │         │ │         │ │
      ▼ ▼         ▼ ▼         ▼ ▼
    ┌─────┐     ┌─────┐     ┌─────┐
    │ ADD │     │ AND │     │ OR  │
    └──┬──┘     └──┬──┘     └──┬──┘
       │           │           │
       └────┬──────┴──────┬────┘
            │             │
            ▼             ▼
        ┌───────────────────┐
        │   4:1 MUX         │
        │   (Select by Op)  │
        └─────────┬─────────┘
                  │
              Result
```

**In flux GPU**:
- See `rtl/src/shader_core/simd_alu.sv`
- Same concept, but 4-wide SIMD!
- Each lane is independent ALU

---

## Part 7: Putting It All Together

### From Gates to GPU

**Level 1: Gates** (transistors)
```
NAND gate = 4 transistors
```

**Level 2: Combinational Logic** (gates)
```
Half Adder = 5 gates
Full Adder = 9 gates
4-bit Adder = 36+ gates
```

**Level 3: Sequential Logic** (gates + storage)
```
D Flip-flop = 6 NAND gates
Register = 32 flip-flops (for 32-bit)
```

**Level 4: Functional Units** (hundreds of gates)
```
ALU = Adder + Logic + Shifter
Register File = Array of registers + MUXes
```

**Level 5: Processor Core** (thousands of gates)
```
Shader Core = ALU + Registers + Decoder
= ~10,000 gates = ~50,000 transistors
```

**Level 6: GPU** (billions of gates!)
```
80 shader cores + Memory + ROPs
= millions of gates
= billions of transistors
```

---

## Hands-On Exercises

### Exercise 1: Design a 2-bit Comparator
**Goal**: Output 1 if A == B

**Hint**:
- Compare each bit with XNOR
- AND the results

**Solution**:
```
A1 ─XNOR─┐
B1 ──┘   │
         ├─AND─ Equal
A0 ─XNOR─┘
B0 ──┘
```

### Exercise 2: 4:1 Multiplexer
**Goal**: Select from 4 inputs using 2 select lines

**Hint**: Use three 2:1 MUXes

### Exercise 3: Count Transistors
**Question**: How many transistors in a 32-bit register?

**Answer**:
- 32 bits × 6 transistors/flip-flop = **192 transistors**
- flux register file: 32 registers × 128 bits × 6 = **24,576 transistors** (one thread)

---

## Connection to flux GPU

### Where You See These Gates

**1. Instruction Decoder** (`instruction_decoder.sv`)
```systemverilog
assign opcode = instruction[6:0];  ← MUX (bits extraction)
```

**2. ALU** (`simd_alu.sv`)
```systemverilog
case (alu_op)
    ALU_ADD: result = a + b;  ← Adder chain
    ALU_MUL: result = a * b;  ← Multiplier array
```

**3. Register File** (`register_file.sv`)
```systemverilog
reg [DATA_WIDTH-1:0] registers [0:1023];  ← Thousands of flip-flops
```

---

## Synthesis: RTL → Gates

**Yosys** (synthesis tool) converts:

```systemverilog
// Your code
assign sum = a + b;
```

↓ **Synthesizes to** ↓

```
Multiple full adders
→ Hundreds of NAND gates
→ Thousands of transistors
```

**Command**:
```bash
cd hw-tools/fpga
make report
# Shows: "Number of LUTs: 8,000"
# LUT = Look-Up Table = pre-built logic function
```

---

## Key Takeaways

1. **Everything is gates**: Your high-level code becomes billions of gates
2. **Building blocks**: Gates → Adders → ALUs → Cores → GPU
3. **Abstraction**: You write SystemVerilog, tools handle gates
4. **Verification matters**: One wrong gate = chip fails!
5. **Trade-offs**: More gates = faster but more area/power

---

## Next Steps

1. **Simulate gates**: Use online tools like [LogicBruno](https://logibruno.web.app/)
2. **Practice HDL**: Verilog tutorial [HDLBits](https://hdlbits.01xz.net/)
3. **Study flux RTL**: Start with `instruction_decoder.sv` (simple logic)
4. **Build your own**: Try designing a simple 8-bit CPU!

---

**Further Reading**:
- "Code: The Hidden Language of Computer Hardware and Software" by Charles Petzold
- [NandGame](https://nandgame.com/) - Build a computer from NAND gates (game!)
- flux source: Every `always @(*)` block = combinational logic = gates!
