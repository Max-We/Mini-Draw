from ShapeManager import ShapeManager
from Shapes import Polygon, Point, Line
from Ui import Ui

# Load shapemanager presets
shape_manager = ShapeManager()
shape_manager.add_shape(Line(Point(200, 200), Point(300,100)))
shape_manager.add_shape(Polygon([Point(20,20), Point(120,205), Point(220, 50)], closed=True))

ui = Ui(shape_manager)