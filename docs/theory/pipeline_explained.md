# GPU Pipeline Explained: Stage-by-Stage Implementation

This document provides a detailed walkthrough of both the **graphics pipeline** and **compute pipeline**, with implementation guidance for each stage.

---

## Graphics Pipeline Deep Dive

![Graphics Pipeline Flow](../diagrams/graphics_pipeline_flow.png)

**Also available:** [Text version with details](../diagrams/graphics_pipeline_flow.txt)

### Stage 1: Vertex Processing

**Input**: Vertex attributes (position, normal, UV, color)
**Output**: Transformed vertices in clip space

**Math**: 
```
// Model-View-Projection transformation
vec4 clipPos = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
```

**Implementation (RTL)**:
```systemverilog
// Simplified vertex shader core
module vertex_shader (
    input  [31:0] vtx_x, vtx_y, vtx_z,      // Input position
    input  [31:0] mvp_matrix [0:15],        // 4x4 transform matrix
    output [31:0] clip_x, clip_y, clip_z, clip_w
);
    // Matrix-vector multiply: 4 dot products
    // Each dot product: 4 FP32 MACs
    assign clip_x = mvp[0]*vtx_x + mvp[1]*vtx_y + mvp[2]*vtx_z + mvp[3];
    // ... (clip_y, clip_z, clip_w similarly)
endmodule
```

**Parallelism**: Process 32-64 vertices simultaneously in SIMT fashion.

---

### Stage 2: Primitive Assembly & Culling

**Purpose**: Group vertices into triangles, discard invisible geometry

**Culling Techniques**:
1. **Backface Culling**: Discard triangles facing away from camera
   ```c
   vec3 normal = cross(v1 - v0, v2 - v0);
   if (dot(normal, viewDir) < 0) discard;
   ```

2. **Frustum Culling**: Discard triangles outside view frustum
   - Check if all vertices outside one clip plane

3. **Degenerate Culling**: Discard zero-area triangles

**Implementation**: Fixed-function hardware (simple logic, not programmable).

---

### Stage 3: Rasterization

**The Core GPU Problem**: Convert triangles to pixels.

#### Triangle Setup

**Compute edge equations**:
```
Edge equation: E(x, y) = (y0 - y1)*x + (x1 - x0)*y + (x0*y1 - x1*y0)
```

**Properties**:
- E(x,y) = 0 → point on edge
- E(x,y) > 0 → inside half-plane
- Point inside triangle if E1, E2, E3 all have same sign

#### Rasterization Algorithm (Simplified)

```python
for y in range(bbox_min_y, bbox_max_y):
    for x in range(bbox_min_x, bbox_max_x):
        e1 = edge_equation_1(x, y)
        e2 = edge_equation_2(x, y)
        e3 = edge_equation_3(x, y)
        
        if e1 >= 0 and e2 >= 0 and e3 >= 0:
            # Pixel (x, y) is inside triangle
            emit_fragment(x, y)
```

**Optimization**: Hierarchical rasterization
- Test 8×8 tile against triangle
- If entirely inside/outside, skip per-pixel tests

#### Attribute Interpolation

Use barycentric coordinates to interpolate vertex attributes:

```
w0 = E1(x,y) / E1(v2)  // Weight for vertex 0
w1 = E2(x,y) / E2(v0)  // Weight for vertex 1
w2 = E3(x,y) / E3(v1)  // Weight for vertex 2

color = w0*color0 + w1*color1 + w2*color2
```

**Perspective-correct interpolation**: Divide by depth, interpolate, multiply back.

---

### Stage 4: Fragment Shading

**Most Parallelizable Stage**: Millions of independent pixel computations.

**Typical Fragment Shader Operations**:
1. **Texture Sampling**: Read and filter textures
2. **Lighting**: Phong/PBR calculations (dot products, powers)
3. **Math**: sin, cos, sqrt, normalize
4. **Output**: Final RGBA color

**Example (GLSL)**:
```glsl
void main() {
    vec3 normal = normalize(vNormal);
    vec3 lightDir = normalize(lightPos - vPosition);
    float diffuse = max(dot(normal, lightDir), 0.0);
    
    vec4 texColor = texture(diffuseMap, vTexCoord);
    fragColor = texColor * diffuse;
}
```

