# flux GPU - ASIC Tape-Out Guide

**Complete guide to fabricating flux GPU as an ASIC using open-source tools**

---

## Overview

This guide covers the complete journey from RTL to silicon using:
- **SkyWater 130nm PDK** (open-source process design kit)
- **OpenLane** (automated RTL-to-GDSII flow)
- **Chip shuttle programs** (affordable multi-project wafers)

**Timeline**: 6-12 months from start to first silicon  
**Cost**: $10-$300 (via shuttle) or $10,000+ (dedicated run)

---

## Prerequisites

### Software Tools

Install the complete open-source ASIC toolchain:

**1. OpenLane** (RTL-to-GDSII flow)
```bash
git clone https://github.com/The-OpenROAD-Project/OpenLane
cd OpenLane
make
```

**2. SkyWater 130nm PDK**
```bash
git clone https://github.com/google/skywater-pdk
cd skywater-pdk
make sky130A
```

**3. Supporting Tools**
- Magic (VLSI layout tool)
- KLayout (GDSII viewer)
- Netgen (LVS checking)
- ngspice (SPICE simulation)

### Knowledge Requirements

- ✅ Digital design fundamentals
- ✅ Verilog/SystemVerilog
- ✅ Basic VLSI concepts (setup/hold, DRC, LVS)
- ⚠️ ASIC-specific knowledge (nice to have)

---

## Step 1: Design Preparation (2-4 weeks)

### Clean RTL for ASIC

**Remove FPGA-specific constructs**:
```systemverilog
// Bad (FPGA-specific):
(* ram_style = "block" *) reg [31:0] memory [0:1023];

// Good (ASIC-compatible):
reg [31:0] memory [0:1023];  // Synth tool will infer SRAM
```

**Use synchronous resets**:
```systemverilog
// Good for ASIC:
always @(posedge clk) begin
    if (!rst_n_sync)  // Synchronized reset
        counter <= 0;
    else
        counter <= counter + 1;
end
```

**Avoid latches** (always specify all cases):
```systemverilog
// Bad (creates latch):
always @(*) begin
    if (sel)
        out = a;
    // Missing else!
end

// Good:
always @(*) begin
    if (sel)
        out = a;
    else
        out = b;
end
```

### Clock Strategy

**For flux GPU**:
- System clock: 25-50 MHz (conservative for 130nm)
- VGA clock: 25.175 MHz (standard)

**Clock tree synthesis** handled by OpenLane automatically.

### Memory Compilation

Large memories (framebuffer, register file) should use **compiled SRAM**:

```tcl
# In OpenLane config.json:
"MACROS": {
  "framebuffer_sram": {
    "gds": "path/to/sram.gds",
    "lef": "path/to/sram.lef"
  }
}
```

SkyWater provides SRAM compiler for generating optimized memory blocks.

---

## Step 2: Synthesis & Floorplanning (1-2 weeks)

### Run OpenLane Synthesis

```bash
cd hw-tools/asic
make synth
```

**Expected output**:
```
=== flux_gpu_asic ===
Number of cells:      15,000-25,000
Chip area:            ~1.5 mm²
Number of nets:       20,000-30,000
Number of registers:  5,000-8,000
```

### Floorplan

```bash
make floorplan
```

**Key decisions**:
- Die size: Based on utilization (aim for 40-50%)
- Aspect ratio: Square (1:1) or rectangular
- Power grid: 25μm pitch (adequate for 130nm)
- I/O placement: Peripheral pads

### Check Floorplan

```bash
make view
# Opens KLayout with floorplan
```

**Verify**:
- ✅ Reasonable die size (<3 mm² for shuttle)
- ✅ Power rails properly placed
- ✅ I/O pads accessible
- ✅ No DRC violations

---

## Step 3: Placement & Routing (2-4 weeks)

### Placement

```bash
make place
```

**This places **all standard cells** on the die. OpenLane optimizes for:
- Timing (meet clock constraints)
- Routability (cells not too dense)
- Power (minimize switching)

