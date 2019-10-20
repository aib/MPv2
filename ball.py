import numpy as np

import gfx
import mp

BALL_VS = """
#version 130

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

in vec3 position;
in vec2 texUV;

out vec2 vf_texUV;

void main() {
	mat4 billboard_view = transpose(mat4(u_view[0], u_view[1], u_view[2], vec4(0, 0, 0, 1)));
	gl_Position = u_projection * u_view * u_model * billboard_view * vec4(position, 1);
	vf_texUV = texUV;
}
"""

BALL_FS = """
#version 130

uniform sampler2D t_ball;

in vec2 vf_texUV;

out vec4 fragColor;

void main() {
	fragColor = texture2D(t_ball, vf_texUV);
}
"""

class Ball:
	VERTICES = [
		[[-1, -1, 0], [+1, -1, 0], [-1, +1, 0]],
		[[-1, +1, 0], [+1, -1, 0], [+1, +1, 0]]
	]
	TEXCOORDS = [
		[[0, 0], [1, 0], [0, 1]],
		[[0, 1], [1, 0], [1, 1]]
	]

	def __init__(self, scene, index):
		self.scene = scene
		self.index = index

		self.enabled = False
		self.program = gfx.Program(BALL_VS, BALL_FS)

		self.vao = gfx.VAO()
		self.vertices_vbo = gfx.VBO.create_with_data(self.VERTICES)
		self.texcoords_vbo = gfx.VBO.create_with_data(self.TEXCOORDS)

		with self.vao:
			self.vao.set_vbo_as_attrib(0, self.vertices_vbo)
			self.vao.set_vbo_as_attrib(1, self.texcoords_vbo)

		self.init([0, 0, 0], [0, 0, 0], 0, 0, None)

	def init(self, pos, dir, speed, radius, texture):
		self.pos = mp.asarray(pos)
		self.dir = mp.asarray(dir)
		self.speed = speed
		self.radius = radius
		self.texture = texture

		if self.texture is not None:
			with self.program:
				self.program.set_uniform('t_ball', self.texture.number)

	def get_distance_to(self, target):
		return mp.norm(self.pos - target)

	def _update_physics(self, dt):
		collision_blacklist = []

		while dt > 0:
			col_tri, col_time, col_pos = self.scene.pick_triangle(self.pos, self.dir*self.speed, self.radius, maxtime=dt, blacklist=collision_blacklist)
			if col_tri is None:
				break

			self.scene.ball_face_collision(self, col_tri.face, col_pos)
			collision_blacklist.append(col_tri)

			self.dir = mp.reflect(-col_tri.normal, self.dir)
			self.pos += self.dir * self.speed * col_time
			dt -= col_time

		self.pos += self.dir * self.speed * dt

	def update(self, dt):
		self._update_physics(dt)

		model = mp.translateM(self.pos) @ mp.scaleM(self.radius)
		with self.program:
			self.program.set_uniform('u_model', model)
			self.program.set_uniform('u_view', self.scene.view)
			self.program.set_uniform('u_projection', self.scene.projection)

	def render(self):
		with self.program:
			self.vao.draw_triangles()
