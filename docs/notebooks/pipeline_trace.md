# GPU Pipeline Visualization (Observable Prototype)

This document describes the structure and logic for an interactive Observable notebook to visualize the GPU pipeline.

## Data Model

The pipeline is modeled as a series of stages:
`Fetch -> Decode -> Execute -> Memory -> Writeback`

Trace data JSON format:
```json
[
  {"cycle": 0, "stage": "FETCH", "instr": "ADD R1, R2, R3", "threadId": 1},
  {"cycle": 1, "stage": "DECODE", "instr": "ADD R1, R2, R3", "threadId": 1},
  {"cycle": 2, "stage": "EXEC", "instr": "ADD R1, R2, R3", "threadId": 1},
  ...
]
```

## D3.js Visualization Plan

1.  **Timeline View**:
    *   **X-Axis**: Cycle Count
    *   **Y-Axis**: Pipeline Stage (stacked)
    *   **Glyphs**: Colorful blocks representing instruction movement.

2.  **Controls**:
    *   **Play/Pause**: Animate the cycle counter.
    *   **Scrub**: Slider to jump to specific cycle.
    *   **Zoom**: Focus on specific warp/thread execution.

## Implementation Snippet (JS Environment)

```javascript
// D3 Setup
const svg = d3.create("svg").attr("viewBox", [0, 0, width, 400]);
const x = d3.scaleLinear().domain([0, 100]).range([margin.left, width - margin.right]);

// Draw Cycle Markers
svg.append("g")
   .call(d3.axisBottom(x));

// Update Loop
function update(cycle) {
    const activeInstrs = traceData.filter(d => d.cycle === cycle);
    // Bind to rectangles...
}
```