### Clock Tree Synthesis (CTS)

```bash
make cts
```

**Builds balanced clock tree** to deliver clock to all flip-flops with minimal skew.

### Routing

```bash
make route
```

**Connects all nets** using metal layers 1-5. This is the most time-consuming step (can take hours).

**Check routing results**:
```bash
make stats
```

Look for:
- ✅ 0 DRC violations
- ✅ 0 antenna violations
- ✅ All nets routed (100%)
- ✅ Timing met (positive slack)

---

## Step 4: Verification (2-3 weeks)

### Design Rule Check (DRC)

```bash
make drc
```

**Checks**: Minimum width, spacing, overlap rules for SkyWater 130nm.

**Goal**: **Zero DRC violations**

If failures:
1. Review violations in Magic
2. Adjust floorplan or placement density
3. Re-run routing

### Layout vs Schematic (LVS)

```bash
make lvs
```

**Verifies**: GDSII layout matches synthesized netlist.

**Goal**: **LVS clean** (all nets match)

### Static Timing Analysis (STA)

```bash
make sta
```

**Checks**: Setup/hold times, max frequency.

**Goal**:
- Setup slack > 0 (at target frequency)
- Hold slack > 0
- No timing violations

**Example output**:
```
Max frequency: 47.3 MHz
Setup slack:   +1.2 ns
Hold slack:    +0.8 ns
Critical path: reg_file → alu → reg_file (21.1 ns)
```

### Functional Verification

**Run gate-level simulation** with Icarus Verilog:
```bash
iverilog -o sim runs/latest/results/synthesis/flux_gpu_asic.v testbench.v
vvp sim
```

**Test**:
- ✅ Basic instructions execute correctly
- ✅ VGA timing correct
- ✅ Triangle rasterization works
- ✅ No X/Z values in simulation

---

## Step 5: GDSII Generation (1 week)

### Generate Final GDSII

```bash
make gdsii
```

**Output**: `runs/latest/results/magic/flux_gpu_asic.gds`

This is the **final chip layout** ready for fabrication!

### Final Checks

```bash
# View in KLayout
klayout runs/latest/results/magic/flux_gpu_asic.gds

# Check file size
ls -lh runs/latest/results/magic/flux_gpu_asic.gds
# Should be 5-50 MB depending on design size
```

### Generate Documentation

**Automatically generated by OpenLane**:
- Die photo (PNG)
- Statistics report
- Timing report
- Power estimate
- Area breakdown

---

## Step 6: Tape-Out Submission (1-2 weeks)

### Choose Fabrication Method

**Option A: ChipIgnite** (Google-sponsored shuttles)
- Cost: FREE (for educational projects)
- Timeline: 3-6 months
- Apply: https://efabless.com/chipignite
- Slots: Limited (competitive)

**Option B: Multi-Project Wafer (MPW)**
- Cost: $10-$300 per design
- Providers: Efabless, TinyTapeout, MOSIS
- Timeline: 3-6 months
- More accessible than ChipIgnite

**Option C: Full Wafer**
- Cost: $10,000-$50,000+
- For: Production runs
- Not recommended for educational projects

### Prepare Submission Package

**Required files**:
1. `flux_gpu_asic.gds` - Layout
2. `flux_gpu_asic.lef` - Abstract view
3. `flux_gpu_asic.v` - Gate-level netlist
4. Datasheet (PDF)
5. Test plan

### Submit to Shuttle

**Example: Efabless MPW**
```bash
# Clone submission template
git clone https://github.com/efabless/caravel_user_project

# Copy your GDS
cp runs/latest/results/magic/flux_gpu_asic.gds caravel_user_project/gds/

# Run pre-check
make precheck

# Submit via GitHub PR
```

**Review process**: 1-2 weeks for acceptance

---

## Step 7: Waiting for Silicon (3-6 months)

