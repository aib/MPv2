import math

import gfx
import mp

SKYBOX_VS = """
#version 130

uniform mat4 u_view;
uniform mat4 u_projection;

in vec3 position;
out vec3 vf_position;

void main() {
	gl_Position = u_projection * u_view * vec4(position, 1);
	vf_position = position;
}
"""

SKYBOX_FS = """
#version 130

uniform samplerCube t_skybox;
uniform vec3 u_camPos;

in vec3 vf_position;
out vec4 fragColor;

void main() {
	vec3 dir = vf_position - u_camPos;
	fragColor = texture(t_skybox, dir);
}
"""

class SkyBox:
	QUADS = [
		[[-1, -1, +1], [+1, -1, +1], [+1, +1, +1], [-1, +1, +1]], # front
		[[+1, -1, -1], [-1, -1, -1], [-1, +1, -1], [+1, +1, -1]], # back
		[[-1, -1, -1], [-1, -1, +1], [-1, +1, +1], [-1, +1, -1]], # left
		[[+1, -1, +1], [+1, -1, -1], [+1, +1, -1], [+1, +1, +1]], # right
		[[-1, +1, +1], [+1, +1, +1], [+1, +1, -1], [-1, +1, -1]], # top
		[[-1, -1, -1], [+1, -1, -1], [+1, -1, +1], [-1, -1, +1]], # bottom
	]

	def __init__(self, scene, distance, texture):
		self.scene = scene
		self.texture = texture

		self.vertices = mp.array(self.QUADS)[:, [[1, 0, 2], [2, 0, 3]]].reshape(-1, 3) * distance

		self.program = gfx.Program(SKYBOX_VS, SKYBOX_FS)
		self.vao = gfx.VAO()
		with self.vao:
			self.vao.create_vbo_attrib(0, self.vertices)

		if self.texture is not None:
			with self.program:
				self.program.set_uniform('t_skybox', self.texture.number)

	def update(self, dt):
		with self.program:
			self.program.set_uniform('u_view', self.scene.view, silent=True)
			self.program.set_uniform('u_projection', self.scene.projection, silent=True)
			self.program.set_uniform('u_camPos', self.scene.camera.get_pos(), silent=True)

	def render(self):
		with self.program:
			self.vao.draw_triangles()
