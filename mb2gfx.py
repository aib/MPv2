import collections
import math
import time

from OpenGL import GL

import mp
import shapes

class Scene:
	def __init__(self, size):
		self.size = size
		self.keys = collections.defaultdict(lambda: False)
		self.cam_pos = { 'theta': math.radians(41), 'phi': math.radians(90 - 15), 'r': 10 }

		GL.glClearColor(.1, 0, .1, 1)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
		GL.glEnable(GL.GL_BLEND)

		self.test_shape = shapes.Hexahedron(self)

		now = time.monotonic()
		self.last_update_time = now

	def update(self):
		now = time.monotonic()
		dt = now - self.last_update_time
		self.last_update_time = now

		if self.keys['w']: self.cam_pos['phi']   -= math.tau/2 * dt
		if self.keys['a']: self.cam_pos['theta'] += math.tau/2 * dt
		if self.keys['s']: self.cam_pos['phi']   += math.tau/2 * dt
		if self.keys['d']: self.cam_pos['theta'] -= math.tau/2 * dt
		if self.keys['q']: self.cam_pos['r']     += 2 * dt
		if self.keys['e']: self.cam_pos['r']     -= 2 * dt

		cam_pos_cartesian = [
			self.cam_pos['r'] * math.sin(self.cam_pos['phi']) * math.cos(self.cam_pos['theta']),
			self.cam_pos['r'] * math.cos(self.cam_pos['phi']),
			self.cam_pos['r'] * math.sin(self.cam_pos['phi']) * math.sin(self.cam_pos['theta']),
		]

		self.model = mp.identityM()
		self.view = mp.lookatM(cam_pos_cartesian, [0, 0, 0], [0, 1, 0])
		self.projection = mp.perspectiveM(math.tau/8, self.size[0] / self.size[1], .1, 100.)

		self.test_shape.update(dt)

	def render(self):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT)

		for f in self.test_shape.faces:
			f.render()

	def key_down(self, key):
		self.keys[key] = True

	def key_up(self, key):
		self.keys[key] = False