While waiting:
- ✅ Prepare test setup (PCB, software)
- ✅ Write detailed test plan
- ✅ Review datasheet
- ✅ Simulate corner cases

**Typical timeline**:
- Month 0: Submission
- Month 1: Manufacturing starts
- Month 3: Wafer fabrication complete
- Month 4: Dicing and packaging
- Month 5: Shipping
- Month 6: Chips arrive!

---

## Step 8: First Silicon Testing (2-4 weeks)

### Initial Power-On

**Procedure**:
1. Visual inspection (microscope)
2. Continuity test (multimeter)
3. Apply power (1.8V carefully!)
4. Check current draw (~10-50 mA expected)
5. Clock input (start slow, 1 MHz)
6. Toggle reset
7. Monitor status pins

### Functional Testing

**Bring-up checklist**:
- [ ] Power supplies OK
- [ ] Clock input working
- [ ] Reset functional
- [ ] Simple register write/read
- [ ] Execute NOP instruction
- [ ] Execute ADD instruction
- [ ] Memory access
- [ ] VGA sync signals
- [ ] Triangle rasterization
- [ ] Full system test

### Debugging

**Common first-silicon issues**:
- ❌ **No response**: Check power, clock, reset
- ❌ **Wrong outputs**: Timing issue, re-check STA
- ❌ **Partial function**: Some blocks work, others don't
- ❌ **Intermittent**: Temperature, voltage sensitivity

**Tools**:
- Logic analyzer (check signals)
- Oscilloscope (timing)
- JTAG debugger (if included)

---

## Cost Breakdown

### DIY Open-Source Approach

| Item | Cost |
|------|------|
| Software tools | $0 (all open-source) |
| SkyWater PDK | $0 (free) |
| OpenLane flow | $0 (free) |
| MPW shuttle slot | $50-$300 |
| PCB for testing | $50-$100 |
| Test equipment (optional) | $200-$500 |
| **Total** | **$300-$900** |

### Traditional Commercial Approach

| Item | Cost |
|------|------|
| EDA tools (Cadence/Synopsys) | $50,000-$200,000/year |
| PDK license | $10,000-$50,000 |
| Dedicated fabrication | $200,000-$1,000,000+ |
| **Total** | **$260,000+** |

**Open-source saves >99% of cost!** 🎉

---

## Resources

### Documentation
- [SkyWater PDK Docs](https://skywater-pdk.readthedocs.io/)
- [OpenLane Docs](https://openlane.readthedocs.io/)
- [Efabless Platform](https://efabless.com/)

### Communities
- [OpenLane Slack](https://invite.skywater.tools/)
- [VLSI Discord servers]
- [r/ASIC subreddit]

### Learning
- "Digital VLSI Design with Verilog" (Elsevier)
- "CMOS VLSI Design" (Weste & Harris)
- Online courses: Coursera, edX

---

## Realistic Expectations

### What Will Work
- ✅ Basic compute operations
- ✅ VGA timing generation
- ✅ Simple triangle rasterization
- ✅ Low-speed operation (25-50 MHz)

### Likely Issues
- ⚠️ Some timing paths may fail
- ⚠️ First batch may have bugs
- ⚠️ Yield may be low (50-80%)
- ⚠️ Performance lower than simulation

### Success Criteria
- ✅ Chip powers on
- ✅ Executes at least one instruction
- ✅ Shows VGA output
- ✅ Learning experience gained!

**First silicon rarely works perfectly - this is normal!**

---

## Next Steps

Ready to tape out?

**Phase 1**: Prepare design (use this guide)  
**Phase 2**: Run OpenLane flow  
**Phase 3**: Verify thoroughly  
**Phase 4**: Submit to shuttle  
**Phase 5**: Wait (3-6 months)  
**Phase 6**: Test first silicon  
**Phase 7**: Document results  
**Phase 8**: Iterate for rev B!  

**Good luck with your tape-out!** 🚀🔬

---

**Questions? Check flux documentation or ask in open-source VLSI communities!**
