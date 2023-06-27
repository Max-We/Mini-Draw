import sys
from copy import copy, deepcopy
from tkinter import Canvas
from typing import List, Union, Tuple

import numpy
import numpy as np

from config import control_point_size, bezier_segments, canvas_width, canvas_height
from Patterns import stripe_mask_v, stripe_mask_h, stripe_mask_c
from Shapes import Line, Shape, Polygon, Point, ControlPoint

# This is necessary for floodfill to work
sys.setrecursionlimit(500000)


class Renderer:
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.show_control_points = True
        self.cache: List[Shape] = None

    def render(self, shapes: List[Shape], color: str, pattern: str):
        # Find changes since last render
        self.canvas.delete("all")
        # self.canvas.create_rectangle(400,400,400,400)
        # self.canvas.create_rectangle(401,400,401,400, outline="red")

        # Order by z-index
        # https://www.perplexity.ai/search/8bbd5f6e-4a1d-48ee-ab76-4ff9ba2534c6?s=c
        shapes.sort(key=lambda x: x.z_index)

        # Draw
        for s in shapes:
            # shapes
            if isinstance(s, Line):
                self.draw_bezier(s)
            elif isinstance(s, Polygon):
                self.draw_polygon(s, color, pattern)
            elif isinstance(s, ControlPoint):
                self.draw_control_point(s)

            # control points
            if self.show_control_points:
                self.draw_control_points_for_shapes(s)

    def toggle_control_points(self):
        self.show_control_points = not self.show_control_points

    def draw_line(self, line: Line):
        pixels = np.zeros((canvas_width, canvas_height), dtype=bool)
        pixels_to_set = np.array(list(self.bresenham(line.p_1.x, line.p_1.y, line.p_3.x, line.p_3.y)), dtype=tuple)
        for p in pixels_to_set:
            if 0 < p[0] < canvas_width and 0 < p[1] < canvas_height:
                self.canvas.create_rectangle(round(p[0]),round(p[1]), round(p[0]), round(p[1]))
                pixels[round(p[0]), round(p[1])] = True

        return pixels

    def draw_bezier(self, line: Line):
        """Draws a quadratic Bézier curve with de casteljau algorithm"""
        points = []
        for t in range(bezier_segments + 1):
            points.append(self.de_casteljau([line.p_1, line.p_2, line.p_3], 1 / bezier_segments * t))

        # Draw lines to connect these points
        pixels = np.zeros((canvas_width, canvas_height), dtype=bool)
        for i in range(len(points) - 1):
            # https://www.perplexity.ai/search/cf60ad1e-3454-4b35-94da-c3975269a871?s=c
            pixels |= self.draw_line(Line(points[i], points[i + 1]))
        return pixels

    def draw_polygon(self, polygon: Polygon, color, pattern):
        lines = polygon.get_lines()
        pixels = np.zeros((canvas_width, canvas_height), dtype=bool)
        for l in lines:
            pixels |= self.draw_bezier(l)

        if polygon.closed:
            self.fill_polygon(polygon, pixels, color, pattern)

        # Bug: Tkinter pixel drawn via create_rect != a real pixel but larger
        # To prevent lines from disappearing we have to ensure that they are drawn last, otherwise fill will take over
        for l in lines:
            self.draw_bezier(l)

    def fill_polygon(self, polygon: Polygon, line_pixels, color: str, pattern: str):
        #  Get the bounding box + small padding to fill
        start, end = polygon.get_bounding_box_points()
        start.x -= 1
        start.y -= 1
        end.x += 1
        end.y += 1
        mask = np.zeros((canvas_width, canvas_height), dtype=bool)
        mask = np.invert(mask)
        mask[start.x:end.x, start.y:end.y] = False
        edited = np.zeros((canvas_width, canvas_height), dtype=bool)

        # Mask everything around the polygon
        mask = self.flood_fill((start.x, start.y), line_pixels, start, end, mask, edited)
        mask = np.invert(mask)

        if pattern == "horizontal":
            mask = mask * stripe_mask_h
        elif pattern == "vertical":
            mask = mask * stripe_mask_v
        elif pattern == "checkers":
            mask = mask * stripe_mask_c
        else:
            mask = mask.astype(int)

        # Fill everything inside the polygon
        for x, y in np.argwhere((mask == 1) | (mask == 2)):
            if start.x <= x <= end.x and start.y <= y <= end.y and not line_pixels[x, y]:
                self.canvas.create_rectangle(x, y, x, y, outline=color if mask[x,y] == 1 else "white")

    def flood_fill(self, point: Tuple[int, int], line_pixels, start: Point, end: Point, mask, edited):
        # Don't render points outside the canvas
        if not (line_pixels.shape[0] > point[0]) or not (line_pixels.shape[1] > point[1]):
            return mask

        is_inside_bounds = start.x <= point[0] <= end.x and start.y <= point[1] <= end.y
        hit_line = line_pixels[point[0], point[1]]

        if edited[point[0], point[1]]:
            return mask
        edited[point[0], point[1]] = True

        # https://de.wikipedia.org/wiki/Floodfill
        if not hit_line and is_inside_bounds:
            mask[point[0], point[1]] = True
            self.flood_fill((point[0], point[1] + 1), line_pixels, start, end, mask, edited)  # ↓
            self.flood_fill((point[0], point[1] - 1), line_pixels, start, end, mask, edited)  # ↑
            self.flood_fill((point[0] + 1, point[1]), line_pixels, start, end, mask, edited)  # →
            self.flood_fill((point[0] - 1, point[1]), line_pixels, start, end, mask, edited)  # ←

        return mask

    def draw_control_point(self, control_point: ControlPoint):
        bounding_box_start, bounding_box_end = control_point.get_bounding_box_points()
        delta_x = bounding_box_end.x - bounding_box_start.x
        delta_y = bounding_box_end.y - bounding_box_start.y

        self.draw_line(Line(bounding_box_start, Point(bounding_box_start.x + delta_x, bounding_box_start.y)))
        self.draw_line(Line(bounding_box_start, Point(bounding_box_start.x, bounding_box_start.y + delta_y)))
        self.draw_line(Line(bounding_box_end, Point(bounding_box_end.x - delta_x, bounding_box_end.y)))
        self.draw_line(Line(bounding_box_end, Point(bounding_box_end.x, bounding_box_end.y - delta_y)))

    def draw_control_points_for_shapes(self, shape: Shape):
        for point in shape.get_control_points():
            self.draw_control_point(ControlPoint(point))

    def de_casteljau(self, points, t):
        # https://www.perplexity.ai/search/f27460a2-8072-4d3d-9d99-ffbbb62673e6?s=u
        if len(points) == 1:
            return points[0]
        else:
            new_points = []
            for i in range(len(points) - 1):
                x = (1 - t) * points[i].x + t * points[i + 1].x
                y = (1 - t) * points[i].y + t * points[i + 1].y
                new_points.append(Point(round(x), round(y)))
            return self.de_casteljau(new_points, t)

    def bresenham(self, x0, y0, x1, y1):
        # Todo: refactor to rest of code style
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
