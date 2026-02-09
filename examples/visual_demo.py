#!/usr/bin/env python3
"""
Visual Triangle Rasterization Demo
Uses matplotlib to show how triangles are rasterized
"""

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("matplotlib not installed. Install with: pip install matplotlib")
    print("Falling back to text-only mode.\n")

# =============================================================================
# Core algorithms (same as math_demo.py)
# =============================================================================

def edge_function(v0, v1, p):
    """Calculate edge function"""
    x0, y0 = v0
    x1, y1 = v1
    px, py = p
    return (y0 - y1) * px + (x1 - x0) * py + x0*y1 - x1*y0

def inside_triangle(p, v0, v1, v2):
    """Check if point is inside triangle"""
    e0 = edge_function(v0, v1, p)
    e1 = edge_function(v1, v2, p)
    e2 = edge_function(v2, v0, p)
    return (e0 >= 0 and e1 >= 0 and e2 >= 0) or \
           (e0 <= 0 and e1 <= 0 and e2 <= 0)

# =============================================================================
# Visualization functions
# =============================================================================

def visualize_edge_function(v0, v1, v2, resolution=50):
    """Visualize the edge function for all 3 edges"""
    if not HAS_MATPLOTLIB:
        print("Matplotlib required for visualization!")
        return
    
    # Create grid
    xs = np.linspace(0, 500, resolution)
    ys = np.linspace(0, 400, resolution)
    X, Y = np.meshgrid(xs, ys)
    
    # Calculate edge functions
    E0 = np.zeros_like(X)
    E1 = np.zeros_like(X)
    E2 = np.zeros_like(X)
    
    for i in range(len(ys)):
        for j in range(len(xs)):
            p = (xs[j], ys[i])
            E0[i, j] = edge_function(v0, v1, p)
            E1[i, j] = edge_function(v1, v2, p)
            E2[i, j] = edge_function(v2, v0, p)
    
    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Edge 0
    im0 = axes[0, 0].contourf(X, Y, E0, levels=20, cmap='RdBu')
    axes[0, 0].plot([v0[0], v1[0]], [v0[1], v1[1]], 'k-', linewidth=3)
    axes[0, 0].set_title('Edge Function 0 (V0→V1)')
    axes[0, 0].set_xlabel('X')
    axes[0, 0].set_ylabel('Y')
    plt.colorbar(im0, ax=axes[0, 0])
    
    # Edge 1
    im1 = axes[0, 1].contourf(X, Y, E1, levels=20, cmap='RdBu')
    axes[0, 1].plot([v1[0], v2[0]], [v1[1], v2[1]], 'k-', linewidth=3)
    axes[0, 1].set_title('Edge Function 1 (V1→V2)')
    axes[0, 1].set_xlabel('X')
    axes[0, 1].set_ylabel('Y')
    plt.colorbar(im1, ax=axes[0, 1])
    
    # Edge 2
    im2 = axes[1, 0].contourf(X, Y, E2, levels=20, cmap='RdBu')
    axes[1, 0].plot([v2[0], v0[0]], [v2[1], v0[1]], 'k-', linewidth=3)
    axes[1, 0].set_title('Edge Function 2 (V2→V0)')
    axes[1, 0].set_xlabel('X')
    axes[1, 0].set_ylabel('Y')
    plt.colorbar(im2, ax=axes[1, 0])
    
    # Combined (inside test)
    Inside = np.zeros_like(X)
    for i in range(len(ys)):
        for j in range(len(xs)):
            p = (xs[j], ys[i])
            Inside[i, j] = 1.0 if inside_triangle(p, v0, v1, v2) else 0.0
    
    axes[1, 1].imshow(Inside, extent=[0, 500, 0, 400], origin='lower', cmap='Reds')
    triangle = plt.Polygon([v0, v1, v2], fill=False, edgecolor='black', linewidth=2)
    axes[1, 1].add_patch(triangle)
    axes[1, 1].set_title('Inside Triangle (All edges same sign)')
    axes[1, 1].set_xlabel('X')
    axes[1, 1].set_ylabel('Y')
    
    plt.tight_layout()
    plt.savefig('edge_function_visualization.png', dpi=150)
    print("✓ Saved: edge_function_visualization.png")
    plt.show()

