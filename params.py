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

BALLS = Range(0, 12, default=1)
BALL_SPEED = Range(0., 30., default=1.)
BALL_RADIUS = Range(.05, .75, default=.2)

SHAPES = Enum([
	shapes.Hexahedron,
	shapes.Octohedron,
	shapes.HexagonPrism,
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
	{ 'name': "Channel 1", 'number': 0, 'program': None },
	{ 'name': "Channel 2", 'number': 1, 'program': None },
	{ 'name': "Channel 3", 'number': 2, 'program': None },
	{ 'name': "Channel 4", 'number': 3, 'program': None },
	{ 'name': "Channel 5", 'number': 4, 'program': None },
	{ 'name': "Channel 6", 'number': 5, 'program': None },
	{ 'name': "Channel 7", 'number': 6, 'program': None },
	{ 'name': "Channel 8", 'number': 7, 'program': None },
	{ 'name': "Channel 9", 'number': 8, 'program': None },
	{ 'name': "Channel 10", 'number': 9, 'program': None },
	{ 'name': "Channel 11", 'number': 10, 'program': None },
	{ 'name': "Channel 12", 'number': 11, 'program': None },
	{ 'name': "Channel 13", 'number': 12, 'program': None },
	{ 'name': "Channel 14", 'number': 13, 'program': None },
	{ 'name': "Channel 15", 'number': 14, 'program': None },
	{ 'name': "Channel 16", 'number': 15, 'program': None },
], default=0)
