import math
import tkinter as tk

from ShapeManager import ShapeManager
from config import control_point_size
from renderer import Renderer
from shapes import Line, Point, Polygon, ControlPoint

shape_manager = ShapeManager()
shape_manager.add_shape(Line(Point(200, 200), Point(300,100)))
shape_manager.add_shape(Polygon([Point(0,0), Point(100,125), Point(200, 20)], closed=True))
shape_manager.add_shape(Polygon([Point(20,20), Point(120,205), Point(220, 50)], closed=True))

grabbed_point = None
def show_control_points(event):
    renderer.toggle_control_points()
    renderer.render(shape_manager.get_shapes())

def render(event):
    renderer.render(shape_manager.get_shapes())

def grab_point(event):
    """Selects the point under the user's cursor."""

    global grabbed_point
    grabbed_point = shape_manager.get_control_point_by_click(Point(event.x, event.y))

def move_point(event):
    """Moves the point to the desired location."""

    global grabbed_point
    if grabbed_point:
        shape_manager.move_point(grabbed_point, Point(event.x, event.y))
        renderer.render(shape_manager.get_shapes())

def drop_point(event):
    """Ends the process of moving the point around."""

    global grabbed_point
    grabbed_point = None

new_shape_points = []
def start_draw(event):
    """Sets the first point that the user is drawing."""

    global new_shape_points
    new_shape_points = []
    new_shape_points.append(Point(event.x, event.y))
    # Temporary show the shape which is being drawn by the user
    renderer.render(shape_manager.get_shapes() + [ControlPoint(new_shape_points[0])])

def has_minimum_distance_to_last_point(point: Point):
    """Don't allow user to draw points on top of each other (bad UX)"""

    line_length = shape_manager.distance_between(new_shape_points[-1], point)
    control_point_diagonal = math.sqrt(2 * (control_point_size ** 2))
    # At least 3 control points should fit on a line (because control points shouldn't overlap)
    return line_length >= control_point_diagonal * 3

def add_point(event):
    """Add a point to the current selection."""

    global new_shape_points

    # Only if drawing is in progress
    if len(new_shape_points) > 0:
        new_point = Point(event.x, event.y)
        if has_minimum_distance_to_last_point(new_point):
            new_shape_points.append(new_point)
        # Temporary show the shape which is being drawn by the user
        renderer.render(shape_manager.get_shapes() + [Polygon(new_shape_points, closed=False, z_index=1000)])

def stop_draw(event):
    """Combine the points to a shape. This results in a single point (1) or line / polygon (>1)."""

    global new_shape_points
    new_point = Point(event.x, event.y)

    if len(new_shape_points) > 2:
        # Add Polygon / Line
        distance_to_origin = shape_manager.distance_between(new_shape_points[0], new_point)
        if distance_to_origin < control_point_size * 2:
            # Closed shape (snap to origin)
            shape_manager.add_shape(Polygon(new_shape_points, closed=True))
        else:
            # Unclosed shape (no snapping)
            if has_minimum_distance_to_last_point(new_point):
                new_shape_points.append(new_point)
            shape_manager.add_shape(Polygon(new_shape_points, closed=False))
    else:
        # Add single point
        shape_manager.add_shape(ControlPoint(new_shape_points[0]))

    renderer.render(shape_manager.get_shapes())
    new_shape_points = []

def clear_canvas(event):
    shape_manager.clear()
    renderer.render(shape_manager.get_shapes())

# https://www.perplexity.ai/search/0522ed03-1bae-4292-9d40-9bdeed7b91c4?s=c
# Create the main window
root = tk.Tk()

# Create the canvas
canvas = tk.Canvas(root, width=400, height=400, bg="white")
canvas.pack()
renderer = Renderer(canvas)

# Register listeners
canvas.bind("<ButtonPress-2>", grab_point)
canvas.bind("<B2-Motion>", move_point)
canvas.bind("<ButtonRelease-2>", drop_point)

canvas.bind("<ButtonPress-1>", start_draw)
canvas.bind("<ButtonPress-3>", add_point)
canvas.bind("<ButtonRelease-1>", stop_draw)

# canvas.bind("<Button-2>", render)
# canvas.bind("<ButtonRelease-1>", end_shape)
root.bind("c", show_control_points)
root.bind("x", clear_canvas)

# Draw a rectangle on the canvas
renderer.render(shape_manager.get_shapes())

# Start the main event loop
root.mainloop()
