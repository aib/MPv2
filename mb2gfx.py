import collections
import glob
import itertools as it
import math
import queue
import time

import numpy as np
from OpenGL import GL

import ball
import camera
import mp
import shapes
import texture

MAX_BALLS = 16

class Scene:
	def __init__(self, size):
		self.size = size
		self.keys = collections.defaultdict(lambda: False)
		self.midi = None

		self._deferred_calls = queue.Queue()

		self.camera = camera.SphericalCamera(
			self,
			pos=[math.radians(41), math.radians(90 - 15), 10],
			speed=[math.tau/2, math.tau/2, 2],
			target=[0, 0, 0],
			up=[0, 1, 0]
		)
#		self.camera = camera.WonderingSphericalCamera(
#			target=[0, 0, 0],
#			up=[0, 1, 0],
#			theta_eq=lambda elapsed: (elapsed * math.tau / 499) % math.tau,
#			phi_eq=lambda elapsed: math.tau/4 - math.sin(elapsed / 131) * (math.tau/16),
#			r_eq=lambda elapsed: 15
#		)
		self.fovy = math.tau / 8
		self.next_free_texture = 1

		GL.glClearColor(0, 0, 0, 0)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
		GL.glEnable(GL.GL_BLEND)

		self.ball_textures = list(map(lambda fn: self.create_texture(fn), glob.glob('texture/ball*.png')))
		self.balls = [ball.Ball(self, i) for i in range(MAX_BALLS)]

#		self.test_shape = shapes.Tetrahedron(self)
		self.test_shape = shapes.Hexahedron(self)
#		self.test_shape = shapes.Icosahedron(self)
#		self.test_shape = shapes.Dodecahedron(self)

		self.set_ball_count(3)

		self.ftex1 = self.create_texture("texture/starfield_alpha.png")
		with self.test_shape.program:
			self.test_shape.program.set_uniform('t_face', self.ftex1.number, silent=True)

		now = time.monotonic()
		self.start_time = now
		self.last_update_time = now

	def set_ball_count(self, count):
		for i in range(MAX_BALLS):
			if i >= count:
				self.balls[i].enabled = False
			elif not self.balls[i].enabled:
				self._init_ball(self.balls[i])
				self.balls[i].enabled = True

	def update(self):
		now = time.monotonic()
		elapsed = now - self.start_time
		dt = now - self.last_update_time
		self.last_update_time = now

		if self.keys['r']: self.fovy -= math.tau / 16 * dt
		if self.keys['f']: self.fovy += math.tau / 16 * dt
		if self.keys['q']: self.camera.move([ 0,  0, 1 / +self.fovy * dt])
		if self.keys['e']: self.camera.move([ 0,  0, 1 / -self.fovy * dt])
#		print(self.fovy, self.camera.get_pos()[2])

		while True:
			try:
				item = self._deferred_calls.get_nowait()
				item[0](*item[1], **item[2])
			except queue.Empty:
				break


		self.camera.update(dt)
		self.model = mp.identityM()
		self.view = self.camera.get_view_matrix()
		self.projection = mp.perspectiveM(self.fovy, self.size[0] / self.size[1], .1, 100.)

		for b in filter(lambda b: b.enabled, self.balls):
			b.update(dt)

		with self.test_shape.program:
			self.test_shape.program.set_uniform('u_balls', [[b.pos[0], b.pos[1], b.pos[2], b.radius if b.enabled else 0] for b in self.balls], silent=True)

		self.test_shape.update(dt)

	def render(self):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT)

		drawables = it.chain(self.test_shape.faces, filter(lambda b: b.enabled, self.balls))

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
		self._defer(self.set_ball_count, note-60)
		pass

	def note_up(self, channel, note, velocity):
		pass

	def note_play(self, channel, note, duration, svel, evel):
		self.midi.play_note(channel, note, duration, svel, evel)
		pass

	def ball_face_collision(self, ball, face, pos):
		face.highlight_time = 3.

	def create_texture(self, image_file):
		number = self.next_free_texture
		self.next_free_texture += 1
		return texture.Texture2D.create_with_image(number, image_file)

	def _defer(self, func, *args, **kwargs):
		self._deferred_calls.put_nowait((func, args, kwargs))

	def _init_ball(self, ball):
		ball.init(
			pos=[0, 0, 0],
			vel=mp.normalize(np.random.standard_normal(3)),
			radius=1.,
			texture=np.random.choice(self.ball_textures)
		)
