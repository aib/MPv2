import shapes

class Range:
	def __init__(self, min_, max_):
		self.MIN = min_
		self.MAX = max_

	def map01(self, v):
		return self.MIN + ((self.MAX - self.MIN) * v)

DEPTH = Range(.1, 1000.)

SHAPE_SCALE = 3.

BALLS = Range(0, 16)
BALL_SPEED = Range(0., 20.)

SHAPES = [
	shapes.Tetrahedron,
	shapes.Hexahedron,
	shapes.Octohedron,
	shapes.Dodecahedron,
	shapes.Icosahedron,
]
SHAPE_INDEX = Range(0, len(SHAPES) - 1)
