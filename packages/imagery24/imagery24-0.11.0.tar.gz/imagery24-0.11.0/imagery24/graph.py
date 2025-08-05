import geopandas as gpd
import networkx as nx
import numpy as np
from shapely import simplify
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import linemerge

from imagery24.utils import gradient_colors, line_list, round_point

Node = tuple[float, float]
Edge = tuple[Node, Node]


def reverse_line(line: LineString) -> LineString:
    return LineString(list(line.coords)[::-1])


def pull_head(line: LineString, target: Point, decay="linear"):
    xs, ys = np.array(line.xy)
    d = np.array([target.x - xs[0], target.y - ys[0]])  # full shift

    # cumulative distance from the head
    seg_len = np.hypot(np.diff(xs), np.diff(ys))
    s = np.concatenate(([0], np.cumsum(seg_len)))
    L = s[-1]

    # choose a weighting function w(s)∈[0,1]
    if decay == "linear":
        w = 1 - s / L
    elif decay == "exp":
        k = 4  # steeper → bends less of the tail
        w = np.exp(-k * s / L)
    else:
        raise ValueError

    xs_new = xs + w * d[0]
    ys_new = ys + w * d[1]
    return LineString(np.column_stack([xs_new, ys_new]))


class LineGraph(nx.Graph):
    TOL = 0.01

    def __init__(self, lines: list[LineString], crs: int, **attr):
        super().__init__(**attr)
        self.crs = crs
        self.add_lines(lines)

    def add_lines(self, lines: list[LineString]):
        for line in lines:
            self.add_line(line)

    def add_line(self, line: LineString) -> Edge:
        rounded_line = LineString(
            [round_point(*coord, self.TOL) for coord in line.coords]
        )

        start, end = rounded_line.coords[0], rounded_line.coords[-1]

        self.add_node(start, geometry=Point(start))
        self.add_node(end, geometry=Point(end))

        if not self.has_edge(start, end):
            self.add_edge(start, end, length=rounded_line.length, geometry=rounded_line)

        return (start, end)

    @property
    def lines(self) -> list[LineString]:
        edges_dict = {
            edge_data.get("id", i): edge
            for i, (edge, edge_data) in enumerate(self.edges.items())
        }

        lines_dict = dict()

        for edge_id, edge in edges_dict.items():
            start_node = self.nodes[edge[0]]
            end_node = self.nodes[edge[1]]
            line = self.edges[edge]["geometry"]

            if edge[1] == line.coords[0]:
                line = reverse_line(line)

            start_node_id = start_node.get("id", edge_id)
            end_node_id = end_node.get("id", edge_id)

            if start_node_id > end_node_id:
                line = reverse_line(line)

            lines_dict[edge_id] = line

        ordered_lines = [lines_dict[i] for i in sorted(lines_dict.keys())]
        return ordered_lines

    def get_leaf_edges(self):
        return [
            edge
            for edge in self.edges
            if self.degree[edge[0]] == 1 or self.degree[edge[1]] == 1
        ]

    def _graph_diameter_path(self) -> list[Node]:
        if self.number_of_nodes() <= 1:
            return list(self.nodes)

        lengths = nx.all_pairs_dijkstra_path_length(self, weight="length")
        u_max: Node | None = None
        v_max: Node | None = None
        max_dist = -1.0
        for u, dist_map in lengths:
            for v, dist in dist_map.items():
                if dist > max_dist:
                    u_max, v_max, max_dist = u, v, dist
        if u_max is None or v_max is None:
            return []

        return nx.shortest_path(self, u_max, v_max, weight="length")

    def plot(self):
        points = [node["geometry"] for node in self.nodes.values()]
        lines = [edge["geometry"] for edge in self.edges.values()]

        points_ids = [node.get("id", i) for i, node in enumerate(self.nodes.values())]
        lines_ids = [edge.get("id", i) for i, edge in enumerate(self.edges.values())]

        points_colors = gradient_colors(len(points))
        lines_colors = gradient_colors(len(lines))

        data_frame = gpd.GeoDataFrame(geometry=[*points, *lines], crs=self.crs)
        data_frame["id"] = [*points_ids, *lines_ids]
        data_frame["x"] = [point.x for point in points] + [
            line.coords[0][0] for line in lines
        ]
        data_frame["y"] = [point.y for point in points] + [
            line.coords[0][1] for line in lines
        ]
        data_frame["length"] = [0 for _ in points] + [line.length for line in lines]
        return data_frame.explore(
            color=[*points_colors, *lines_colors], style_kwds={"weight": 5}
        )

    def plot_leaf_edges(self):
        leaf_edges = self.get_leaf_edges()
        leaf_lines = [self.edges[edge]["geometry"] for edge in leaf_edges]

        colors = gradient_colors(len(leaf_lines))
        data_frame = gpd.GeoDataFrame(geometry=leaf_lines, crs=self.crs)
        return data_frame.explore(color=colors)

    def leaf_nodes_parent_nodes(self):
        leaf_edges = self.get_leaf_edges()

        edges_nodes = {edge[0] for edge in leaf_edges} | {
            edge[1] for edge in leaf_edges
        }

        parent_nodes = {node for node in edges_nodes if self.degree[node] > 1}

        return parent_nodes

    def enumerate_graph_longest_path(self) -> tuple[list[Node], list[Edge]]:
        if self.number_of_nodes() == 0:
            return [], []
        path = self._graph_diameter_path()
        node_order = path + [n for n in self.nodes if n not in path]

        for idx, n in enumerate(node_order):
            self.nodes[n]["id"] = idx

        path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        remaining_edges = [e for e in self.edges if set(e) not in map(set, path_edges)]
        edge_order = path_edges + remaining_edges

        for idx, (u, v) in enumerate(edge_order):
            if self.has_edge(u, v):
                self.edges[u, v]["id"] = idx
            else:
                self.edges[v, u]["id"] = idx

        return node_order, edge_order

    def get_two_child_nodes(self, parent_node) -> tuple[Node, Node] | None:
        edges = [edge for edge in self.get_leaf_edges() if parent_node in edge]

        edges.sort(key=lambda e: self.edges[e]["length"])

        if len(edges) < 2:
            return None

        length_a, length_b = (
            self.edges[edges[0]]["length"],
            self.edges[edges[1]]["length"],
        )

        if length_a / length_b > 2 or length_b / length_a > 2:
            return None

        edge_a, edge_b = edges[0], edges[1]

        node_a = edge_a[1] if edge_a[0] == parent_node else edge_a[0]
        node_b = edge_b[1] if edge_b[0] == parent_node else edge_b[0]

        return node_a, node_b

    def merge_two_leaf_edges(self, parent_node):
        child_nodes = self.get_two_child_nodes(parent_node)

        if child_nodes is None:
            return

        node_a, node_b = child_nodes

        vector_a = (node_a[0] - parent_node[0], node_a[1] - parent_node[1])
        vector_b = (node_b[0] - parent_node[0], node_b[1] - parent_node[1])

        average_vector = (
            (vector_a[0] + vector_b[0]) / 2,
            (vector_a[1] + vector_b[1]) / 2,
        )

        point_ab = Point(
            parent_node[0] + average_vector[0], parent_node[1] + average_vector[1]
        )

        self.add_line(LineString([parent_node, point_ab]))

        self.remove_node(node_a)
        self.remove_node(node_b)

        self.linemerge()

    def linemerge(self, tolerance: float | None = None) -> None:
        lines = linemerge([edge["geometry"] for edge in self.edges.values()])

        if tolerance is not None:
            lines = simplify(lines, tolerance=tolerance)

        self.clear()
        self.add_lines(line_list(lines))

    def merge_edge(self, edge: Edge):
        is_reversed = self.degree[edge[0]] == 1

        parent_node = edge[1] if is_reversed else edge[0]
        leaf_node = edge[0] if is_reversed else edge[1]
        line = self.edges[edge]["geometry"]

        line = reverse_line(line) if line.coords[0] != parent_node else line

        adjacent_edges = [
            e for e in self.edges if parent_node in e and leaf_node not in e
        ]

        if not len(adjacent_edges) == 2:
            return  # We can only merge if there are exactly two adjacent edges

        edge_a, edge_b = adjacent_edges

        line_a = self.edges[edge_a]["geometry"]
        line_b = self.edges[edge_b]["geometry"]

        # Make sure that adjacent edges start from the parent node
        a_is_reversed = line_a.coords[0] != parent_node
        b_is_reversed = line_b.coords[0] != parent_node

        if a_is_reversed:
            line_a = reverse_line(line_a)

        if b_is_reversed:
            line_b = reverse_line(line_b)

        adjacent_edges_length = sum(
            self.edges[edge]["length"] for edge in [edge_a, edge_b]
        )

        edge_length = self.edges[edge]["length"]

        coefficient = edge_length / adjacent_edges_length

        self.remove_node(leaf_node)
        self.remove_node(parent_node)

        new_parent_node = line.interpolate(coefficient, normalized=True)

        new_line_a = pull_head(line_a, new_parent_node, decay="linear")
        new_line_b = pull_head(line_b, new_parent_node, decay="linear")

        self.add_lines([new_line_a, new_line_b])

        self.linemerge()

    def simplify(self, max_depth: int = 1, max_edge_length: float = float("inf")):
        if max_depth == 0 or len(self.edges) < 2:
            return

        to_merge = None
        min_length = max_edge_length

        for edge in self.get_leaf_edges():
            length = self.edges[edge]["length"]

            if length < min_length:
                to_merge = edge
                min_length = length

        if to_merge:
            self.merge_edge(to_merge)
            self.simplify(max_depth - 1, max_edge_length=max_edge_length)

    def merge_leaves_within_polygon_pairwise(self, polygon: Polygon, max_depth: int = 1):
        parent_nodes = self.leaf_nodes_parent_nodes()

        if len(parent_nodes) < 1 or max_depth == 0:
            return

        nodes = None

        while nodes is None and len(parent_nodes) > 0:
            parent = parent_nodes.pop()
            nodes = self.get_two_child_nodes(parent)

            if nodes is not None:
                line = LineString([*nodes])

                if line.within(polygon):
                    self.merge_two_leaf_edges(parent)

                    self.merge_leaves_within_polygon_pairwise(polygon, max_depth - 1)
                else:
                    nodes = None

        if nodes is None:
            return
