# Hardware Testing Checklist

**Pre-flight checklist for FPGA testing with VGA output**

---

## ⚠️ Note

This checklist is for **future use** when you acquire the necessary hardware. All items can be prepared in advance using simulation.

---

## Equipment Checklist

### Required Hardware

- [ ] **ULX3S FPGA Board** (LFE5U-85F recommended)
  - Alternative: Any ECP5 board with sufficient resources
  - Min specs: 40k LUTs, 100 BRAMs
  
- [ ] **VGA Monitor**
  - Must support 640×480 @ 60Hz
  - Standard 15-pin VGA connector
  
- [ ] **USB Cable** (Type-A to Micro-B or Type-C)
  - For FPGA programming and power
  - Must support data transfer (not charge-only)
  
- [ ] **VGA Connection** (choose one):
  - **Option A**: Pmod VGA breakout board (~$15)
  - **Option B**: Custom resistor network (see wiring guide)
  - **Option C**: VGA DAC board

### Optional but Helpful

- [ ] **Oscilloscope** or logic analyzer
  - For debugging sync signals
  - Not required but very helpful
  
- [ ] **Multimeter**
  - Verify power supply voltages
  - Check resistor values
  
- [ ] **Breadboard + Jumper wires**
  - For prototyping VGA connections
  - Before soldering

---

## Software Prerequisites

### Development Tools

- [ ] **Yosys** (synthesis)
  ```bash
  yosys --version  # Should be 0.9+
  ```

- [ ] **nextpnr-ecp5** (place & route)
  ```bash
  nextpnr-ecp5 --version
  ```

- [ ] **ecppack** (bitstream generation)
  ```bash
  ecppack --help
  ```

- [ ] **fujprog** or **openocd** (programming)
  ```bash
  fujprog --help
  # OR
  openocd --version
  ```

### Testing Environment

- [ ] **Python 3.7+** with packages:
  ```bash
  pip install pyserial numpy
  ```

- [ ] **Repository cloned** and tools working:
  ```bash
  cd Flux/flux
  python sw-toolchain/asm/assembler.py --help
  python sw-toolchain/sim/simulator.py --help
  ```

---

## Pre-Synthesis Validation

### Simulation Tests (Do This First!)

- [ ] **Shader core simulation**
  ```bash
  cd rtl/test
  pytest test_shader_core.py -v
  ```
  **Expected**: All tests pass ✓

- [ ] **VGA timing simulation** (if available)
  - Verify 640×480 @ 60Hz timings in waveform
  - Check hsync/vsync polarities

- [ ] **Rasterizer simulation**
  - Test triangle drawing in Python
  ```bash
  cd hw-tools/graphics
  python triangle_demo.py simulation
  ```
  **Expected**: No errors, registers updated correctly

- [ ] **Assembler + Simulator workflow**
  ```bash
  cd sw-toolchain/asm
  python assembler.py ../../examples/vecadd.s
  cd ../sim
  python simulator.py ../../examples/vecadd.hex
  ```
  **Expected**: Correct results displayed

### Code Review

- [ ] **Check all file paths** in `hw-tools/fpga/synth.ys`
  - Verify all `.sv` files exist
  - Check relative paths are correct

- [ ] **Review pin constraints** in `ulx3s.lpf`
  - Match your board version (85F vs 45F vs 12F)
  - Verify GPIO pin assignments

- [ ] **Check top module** matches synthesis target
  - Should be `gpu_graphics_top` for graphics
  - Or `shader_core` for compute-only

---

## Synthesis Workflow

### Step 1: Static Analysis

- [ ] **Lint RTL code**
  ```bash
  verilator --lint-only -Wall rtl/src/**/*.sv
  ```
  **Expected**: No warnings or errors

- [ ] **Check syntax**
  ```bash
  yosys -p "read_verilog -sv rtl/src/**/*.sv; hierarchy -check"
  ```
  **Expected**: Clean output

### Step 2: Synthesis

- [ ] **Clean previous builds**
  ```bash
  cd hw-tools/fpga
  make clean
  ```

- [ ] **Run synthesis**
  ```bash
  make synth
  ```
  **Expected**: 
  - No errors
  - `flux_gpu.json` created
  - Resource report shows <15% LUT usage

- [ ] **Review resource usage**
  ```bash
  make report
  ```
  **Check**:
  - LUTs: ~10,500 (should be <20% of target)
  - BRAMs: ~80-100 (should be <50%)
  - Timing: No critical warnings

