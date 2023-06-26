import math

import tkinter as tk

from ShapeManager import ShapeManager
from config import control_point_size, canvas_width, canvas_height
from renderer import Renderer
from shapes import Point, ControlPoint, Line, Polygon, Shape


class Ui:
    grabbed_point: Point = None
    renderer: Renderer
    shape_manager: ShapeManager

    def __init__(self, shape_manager: ShapeManager):
        self.shape_manager = shape_manager

        # https://www.perplexity.ai/search/0522ed03-1bae-4292-9d40-9bdeed7b91c4?s=c
        # Create the main window
        self.root = tk.Tk()

        # Create the canvas & renderer
        canvas = tk.Canvas(self.root, width=canvas_width, height=canvas_height, bg="white")
        canvas.pack()
        self.renderer = Renderer(canvas)

        self.register_keybinds(canvas)

        # Initial rendering
        self.renderer.render(self.shape_manager.get_shapes())

        # Run
        self.root.mainloop()

    def register_keybinds(self, canvas):
        # Moving points
        canvas.bind("<ButtonPress-2>", self.grab_point)
        canvas.bind("<B2-Motion>", self.move_point)
        canvas.bind("<ButtonRelease-2>", self.drop_point)

        # Drawing shapes
        canvas.bind("<ButtonPress-1>", self.start_draw)
        canvas.bind("<ButtonPress-3>", self.add_point)
        canvas.bind("<ButtonRelease-1>", self.stop_draw)

        # Keyboard
        self.root.bind("c", self.show_control_points)
        self.root.bind("x", self.clear_canvas)

    def show_control_points(self, event):
        self.renderer.toggle_control_points()
        self.renderer.render(self.shape_manager.get_shapes())

    def grab_point(self, event):
        """Selects the point under the user's cursor."""

        self.grabbed_point = self.shape_manager.get_shape_by_click(Point(event.x, event.y))

    def move_point(self, event):
        """Moves the point to the desired location."""

        if self.grabbed_point:
            self.shape_manager.move_point(self.grabbed_point, Point(event.x, event.y))
            self.renderer.render(self.shape_manager.get_shapes())

    def drop_point(self, event):
        """Ends the process of moving the point around."""
        self.grabbed_point = None

    new_shape_points = []

    def start_draw(self, event):
        """Sets the first point that the user is drawing."""

        global new_shape_points
        new_shape_points = []
        new_shape_points.append(Point(event.x, event.y))
        # Temporary show the shape which is being drawn by the user
        self.renderer.render(self.shape_manager.get_shapes() + [ControlPoint(new_shape_points[0])])

    def has_minimum_distance_to_last_point(self, point: Point):
        """Don't allow user to draw points on top of each other (bad UX)"""

        line_length = self.shape_manager.distance_between(new_shape_points[-1], point)
        control_point_diagonal = math.sqrt(2 * (control_point_size ** 2))
        # At least 3 control points should fit on a line (because control points shouldn't overlap)
        return line_length >= control_point_diagonal * 3

    def add_point(self, event):
        """Add a point to the current selection."""

        global new_shape_points

        # Only if drawing is in progress
        if len(new_shape_points) > 0:
            new_point = Point(event.x, event.y)
            if self.has_minimum_distance_to_last_point(new_point):
                new_shape_points.append(new_point)
            # Temporary show the shape which is being drawn by the user
            self.renderer.render(
                self.shape_manager.get_shapes() + [Polygon(new_shape_points, closed=False, z_index=1000)])

    def stop_draw(self, event):
        """Combine the points to a shape. This results in a single point (1) or line / polygon (>1)."""

        global new_shape_points
        new_point = Point(event.x, event.y)

        distance_to_origin = self.shape_manager.distance_between(new_shape_points[0], new_point)
        if distance_to_origin < control_point_size * 2:
            # Closed shape (filled polygon)
            if len(new_shape_points) == 1:
                self.shape_manager.add_shape(ControlPoint(new_shape_points[0]))
            elif len(new_shape_points) == 2:
                self.shape_manager.add_shape(Line(new_shape_points[0], new_shape_points[1]))
            else:
                self.shape_manager.add_shape(Polygon(new_shape_points, closed=True))
        else:
            # Unclosed shape (just a line with multiple bends)
            if self.has_minimum_distance_to_last_point(new_point):
                new_shape_points.append(new_point)
            self.shape_manager.add_shape(Polygon(new_shape_points, closed=False))

        self.renderer.render(self.shape_manager.get_shapes())
        new_shape_points = []

    def clear_canvas(self, event):
        self.shape_manager.clear()
        self.renderer.render(self.shape_manager.get_shapes())
