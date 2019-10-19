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
import skybox
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
		GL.glEnable(GL.GL_TEXTURE_CUBE_MAP_SEAMLESS)

		skybox_texture = None
		self.skybox = skybox.SkyBox(self, params.DEPTH.MAX / 4, skybox_texture)

		self.ball_textures = list(map(lambda fn: self.create_texture(fn), glob.glob('texture/ball*.png')))
		self.balls = [ball.Ball(self, i) for i in range(params.BALLS.MAX)]

		self.shapes = [shape(self) for shape in params.SHAPES]

		self.set_ball_speed(1.)
		self.set_ball_radius(.2)
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
			b.speed = speed

	def set_ball_radius(self, radius):
		self._ball_radius = radius
		for b in self.enabled_balls():
			b.radius = radius

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

		self.view = self.camera.get_view_matrix()
		self.projection = mp.perspectiveM(math.tau/8, self.size[0] / self.size[1], params.DEPTH.MIN, params.DEPTH.MAX)

		self.skybox.update(dt)

		for b in self.enabled_balls():
			b.update(dt)

		for b in self.enabled_balls():
			if b.get_distance_to(mp.array([0, 0, 0])) > self.active_shape.radius:
				self._reset_ball(b)

		self.active_shape.update(dt)

	def render(self):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT)

		self.skybox.render()

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

	def create_texture(self, image_file, cls=texture.Texture2D, **kwargs):
		number = self.next_free_texture
		self.next_free_texture += 1
		return cls.create_with_image(number, image_file, **kwargs)

	def _drawable_sort_key(self, drawable):
		if isinstance(drawable, shape.Face):
			if np.dot(drawable.normal, drawable.midpoint - self.camera.get_pos()) <= 0:
				return -2 * params.DEPTH.MAX
			else:
				return +2 * params.DEPTH.MAX

		return drawable.get_distance_to(self.camera.get_pos())

	def _reset_ball(self, ball):
		ball.init(
			pos=[0, 0, 0],
			dir=mp.normalize(np.random.standard_normal(3)),
			speed=self._ball_speed,
			radius=self._ball_radius,
			texture=np.random.choice(self.ball_textures)
		)