**Hardware Execution**:
- Group 32 fragments into a warp
- Execute shader instruction-by-instruction
- Texture unit handles `texture()` calls
- ALUs handle math operations

---

### Stage 5: Depth/Stencil Testing

**Z-Buffer Algorithm**:
```c
// For each fragment at (x, y):
if (fragment_depth < depth_buffer[x][y]) {
    depth_buffer[x][y] = fragment_depth;
    color_buffer[x][y] = fragment_color;  // Visible
} else {
    discard;  // Occluded
}
```

**Early-Z Optimization**: Test depth *before* fragment shader
- Saves shader execution on occluded pixels
- Requires depth write in shader is disabled

**Stencil Buffer**: 8-bit per-pixel mask for advanced effects (shadows, outlines)

---

### Stage 6: Blending & ROPs

**Alpha Blending**:
```c
// Standard transparency blend
output = src_color * src_alpha + dst_color * (1 - src_alpha);
```

**Blending Modes**:
- Additive: `src + dst` (lights, particles)
- Multiply: `src * dst` (shadows)
- Min/Max: min(src, dst)

**ROPs (Render Output Units)**:
- Dedicated hardware for blending and writeback
- Handle memory compression (lossless DXT)
- Modern GPUs: 64-128 ROPs

---

## Compute Pipeline

**Simpler Model**: Just kernel execution, no graphics-specific stages.

### Kernel Launch Flow

1. **CPU Side**:
   ```c
   kernel<<<blocks, threads_per_block>>>(data, size);
   ```

2. **Command Processor**: Parses grid dimensions, kernel pointer

3. **Scheduler**: Assigns thread blocks to available shader cores

4. **Execution**: Each core runs warps until block completes

5. **Completion**: Synchronize, notify CPU

### Compute Kernel Example

**Vector Add (CUDA)**:
```cuda
__global__ void vector_add(float *a, float *b, float *c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) {
        c[i] = a[i] + b[i];
    }
}
```

**Execution on Hardware**:
- Launch with 1M elements, 256 threads/block
- 3906 blocks total
- Each warp (32 threads) executes in lockstep
- Memory coalescing: Threads 0-31 read consecutive addresses

---

## Memory Access Patterns

### Texture Sampling (Graphics Pipeline)

**Bilinear Filtering**:
```
Sample 4 nearest texels, interpolate:
result = (1-fx)*(1-fy)*t00 + fx*(1-fy)*t10 + (1-fx)*fy*t01 + fx*fy*t11
```

**Texture Cache**: Optimized for 2D locality
- Cache lines organized by tiles (e.g., 8×8 pixels)
- Anisotropic filtering: Adaptive sampling along view angle

### Cache Behavior

**Access Pattern Example**:
```c
// Thread i computes element i*stride
output[i * stride] = input[i * stride] + 1;
```

- stride=1 → Coalesced (one cache line)
- stride=32 → Strided (32 cache lines, terrible performance)

---

## Implementation Checklist

### Minimal GPU (Educational)

- [ ] **Vertex Shader**: 4×4 matrix multiply unit
- [ ] **Rasterizer**: Triangle setup + edge walking
- [ ] **Fragment Shader**: 4-lane SIMD ALU (FP32 add/mul)
- [ ] **Z-buffer**: Depth test + framebuffer
- [ ] **Memory**: Simple AXI master for VRAM access

**Expected Performance**: 
- 100 MHz clock
- 1-2 MPixels/sec
- Enough to render simple 3D scenes at 320×240 @ 30 FPS

### Production GPU (Industry)

- [ ] 40-80 shader cores, each with 64-128 ALUs
- [ ] Advanced rasterizer (hierarchical, conservative)
- [ ] Texture units with compression (BC1-7, ASTC)
- [ ] L1/L2 caches with compaction
- [ ] ROPs with blending and compression
- [ ] Command processor with DMA engines

**Expected Performance**:
- 1.5-2.5 GHz clock
- 10-40 TFLOPS compute
- 100+ GPixels/sec rasterization

---

## Next Steps

Now that you understand the pipeline, proceed to:
1. [Memory Systems](memory_systems.md): Deep dive on caches and bandwidth optimization
2. [Toolchain Guide](../setup/toolchain_guide.md): Set up your development environment
3. [RTL Implementation](../../rtl/README.md): Start building the shader core
