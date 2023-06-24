from ShapeManager import ShapeManager
from shapes import Polygon, Point, Line
from ui import Ui

# Load shapemanager presets
shape_manager = ShapeManager()
shape_manager.add_shape(Line(Point(200, 200), Point(300,100)))
# shape_manager.add_shape(Polygon([Point(0,0), Point(100,125), Point(200, 20)], closed=True))
shape_manager.add_shape(Polygon([Point(20,20), Point(120,205), Point(220, 50)], closed=True))

ui = Ui(shape_manager)