import math
import time

import numpy as np
from OpenGL import GL

import ball
import gfx
import mp
import objreader
import physics as phy
import shape
import texture

class Scene(gfx.Scene):
	def do_init(self, size):
		GL.glDisable(GL.GL_DEPTH_TEST)
		GL.glEnable(GL.GL_BLEND)
		GL.glEnable(GL.GL_TEXTURE_2D)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

		self.projection = gfx.perspective_projection_matrix(math.tau/8, size, (.1, 100.))

		with open("scene.vert", 'r') as f: vs = f.read()
		with open("scene.frag", 'r') as f: fs = f.read()
		self.program = gfx.Program(vs, fs)

		self.ball = ball.Ball(
			self,
			[0, 5, -8],
			[-2.2, -1, 0]
		)
		self.ball.vel /= .2

		self.shape = shape.Hexahedron(self)

		self.texture = texture.Texture2D()
		self.texture.load_image("/tmp/T_UV_Map.jpg")

	def do_update(self, dt):
		self.model = np.eye(4, dtype=np.float32) @ gfx.scaling_matrix(2) @ gfx.translation_matrix(5, 0, 0)
		self.view = (np.eye(4, dtype=np.float32)
			@ gfx.rotation_matrix([0, 1, 0], self.elapsed/3)
			@ gfx.translation_matrix(0, -2.01, -20)
		)

		self.ball.update(dt)
		self.shape.update(dt)

	def do_render(self):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT)

		with self.program:
			self.update_uniforms()
			self.ball.render()

		self.shape.render()
