#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amiga Boing Ball → SVG (orthographic, faceted)
License: GNU LGPL v3.0 or later
Author: (you)

Design notes:
- Right-handed world: +X right, +Y into screen, +Z up. Camera looks along −Y.
- Sphere parameterization: lat ∈ [−π/2, +π/2], lon ∈ [0, 2π), 8 latitude bands, 16 longitude gores.
- Spin is about the polar axis (+Z) FIRST, then tilt is applied about +Y by tilt_deg (positive = clockwise lean to the right from the viewer).
- Orthographic projection: (x, y, z) → (sx, sy) with sx = cx + x, sy = cy − z.
- Backface culling: keep triangles with dot(normal, view_dir) < 0 where view_dir = (0, −1, 0).
- No painter’s algorithm necessary.
- Facet edges can be stroked (defaults off with stroke width 0).

Planned extension: optional grid background panel behind the ball (left as hook below).
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

# Geometry
LONG_GORES = 16   # around (must be even for checker)
LAT_BANDS  = 8    # pole-to-pole (must be even for checker)

# Radius and placement
RADIUS = min(CANVAS_W, CANVAS_H) * 0.5
CX = CANVAS_W * 0.5
CY = CANVAS_H * 0.5

# Orientation (degrees)
TILT_DEG = 16.0    # rotate about +Y (clockwise lean to the right from viewer)
SPIN_DEG = 0.0     # rotate about +Z (polar axis)

# Edge styling
STROKE_WIDTH = 0.0
# Stroke same as fill per requirement; expose override here if wanted later:
STROKE_OVERRIDE = None  # e.g., "#222222" or None to match fill

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
    # +Y axis rotation (right-handed):
    # x' =  c*x + s*z
    # y' =  y
    # z' = -s*x + c*z
    return (c*x + s*z, y, -s*x + c*z)

def cross(a: Vec3, b: Vec3) -> Vec3:
    ax, ay, az = a
    bx, by, bz = b
    return (ay*bz - az*by, az*bx - ax*bz, ax*by - ay*bx)

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
    # Orthographic from +Y toward origin: drop Y; SVG y-positive downward
    x, _, z = p
    return (CX + x, CY - z)

def polygon_svg(points2d: List[Vec2], fill: str, stroke_width: float, stroke_color: str) -> str:
    pts = " ".join(f"{x:.3f},{y:.3f}" for x, y in points2d)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke_color}" stroke-width="{stroke_width:.3f}" />\n'

def build_boing_svg() -> str:
    assert LAT_BANDS % 2 == 0 and LONG_GORES % 2 == 0, "Even counts required for checkerboard."
    # Precompute lat/lon rings
    lats = [(-math.pi/2) + (i * math.pi / LAT_BANDS) for i in range(LAT_BANDS + 1)]
    lons = [(j * 2*math.pi / LONG_GORES) for j in range(LONG_GORES + 1)]  # wrap last==2π

    # Transform helpers
    def xform(v: Vec3) -> Vec3:
        # Spin about Z, then tilt about Y
        return rot_y(rot_z(v, SPIN_DEG), TILT_DEG)

    view_dir = (0.0, -1.0, 0.0)  # camera looks along −Y

    # SVG assembly
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}">\n')

    if DRAW_BACKGROUND:
        svg.append(f'  <rect x="0" y="0" width="{CANVAS_W}" height="{CANVAS_H}" fill="{BACKGROUND_COLOR}"/>\n')

    # Optional future: call a grid_background(svg) here if enabled.

    # Generate facets
    for i in range(LAT_BANDS):
        lat0, lat1 = lats[i], lats[i+1]
        for j in range(LONG_GORES):
            lon0, lon1 = lons[j], lons[j+1]

            # Four corners on the sphere
            v00 = sph_to_cart(lat0, lon0, RADIUS)
            v10 = sph_to_cart(lat1, lon0, RADIUS)
            v11 = sph_to_cart(lat1, lon1, RADIUS)
            v01 = sph_to_cart(lat0, lon1, RADIUS)

            # Apply orientation transforms
            w00 = xform(v00)
            w10 = xform(v10)
            w11 = xform(v11)
            w01 = xform(v01)

            # Two triangles, outward winding (object-space param order)
            tris = [
                (w00, w10, w11),
                (w00, w11, w01),
            ]

            # Checker color
            fill = COLOR_RED if ((i + j) % 2 == 0) else COLOR_WHITE
            stroke_color = STROKE_OVERRIDE if STROKE_OVERRIDE is not None else fill

            # Emit only front-facing triangles (backface culling)
            for (a, b, c_) in tris:
                n = cross(sub(b, a), sub(c_, a))  # triangle normal (not normalized)
                if dot(n, view_dir) < 0.0:        # facing camera
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
