# FPGA Testing Guide for flux GPU with Graphics

**Testing the complete GPU with VGA output on ULX3S**

---

## Prerequisites

### Hardware Required
- ✅ ULX3S FPGA board (LFE5U-85F)
- ✅ USB cable (for programming + power)
- ✅ VGA monitor
- ✅ VGA breakout cable OR custom wiring

### Software Required
- ✅ Yosys (synthesis)
- ✅ nextpnr-ecp5 (place & route)
- ✅ ecppack (bitstream generation)
- ✅ OpenOCD or fujprog (programming)

---

## Step 1: Synthesize for FPGA

### Build Complete Design

```bash
cd hw-tools/fpga

# Clean previous builds
make clean

# Synthesize graphics pipeline
make all

# Expected output:
# - flux_gpu.json (netlist)
# - flux_gpu_out.config (placed design)
# - flux_gpu.bit (bitstream)
```

### Check Resource Usage

```bash
make report
```

**Expected Resources**:
- LUTs: ~10,500 (12% of 84k)
- FFs: ~13,500
- BRAMs: ~96 (46% of 208)
- Frequency: 50 MHz system, 25 MHz VGA

**If synthesis fails**:
- Check file paths in `synth.ys`
- Verify all `.sv` files exist
- Check syntax errors with `verilator --lint-only`

---

## Step 2: VGA Wiring

### Option A: VGA Breakout Board (Recommended)

Use a commercial VGA breakout (Pmod VGA or similar):
- Connect to ULX3S GPIO header
- Follow breakout board pinout

### Option B: Custom Wiring

**VGA DB-15 Connector Pinout**:
```
Pin 1:  Red       → ULX3S GP0-GP7 via resistors
Pin 2:  Green     → ULX3S GP8-GP15 via resistors
Pin 3:  Blue      → ULX3S GP16-GP23 via resistors
Pin 13: H-Sync    → ULX3S GP24 (direct)
Pin 14: V-Sync    → ULX3S GP25 (direct)
Pin 5,6,7,8,10: GND
```

**Resistor Network** (3.3V logic → 0.7V analog):
```
ULX3S GPIO (3.3V)
    |
  270Ω
    |
    +-------- to VGA pin
    |
  470Ω
    |
   GND
```

Each color channel needs 8 resistor dividers (one per bit).

**Simplified 3-bit Color** (if resistors are limited):
- Use only R[7], G[7], B[7] (MSB bits)
- 8 colors only, but easier to wire

---

## Step 3: Program FPGA

### Using fujprog (Recommended)

```bash
# Program SRAM (temporary, lost on power-off)
fujprog flux_gpu.bit

# OR: Program Flash (persistent)
fujprog -j FLASH flux_gpu.bit
```

### Using OpenOCD

```bash
openocd -f ulx3s_prog.cfg -c "program_file flux_gpu.bit"
```

**LEDs should light up on the ULX3S board indicating power and activity.**

---

## Step 4: Test VGA Output

### Test 1: Check Sync Signals

**Equipment**: Oscilloscope (optional but helpful)

**Verify**:
- H-Sync: ~31.5 kHz square wave (negative polarity)
- V-Sync: ~60 Hz square wave (negative polarity)

**Without oscilloscope**:
- Monitor should detect signal and show "640×480 @ 60Hz"
- May display black screen initially (framebuffer is empty)

### Test 2: Display Test Pattern

**Method A: Hardcoded Pattern** (modify RTL):

Edit `vga_controller.sv` to output test pattern instead of framebuffer:

```systemverilog
// Near end of module, replace:
// vga_r <= pixel_data_reg[23:16];

// With test pattern:
always @(*) begin
    if (display_en_reg) begin
        if (pixel_x < 213)      vga_r = 8'hFF; // Red bar
        else if (pixel_x < 426) vga_g = 8'hFF; // Green bar  
        else                    vga_b = 8'hFF; // Blue bar
    end else begin
        vga_r = 8'h00;
        vga_g = 8'h00;
        vga_b = 8'h00;
    end
end
```

Re-synthesize and program.

**Expected**: Three vertical color bars (red, green, blue).

---

## Step 5: Test Triangle Rasterization

### Prepare Test Program

**Option 1: Hardcoded Triangle** (modify RTL):

Edit `gpu_graphics_top.sv` to add test logic:

