import shapes

class Range:
	def __init__(self, min_, max_, default=None):
		self.MIN = min_
		self.MAX = max_
		self.DEFAULT = default

class Enum:
	def __init__(self, values, default=None):
		self.values = values
		self.COUNT = len(values)
		self.MIN = 0
		self.MAX = self.COUNT - 1
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

CUSTOM_NOTE_LENGTH = object()
NOTE_LENGTHS = Enum([
	.0625,
	.125,
	.25,
	.5,
	1.,
	2.,
	CUSTOM_NOTE_LENGTH
], default=3)

CHANNELS = Enum([
	{ 'name': "Channel 1", 'number': 1 },
	{ 'name': "Channel 2", 'number': 2 },
	{ 'name': "Channel 3", 'number': 3 },
	{ 'name': "Channel 4", 'number': 4 },
	{ 'name': "Channel 5", 'number': 5 },
	{ 'name': "Channel 6", 'number': 6 },
	{ 'name': "Channel 7", 'number': 7 },
	{ 'name': "Channel 8", 'number': 8 },
], default=0)
