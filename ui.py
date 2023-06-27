import math
import pickle

import tkinter as tk
from tkinter import filedialog, colorchooser
from typing import List

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
        self.root.title("MiniDraw")

        # Create the canvas & renderer
        canvas = tk.Canvas(self.root, width=canvas_width, height=canvas_height, bg="white")
        canvas.grid(row=1, columnspan=4)
        self.renderer = Renderer(canvas)

        # Create controls
        self.init_color_buttons()
        self.init_fill_pattern_buttons()
        self.init_fill_save_load_buttons()

        self.register_keybinds(canvas)

        # Initial rendering
        self.render()

        # Run
        self.root.mainloop()

    def init_color_buttons(self):
        self.color_selection = tk.StringVar(value="#34A1BC")
        tk.Label(self.root, text=f"Color").grid(row=4, column=0, columnspan=2, pady=(10,0), sticky="W", padx=(25,0))
        tk.Label(self.root, text=f"{self.color_selection.get()}").grid(row=4, column=2, sticky="W", padx=(30,0), pady=(10,0))
        tk.Button(self.root, text="Color Picker", command=self.choose_color).grid(row=4, column=3, pady=(10,0))

    def choose_color(self):
        selection = colorchooser.askcolor(title="Choose color", color=self.color_selection.get())
        if selection[1]:
            self.color_selection.set(selection[1])
            self.render()

    def init_fill_pattern_buttons(self):
        self.pattern_selection = tk.StringVar(value="none")
        tk.Radiobutton(self.root, text="None", variable=self.pattern_selection, value="none", command=self.render).grid(row=5, column=2, sticky="W", pady=(20,0))
        tk.Radiobutton(self.root, text="Horizontal", variable=self.pattern_selection, value="vertical", command=self.render).grid(row=5, column=3, sticky="w", pady=(20,0))
        tk.Radiobutton(self.root, text="Vertical", variable=self.pattern_selection, value="horizontal", command=self.render).grid(row=6, column=2, sticky="W")
        tk.Radiobutton(self.root, text="Checkers", variable=self.pattern_selection, value="checkers", command=self.render).grid(row=6, column=3, sticky="w")
        tk.Label(self.root, text="Pattern").grid(row=5, column=0, columnspan=2, rowspan=2, pady=(20,0), sticky="W", padx=(25,0))

    def init_fill_save_load_buttons(self):
        # https://www.perplexity.ai/search/16ea9d17-306d-4176-bfe9-e6e2ec93d02a?s=c
        tk.Button(self.root, text="Load", command=self.load).grid(row=0, column=0, sticky="W")
        tk.Button(self.root, text="Save", command=self.save).grid(row=0, column=3, sticky="E")

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
        self.render()

    def grab_point(self, event):
        """Selects the point under the user's cursor."""

        self.grabbed_point = self.shape_manager.get_shape_by_click(Point(event.x, event.y))

    def move_point(self, event):
        """Moves the point to the desired location."""

        if self.grabbed_point:
            self.shape_manager.move_point(self.grabbed_point, Point(event.x, event.y))
            self.render()

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
        self.render(self.shape_manager.get_shapes() + [ControlPoint(new_shape_points[0])])

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
        # https://www.perplexity.ai/search/1c73ef15-23b2-4936-a4db-6294e63533e0?s=c
        if "new_shape_points" in globals() and len(new_shape_points) > 0:
            new_point = Point(event.x, event.y)
            if self.has_minimum_distance_to_last_point(new_point):
                new_shape_points.append(new_point)
            # Temporary show the shape which is being drawn by the user
            self.render(self.shape_manager.get_shapes() + [Polygon(new_shape_points, closed=False, z_index=1000)])

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

        self.render()
        new_shape_points = []

    def save(self):
        # https://www.perplexity.ai/search/df10d36c-17b3-45e0-a9e9-3eb8efc8e1ce?s=c
        f = filedialog.asksaveasfile(initialdir="~", title="Save file", defaultextension=".mdr", filetypes=(("MiniDraw file", "*.mdr"), ("All files", "*.*")), mode="wb")
        if f is not None:
            pickle.dump(self.shape_manager, f)
            f.close()
            self.render()

    def load(self):
        # https://www.perplexity.ai/search/df10d36c-17b3-45e0-a9e9-3eb8efc8e1ce?s=c
        f = filedialog.askopenfile(initialdir="~", title="Select a directory", filetypes=(("MiniDraw files", "*.mdr"), ("All files", "*.*")), mode="rb")
        if f is not None:
            self.shape_manager = pickle.load(f)
            f.close()
            self.render()

    def clear_canvas(self, event):
        self.shape_manager.clear()
        self.render()

    def render(self, shapes: List[Shape]=None):
        self.renderer.render(self.shape_manager.get_shapes() if not shapes else shapes, self.color_selection.get(), self.pattern_selection.get())
