import collections
import math
import time

from OpenGL import GL

import mp

class Scene:
	def __init__(self, size):
		self.size = size
		self.keys = collections.defaultdict(lambda: False)

		GL.glClearColor(.1, 0, .1, 1)

		now = time.monotonic()
		self.last_update_time = now

	def update(self):
		now = time.monotonic()
		dt = now - self.last_update_time
		self.last_update_time = now

		self.model = mp.identityM()
		self.view = mp.lookatM([-5, 2, 10], [0, 0, 0], [0, 1, 0])
		self.projection = mp.perspectiveM(math.tau/8, self.size[0] / self.size[1], .1, 100.)

	def render(self):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT)

	def key_down(self, key):
		self.keys[key] = True

	def key_up(self, key):
		self.keys[key] = False
