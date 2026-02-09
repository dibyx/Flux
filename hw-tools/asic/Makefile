# OpenLane Makefile for flux GPU ASIC

DESIGN_NAME = flux_gpu_asic
OPENLANE_DIR ?= $(HOME)/openlane
PDK_ROOT ?= $(HOME)/pdk

# Default target
.PHONY: all
all: help

.PHONY: help
help:
	@echo "flux GPU ASIC Synthesis - OpenLane Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  synth       - Run synthesis only"
	@echo "  floorplan   - Run through floorplanning"
	@echo "  place       - Run through placement"
	@echo "  cts         - Run through clock tree synthesis"
	@echo "  route       - Run through routing"
	@echo "  gdsii       - Generate final GDSII"
	@echo "  full        - Run complete flow (synth → GDSII)"
	@echo "  drc         - Run Design Rule Check"
	@echo "  lvs         - Run Layout vs Schematic"
	@echo "  sta         - Run Static Timing Analysis"
	@echo "  clean       - Clean build artifacts"
	@echo "  view        - View layout in KLayout"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - OpenLane installed at: $$OPENLANE_DIR"
	@echo "  - SkyWater PDK at: $$PDK_ROOT"

.PHONY: check-env
check-env:
	@if [ ! -d "$(OPENLANE_DIR)" ]; then \
		echo "Error: OpenLane not found at $(OPENLANE_DIR)"; \
		echo "Install: https://github.com/The-OpenROAD-Project/OpenLane"; \
		exit 1; \
	fi
	@if [ ! -d "$(PDK_ROOT)" ]; then \
		echo "Error: PDK not found at $(PDK_ROOT)"; \
		echo "Install SkyWater PDK"; \
		exit 1; \
	fi
	@echo "✓ Environment OK"

.PHONY: synth
synth: check-env
	@echo "Running synthesis..."
	cd $(OPENLANE_DIR) && make mount && \
	./flow.tcl -design $(PWD) -tag synth_$(shell date +%Y%m%d_%H%M%S) -synth_explore

.PHONY: floorplan
floorplan: check-env
	@echo "Running floorplan..."
	cd $(OPENLANE_DIR) && make mount && \
	./flow.tcl -design $(PWD) -tag fp_$(shell date +%Y%m%d_%H%M%S) -init_fp -io_placer

.PHONY: place
place: check-env
	@echo "Running placement..."
	cd $(OPENLANE_DIR) && make mount && \
	./flow.tcl -design $(PWD) -tag place_$(shell date +%Y%m%d_%H%M%S) -place

.PHONY: cts
cts: check-env
	@echo "Running clock tree synthesis..."
	cd $(OPENLANE_DIR) && make mount && \
	./flow.tcl -design $(PWD) -tag cts_$(shell date +%Y%m%d_%H%M%S) -cts

.PHONY: route
route: check-env
	@echo "Running routing..."
	cd $(OPENLANE_DIR) && make mount && \
	./flow.tcl -design $(PWD) -tag route_$(shell date +%Y%m%d_%H%M%S) -route

.PHONY: gdsii
gdsii: check-env
	@echo "Generating GDSII..."
	cd $(OPENLANE_DIR) && make mount && \
	./flow.tcl -design $(PWD) -tag gdsii_$(shell date +%Y%m%d_%H%M%S) -write_gds

.PHONY: full
full: check-env
	@echo "Running complete ASIC flow..."
	cd $(OPENLANE_DIR) && make mount && \
	./flow.tcl -design $(PWD) -tag run_$(shell date +%Y%m%d_%H%M%S)

.PHONY: drc
drc:
	@echo "Running Design Rule Check..."
	@if [ -f runs/latest/results/magic/*.gds ]; then \
		magic -noconsole -dnull -rcfile $(PDK_ROOT)/sky130A/libs.tech/magic/sky130A.magicrc \
		      -drc runs/latest/results/magic/*.gds; \
	else \
		echo "Error: No GDSII found. Run 'make gdsii' first."; \
	fi

.PHONY: lvs
lvs:
	@echo "Running Layout vs Schematic..."
	@echo "LVS check (requires netgen)"
	@if [ -f runs/latest/results/magic/*.spice ]; then \
		netgen -batch lvs runs/latest/results/magic/*.spice runs/latest/results/synthesis/*.v; \
	else \
		echo "Error: No SPICE netlist found"; \
	fi

.PHONY: sta
sta:
	@echo "Running Static Timing Analysis..."
	@if [ -f runs/latest/results/synthesis/*.v ]; then \
		sta runs/latest/results/synthesis/*.v; \
	else \
		echo "Error: No synthesized netlist found"; \
	fi

.PHONY: view
view:
	@echo "Opening layout in KLayout..."
	@if [ -f runs/latest/results/magic/*.gds ]; then \
		klayout runs/latest/results/magic/*.gds; \
	else \
		echo "Error: No GDSII found. Run 'make gdsii' first."; \
	fi

.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	rm -rf runs/*
	@echo "✓ Clean complete"

.PHONY: stats
stats:
	@echo "Design Statistics:"
	@if [ -f runs/latest/reports/synthesis/1-synthesis.stat.rpt ]; then \
		cat runs/latest/reports/synthesis/1-synthesis.stat.rpt; \
	else \
		echo "No statistics available. Run synthesis first."; \
	fi

.PHONY: area
area:
	@echo "Area Report:"
	@grep -i "Chip area" runs/latest/reports/synthesis/*.rpt 2>/dev/null || echo "Run synthesis first"

.PHONY: timing
timing:
	@echo "Timing Summary:"
	@grep -A10 "worst slack" runs/latest/reports/timing/*.rpt 2>/dev/null || echo "Run timing analysis first"
