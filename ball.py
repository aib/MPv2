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
	gl_Position = u_projection * u_view * u_model * vec4(position, 1);
	vf_texUV = texUV;
}
"""

BALL_FS = """
#version 130

in vec2 vf_texUV;

out vec4 fragColor;

void main() {
	fragColor = vec4(1, 1, 1, 1);
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

	def __init__(self, scene, pos, vel):
		self.scene = scene
		self.pos = mp.array(pos)
		self.vel = mp.array(vel)

		self.program = gfx.Program(BALL_VS, BALL_FS)

		self.vao = gfx.VAO()
		self.vertices_vbo = gfx.VBO.create_with_data(self.VERTICES)
		self.texcoords_vbo = gfx.VBO.create_with_data(self.TEXCOORDS)

		with self.vao:
			self.vao.set_vbo_as_attrib(0, self.vertices_vbo)
			self.vao.set_vbo_as_attrib(1, self.texcoords_vbo)

	def get_distance_to(self, target):
		return np.linalg.norm(self.pos - target)

	def update(self, dt):
		self.pos += self.vel * dt

		# Rotate so basis matches that of the eye
		billboard_rot = mp.from3vecM(
			self.scene.camera.get_right(),
			self.scene.camera.get_up(),
			self.scene.camera.get_forward()
		)

		model = billboard_rot @ mp.translateM(self.pos)
		with self.program:
			self.program.set_uniform('u_model', model)
			self.program.set_uniform('u_view', self.scene.view)
			self.program.set_uniform('u_projection', self.scene.projection)

	def render(self):
		with self.program:
			self.vao.draw_triangles()
