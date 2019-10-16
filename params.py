class Range:
	def __init__(self, min_, max_):
		self.MIN = min_
		self.MAX = max_

	def map01(self, v):
		return self.MIN + ((self.MAX - self.MIN) * v)

DEPTH = Range(.1, 100.)

SHAPE_SCALE = 3.

BALLS = Range(0, 16)