def visualize_rasterization_steps(v0, v1, v2):
    """Show step-by-step rasterization process"""
    if not HAS_MATPLOTLIB:
        print("Matplotlib required for visualization!")
        return
    
    # Get bounding box
    xs = [v0[0], v1[0], v2[0]]
    ys = [v0[1], v1[1], v2[1]]
    min_x, max_x = int(min(xs)), int(max(xs))
    min_y, max_y = int(min(ys)), int(max(ys))
    
    # Test all pixels
    inside_pixels = []
    outside_pixels = []
    
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if inside_triangle((x, y), v0, v1, v2):
                inside_pixels.append((x, y))
            else:
                outside_pixels.append((x, y))
    
    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Step 1: Triangle + Bounding Box
    axes[0].plot([v0[0], v1[0], v2[0], v0[0]], 
                 [v0[1], v1[1], v2[1], v0[1]], 'b-', linewidth=2, label='Triangle')
    rect = patches.Rectangle((min_x, min_y), max_x-min_x, max_y-min_y,
                              linewidth=2, edgecolor='r', facecolor='none',
                              label='Bounding Box')
    axes[0].add_patch(rect)
    axes[0].scatter([v0[0], v1[0], v2[0]], [v0[1], v1[1], v2[1]], 
                    c='blue', s=100, zorder=5)
    axes[0].set_title('Step 1: Calculate Bounding Box')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[0].set_aspect('equal')
    
    # Step 2: Test pixels
    if outside_pixels:
        ox, oy = zip(*outside_pixels)
        axes[1].scatter(ox, oy, c='lightgray', s=20, alpha=0.5, label='Outside')
    if inside_pixels:
        ix, iy = zip(*inside_pixels)
        axes[1].scatter(ix, iy, c='red', s=20, label='Inside')
    triangle = plt.Polygon([v0, v1, v2], fill=False, edgecolor='blue', linewidth=2)
    axes[1].add_patch(triangle)
    axes[1].set_title(f'Step 2: Test {len(inside_pixels) + len(outside_pixels)} Pixels')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].set_aspect('equal')
    
    # Step 3: Final result
    if inside_pixels:
        ix, iy = zip(*inside_pixels)
        axes[2].scatter(ix, iy, c='red', s=30, marker='s')
    triangle = plt.Polygon([v0, v1, v2], fill=True, facecolor='red', 
                           edgecolor='darkred', alpha=0.7, linewidth=2)
    axes[2].add_patch(triangle)
    axes[2].set_title(f'Step 3: Fill Triangle ({len(inside_pixels)} pixels)')
    axes[2].grid(True, alpha=0.3)
    axes[2].set_aspect('equal')
    
    for ax in axes:
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
    
    plt.tight_layout()
    plt.savefig('rasterization_steps.png', dpi=150)
    print("✓ Saved: rasterization_steps.png")
    plt.show()

def visualize_scene(triangles):
    """Visualize multiple triangles"""
    if not HAS_MATPLOTLIB:
        print("Matplotlib required for visualization!")
        return
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for v0, v1, v2, color, name in triangles:
        # Convert hex color to matplotlib format
        r = ((color >> 16) & 0xFF) / 255.0
        g = ((color >> 8) & 0xFF) / 255.0
        b = (color & 0xFF) / 255.0
        
        triangle = plt.Polygon([v0, v1, v2], facecolor=(r, g, b), 
                               edgecolor='black', alpha=0.7, linewidth=1.5,
                               label=name)
        ax.add_patch(triangle)
    
    ax.set_xlim(0, 640)
    ax.set_ylim(0, 480)
    ax.set_aspect('equal')
    ax.set_xlabel('X (pixels)')
    ax.set_ylabel('Y (pixels)')
    ax.set_title('flux GPU - Multi-Triangle Scene')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.invert_yaxis()  # Match screen coordinates
    
    plt.tight_layout()
    plt.savefig('triangle_scene.png', dpi=150)
    print("✓ Saved: triangle_scene.png")
    plt.show()

# =============================================================================
# Main program
# =============================================================================

def main():
    print("="*60)
    print("flux GPU - Visual Triangle Rasterization Demo")
    print("="*60)
    
    if not HAS_MATPLOTLIB:
        print("\n⚠️  This demo requires matplotlib!")
        print("Install with: pip install matplotlib")
        return
    
    # Demo triangle
    V0 = (100, 100)
    V1 = (400, 100)
    V2 = (250, 300)
    
    print(f"\nTriangle vertices: {V0}, {V1}, {V2}")
    
    # Demo 1: Edge function visualization
    print("\n1. Visualizing edge functions...")
    visualize_edge_function(V0, V1, V2)
    
    # Demo 2: Rasterization steps
    print("\n2. Visualizing rasterization steps...")
    visualize_rasterization_steps(V0, V1, V2)
    
    # Demo 3: Multi-triangle scene
    print("\n3. Visualizing multi-triangle scene...")
    triangles = [
        ((100, 100), (400, 100), (250, 300), 0xFF0000, "Red"),
        ((200, 150), (500, 200), (300, 400), 0x00FF00, "Green"),
        ((50, 200), (150, 400), (400, 350), 0x0000FF, "Blue"),
    ]
    visualize_scene(triangles)
    
    print("\n✓ All visualizations complete!")
    print("\nGenerated images:")
    print("  - edge_function_visualization.png")
    print("  - rasterization_steps.png")
    print("  - triangle_scene.png")

if __name__ == "__main__":
    main()
