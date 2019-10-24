import shapes

class Range:
	def __init__(self, min_, max_, default=None):
		self.MIN = min_
		self.MAX = max_
		self.DEFAULT = default

class Enum:
	def __init__(self, values, default=None):
		self.values = values
		self.MIN = 0
		self.MAX = len(values) - 1
		self.DEFAULT = default

	def __len__(self): return len(self.values)
	def __iter__(self): return iter(self.values)
	def __getitem__(self, i): return self.values[i]

DEPTH = Range(.1, 1000.)

SHAPE_SCALE = 3.

BALLS = Range(0, 16, default=1)
BALL_SPEED = Range(0., 20., default=1.)
BALL_RADIUS = Range(.05, 1., default=.2)

SHAPES = Enum([
	shapes.Tetrahedron,
	shapes.Hexahedron,
	shapes.Octohedron,
	shapes.Dodecahedron,
	shapes.Icosahedron,
], default=4)

VOLUME = Range(0, 127, 64)