### Step 3: Place & Route

- [ ] **Run place & route**
  ```bash
  make pnr
  ```
  **Expected**:
  - Converges successfully
  - `flux_gpu_out.config` created
  - Timing meets 50 MHz (system) and 25 MHz (VGA)

- [ ] **Check timing report**
  ```bash
  make timing
  ```
  **Look for**:
  - Max frequency ≥ 50 MHz
  - Setup/hold times met
  - No critical paths

### Step 4: Bitstream Generation

- [ ] **Generate bitstream**
  ```bash
  make bitstream
  ```
  **Expected**: `flux_gpu.bit` file created (~2 MB)

- [ ] **Verify bitstream**
  ```bash
  ls -lh flux_gpu.bit
  ```
  **Size**: Should be 1-3 MB

---

## Hardware Setup

### FPGA Board Preparation

- [ ] **Visual inspection**
  - No damaged components
  - No bent pins
  - Clean and dry

- [ ] **Power test**
  - Connect USB only (no other connections)
  - Board LEDs should light up
  - Check for unusual heat or smells

### VGA Wiring (Critical!)

**Option A: Pmod VGA** (Recommended)

- [ ] Connect Pmod VGA to GPIO header
- [ ] Match pin numbers to constraints file
- [ ] Verify with multimeter (no shorts)

**Option B: Custom Resistor Network**

For each color channel (R, G, B):
```
[ULX3S GPIO] --[270Ω]--+--[To VGA Pin]
                        |
                      [470Ω]
                        |
                       GND
```

- [ ] **Red channel** (8 bits):
  - GP0-GP7 → VGA Pin 1
  - 8 resistor dividers built
  - Tested with multimeter
  
- [ ] **Green channel** (8 bits):
  - GP8-GP15 → VGA Pin 2
  - 8 resistor dividers built
  
- [ ] **Blue channel** (8 bits):
  - GP16-GP23 → VGA Pin 3
  - 8 resistor dividers built
  
- [ ] **H-Sync**:
  - GP24 → VGA Pin 13 (direct connection)
  
- [ ] **V-Sync**:
  - GP25 → VGA Pin 14 (direct connection)
  
- [ ] **Ground**:
  - ULX3S GND → VGA Pins 5,6,7,8,10

- [ ] **Connection verification**:
  - Continuity test all signals
  - No shorts between signals
  - No shorts to power

---

## Programming & Initial Test

### Step 1: Program FPGA

- [ ] **Connect USB cable**
  - Board powers up
  - OS recognizes device
  
- [ ] **Program SRAM** (temporary, for testing)
  ```bash
  fujprog flux_gpu.bit
  ```
  **OR**
  ```bash
  openocd -f ulx3s_prog.cfg -c "program_file flux_gpu.bit"
  ```
  
  **Expected**:
  - Programming completes (10-30 seconds)
  - "Success" message
  - Board LEDs change pattern

- [ ] **Visual check**
  - LEDs blinking/active
  - No smoke or unusual heat
  - Board stable

### Step 2: VGA Signal Check

- [ ] **Connect VGA monitor**
  - Secure cable connection
  - Monitor powered on
  - Monitor set to correct input

- [ ] **Check monitor detection**
  **Expected**: Monitor should detect signal
  - Display shows "640×480 @ 60Hz" or similar
  - May show black screen (framebuffer empty) - this is OK!

- [ ] **No signal?** Debug steps:
  1. Check VGA cable firmly connected
  2. Try different monitor
  3. Verify pin connections
  4. Check synthesis log for errors
  5. Use oscilloscope on sync signals

---

## Functional Testing

### Test 1: Test Pattern (Simplest)

- [ ] **Modify RTL** for hardcoded pattern:
  Edit `vga_controller.sv` to output color bars
  
- [ ] **Re-synthesize and program**
  
- [ ] **Verify output**:
  **Expected**: Three vertical bars (red, green, blue)

- [ ] **Result**: ✓ / ✗ / Notes: _______________

### Test 2: Framebuffer Access

- [ ] **Test pattern from firmware**:
  ```bash
  cd hw-tools/graphics
  python fill_screen_test.py uart  # If UART working
  ```
  
- [ ] **Verify**:
  - Send color commands via UART
  - Screen changes color
  
