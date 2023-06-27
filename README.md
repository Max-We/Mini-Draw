# ✏️ Mini Draw ✏️

Mini Draw is a small python project that lets you create drawings with various shapes and bézier curves.

![](showcase.webm)

## Controls

Click and hold the `left mouse button` to draw a line. Release the button once the line is finished.

While drawing a line with the left mouse button, click the `right mouse button` to set checkpoints. This lets you create lines with multiple segments

You can create polygons by drawing multi-line segments and releasing the last point on the origin point of the line to close the shape.

Use the `middle mouse button` to draw the control points. With this action you can move lines and create bézier curves.

Press `x` to clear the canvas and `c` to toggle the visibility of the control points.

## Installation

To use Mini Draw, please install tkinter and numpy on your machine.

```shell
# Ubuntu
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

```text
pip install numpy
```

## Implementation details

- Bresenham algorithm to draw lines
- De Casteljau algorithm to create segments of bézier curves
- tkinter for various ui elements
- `tkinter.create_rectangle` to set all pixels individually (no helper functions like `create_line`)
- numpy to store pixel matrices
- Structured into components `Ui`, `ShapeManager` and `Renderer` (separation of concerns)