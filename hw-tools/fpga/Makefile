# Makefile for flux GPU FPGA synthesis
# Target: ULX3S (ECP5 LFE5U-85F)

# Paths
RTL_DIR = ../../rtl/src
BUILD_DIR = build

# Tools
YOSYS = yosys
NEXTPNR = nextpnr-ecp5
ECPPACK = ecppack
OPENOCD = openocd

# Target device
DEVICE = 85k
PACKAGE = CABGA381

# Files
TOP = gpu_top
SYNTH_SCRIPT = synth.ys
CONSTRAINTS = ulx3s.lpf
JSON = $(BUILD_DIR)/$(TOP).json
TEXTCFG = $(BUILD_DIR)/$(TOP).config
BITSTREAM = $(BUILD_DIR)/$(TOP).bit

# Default target
all: $(BITSTREAM)

# Create build directory
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

# Synthesis with Yosys
$(JSON): $(SYNTH_SCRIPT) | $(BUILD_DIR)
	@echo "==> Running Yosys synthesis..."
	$(YOSYS) -s $(SYNTH_SCRIPT) -l $(BUILD_DIR)/synth.log
	@mv gpu_top.json $(JSON)
	@echo "✓ Synthesis complete"

# Place and Route with nextpnr
$(TEXTCFG): $(JSON) $(CONSTRAINTS)
	@echo "==> Running nextpnr (Place & Route)..."
	$(NEXTPNR) --$(DEVICE) --package $(PACKAGE) \
	           --json $(JSON) \
	           --lpf $(CONSTRAINTS) \
	           --textcfg $(TEXTCFG) \
	           --freq 50 \
	           --timing-allow-fail \
	           2>&1 | tee $(BUILD_DIR)/pnr.log
	@echo "✓ Place and Route complete"

# Bitstream generation
$(BITSTREAM): $(TEXTCFG)
	@echo "==> Generating bitstream..."
	$(ECPPACK) --compress $(TEXTCFG) $(BITSTREAM)
	@echo "✓ Bitstream ready: $(BITSTREAM)"

# Program FPGA via USB
prog: $(BITSTREAM)
	@echo "==> Programming FPGA..."
	$(OPENOCD) -f ulx3s_prog.cfg

# Resource usage report
report: $(JSON)
	@echo "==> Resource Usage Report:"
	@grep -A 20 "Printing statistics" $(BUILD_DIR)/synth.log

# Timing report
timing: $(TEXTCFG)
	@echo "==> Timing Report:"
	@grep -E "Max frequency|Critical path" $(BUILD_DIR)/pnr.log

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIR)
	rm -f *.json

# Help
help:
	@echo "flux FPGA Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all     - Build bitstream (default)"
	@echo "  prog    - Program FPGA via USB"
	@echo "  report  - Show resource utilization"
	@echo "  timing  - Show timing summary"
	@echo "  clean   - Remove build artifacts"
	@echo ""
	@echo "Requirements:"
	@echo "  - yosys (synthesis)"
	@echo "  - nextpnr-ecp5 (place & route)"
	@echo "  - ecppack (bitstream)"
	@echo "  - openocd (programming)"

.PHONY: all prog report timing clean help
