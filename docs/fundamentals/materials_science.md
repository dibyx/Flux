# Materials Science for GPU Design

**Understanding the chemistry behind computer chips**

---

## Why Materials Matter

A modern GPU contains **50+ different materials**, each chosen for specific properties. This guide explains the chemistry and physics behind these choices.

---

## Core Materials

### 1. Silicon (Si)

**Chemical Properties**:
- Atomic number: 14
- Electron configuration: [Ne] 3s² 3p²
- Crystal structure: Diamond cubic
- Melting point: 1414°C

**Why Silicon?**
✓ **Perfect electron configuration**: 4 valence electrons  
✓ **Stable oxide** (SiO₂): Acts as excellent insulator  
✓ **Abundant**: 28% of Earth's crust  
✓ **Large crystals**: Can grow 300mm diameter wafers  
✓ **Mature technology**: 70+ years of development  

**Alternatives**:
- **Germanium (Ge)**: First semiconductors, but worse oxide
- **Gallium Arsenide (GaAs)**: Faster, but toxic and brittle
- **Silicon Carbide (SiC)**: High power, but expensive

**In flux GPU**: Every transistor channel is silicon!

---

### 2. Silicon Dioxide (SiO₂)

**Formation**:
```
Si + O₂ → SiO₂ (at high temp)
```

