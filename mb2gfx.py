import collections
import glob
import itertools as it
import math
import time

import numpy as np
from OpenGL import GL

import ball
import camera
import controller
import mp
import params
import shape
import shapes
import texture

class Scene:
	def __init__(self, size, midi):
		self.size = size
		self.keys = collections.defaultdict(lambda: False)
		self.midi = midi

		self.controller = controller.Controller(self, midi)
		self.midi.set_controller(self.controller)

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
		self.balls = [ball.Ball(self, i) for i in range(params.BALLS.MAX)]

		self.shapes = [shape(self) for shape in params.SHAPES]

		self.set_ball_speed(1.)
		self.set_ball_count(3)

		self.set_shape(4)

		now = time.monotonic()
		self.last_update_time = now

	def enabled_balls(self):
		return [b for b in self.balls if b.enabled]

	def set_ball_count(self, count):
		for i in range(params.BALLS.MAX):
			if i >= count:
				self.balls[i].enabled = False
			elif not self.balls[i].enabled:
				self._reset_ball(self.balls[i])
				self.balls[i].enabled = True

	def set_ball_speed(self, speed):
		self._ball_speed = speed
		for b in self.enabled_balls():
			self._update_ball_speed(b)

	def reset_balls(self):
		for b in self.enabled_balls():
			self._reset_ball(b)

	def set_shape(self, i):
		self.active_shape = self.shapes[i]

	def update(self):
		now = time.monotonic()
		dt = now - self.last_update_time
		self.last_update_time = now

		self.controller.update(dt)

		self.camera.update(dt)

		self.model = mp.identityM()
		self.view = self.camera.get_view_matrix()
		self.projection = mp.perspectiveM(math.tau/8, self.size[0] / self.size[1], params.DEPTH.MIN, params.DEPTH.MAX)

		for b in self.enabled_balls():
			b.update(dt)

		self.active_shape.update(dt)

	def render(self):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT)

		drawables = it.chain(self.active_shape.faces, self.enabled_balls())

		for drawable in sorted(drawables, key=self._drawable_sort_key, reverse=True):
			drawable.render()

	def get_all_faces(self):
		return self.active_shape.faces

	def key_down(self, key):
		self.keys[key] = True

	def key_up(self, key):
		self.keys[key] = False

	def ball_face_collision(self, ball, face, pos):
		pass

	def create_texture(self, image_file):
		number = self.next_free_texture
		self.next_free_texture += 1
		return texture.Texture2D.create_with_image(number, image_file)

	def _drawable_sort_key(self, drawable):
		if isinstance(drawable, shape.Face):
			if np.dot(drawable.normal, drawable.midpoint - self.camera.get_pos()) >= 0:
				return -2 * params.DEPTH.MAX
			else:
				return +2 * params.DEPTH.MAX

		return drawable.get_distance_to(self.camera.get_pos())

	def _reset_ball(self, ball):
		ball.init(
			pos=[0, 0, 0],
			dir=mp.normalize(np.random.standard_normal(3)),
			speed=1.,
			radius=1.,
			texture=np.random.choice(self.ball_textures)
		)
		self._update_ball_speed(ball)

	def _update_ball_speed(self, ball):
		ball.speed = self._ball_speed
