import math
from typing import List

from config import control_point_size
from shapes import Shape, Point


class ShapeManager:
    def __init__(self):
        self.shapes: List[Shape] = []

    def add_shape(self, shape):
        shape.z_index = len(self.shapes)
        self.shapes.append(shape)

    def clear(self):
        self.shapes = []

    def get_shapes(self):
        return self.shapes

    def get_control_point_by_click(self, click_point: Point):
        for s in self.shapes:
            for c in s.get_control_points():
                if abs(c.x - click_point.x) < control_point_size and abs(c.y - click_point.y) < control_point_size:
                    return c.id

    def move_point(self, point_id, new_pos: Point):
        for s in self.shapes:
            for c in s.get_control_points():
                if c.id == point_id:
                    c.x = new_pos.x
                    c.y = new_pos.y
                    return

    def distance_between(self, p_1: Point, p_2: Point):
        # https://en.wikipedia.org/wiki/Euclidean_distance
        return math.sqrt((p_2.x - p_1.x)**2 + (p_2.y - p_1.y)**2)