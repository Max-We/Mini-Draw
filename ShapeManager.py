import math
from typing import List

from Shapes import Shape, Point, Line, Polygon
from config import control_point_size, canvas_width, canvas_height


class ShapeManager:
    """
    Manages all shapes on the canvas
    """

    def __init__(self):
        self.shapes: List[Shape] = []

    def add_shape(self, shape):
        """
        Add a shape to the collection and sets z-index based on position
        """
        shape.z_index = len(self.shapes)
        self.shapes.append(shape)

    def clear(self):
        """
        Clears all shapes
        """
        self.shapes.clear()

    def get_shapes(self):
        """
        Gets the shapes
        """
        return self.shapes

    def get_shape_by_click(self, click_point: Point):
        """
        Add a shape to the collection and sets z-index based on position
        """
        for s in self.shapes:
            for c in s.get_control_points():
                if abs(c.x - click_point.x) < control_point_size and abs(c.y - click_point.y) < control_point_size:
                    if isinstance(s, Line):
                        if c == s.p2:
                            s.is_bezier = True
                    return c.id

    def move_point(self, point_id, new_point_pos: Point):
        """
        Moves a point to a new position and updates all connected lines
        """
        # Don't move points outside the canvas
        if not (0 < new_point_pos.x < canvas_width) or not (0 < new_point_pos.y < canvas_height):
            return

        # Find all lines connected to the control point (more than one is possible)
        for s in self.shapes:
            old_point_pos = None
            lines_to_consider = []
            lines_to_readjust = []

            if isinstance(s, Line):
                lines_to_consider.append(s)
            elif isinstance(s, Polygon):
                for l in s.lines:
                    lines_to_consider.append(l)

            for l in lines_to_consider:
                for c in l.get_control_points():
                    if c.id == point_id:
                        old_point_pos = c
                        # Readjusting the control point should only be done if:
                        # 1. the point wasn't moved by the user (is default control point)
                        # 2. and the user hasn't moved the control point
                        if l.has_centered_control_point() and l.p2 != c:
                            # Checking if the control point is centered has to be done before one of the points
                            # is updated (would be false 100% otherwise
                            lines_to_readjust.append(l)

            if old_point_pos:
                old_point_pos.x = new_point_pos.x
                old_point_pos.y = new_point_pos.y
            for l in lines_to_readjust:
                l.center_control_point()

    def distance_between(self, p1: Point, p2: Point):
        """
        Euclidean distance between two points based on https://en.wikipedia.org/wiki/Euclidean_distance
        """
        return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)