```systemverilog
// Add test controller
reg [31:0] test_counter;
reg test_done;

always @(posedge clk_sys) begin
    if (!rst_n) begin
        test_counter <= 0;
        test_done <= 0;
    end else if (!test_done && test_counter == 1000000) begin
        // Trigger triangle draw after 1M clocks (~20ms)
        tri_draw <= 1;
        test_done <= 1;
    end else begin
        tri_draw <= 0;
        test_counter <= test_counter + 1;
    end
end

// Hardcode triangle vertices
assign tri_v0_x = 10'd100;
assign tri_v0_y = 10'd200;
assign tri_v1_x = 10'd500;
assign tri_v1_y = 10'd200;
assign tri_v2_x = 10'd300;
assign tri_v2_y = 10'd400;
assign tri_color = 24'hFF0000;  // Red
```

**Expected**: Red triangle appears on screen after boot.

**Option 2: Button-Triggered** (use BTN1):

Connect `tri_draw` to button input (already in constraints).

Press BTN1 → Triangle draws.

---

## Step 6: Debug Issues

### Problem: No VGA Signal

**Check**:
1. Monitor powered on and set to VGA input
2. Cable connected firmly
3. ULX3S powered (LEDs lit)
4. Bitstream programmed successfully

**Debug**:
- Test with simpler design (LED blink)
- Try different monitor
- Check pin assignments in `.lpf` file

### Problem: Garbled Display

**Causes**:
- Wrong pixel clock (should be 25 MHz)
- Timing violations
- Insufficient resistor network

**Fix**:
- Verify PLL configuration
- Check timing report: `make timing`
- Add termination resistors

### Problem: Triangle Not Appearing

**Check**:
1. Framebuffer initialized (should be black)
2. Rasterizer triggered
3. Coordinates within bounds
4. Color not black (0x000000)

**Debug**:
- Add LED indicators for `tri_busy`, `tri_done`
- Use ILA (Integrated Logic Analyzer) to probe signals
- Verify in simulation first

---

## Step 7: Performance Testing

### Measure Rasterization Time

Add performance counter in RTL:

```systemverilog
reg [31:0] rast_cycles;

always @(posedge clk_sys) begin
    if (tri_draw) begin
        rast_cycles <= 0;
    end else if (tri_busy) begin
        rast_cycles <= rast_cycles + 1;
    end
end

// Output to LEDs (binary)
assign led = rast_cycles[31:24];  // Show upper bits
```

**Expected**:
- Small triangle (100×100): ~10,000 cycles = 200 μs @ 50 MHz
- Large triangle (400×400): ~160,000 cycles = 3.2 ms

### Triangle Throughput

Calculate triangles per second:
```
TPS = Clock Freq / Avg Cycles per Triangle
    = 50 MHz / 10,000
    = 5,000 triangles/second (small)
    = 50 MHz / 160,000  
    = 312 triangles/second (large)
```

---

## Step 8: Advanced Tests

### Multiple Triangles

Draw multiple overlapping triangles by triggering rasterizer multiple times with different coordinates.

### Color Variation

Test all color channels:
- 0xFF0000 (red)
- 0x00FF00 (green)  
- 0x0000FF (blue)
- 0xFFFF00 (yellow)
- 0xFF00FF (magenta)
- 0x00FFFF (cyan)
- 0xFFFFFF (white)

### Full-Screen Fill

Draw large triangle covering entire screen to test worst-case performance.

---

## Expected Results

✅ **VGA Output**: 640×480 @ 60Hz display  
✅ **Test Pattern**: RGB color bars visible  
✅ **Triangle**: Solid colored triangle renders correctly  
✅ **Performance**: ~200 μs per small triangle  
✅ **Resource Usage**: Fits in FPGA (12% LUTs)  

---

## Troubleshooting Reference

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| No video signal | Wrong pins/clock | Check `.lpf`, verify 25 MHz |
| Black screen | Framebuffer empty | Add test pattern first |
| Wrong colors | Resistor values | Adjust divider network |
| Flickering | Timing violations | Check synthesis report |
| Garbled image | Clock issues | Verify PLL configuration |
| No triangle | Rasterizer not triggered | Add debug LEDs |

---

## Safety Notes

⚠️ **VGA Voltage**: Modern monitors are tolerant, but use proper resistor dividers  
⚠️ **Electrostatic Discharge**: Handle FPGA board with anti-static precautions  
⚠️ **Power**: ULX3S draws ~500mA, ensure USB port can supply  

---

## Success Criteria

To mark this task complete:
- [ ] Bitstream builds without errors
- [ ] VGA monitor detects 640×480 signal
- [ ] Test pattern displays correctly
- [ ] At least one triangle renders
- [ ] Performance meets spec (~200 μs/triangle)

---

## Next Steps

After successful FPGA test:
1. Document actual performance numbers
2. Capture screenshots/photos
3. Update roadmap to 100% complete
4. Share results with community!

---

**Good luck with your FPGA testing!** 🚀

For issues, consult:
- ULX3S documentation
- VGA timing specifications
- flux GitHub issues
