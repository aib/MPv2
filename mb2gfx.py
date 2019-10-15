import collections
import glob
import itertools as it
import math
import time

import numpy as np
from OpenGL import GL

import ball
import camera
import mp
import shapes
import texture

class Scene:
	def __init__(self, size):
		self.size = size
		self.keys = collections.defaultdict(lambda: False)
		self.midi = None
		self.camera = camera.SphericalCamera(
			self,
			pos=[math.radians(41), math.radians(90 - 15), 10],
			speed=[math.tau/2, math.tau/2, 2],
			target=[0, 0, 0],
			up=[0, 1, 0]
		)
		self.next_free_texture = 1

		GL.glClearColor(.1, 0, .1, 1)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
		GL.glEnable(GL.GL_BLEND)

		self.ball_textures = list(map(lambda fn: self.create_texture(fn), glob.glob('texture/ball*.png')))

		self.test_shape = shapes.Hexahedron(self)
		self.test_ball = ball.Ball(self, [0, 0, 0], [-.1, 0, 0], 1, np.random.choice(self.ball_textures))

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

		drawables = it.chain(self.test_shape.faces, [self.test_ball])

		for drawable in sorted(drawables, key=lambda d: d.get_distance_to(self.camera.get_pos()), reverse=True):
			drawable.render()

	def get_all_faces(self):
		return self.test_shape.faces

	def key_down(self, key):
		self.keys[key] = True

	def key_up(self, key):
		self.keys[key] = False

	def midi_connected(self, midi):
		self.midi = midi

	def note_down(self, channel, note, velocity):
		pass

	def note_up(self, channel, note, velocity):
		pass

	def note_play(self, channel, note, duration, svel, evel):
		pass

	def create_texture(self, image_file):
		number = self.next_free_texture
		self.next_free_texture += 1
		return texture.Texture2D.create_with_image(number, image_file)
