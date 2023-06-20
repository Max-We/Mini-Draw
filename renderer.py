from copy import copy
from tkinter import Canvas
from typing import List, Union

from config import control_point_size, bezier_segments
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
                self.draw_bezier(s)
            elif isinstance(s, Polygon):
                self.draw_polygon(s)
            elif isinstance(s, ControlPoint):
                self.draw_control_point(s)

            # control points
            if self.show_control_points:
                self.draw_control_points_for_shapes(s)

    def toggle_control_points(self):
        self.show_control_points = not self.show_control_points

    def draw_line(self, line: Line):
        points = list(self.bresenham(line.p_1.x, line.p_1.y, line.p_3.x, line.p_3.y))
        for p in points:
            self.canvas.create_rectangle(p[0],p[1],p[0],p[1])

    def draw_bezier(self, line: Line):
        """Draws a quadratic Bézier curve with de casteljau algorithm"""
        points = []
        for t in range(bezier_segments+1):
            points.append(self.de_casteljau([line.p_1, line.p_2, line.p_3], 1/bezier_segments*t))

        # Draw lines to connect these points
        for i in range(len(points)-1):
            self.draw_line(Line(points[i], points[i+1]))

    def draw_polygon(self, polygon: Polygon):
        lines = polygon.get_lines()
        for l in lines:
            self.draw_bezier(l)

    def draw_control_point(self, control_point: ControlPoint):
        bounding_box_start, bounding_box_end = control_point.get_bounding_box_points()
        delta_x = bounding_box_end.x - bounding_box_start.x
        delta_y = bounding_box_end.y - bounding_box_start.y

        self.draw_line(Line(bounding_box_start, Point(bounding_box_start.x+delta_x, bounding_box_start.y)))
        self.draw_line(Line(bounding_box_start, Point(bounding_box_start.x, bounding_box_start.y+delta_y)))
        self.draw_line(Line(bounding_box_end, Point(bounding_box_end.x-delta_x, bounding_box_end.y)))
        self.draw_line(Line(bounding_box_end, Point(bounding_box_end.x, bounding_box_end.y-delta_y)))

    def draw_control_points_for_shapes(self, shape: Shape):
        for point in shape.get_control_points():
            self.draw_control_point(ControlPoint(point))

    def _calculate_linear(self, t, w):
        """
        Calculates x + y combined with the weights
        https://incolumitas.com/2013/10/06/plotting-bezier-curves/
        """
        x = t
        y = 1 - t
        return w[0] * x + w[1] * y

    def de_casteljau(self, points, t):
        # https://www.perplexity.ai/search/f27460a2-8072-4d3d-9d99-ffbbb62673e6?s=u
        if len(points) == 1:
            return points[0]
        else:
            new_points = []
            for i in range(len(points) - 1):
                x = (1 - t) * points[i].x + t * points[i + 1].x
                y = (1 - t) * points[i].y + t * points[i + 1].y
                new_points.append(Point(x, y))
            return self.de_casteljau(new_points, t)

    def bresenham(self, x0, y0, x1, y1):
        # ChatGPT with slight adaptations: https://chat.openai.com/share/5decad65-9c9d-4329-9bb8-7ad107222f51
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        steep = dy > dx
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
            dx, dy = dy, dx
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        y = y0
        ystep = 1 if y0 < y1 else -1
        error = 0
        for x in range(round(x0), round(x1) + 1):
            if steep:
                yield (y, x)
            else:
                yield (x, y)
            error += dy
            if 2 * error >= dx:
                y += ystep
                error -= dx

    def _calculate_bezier_quadratic(self, t, w):
        """
        Calculates x^2 + 2xy + y^2 combined with the weights
        https://incolumitas.com/2013/10/06/plotting-bezier-curves/
        """
        x = t
        y = 1 - t
        return w[0] * (x ** 2) + w[1] * 2 * x * y + w[2] * (y ** 2)