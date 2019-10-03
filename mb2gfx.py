import math
import time

import numpy as np

from OpenGL import GL
from OpenGL.GL import shaders

import gfx

class Scene(gfx.Scene):
	def __init__(self, size):
		super().__init__(size)

		self.vert = gfx.VBO.create(np.array([[0, 1, 0],    [-1,-1, 0],     [1,-1, 0]],      'f'))
		self.cols = gfx.VBO.create(np.array([[1, 0, 0, 1], [0, 1, 0, 0.5], [0, 0, 1, 0.1]], 'f'))

		self.program = gfx.create_program('scene.vert', 'scene.frag')

		self.view[3][2] = -5
		self.projection = gfx.get_perspective_projection(size, (.1, 100.))

		self.vao = gfx.VAO()

		with self.vao:
			self.vao.set_vbo_as_attrib(0, self.vert)
			self.vao.set_vbo_as_attrib(1, self.cols)


	def render(self):
		elapsed = time.monotonic() - self.start_time

		GL.glClear(GL.GL_COLOR_BUFFER_BIT)

		shaders.glUseProgram(self.program)
		self.set_uniforms(elapsed)

		with self.vao:
			GL.glDrawArrays(GL.GL_TRIANGLES, 0, 9)
