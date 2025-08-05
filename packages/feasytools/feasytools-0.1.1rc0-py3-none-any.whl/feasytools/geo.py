import heapq
from typing import List, Tuple, TypeVar, Generic, Any, Iterable, Optional


class Point:
    """A 2D point class."""
    __slots__ = ("x", "y")
    def __init__(self, x: float, y: float):
        """Initialize a point with x and y coordinates."""
        self.x = x
        self.y = y

    def dist_to(self, other: "Point") -> float:
        """Calculate the Euclidean distance to another point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def __repr__(self):
        return f"Point({self.x}, {self.y})"
    
    def __lt__(self, other: "Point") -> bool:
        """Less than comparison based on x and y coordinates."""
        return (self.x, self.y) < (other.x, other.y)
    
    def __gt__(self, other: "Point") -> bool:
        """Greater than comparison based on x and y coordinates."""
        return (self.x, self.y) > (other.x, other.y)
    
    def __eq__(self, other: "Point") -> bool:
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __getitem__(self, idx: int):
        if idx == 0:
            return self.x
        elif idx == 1:
            return self.y
        else:
            raise IndexError("Index can only be 0 or 1")

    def __setitem__(self, idx: int, value: float):
        if idx == 0:
            self.x = value
        elif idx == 1:
            self.y = value
        else:
            raise IndexError("Index can only be 0 or 1")


TLabel = TypeVar("TLabel")

class KDTree(Generic[TLabel]):
    """A 2D KD-Tree for nearest neighbor search. Each node is a point with string label in 2D space."""
    def __init__(
        self, points: Iterable[Point], labels: Optional[Iterable[TLabel]] = None, reverse_mapping: bool = False
    ):
        """
        Initialize the KD-Tree with a list of points and optional labels.
            points: An iterable of Point objects. If a list is provided, it will be used directly; otherwise, it will be converted to a list.
            labels: An optional iterable of labels corresponding to the points. If provided, it should have the same length as points.
            reverse_mapping: If True and labels are provided, a reverse mapping from labels to points will be created. Labels must be unique in this case.
        """
        self.__pts = points if isinstance(points, list) else list(points)
        if labels is not None:
            self.labels = {point: label for point, label in zip(self.__pts, labels)}
            assert len(self.labels) == len(self.__pts), "Points and labels must have the same length, and points must be unique"
            if reverse_mapping:
                self.reverse_labels = {label: point for point, label in self.labels.items()}
                assert len(self.reverse_labels) == len(self.labels), "Labels must be unique for reverse mapping"
            else:
                self.reverse_labels = {}
        else:
            self.labels = {}
            self.reverse_labels = {}
        self.root = self._build(0, self.__pts)

    @property
    def points(self) -> "List[Point]":
        """Get all points in the KD-Tree."""
        return self.__pts
    
    def items(self) -> "Iterable[Tuple[Point, Any]]":
        """Get all (point, label) pairs in the KD-Tree."""
        assert len(self.labels) > 0, "No mapping available"
        return self.labels.items()
    
    def get(self, label: TLabel) -> Optional[Point]:
        """Get the point associated with a label."""
        assert len(self.reverse_labels) > 0, "No reverse mapping available"
        return self.reverse_labels.get(label)
    
    def __getitem__(self, label: TLabel) -> Point:
        """Get the point associated with a label."""
        assert len(self.reverse_labels) > 0, "No reverse mapping available"
        return self.reverse_labels[label]
    
    def __len__(self) -> int:
        """Get the number of points in the KD-Tree."""
        return len(self.__pts)
    
    def _build(self, depth: int, points: "List[Point]"):
        if not points:
            return None
        axis = depth % 2
        points.sort(key=lambda point: (point.x, point.y)[axis])
        median = len(points) // 2
        return {
            "point": points[median],
            "left": self._build(depth + 1, points[:median]),
            "right": self._build(depth + 1, points[median + 1 :]),
        }

    def _nearest(self, node: Optional[dict], point: Point, depth: int):
        if node is None:
            return None
        axis = depth % 2
        next_branch = None
        opposite_branch = None
        if point[axis] < node["point"][axis]:
            next_branch = node["left"]
            opposite_branch = node["right"]
        else:
            next_branch = node["right"]
            opposite_branch = node["left"]
        best = self._closest(
            point, self._nearest(next_branch, point, depth + 1), node["point"]
        )
        if self._should_visit(point, best, node["point"]):
            best = self._closest(
                point, self._nearest(opposite_branch, point, depth + 1), best
            )
        return best

    def _k_nearest(
        self, node: Optional[dict], point: Point, depth: int, k: int, heap: list
    ):
        if node is None:
            return
        axis = depth % 2
        next_branch = None
        opposite_branch = None
        if point[axis] < node["point"][axis]:
            next_branch = node["left"]
            opposite_branch = node["right"]
        else:
            next_branch = node["right"]
            opposite_branch = node["left"]

        self._k_nearest(next_branch, point, depth + 1, k, heap)

        dist = point.dist_to(node["point"])
        if len(heap) < k:
            heapq.heappush(heap, (-dist, node["point"]))
        elif dist < -heap[0][0]:
            heapq.heappushpop(heap, (-dist, node["point"]))

        if len(heap) < k or abs(point[axis] - node["point"][axis]) < -heap[0][0]:
            self._k_nearest(opposite_branch, point, depth + 1, k, heap)

    def k_nearest(self, point: Point, k: int) -> "List[Point]":
        heap = []
        if k > len(self.__pts):
            k = len(self.__pts)
        self._k_nearest(self.root, point, 0, k, heap)
        return [item[1] for item in sorted(heap, key=lambda x: -x[0])]

    def k_nearest_mapped(self, point: Point, k: int) -> "List[TLabel]":
        if self.labels is None:
            raise ValueError("No map given")
        heap = []
        if k > len(self.__pts):
            k = len(self.__pts)
        self._k_nearest(self.root, point, 0, k, heap)
        return [self.labels[item[1]] for item in sorted(heap, key=lambda x: -x[0])]

    def _closest(self, point: Point, p1: Optional[Point], p2: Optional[Point]):
        if p1 is None:
            return p2
        if p2 is None:
            return p1
        d1 = point.dist_to(p1)
        d2 = point.dist_to(p2)
        return p1 if d1 < d2 else p2

    def _should_visit(self, point: Point, best: Optional[Point], node: Point):
        if best is None:
            return True
        return point.dist_to(node) < point.dist_to(best)

    def nearest(self, point: Point):
        return self._nearest(self.root, point, 0)

    def nearest_mapped(self, point: Point):
        if self.labels is None:
            raise ValueError("No map given")
        p = self.nearest(point)
        if p is None:
            raise RuntimeError("No segment found")
        return self.labels[p]

class Seg:
    """A line segment defined by two points."""
    __slots__ = ("p1", "p2")
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def dist_to(self, point: Point) -> float:
        x0, y0 = self.p1.x, self.p1.y
        x1, y1 = self.p2.x, self.p2.y
        x2, y2 = point.x, point.y

        dx = x1 - x0
        dy = y1 - y0

        if dx == 0 and dy == 0:
            # The segment is actually a point
            return point.dist_to(self.p1)

        t = ((x2 - x0) * dx + (y2 - y0) * dy) / (dx * dx + dy * dy)

        if t < 0:
            # The closest point is p1
            return point.dist_to(self.p1)
        elif t > 1:
            # The closest point is p2
            return point.dist_to(self.p2)
        else:
            # The closest point is on the segment
            closest_x = x0 + t * dx
            closest_y = y0 + t * dy
            closest_point = Point(closest_x, closest_y)
            return point.dist_to(closest_point)

    def intersects_with(self, seg: "Seg") -> bool:
        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y
        x3, y3 = seg.p1.x, seg.p1.y
        x4, y4 = seg.p2.x, seg.p2.y

        def ccw(x1, y1, x2, y2, x3, y3):
            return (y3 - y1) * (x2 - x1) > (y2 - y1) * (x3 - x1)

        return ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4) and ccw(
            x1, y1, x2, y2, x3, y3
        ) != ccw(x1, y1, x2, y2, x4, y4)

    def divide(self, k: int) -> "List[Point]":
        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y
        return [
            Point(x1 + (x2 - x1) * i / k, y1 + (y2 - y1) * i / k) for i in range(1, k)
        ]

    @property
    def length(self) -> float:
        return self.p1.dist_to(self.p2)

    def __repr__(self):
        return f"Seg({self.p1}, {self.p2})"

    def __eq__(self, other: "Seg") -> bool:
        return self.p1 == other.p1 and self.p2 == other.p2

    def __hash__(self):
        return hash((self.p1, self.p2))

    def __str__(self):
        return f"({self.p1}--{self.p2})"


class EdgeFinder:
    def __init__(self, segs: "dict[str, List[tuple[float, float]]]"):
        self.__pts: dict[Point, str] = {}
        for edge, shape in segs.items():
            for i, (x, y) in enumerate(shape):
                p = Point(x, y)
                self.__pts[p] = edge
                p0 = Point(shape[i - 1][0], shape[i - 1][1])
                seg = Seg(p, p0)
                for pp in seg.divide(max(1, int(seg.length / 10))):
                    self.__pts[pp] = edge
        self.kdtree = KDTree(self.__pts.keys())

    def find_nearest_edge(self, point: Point) -> "tuple[float, str]":
        nearest_point = self.kdtree.nearest(point)
        if nearest_point is None:
            raise RuntimeError("No segment found")
        return point.dist_to(nearest_point), self.__pts[nearest_point]


__all__ = ["Point", "Seg", "KDTree", "EdgeFinder"]