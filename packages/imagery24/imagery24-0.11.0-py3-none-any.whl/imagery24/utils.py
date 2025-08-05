from shapely.geometry import LineString, MultiLineString


def gradient_colors(n, start_hex="#FF0000", end_hex="#0000FF"):
    if n < 2:
        return [start_hex] if n == 1 else []

    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb):
        return "#{:02X}{:02X}{:02X}".format(*rgb)

    start_rgb = hex_to_rgb(start_hex)
    end_rgb = hex_to_rgb(end_hex)

    gradient = []
    for i in range(n):
        interpolated = tuple(
            int(start_rgb[j] + (end_rgb[j] - start_rgb[j]) * i / (n - 1))
            for j in range(3)
        )
        gradient.append(rgb_to_hex(interpolated))

    return gradient


def line_list(geometry: LineString | MultiLineString) -> list[LineString]:
    return list(geometry.geoms) if isinstance(geometry, MultiLineString) else [geometry]

def round_point(x: float, y: float, tolerance: float = 1) -> tuple[float, float]:
    """Snap *point* to a grid of size *tol* so nearly‑identical vertices collapse."""
    return (round(x / tolerance) * tolerance, round(y / tolerance) * tolerance)
