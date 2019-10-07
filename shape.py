import numpy as np

import gfx
import objreader
import physics as phy

SHAPE_VS = """
#version 130

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

in vec3 position;
in vec3 bary;

out vec3 vf_bary;

void main() {
	gl_Position = u_projection * u_view * u_model * vec4(position, 1);
	vf_bary = bary;
}
"""

SHAPE_FS = """
#version 130

in vec3 vf_bary;

out vec4 fragColor;

void main() {
	float edge_distance = min(vf_bary.x, min(vf_bary.y, vf_bary.z));
	float edge = 1 - step(.05, edge_distance);
	fragColor = vec4(vf_bary, edge);
}
"""

class Shape:
	def __init__(self, scene):
		self.scene = scene

		with open(self.get_obj_file(), 'r') as f:
			self.vertices, t, n = objreader.read_obj_np(f)

		self.program = gfx.Program(SHAPE_VS, SHAPE_FS)
		self.vao = gfx.VAO()
		self.vertices_vbo = gfx.VBO.create(self.vertices)
		self.bary_vbo = gfx.VBO.create(np.asarray(gfx.get_barycentric_coordinates(self.vertices), dtype=np.float32))

		with self.vao:
			self.vao.set_vbo_as_attrib(0, self.vertices_vbo)
			self.vao.set_vbo_as_attrib(1, self.bary_vbo)

	def get_obj_file(self):
		raise NotImplementedError()

	def get_wires(self):
		raise NotImplementedError()

	def update(self, dt):
		pass

	def render(self):
		with self.program:
			self.scene.model = np.eye(4)
			self.scene.update_uniforms()
			self.vao.draw_triangles()

	def _get_wire_data(self, wires):
		wires = np.asarray(wires, dtype=np.float32)
		wires3 = np.tile(wires, (1, 1, 3)).reshape(wires.shape[0], 3, 3)
		return gfx.VBO.create(wires3)
