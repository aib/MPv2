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
	{ 'name': "Cello", 'number': 1, 'program': 42 },
	{ 'name': "Steel String Guitar", 'number': 2, 'program': 25 },
	{ 'name': "Marimba", 'number': 3, 'program': 12 },
	{ 'name': "Melodic Tom", 'number': 4, 'program': 117 },
	{ 'name': "Steel Drums", 'number': 5, 'program': 114 },
	{ 'name': "Koto", 'number': 6, 'program': 107 },
	{ 'name': "Harp", 'number': 7, 'program': 46 },
	{ 'name': "Synth Bass", 'number': 8, 'program': 38 },
], default=0)
