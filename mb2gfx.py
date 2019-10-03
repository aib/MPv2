import math
import time

import numpy as np

from OpenGL import GL

import gfx
import objreader

class Scene(gfx.Scene):
	def do_init(self, size):
		GL.glEnable(GL.GL_DEPTH_TEST)

		self.projection = gfx.perspective_projection_matrix(math.tau/8, size, (.1, 100.))

		with open("scene.vert", 'r') as f:
			vs = f.read()
		with open("scene.frag", 'r') as f:
			fs = f.read()
		self.program = gfx.Program(vs, fs)

		with open('obj/dodecahedron.obj', 'r') as f:
			v, t, n = objreader.read_obj_np(f)
			vb = gfx.VBO.create(v)
			vn = gfx.VBO.create(n)

		self.vao = gfx.VAO()

		with self.vao:
			self.vao.set_vbo_as_attrib(0, vb)
			self.vao.set_vbo_as_attrib(1, vn)

	def do_render(self, elapsed, dt):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

		self.model = np.eye(4, dtype=np.float32) @ gfx.scaling_matrix(3)
		self.view = (np.eye(4, dtype=np.float32)
			@ gfx.rotation_matrix([0, 1, 0], elapsed/2)
			@ gfx.translation_matrix(0, 0, -20)
		)

		with self.program:
			self.set_uniforms(self.program, elapsed)
			draw_vao(self.vao)

def draw_vao(vao):
	main_vbo = vao.attribs[0]
	with vao:
		GL.glDrawArrays(GL.GL_TRIANGLES, 0, np.prod(main_vbo.data.shape[:-1]))
