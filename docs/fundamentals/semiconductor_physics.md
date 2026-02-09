# Semiconductor Physics & Chip Design Fundamentals

**A beginner's guide to how GPUs work at the atomic level**

---

## Table of Contents
1. [Atoms to Transistors](#atoms-to-transistors)
2. [Logic Gates](#logic-gates)
3. [From Gates to GPU](#from-gates-to-gpu)
4. [Materials Science](#materials-science)

---

## Atoms to Transistors

### The Silicon Atom

**Why silicon?**
- 14 electrons (atomic number 14)
- 4 valence electrons → perfect for semiconductor behavior
- Abundant (28% of Earth's crust)
- Stable crystal structure

```
Silicon Atom (Si)
     Nucleus
    ●  +14
   / \ 
  Shells:
  - Inner: 10 electrons (full)
  - Outer: 4 electrons (valence)
  
  These 4 valence electrons allow:
  ✓ Bonding with neighbors (creates crystal)
  ✓ Controlled conductivity (with doping)
```

### Pure Silicon Crystal

**Diamond cubic structure**:
- Each Si atom bonds with 4 neighbors
- Perfect crystal at room temp → **insulator**
- No free electrons to carry current

```
   Si --- Si --- Si
   |      |      |
   Si --- Si --- Si  ← 3D lattice
   |      |      |
   Si --- Si --- Si
```

**Problem**: Pure silicon doesn't conduct electricity!  
**Solution**: Add impurities (doping)

---

## Doping: Creating Semiconductors

### N-Type (Negative) Doping

**Add phosphorus (P) atoms**:
- P has 5 valence electrons (vs Si's 4)
- Extra electron becomes **free** to move
- Creates electron "donors"

```
After doping with P:
   Si --- Si --- Si
   |      |      |
   Si --- P  --- Si  ← P has extra electron (-)
   |      |      |
   Si --- Si --- Si
   
   Free electron: ⚫ (can move!)
```

### P-Type (Positive) Doping

**Add boron (B) atoms**:
- B has 3 valence electrons (vs Si's 4)
- Creates "hole" (missing electron)
- Holes act like positive charges

```
After doping with B:
   Si --- Si --- Si
   |      |      |
   Si --- B  --- Si  ← B has a hole (⊕)
   |      |      |
   Si --- Si --- Si
   
   Hole: ⊕ (electrons jump into it)
```

---

## The Transistor: Building Block of GPUs

### MOSFET (Metal-Oxide-Semiconductor Field-Effect Transistor)

**Structure**:
```
        Gate (Metal)
           |
    ┌──────▼──────┐
    │   SiO₂      │ ← Insulator (oxide layer)
    ├─────────────┤
    │ P-type Si   │ ← Channel
    │             │
 N+ │             │ N+  ← Source & Drain (heavily doped)
────┴─────────────┴────
    ▲             ▲
  Source        Drain
```

**How it works**:

**OFF State** (Gate = 0V):
- P-type channel blocks current
- Source → Drain: No path ❌
- Transistor = **OPEN SWITCH**

```
Source ─┤├─ Drain  (blocked)
        No current flow
```

**ON State** (Gate = +5V):
- Electric field attracts electrons
- Creates N-channel in P-type
- Source → Drain: Path exists ✓
- Transistor = **CLOSED SWITCH**

```
Source ─┼┼─ Drain  (conducting)
        Current flows!
```

**Key insight**: Voltage at gate controls current!

---

## Logic Gates from Transistors

### NAND Gate (Universal Gate)

**Circuit** (2 transistors):
```
         +VDD (+5V)
           │
           ├─── Pull-up resistor
           │
           ├─── Output
           │
    A ────┤├───┐
           │    │
    B ────┤├───┴─── Ground
           │
```

**Truth Table**:
| A | B | Output |
|---|---|--------|
| 0 | 0 |   1    |
| 0 | 1 |   1    |
| 1 | 0 |   1    |
| 1 | 1 |   0    | ← Only FALSE when both ON

**Why NAND is special**: You can build ANY logic gate from NAND!

```
NOT:  A ─NAND─ A = NOT A
AND:  A ─NAND─ B ─NOT─ = A AND B
OR:   NOT A ─NAND─ NOT B = A OR B
```

### Building an Adder

**Half Adder** (adds 2 bits):
```
Inputs: A, B
Outputs: Sum, Carry

Sum   = A XOR B  ← Needs 4 NANDs
Carry = A AND B  ← Needs 2 NANDs

Total: 6 transistors per half-adder
```

**Full Adder** (adds 3 bits: A + B + Carry_in):
- Uses 2 half-adders
- ~28 transistors total

**32-bit Adder**:
- 32 full adders chained
- ~900 transistors!
- This is just ONE instruction in our ALU

---

## From Gates to GPU

### Hierarchy of Complexity

```
1 Transistor
  ↓
Logic Gate (2-6 transistors)
  ↓
Adder/Multiplexer (10-100 transistors)
  ↓
ALU (1,000-10,000 transistors)
  ↓
Shader Core (100,000-1M transistors)
  ↓
GPU (10 billion transistors!)
```

### Transistor Budget (Modern GPU)

| Component | Transistors | Percentage |
|-----------|-------------|------------|
| **Shader Cores** | 8 billion | 80% |
| Memory Controllers | 500 million | 5% |
| L2 Cache | 1 billion | 10% |
| ROPs, Texture Units | 300 million | 3% |
| Control Logic | 200 million | 2% |
| **Total** | **~10 billion** | **100%** |

**Example**: NVIDIA RTX 4090 has **76 billion transistors**!

---

## Materials Science

### Why Different Materials?

| Material | Use in GPU | Property |
|----------|-----------|----------|
| **Silicon (Si)** | Transistors | Semiconductor |
| **Silicon Dioxide (SiO₂)** | Gate insulator | Electrical insulator |
| **Copper (Cu)** | Wires | High conductivity |
| **Aluminum (Al)** | Older wires | Good conductor, cheaper |
| **Tungsten (W)** | Vias (vertical connections) | High melting point |
| **Hafnium Oxide (HfO₂)** | Advanced gates | Better insulator than SiO₂ |

### Manufacturing Process (Simplified)

**Step 1: Grow Silicon Wafer**
- Start with ultra-pure silicon crystal
- Typical: 300mm diameter, 0.7mm thick
- Each wafer → hundreds of chips

**Step 2: Photolithography**
```
1. Coat wafer with photoresist (light-sensitive)
2. Place mask with circuit pattern
3. Expose to UV light (193nm wavelength)
4. Develop: exposed areas dissolve
5. Etch: remove silicon in pattern
6. Repeat 50+ times for different layers!
```

**Step 3: Doping**
- Ion implantation: shoot phosphorus/boron ions
- Diffusion: heat to spread dopants
- Precision: ~10¹⁵ atoms/cm³

**Step 4: Metallization**
- Deposit copper for wires
- Create 10-15 metal layers
- Connect billions of transistors

**Result**: Modern 5nm chip has:
- **50 billion** transistors
- **15 metal layers**
- Features as small as **5 nanometers** (15 silicon atoms!)

---

## Modern Process Nodes

### What "5nm" Really Means

**Historical**:
- 1990s: "130nm" = actual transistor gate length
- Today: "5nm" = **marketing term**
- Actual gate length: ~18-20nm

**Why it matters**:
- Smaller → More transistors per area
- More transistors → More powerful GPU
- But: Heat density increases!

### Process Evolution

| Year | Node | Transistors (GPU) |
|------|------|-------------------|
| 2010 | 40nm | 3 billion |
| 2014 | 28nm | 8 billion |
| 2018 | 12nm | 18 billion |
| 2020 | 7nm  | 28 billion |
| 2024 | 5nm  | 76 billion |

**Moore's Law**: Transistor count doubles every ~2 years (slowing down!)

---

## Quantum Effects (Advanced Topic)

At 5nm, quantum mechanics becomes important:

### 1. Tunneling
- Electrons can "jump through" thin barriers
- Gate oxide: <1nm thick
- Leakage current increases → power waste

### 2. Variability
- Individual atoms matter
- One misplaced dopant → transistor failure
- Yield: Only 70-90% of chips work!

**Solutions**:
- FinFET transistors (3D structure)
- High-κ dielectrics (HfO₂)
- EUV lithography (13.5nm wavelength)

---

## Key Takeaways for GPU Design

1. **Transistors are switches**: Controlled by voltage
2. **Logic gates**: Built from transistors (NAND = universal)
3. **Everything is layers**: 
   - Transistors (silicon)
   - Insulators (oxide)
   - Wires (copper)
4. **Scaling challenges**:
   - Smaller = faster + more power-efficient
   - But: harder to manufacture, quantum effects
5. **Materials matter**:
   - Different materials for different jobs
   - Purity is critical (99.9999999%!)

---

## Hands-On: Estimate GPU Transistor Count

**Our flux Shader Core**:
- 4-wide ALU: ~2,000 transistors per lane = **8,000**
- Register file (32 threads × 32 regs × 128-bit): ~**500,000**
- Decoder + control: ~**50,000**
- **Total per core: ~560,000 transistors**

**Scale to production**:
- 80 shader cores: 45 million
- L2 cache (8MB): 500 million
- Memory controller: 100 million
- **Estimated total: ~650 million transistors**

(Real GPUs have 10-100× more due to additional features!)

---

## Further Reading

**Books**:
- "Digital Design and Computer Architecture" by Harris & Harris
- "CMOS VLSI Design" by Weste & Harris

**Online**:
- [How Transistors Work](https://www.youtube.com/watch?v=IcrBqCFLHIY) (Video)
- [Semiconductor Manufacturing](https://semiengineering.com/)

**Your GPU**:
- Study `rtl/src/shader_core/simd_alu.sv`
- Each `+` operation → thousands of transistors!
- Synthesis tool converts RTL → transistors automatically

---

**Next**: [Logic Gates Tutorial](logic_gates_tutorial.md) for hands-on gate design
