# Amiga Boing Ball SVG Renderer

This repository contains a single Python script — [`src/boing.py`](src/boing.py) — which procedurally generates a **3D faceted Amiga Boing Ball** and renders it as a clean, vectorized **SVG** image.  

Two sample outputs are included:

- [`output/example/boing1.svg`](output/example/boing1.svg): Ball only, transparent background.  
- [`output/example/boing2.svg`](output/example/boing2.svg): Ball with purple orthographic grid background.

---

## Overview

The program builds a **lat-long tessellated sphere** (8 latitude bands × 16 longitude gores), colored in the classic red/white checker pattern.  
It applies an **orthographic projection** (no perspective) and supports:

- Configurable tilt and spin of the sphere.  
- Optional backface culling to eliminate rear facets.  
- Optional flat grid background with crisp vector lines.  
- All scene parameters controlled by constants at the top of the script.

The script outputs a fully valid SVG file.

---

## Methodology

### Coordinate System and Projection

- Right-handed world:
  - +X → right
  - +Y → into the screen (camera looks along −Y)
  - +Z → up  
- Orthographic projection:  
  `(x, y, z) → (sx, sy)` with  
  `sx = CX + x`, `sy = CY − z`
- The Boing Ball is generated as a sphere in object space, then transformed by:
  1. **Spin** about the Z axis (its polar axis)
  2. **Tilt** about the Y axis (leaning right from the viewer)
- Only triangles whose outward normal faces the camera (`dot(n, view_dir) < 0`) are emitted.

---

### Scene Construction Steps

1. **Generate sphere vertices**  
   Uniformly spaced latitude and longitude lines subdivide the sphere.
2. **Form facets**  
   Each rectangular patch is split into two triangles for robust backface culling.
3. **Apply transformations**  
   Spin (Z) → Tilt (Y) rotation matrices are applied to all vertices.
4. **Project to 2D**  
   Orthographic projection flattens the coordinates into SVG space.
5. **Cull and emit**  
   Triangles facing away from the camera are skipped.  
   Visible triangles are drawn as `<polygon>` elements with flat fill.
6. **Optional grid**  
   The orthographic grid is drawn as `<line>` and `<rect>` elements before the sphere.

---

## Configuration Constants

All parameters are defined in a single section at the top of `src/boing.py`.  
No command-line arguments are required.

### Output
| Constant | Description | Default |
|-----------|--------------|----------|
| `OUT_SVG_FILENAME` | Output filename | `"boing.svg"` |
| `CANVAS_W`, `CANVAS_H` | SVG canvas size in px | 500×500 |

### Colors and Background
| Constant | Description | Default |
|-----------|--------------|----------|
| `COLOR_RED`, `COLOR_WHITE` | Checker colors | `#ff0000`, `#ffffff` |
| `DRAW_BACKGROUND` | Boolean for solid background | `False` |
| `BACKGROUND_COLOR` | Background fill color | `#aaaaaa` |

### Sphere Geometry
| Constant | Description | Default |
|-----------|--------------|----------|
| `LONG_GORES` | Longitudinal segments | 16 |
| `LAT_BANDS` | Latitudinal segments | 8 |
| `RADIUS` | Sphere radius (in SVG units) | `min(W,H)/2` |
| `CX`, `CY` | Sphere center position | Canvas center |
| `TILT_DEG` | Tilt about Y axis (right lean) | 16° |
| `SPIN_DEG` | Spin about polar Z axis | 0° |
| `STROKE_WIDTH` | Facet edge width | 0.0 |
| `STROKE_OVERRIDE` | Edge color override | `None` (uses fill color) |

### Grid Configuration
| Constant | Description | Default |
|-----------|--------------|----------|
| `DRAW_GRID` | Enable/disable grid | `True` |
| `GRID_COLOR` | Grid line color | `#660066` |
| `GRID_STROKE_WIDTH` | Grid line width | 1.0 |
| `GRID_CELL_W`, `GRID_CELL_H` | Grid cell size | 50×50 |
| `GRID_CELLS_W`, `GRID_CELLS_H` | Number of cells drawn | 10×10 |
| `GRID_ORIGIN_X`, `GRID_ORIGIN_Y` | Top-left origin of grid | Auto-computed to center the grid |

---

## Output Structure

The resulting SVG includes:
```xml
<svg ...>
  [optional background rect]
  [optional grid group <g> ...]
  [polygon facets for visible triangles]
</svg>
```

Each polygon represents one visible triangle on the sphere, with no shading or lighting applied.  
Facets share edges perfectly—rendered output is clean, high-resolution, and faithful to the Amiga original’s faceted aesthetic.

---

## Extensibility

The code is intentionally modular to support future enhancements:

- **Perspective floor grid** (as in the original demo)
- **Simple drop shadow** behind the ball
- **Animated SVG sequences** or generated frame series
- **Lighting/shading passes** for realism

---

## License

This project is licensed under the **GNU Lesser General Public License v3.0 (LGPL-3.0)** or later.  
See the header in `src/boing.py` for details.

---
