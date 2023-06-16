from tkinter import Canvas
from typing import List, Union

from config import control_point_size
from shapes import Line, Shape, Polygon, Point, ControlPoint


class Renderer:
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.show_control_points = True

    def render(self, shapes: List[Shape]):
        self.canvas.delete("all")

        # Order by z-index
        # https://www.perplexity.ai/search/8bbd5f6e-4a1d-48ee-ab76-4ff9ba2534c6?s=c
        shapes.sort(key=lambda x: x.z_index)

        # Draw
        for s in shapes:
            # shapes
            if isinstance(s, Line):
                self.draw_line(s)
            elif isinstance(s, Polygon):
                self.draw_polygon(s)
            elif isinstance(s, ControlPoint):
                self.draw_control_point(s)

            # control points
            if self.show_control_points:
                self.draw_control_points(s)

            # p1, p2 = s.get_bounding_box_points()
            # self.canvas.create_rectangle(p1.x, p1.y, p2.x, p2.y, fill=None)

    def toggle_control_points(self):
        self.show_control_points = not self.show_control_points

    def draw_line(self, line: Line):
        self.canvas.create_line(line.p_1.x, line.p_1.y, line.p_2.x, line.p_2.y)
        pass

    def draw_polygon(self, polygon: Polygon):
        lines = polygon.get_lines()
        for l in lines:
            self.draw_line(l)

    def draw_control_point(self, control_point: ControlPoint):
        bounding_box_start, bounding_box_end = control_point.get_bounding_box_points()
        self.canvas.create_rectangle(bounding_box_start.x, bounding_box_start.y, bounding_box_end.x, bounding_box_end.y)

    def draw_control_points(self, shape: Shape):
        for point in shape.get_control_points():
            self.draw_control_point(ControlPoint(point))
