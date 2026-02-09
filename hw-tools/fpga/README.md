# FPGA Build System README

## Quick Start

```bash
cd flux/hw-tools/fpga
make all        # Synthesize + Place & Route + Generate bitstream
make report     # View resource usage
make timing     # View timing summary
make prog       # Program ULX3S board (if connected)
```

## Files

| File | Purpose |
|------|---------|
| `synth.ys` | Yosys synthesis script |
| `ulx3s.lpf` | Pin constraints for ULX3S board |
| `Makefile` | Build automation |
| `ulx3s_prog.cfg` | OpenOCD programming config |

## Target Board

**ULX3S** (ECP5 LFE5U-85F)
- 85k LUTs
- 208 KB BRAM
- DSP slices for FP32 operations
- HDMI/VGA output
- USB programming

## Requirements

Install open-source ECP5 toolchain:
```bash
sudo apt install yosys nextpnr-ecp5 fpga-icestorm openocd
```

See [../docs/setup/fpga_build.md](../../docs/setup/fpga_build.md) for detailed instructions.

## Expected Results

**Resource Usage** (shader core only):
- LUTs: ~8,000 / 85,000 (9%)
- FFs: ~12,000 / 85,000 (14%)
- BRAMs: ~32 / 208 (15%)

**Timing**: Should meet 50 MHz target

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Undefined modules | Check file paths in `synth.ys` |
| Timing fails | Reduce frequency: `--freq 40` |
| Programming fails | Check USB connection, try `ujprog` |

## Next Steps

1. Test synthesis: `make all`
2. Verify resources: `make report`
3. Program board: `make prog`
4. Add test program to instruction memory
5. Observe LED outputs

---

For full documentation, see: [FPGA Build Guide](../../docs/setup/fpga_build.md)
