import numpy as np
from OpenGL import GL

import gfx
import objreader
import physics as phy

BALL_VS = """
#version 130

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

in vec3 position;

void main() {
	gl_Position = u_projection * u_view * u_model * vec4(position, 1);
}
"""

BALL_FS = """
#version 130

out vec4 fragColor;

void main() {
	fragColor = vec4(1, 1, 1, 1);
}
"""

class Ball:
	def __init__(self, scene, pos, vel):
		self.scene = scene
		self.pos = np.array(pos, dtype=np.float32)
		self.vel = np.array(vel, dtype=np.float32)
		"""
		import mb2gfx
		self.tri = mb2gfx.Triangle(
			[-20, 0, 0],
			[0, 0, -80],
			[+20, 0, 00],
		)
		"""

		self.program = gfx.Program(BALL_VS, BALL_FS)
		self.vao = gfx.VAO()
		with open('obj/sphere.obj') as f:
			v, t, n = objreader.read_obj_np(f)
		self.vpos = v
		self.vbo = gfx.VBO().create(v)
		self.update(0)

		with self.vao:
			self.vao.set_vbo_as_attrib(0, self.vbo)

	def update(self, dt):
		"""
		itime = phy.get_intersection_time(self.tri.p0, self.tri.p1, self.tri.p2, self.pos, self.vel, .5)

		if itime is not None and itime > 0:
			while itime < dt:
				print("boing at", itime, "with", dt, "left", self.pos)
				self.pos += self.vel * itime
				dt -= itime
				n = phy.get_triangle_normal(self.tri.p0, self.tri.p1, self.tri.p2)
				ref = phy.reflect(n, self.vel)
				self.vel = ref
				break
		"""

		self.pos += self.vel * dt

	def render(self):
		self.scene.model = np.eye(4, dtype=np.float32) @ gfx.translation_matrix(self.pos[0], self.pos[1], self.pos[2])
		with self.program:
			self.scene.update_uniforms()
			self.vao.draw_triangles()
