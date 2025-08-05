from __future__ import annotations

from typing import List

from centerline.geometry import Centerline
from shapely import voronoi_polygons
from shapely.geometry import (
    LineString,
    MultiPoint,
    Point,
    Polygon,
)
from shapely.ops import linemerge

from imagery24.graph import LineGraph
from imagery24.utils import line_list

__all__ = ["split_polygon"]


Coordinate = tuple[float, float]


def _spaced_points(lines: list[LineString], spacing: float) -> List[Point]:
    """Return approximately equally‑spaced points *on every branch* of *lines*.

    * ``spacing`` refers to the *desired* interval. Because the total branch length is
      finite, the exact distance between adjacent points is *adjusted* (up to ±½ spacing)
      so that the points are perfectly evenly distributed along each branch.
    * No point is placed **exactly** at a junction or branch‑start – the first point is
      offset by ½ adjusted spacing to avoid duplicates between branches.
    """
    if spacing <= 0:
        raise ValueError("spacing must be > 0")

    placed: list[Point] = []

    for line in lines:
        length = line.length
        if length < spacing * 2:
            continue  # too short for even one point

        n = int((length - spacing) // spacing) + 1
        adjusted_spacing = length / n

        for k in range(0, n):
            pt = line.interpolate((k + 0.5) * adjusted_spacing)
            placed.append(pt)

    return placed


def _voronoi_split(poly: Polygon, seeds: List[Point]) -> List[Polygon]:
    """Return a list of polygons obtained by clipping the Voronoi diagram of *seeds*
    with *poly*.

    Multi‑polygons are post‑processed so that the largest component stays in the
    resulting list while every smaller component is merged into the *smallest*
    of its neighbouring polygons.  The original order (driven by the Voronoi
    cells) is preserved.
    """

    # 1. Build the (ordered) Voronoi diagram clipped to *poly*
    diagram = voronoi_polygons(MultiPoint(seeds), extend_to=poly, ordered=True)

    polys: List[Polygon] = []  # final output (in order)
    pending_smalls: list[Polygon] = []  # smaller pieces waiting to be merged

    # 2. Collect polygons, keeping only the biggest piece of every MultiPolygon
    for cell in diagram.geoms:
        clipped = cell.intersection(poly)
        if clipped.is_empty:
            continue

        if isinstance(clipped, Polygon):
            polys.append(clipped)
        else:  # MultiPolygon
            parts = sorted(clipped.geoms, key=lambda g: g.area, reverse=True)
            polys.append(parts[0])  # keep the biggest piece in place
            pending_smalls.extend(parts[1:])  # queue all the rest for merging

    # 3. Merge each small piece with the *smallest* of its neighbours
    for small in pending_smalls:
        # Find neighbours that touch or intersect the small piece
        neighbour_ids = [
            i for i, p in enumerate(polys) if p.touches(small) or p.intersects(small)
        ]

        if not neighbour_ids:  # fallback: pick the overall smallest polygon
            neighbour_ids = range(len(polys))

        # Choose the neighbour with the smallest area among the candidates
        target_idx = min(neighbour_ids, key=lambda i: polys[i].area)

        # Union the small piece into the chosen neighbour
        polys[target_idx] = polys[target_idx].union(small)

    return polys


def split_polygon(polygon: Polygon, spacing: float, max_depth=10):
    if max_depth == 0:
        return [polygon]

    try:
        centerlines = line_list(linemerge(Centerline(polygon, spacing / 4).geometry))
        graph = LineGraph(centerlines, crs=None)
        graph.linemerge(spacing / 10)
        graph.simplify(max_depth=len(graph.get_leaf_edges()), max_edge_length=spacing)
        graph.merge_leaves_within_polygon_pairwise(polygon, max_depth=len(graph.get_leaf_edges()))
        graph.enumerate_graph_longest_path()
        points = _spaced_points(graph.lines, spacing)
        polygons = _voronoi_split(polygon, points)
    except Exception as e:
        print(e)
        return [polygon]

    if len(polygons) < 2:
        return [polygon]

    data = []

    for x in polygons:
        data.extend(split_polygon(x, spacing, max_depth - 1))

    return data
