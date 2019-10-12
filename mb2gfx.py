import collections
import math
import time

from OpenGL import GL

import ball
import camera
import mp
import shapes

class Scene:
	def __init__(self, size):
		self.size = size
		self.keys = collections.defaultdict(lambda: False)
		self.camera = camera.SphericalCamera(
			pos=[math.radians(41), math.radians(90 - 15), 10],
			speed=[math.tau/2, math.tau/2, 2],
			target=[0, 0, 0],
			up=[0, 1, 0]
		)

		GL.glClearColor(.1, 0, .1, 1)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
		GL.glEnable(GL.GL_BLEND)

		self.test_shape = shapes.Hexahedron(self)
		self.test_ball = ball.Ball(self, [0, 0, 0], [-.1, 0, 0])

		now = time.monotonic()
		self.last_update_time = now

	def update(self):
		now = time.monotonic()
		dt = now - self.last_update_time
		self.last_update_time = now

		if self.keys['w']: self.camera.move([ 0, -dt, 0 ])
		if self.keys['a']: self.camera.move([+dt, 0,  0 ])
		if self.keys['s']: self.camera.move([ 0, +dt, 0 ])
		if self.keys['d']: self.camera.move([-dt, 0,  0 ])
		if self.keys['q']: self.camera.move([ 0,  0, +dt])
		if self.keys['e']: self.camera.move([ 0,  0, -dt])

		self.model = mp.identityM()
		self.view = self.camera.get_view_matrix()
		self.projection = mp.perspectiveM(math.tau/8, self.size[0] / self.size[1], .1, 100.)

		self.test_ball.update(dt)
		self.test_shape.update(dt)

	def render(self):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT)

		for f in self.test_shape.faces:
			f.render()

		self.test_ball.render()

	def key_down(self, key):
		self.keys[key] = True

	def key_up(self, key):
		self.keys[key] = False
