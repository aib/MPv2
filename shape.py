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
in vec3 wires;

out vec3 vf_bary;
out vec3 vf_wires;

void main() {
	gl_Position = u_projection * u_view * u_model * vec4(position, 1);
	vf_bary = bary;
	vf_wires = wires;
}
"""

SHAPE_FS = """
#version 130

uniform float u_time;

in vec3 vf_bary;
in vec3 vf_wires;

out vec4 fragColor;

void main() {
//	float edge_distance = min(vf_bary.x, min(vf_bary.y, vf_bary.z));
	vec3 wire_bary = (1 - vf_wires) + vf_bary;
	float edge_distance = min(wire_bary.x, min(wire_bary.y, wire_bary.z));

	float edge = 1 - step(.05, edge_distance);

	float hil = sin(u_time*2) / 2 + 0.5;
	vec4 cc = vec4(vf_bary, .95);//hil);

	fragColor = mix(cc, vec4(vf_bary, edge), edge);
}
"""

class Shape:
	def __init__(self, scene):
		self.scene = scene

		with open(self.get_obj_file(), 'r') as f:
			self.vertices, t, n = objreader.read_obj_np(f)

		self.program = gfx.Program(SHAPE_VS, SHAPE_FS)
		self.vao = gfx.VAO()
		self.vertices_vbo = gfx.VBO.create(self.vertices*3)
		self.bary_vbo = gfx.VBO.create(np.asarray(gfx.get_barycentric_coordinates(self.vertices), dtype=np.float32))
		self.wires_vbo = self._get_wire_data(self.get_wires())

		with self.vao:
			self.vao.set_vbo_as_attrib(0, self.vertices_vbo)
			self.vao.set_vbo_as_attrib(1, self.bary_vbo)
			self.vao.set_vbo_as_attrib(2, self.wires_vbo)

		wires = []
		for triangle in self.vertices:
			p0, p1, p2 = triangle
			a2 = phy.angle_between(p0-p2, p1-p2)
			a0 = phy.angle_between(p1-p0, p2-p0)
			a1 = phy.angle_between(p2-p1, p0-p1)
			import math
			print(math.degrees(a0), math.degrees(a1), math.degrees(a2))
			r45 = (math.tau/8) * 1.01
			edge = [1 if a0 < r45 else 0, 1 if a1 < r45 else 0, 1 if a2 < r45 else 0]
			wires.append(edge)

		print(wires)
		self.wires_vbo = self._get_wire_data(wires)
		with self.vao:
			self.vao.set_vbo_as_attrib(2, self.wires_vbo)



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

class Hexahedron(Shape):
	def get_obj_file(self):
		return 'obj/hexahedron.obj'

	def get_wires(self):
		return [
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 0],
			[1, 1, 1],
			[1, 1, 1],
			[0, 1, 1]
		]