**Properties**:
- **Insulator**: Bandgap = 9 eV (vs Si's 1.1 eV)
- **Dielectric constant**: κ ≈ 3.9
- **Thermal stability**: Withstands 900°C processing
- **Thickness in modern chips**: 1-2 nm (4-8 atomic layers!)

**Use Cases**:
- **Gate oxide**: Insulates gate from channel
- **Interlayer dielectric**: Separates metal wires
- **Passivation**: Protects chip surface

**Problem at 5nm**: Too thin → electrons tunnel through!

**Solution**: High-κ dielectrics (see below)

---

### 3. Copper (Cu)

**Properties**:
- Conductivity: 5.96×10⁷ S/m (excellent!)
- Melting point: 1085°C
- Atomic weight: 63.5

**Why Copper for Wires?**
✓ **Low resistance**: 2× better than aluminum  
✓ **Electromigration resistance**: Atoms don't move as easily  
✓ **Cost**: Relatively cheap  

**Challenges**:
- **Diffuses into silicon**: Must use barrier layers
- **Harder to etch**: Can't use plasma like aluminum
- **Solution**: Damascene process (fill trenches)

**In Modern GPUs**:
- 10-15 metal layers
- Finest pitch: 30-40 nm
- Total wire length per chip: **~10 km!**

---

### 4. Hafnium Oxide (HfO₂)

**Discovery**: 2007 (Intel 45nm)

**Properties**:
- Dielectric constant: κ ≈ 25 (vs SiO₂'s 3.9)
- Bandgap: 6 eV
- **High-κ material**: More capacitance, less leakage

**Why It Replaced SiO₂**:
```
Capacitance = ε₀ × κ × Area / thickness

SiO₂: Need 1nm thickness → tunnel leakage!
HfO₂: Use 3nm thickness, same capacitance, less leakage
```

**Trade-off**: More expensive to deposit

---

## Doping Materials

### N-Type Dopants (Donors)

**Phosphorus (P)**:
- Atomic number: 15 (5 valence electrons)
- Concentration: ~10¹⁶ - 10¹⁸ atoms/cm³
- Diffuses easily → good for deep junctions

**Arsenic (As)**:
- Atomic number: 33 (5 valence electrons)
- Heavier → diffuses slower
- Used for shallow junctions

**Antimony (Sb)**:
- Atomic number: 51
- Very heavy → minimal diffusion
- For ultra-precise doping profiles

### P-Type Dopants (Acceptors)

**Boron (B)**:
- Atomic number: 5 (3 valence electrons)
- Small atom → diffuses quickly
- Most common p-type dopant

**Indium (In)** & **Gallium (Ga)**:
- Heavier alternatives
- Special applications

---

## Metal Layers

### Layer Stack (Bottom to Top)

| Layer | Material | Purpose | Thickness |
|-------|----------|---------|-----------|
| **Transistor contact** | Tungsten (W) | Heat-resistant | 50-100 nm |
| **M1-M3** (local) | Copper (Cu) | Short connections | 50-80 nm wide |
| **M4-M8** (intermediate) | Copper | Medium routing | 100-200 nm |
| **M9-M12** (global) | Copper | Power, long wires | 500-1000 nm |
| **Top** | Aluminum + Cu | Thick power rails | 2-5 μm |

**Why Different Sizes?**
- Thin wires: High density, high resistance
- Thick wires: Low resistance, carry more current

**In flux GPU**: ~10 layers estimated for full implementation

---

## Advanced Materials (5nm and Below)

### 1. Cobalt (Co)

**Use**: Contacts and local interconnects

**Why?**
- Better than copper at < 10nm width
- Doesn't need barrier layer
- First used: 7nm nodes

### 2. Ruthenium (Ru)

**Use**: Future interconnects (2nm, 1nm)

**Properties**:
- Better conductivity than Cu at tiny sizes
- Expensive! (Precious metal)

### 3. 2D Materials (Research)

**Graphene** (C):
- Single layer of carbon atoms
- Ultra-high conductivity
- Problem: Hard to manufacture, no bandgap

**Molybdenum Disulfide (MoS₂)**:
- Semiconductor with bandgap
- Atomic-scale thickness
- Potential future transistor channel

---

## Physical Vapor Deposition (PVD)

**How metals are deposited**:

**Sputtering**:
```
1. Put target (copper block) in vacuum
2. Bombard with argon ions (Ar⁺)
3. Copper atoms knocked off
4. Drift to wafer, stick to surface
5. Build up layer atom-by-atom
```

**Typical parameters**:
- Pressure: 10⁻⁶ Torr (ultra-vacuum)
- Temperature: 200-400°C
- Rate: 1-10 nm/minute

---

## Chemical Vapor Deposition (CVD)

**How insulators are deposited**:

**Example: SiO₂ deposition**
```
SiH₄ (silane gas) + O₂ → SiO₂ + 2H₂
       ↑                   ↓
   Reactants           Solid film
```

**Process**:
1. Flow gases into chamber
2. Heat wafer (300-800°C)
3. Chemical reaction on surface
4. SiO₂ grows layer-by-layer

**Atomic Layer Deposition (ALD)**: 
- Grows 1 atomic layer at a time
- Ultra-precise control
- Used for HfO₂

---

## Ion Implantation

**How doping is done**:

```
Ion Source → Acceleration → Mass Selection → Wafer
(P or B)     (20-200 keV)    (Filter)       (Target)

Example: Phosphorus implant
P → P⁺ (ionize)
P⁺ → Accelerate to 50 keV
P⁺ → Shoot into silicon at high speed
P → Embeds ~100 nm deep
```

**Annealing** (activation):
- Heat to 900-1100°C
- Dopant atoms move to lattice sites
- Become electrically active

---

## Etching

### Dry Etching (Plasma)

**Reactive Ion Etching (RIE)**:
```
SF₆ gas → Plasma (SF₆⁺, F radicals)
F atoms → Attack silicon
Si + 4F → SiF₄ (gas) ↑ (removed by vacuum)
```

**Anisotropic**: Etches straight down (not sideways)

### Wet Etching

**Example**: HF (hydrofluoric acid) vs SiO₂
```
SiO₂ + 6HF → H₂SiF₆ + 2H₂O
```

**Isotropic**: Etches all directions (rounded profile)

**Safety**: HF is extremely dangerous! (Penetrates skin)

---

## Purity Requirements

### Why 99.9999999% Pure?

**"Nine nines" (99.9999999%)**:

In 1 cm³ of silicon (5×10²² atoms):
- Impurities allowed: ~10¹³ atoms
- That's **1 in every 5 billion atoms!**

**Why so strict?**
- Unwanted impurities → change electrical properties
- One metal atom → can short transistor
- Process control → add dopants precisely

**Measurement**: Secondary Ion Mass Spectrometry (SIMS)

---

## Thermal Budget

**Problem**: Each processing step adds heat

**Effects of Heat**:
- Dopants diffuse (blur junction boundaries)
- Metals inter-diffuse (shorts!)
- Oxides grow thicker

**Solution**: "Low thermal budget" processes
- Laser annealing (heat only surface)
- Rapid Thermal Processing (RTP): 1-10 seconds vs hours

---

## Mechanical Properties

### Stress Management

**Problem**: Different materials expand at different rates

```
Copper: Expansion coefficient = 17 ppm/°C
Silicon: Expansion coefficient = 2.6 ppm/°C

Δ = 6× difference!
```

**At 100°C temperature swing**:
- Copper expands 0.17%
- Silicon expands 0.026%
- Result: **Stress** → cracks, delamination

**Solutions**:
- Barrier layers (TiN, Ta)
- Stress-relief layers
- Careful layer thickness design

---

## Chemistry in Manufacturing

### 1. Cleaning (RCA Clean)

**SC-1**: Remove organics
```
NH₄OH + H₂O₂ + H₂O (80-90°C)
```

**SC-2**: Remove metals
```
HCl + H₂O₂ + H₂O (70-80°C)
```

**Critical**: One dust particle = dead chip!

### 2. Photoresist

**Positive resist**:
- Exposed area becomes soluble
- Washed away by developer

**Negative resist**:
- Exposed area becomes insoluble
- Unexposed washed away

**Chemistry**: Light breaks polymer chains

---

## Material Innovations by Node

| Node | Key Material Innovation |
|------|------------------------|
| 130nm | Copper interconnects |
| 90nm | Strained silicon (faster!) |
| 45nm | High-κ/metal gate (HfO₂) |
| 22nm | FinFET (3D transistors) |
| 7nm | EUV lithography, Cobalt |
| 5nm | Extreme EUV, Ruthenium (research) |
| Future | 2D materials, Graphene? |

---

## Sustainability Concerns

**Water Usage**: 
- 1 chip consumes ~7,000 liters of ultra-pure water
- Fab needs 10 million liters/day

**Chemicals**:
- Hazardous: HF, arsine (AsH₃), phosphine (PH₃)
- Waste treatment critical

**Energy**:
- Modern fab: 50-100 MW power consumption
- Equivalent to small city

**Recycling**:
- Silicon reclaimed from test wafers
- Chemicals recycled where possible

---

## Hands-On: Materials in flux GPU

### Estimate Material Quantities

**One Shader Core** (hypothetical 28nm process):

| Material | Amount (per core) | Use |
|----------|----------|-----|
| Silicon | 0.05 mm² × 100 μm | Substrate |
| SiO₂ | 20 layers × 0.0001 mm² | Insulation |
| Copper | 10 layers × 50% fill | Wiring |
| Tungsten | 1 million vias | Contacts |
| HfO₂ | 560,000 transistors × 10 nm² | Gate oxide |

**80-core GPU**:
- Die size: ~200 mm²
- Materials: μg quantities of exotic elements!

---

## Key Takeaways

1. **Silicon**: The foundation (transistors, substrate)
2. **Dielectrics**: SiO₂ → HfO₂ for newer nodes
3. **Metals**: Al → Cu → Co/Ru as nodes shrink
4. **Purity**: 99.9999999% required
5. **Process**: Deposit, pattern, etch (repeat 50+ times!)
6. **Trade-offs**: Cost vs performance vs reliability

---

## Further Reading

**Books**:
- "Semiconductor Manufacturing Technology" by Quirk & Serda
- "Materials Science of Thin Films" by Ohring

**Videos**:
- [How Computer Chips Are Made](https://www.youtube.com/watch?v=35jWSQXXQgY) (ASML)
- [Intel Fab Tour](https://www.youtube.com/watch?v=d9SWNLZvA8g)

**Tools to Explore**:
- Yosys report: `make report` (shows physical implementation)
- Cross-sections: Search "chip die shot" on Google Images

---

**Next**: [Firmware Basics](../hw-tools/firmware/README.md) for programming your GPU
