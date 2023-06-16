import uuid
from abc import abstractmethod, ABC
from typing import List, Tuple

from config import control_point_size


class Point:
    def __init__(self, x, y):
        self.id = uuid.uuid1()
        self.x = x
        self.y = y


def get_min_max_points(points: List[Point]) -> Tuple[Point, Point]:
    min_x = None
    min_y = None
    max_x = None
    max_y = None

    for p in points:
        if min_x is None or p.x < min_x:
            min_x = p.x
        if min_y is None or p.y < min_y:
            min_y = p.y
        if max_x is None or p.x > max_x:
            max_x = p.x
        if max_y is None or p.y > max_y:
            max_y = p.y

    print(min_x, min_y, max_x, max_y)

    return Point(min_x, min_y), Point(max_x, max_y)


# https://www.perplexity.ai/search/4bb59136-8fb8-4a4e-bb5a-f942cef1b8e7?s=c
class Shape(ABC):
    z_index: int

    @abstractmethod
    def get_control_points(self) -> List[Point]:
        pass

    @abstractmethod
    def get_bounding_box_points(self) -> List[Point]:
        return


class Line(Shape):
    def __init__(self, p_1: Point, p_2: Point):
        self.p_1 = p_1
        self.p_2 = p_2
        # Control point for quadratic bezier curve
        self.p_3 = Point((p_1.x + p_2.x) // 2, (p_1.y + p_2.y) // 2)
        self.control_points = [self.p_1, self.p_2, self.p_3]

    def get_control_points(self):
        return self.control_points

    def get_bounding_box_points(self) -> Tuple[Point, Point]:
        return get_min_max_points([self.p_1, self.p_2])


class ControlPoint(Shape):
    def __init__(self, p: Point, z_index=1):
        self.p: Point = p
        self.z_index = z_index

    def get_control_points(self):
        return [self.p]

    def get_bounding_box_points(self) -> Tuple[Point, Point]:
        start_point = Point(self.p.x-control_point_size, self.p.y-control_point_size)
        end_point = Point(self.p.x+control_point_size, self.p.y+control_point_size)
        return start_point, end_point


class Polygon(Shape):
    def __init__(self, points: List[Point], closed=False, z_index=0):
        # Generate lines
        self.lines: List[Line] = []
        self.closed = closed
        self.z_index = z_index
        last_point = None
        for current_point in points:
            if last_point:
                self.lines.append(Line(last_point, current_point))
            last_point = current_point
        if self.closed:
            self.lines.append(Line(points[-1], points[0]))

        # Get control points (for the polygon)
        self.control_points: List[Point] = []
        for l in self.lines:
            for c in l.get_control_points():
                # Todo: does this filter all or on object base?
                if c not in self.control_points:
                    self.control_points.append(c)

    def get_lines(self) -> List[Line]:
        return self.lines

    def get_control_points(self):
        return self.control_points

    def get_bounding_box_points(self) -> Tuple[Point, Point]:
        return get_min_max_points(self.control_points)