- [ ] **Result**: ✓ / ✗ / Notes: _______________

### Test 3: Triangle Rasterization

- [ ] **Hardcode triangle** in RTL:
  - Modify `gpu_graphics_top.sv`
  - Add auto-trigger logic
  
- [ ] **Expected**:
  - Triangle appears on screen
  - Correct color
  - Correct position
  
- [ ] **Result**: ✓ / ✗ / Notes: _______________

### Test 4: Dynamic Triangles

- [ ] **Button-triggered drawing**:
  - Press BTN1
  - Triangle draws
  
- [ ] **Multiple triangles**:
  - Draw 3+ triangles
  - Different colors
  - Verify overlapping
  
- [ ] **Result**: ✓ / ✗ / Notes: _______________

---

## Performance Measurement

### Rasterization Speed

- [ ] **Add cycle counter** to RTL:
  ```systemverilog
  reg [31:0] cycles;
  always @(posedge clk) begin
      if (tri_draw) cycles <= 0;
      else if (tri_busy) cycles <= cycles + 1;
  end
  assign led = cycles[31:24];  // Display on LEDs
  ```

- [ ] **Measure small triangle** (100×100):
  - Cycles: ____________
  - Time @ 50MHz: ____________ μs
  - **Target**: ~200 μs (10,000 cycles)

- [ ] **Measure large triangle** (400×400):
  - Cycles: ____________
  - Time @ 50MHz: ____________ ms
  - **Target**: ~3.2 ms (160,000 cycles)

### Frame Rate

- [ ] **Calculate max FPS**:
  ```
  Triangles/second = 50MHz / avg_cycles
  FPS (100 tri/frame) = triangles/second / 100
  ```
  
  - Measured: ____________ FPS
  - **Target**: 30-60 FPS for simple scenes

---

## Validation Checklist

### Visual Quality

- [ ] **Colors correct**
  - Red, green, blue display properly
  - No color channel swaps
  - No inverted colors

- [ ] **Geometry correct**
  - Triangles have straight edges
  - Correct fill (no gaps)
  - Vertices at specified coordinates

- [ ] **No artifacts**
  - No flickering
  - No screen tearing
  - No random pixels

### Electrical

- [ ] **Power consumption**
  - Measure USB current
  - Should be <500mA
  - No excessive heat

- [ ] **Signal integrity**
  - Clean sync signals (oscilloscope)
  - No ringing or overshoot
  - Proper voltage levels

---

## Documentation

### Record Results

- [ ] **Take photos/videos**
  - Test pattern output
  - Triangle rendering
  - Multiple triangles

- [ ] **Log measurements**
  - Resource usage (actual)
  - Performance metrics
  - Power consumption

- [ ] **Note issues**
  - Any bugs found
  - Workarounds applied
  - Future improvements

### Update Documentation

- [ ] **Update roadmap**
  - Mark FPGA testing complete
  - Add actual performance data

- [ ] **Update README**
  - Add photos of working system
  - Note any hardware-specific quirks

---

## Success Criteria

To mark FPGA testing as **complete**, verify:

✅ **Synthesis**: Builds without errors, meets timing  
✅ **Programming**: FPGA configures successfully  
✅ **VGA Output**: Monitor detects 640×480 @ 60Hz  
✅ **Test Pattern**: Color bars display correctly  
✅ **Triangle**: At least one triangle renders  
✅ **Performance**: Meets timing targets (~200 μs/triangle)  
✅ **Stability**: Runs for 10+ minutes without issues  

---

## Troubleshooting Quick Reference

| Issue | Check | Fix |
|-------|-------|-----|
| No synthesis | File paths | Fix synth.ys |
| Won't program | USB driver | Install fujprog/openocd |
| No VGA signal | Pin connections | Verify ulx3s.lpf |
| Wrong colors | Channel mapping | Swap R/G/B pins |
| Garbled output | Timing | Check clock PLL |
| No triangle | Trigger logic | Add debug LEDs |

---

## When You Get Hardware

1. **Start simple**: Just get LEDs blinking first
2. **One step at a time**: Test pattern → Framebuffer → Triangle
3. **Document everything**: Photos, logs, measurements
4. **Ask for help**: FPGA communities are friendly!

**This checklist ensures nothing is forgotten when hardware becomes available** ✓

---

**Estimated completion time**: 4-8 hours (first time with hardware)

**Good luck!** 🚀
