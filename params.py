import shapes

class Range:
	def __init__(self, min_, max_, default=None):
		self.MIN = min_
		self.MAX = max_
		self.DEFAULT = default

DEPTH = Range(.1, 1000.)

SHAPE_SCALE = 3.

BALLS = Range(0, 16, default=1)
BALL_SPEED = Range(0., 20., default=1.)
BALL_RADIUS = Range(.05, 1., default=.2)

SHAPES = [
	shapes.Tetrahedron,
	shapes.Hexahedron,
	shapes.Octohedron,
	shapes.Dodecahedron,
	shapes.Icosahedron,
]
SHAPE_INDEX = Range(0, len(SHAPES) - 1, default=4)

VOLUME = Range(0, 127, 64)
