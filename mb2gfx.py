import math
import time

import numpy as np

from OpenGL import GL
from OpenGL.arrays import vbo
from OpenGL.GL import shaders

import gfx

class Scene(gfx.Scene):
	def __init__(self, size):
		super().__init__(size)

		self.hmm = vbo.VBO(
			np.array([
				[ 0, 1, 0],
				[-1,-1, 0],
				[ 1,-1, 0],
				[ 2,-1, 0],
				[ 4,-1, 0],
				[ 4, 1, 0],
				[ 2,-1, 0],
				[ 4, 1, 0],
				[ 2, 1, 0],
			],'f')
		)

		self.program = gfx.create_program('scene.vert', 'scene.frag')

		self.view[3][2] = -5
		self.projection = gfx.get_perspective_projection(size, (.1, 100.))

	def render(self):
		now = time.monotonic() - self.start_time

		GL.glClear(GL.GL_COLOR_BUFFER_BIT)

		shaders.glUseProgram(self.program)
		self.set_uniforms(now)

		try:
			self.hmm.bind()
			try:
				GL.glEnableClientState(GL.GL_VERTEX_ARRAY);
				GL.glVertexPointerf(self.hmm)
				GL.glDrawArrays(GL.GL_TRIANGLES, 0, 9)
			finally:
				self.hmm.unbind()
				GL.glDisableClientState(GL.GL_VERTEX_ARRAY);
		finally:
			shaders.glUseProgram(0)
