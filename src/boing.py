#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amiga Boing Ball → SVG (orthographic, faceted) + optional background grid
License: GNU LGPL v3.0 or later
Author: (you)

World frame:
- Right-handed: +X right, +Y into screen, +Z up. Camera looks along −Y.
- Orthographic projection: (x, y, z) → (sx, sy) with sx = cx + x, sy = cy − z.

Orientation:
- Spin about +Z (polar axis) FIRST, then tilt about +Y by TILT_DEG
  (positive = clockwise lean to the viewer’s right).

Backface culling:
- Keep triangles with dot(normal, view_dir) < 0, view_dir = (0, −1, 0).
"""

import math
from typing import List, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# Configuration (edit here)

OUT_SVG_FILENAME = "boing.svg"

# Canvas
CANVAS_W = 500
CANVAS_H = 500

# Colors
COLOR_RED = "#ff0000"
COLOR_WHITE = "#ffffff"

# Background
DRAW_BACKGROUND = False
BACKGROUND_COLOR = "#aaaaaa"

# Geometry (sphere)
LONG_GORES = 16   # around (must be even for checker)
LAT_BANDS  = 8    # pole-to-pole (must be even for checker)

# Radius and placement
RADIUS = min(CANVAS_W, CANVAS_H) * 0.5
CX = CANVAS_W * 0.5
CY = CANVAS_H * 0.5

# Orientation (degrees)
TILT_DEG = 16.0    # rotate about +Y (clockwise lean to the right from viewer)
SPIN_DEG = 0.0     # rotate about +Z (polar axis)

# Edge styling for facets
STROKE_WIDTH = 0.0
STROKE_OVERRIDE = None  # None → stroke matches fill; or set to a hex color

# ── GRID CONFIG ───────────────────────────────────────────────────────────────
DRAW_GRID = True
GRID_COLOR = "#660066"
GRID_STROKE_WIDTH = 1.0
GRID_CELL_W = 50.0
GRID_CELL_H = 50.0
GRID_CELLS_W = 10
GRID_CELLS_H = 10
# Grid origin defaults so that the grid’s center is the canvas center:
GRID_ORIGIN_X = CX - (GRID_CELLS_W * GRID_CELL_W) / 2.0
GRID_ORIGIN_Y = CY - (GRID_CELLS_H * GRID_CELL_H) / 2.0
# ──────────────────────────────────────────────────────────────────────────────

Vec3 = Tuple[float, float, float]
Vec2 = Tuple[float, float]

def deg2rad(a: float) -> float:
    return a * math.pi / 180.0

def rot_z(p: Vec3, a_deg: float) -> Vec3:
    a = deg2rad(a_deg)
    c, s = math.cos(a), math.sin(a)
    x, y, z = p
    return (c*x - s*y, s*x + c*y, z)

def rot_y(p: Vec3, a_deg: float) -> Vec3:
    a = deg2rad(a_deg)
    c, s = math.cos(a), math.sin(a)
    x, y, z = p
    # +Y rotation (right-handed)
    return (c*x + s*z, y, -s*x + c*z)

def cross(a: Vec3, b: Vec3) -> Vec3:
    ax, ay, az = a
    bx, by, bz = b
    return (ay*bz - az*by, az*bx - ax*bz, ax*by - ay*bz)

def sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def dot(a: Vec3, b: Vec3) -> float:
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def sph_to_cart(lat: float, lon: float, r: float) -> Vec3:
    # lat: −π/2..+π/2, lon: 0..2π
    cl = math.cos(lat)
    x = r * cl * math.cos(lon)
    y = r * cl * math.sin(lon)
    z = r * math.sin(lat)
    return (x, y, z)

def project_to_svg(p: Vec3) -> Vec2:
    x, _, z = p
    return (CX + x, CY - z)

def polygon_svg(points2d: List[Vec2], fill: str, stroke_width: float, stroke_color: str) -> str:
    pts = " ".join(f"{x:.3f},{y:.3f}" for x, y in points2d)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke_color}" stroke-width="{stroke_width:.3f}" />\n'

def grid_svg() -> str:
    """Generate an orthographic X/Z grid with optional overflow beyond canvas."""
    x0 = GRID_ORIGIN_X
    y0 = GRID_ORIGIN_Y
    w = GRID_CELLS_W * GRID_CELL_W
    h = GRID_CELLS_H * GRID_CELL_H
    parts = []
    parts.append(
        f'<g stroke="{GRID_COLOR}" stroke-width="{GRID_STROKE_WIDTH}" '
        f'shape-rendering="crispEdges" stroke-linecap="butt" fill="none">\n'
    )
    # Outer border
    parts.append(f'  <rect x="{x0:.3f}" y="{y0:.3f}" width="{w:.3f}" height="{h:.3f}" />\n')
    # Vertical lines
    for c in range(1, GRID_CELLS_W):
        x = x0 + c * GRID_CELL_W
        parts.append(f'  <line x1="{x:.3f}" y1="{y0:.3f}" x2="{x:.3f}" y2="{(y0+h):.3f}" />\n')
    # Horizontal lines
    for r in range(1, GRID_CELLS_H):
        y = y0 + r * GRID_CELL_H
        parts.append(f'  <line x1="{x0:.3f}" y1="{y:.3f}" x2="{(x0+w):.3f}" y2="{y:.3f}" />\n')
    parts.append('</g>\n')
    return "".join(parts)

def build_boing_svg() -> str:
    assert LAT_BANDS % 2 == 0 and LONG_GORES % 2 == 0, "Even counts required for checkerboard."

    lats = [(-math.pi/2) + (i * math.pi / LAT_BANDS) for i in range(LAT_BANDS + 1)]
    lons = [(j * 2*math.pi / LONG_GORES) for j in range(LONG_GORES + 1)]  # wrap last==2π

    def xform(v: Vec3) -> Vec3:
        return rot_y(rot_z(v, SPIN_DEG), TILT_DEG)

    view_dir = (0.0, -1.0, 0.0)  # camera looks along −Y

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}">\n')

    if DRAW_BACKGROUND:
        svg.append(f'  <rect x="0" y="0" width="{CANVAS_W}" height="{CANVAS_H}" fill="{BACKGROUND_COLOR}"/>\n')

    if DRAW_GRID:
        svg.append(grid_svg())

    # Sphere facets
    for i in range(LAT_BANDS):
        lat0, lat1 = lats[i], lats[i+1]
        for j in range(LONG_GORES):
            lon0, lon1 = lons[j], lons[j+1]

            v00 = sph_to_cart(lat0, lon0, RADIUS)
            v10 = sph_to_cart(lat1, lon0, RADIUS)
            v11 = sph_to_cart(lat1, lon1, RADIUS)
            v01 = sph_to_cart(lat0, lon1, RADIUS)

            w00 = xform(v00)
            w10 = xform(v10)
            w11 = xform(v11)
            w01 = xform(v01)

            tris = [
                (w00, w10, w11),
                (w00, w11, w01),
            ]

            fill = COLOR_RED if ((i + j) % 2 == 0) else COLOR_WHITE
            stroke_color = STROKE_OVERRIDE if STROKE_OVERRIDE is not None else fill

            for (a, b, c_) in tris:
                n = cross(sub(b, a), sub(c_, a))
                if dot(n, view_dir) < 0.0:
                    pts2d = [project_to_svg(a), project_to_svg(b), project_to_svg(c_)]
                    svg.append("  " + polygon_svg(pts2d, fill, STROKE_WIDTH, stroke_color))

    svg.append("</svg>\n")
    return "".join(svg)

def main() -> None:
    content = build_boing_svg()
    with open(OUT_SVG_FILENAME, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote {OUT_SVG_FILENAME}")

if __name__ == "__main__":
    main()
