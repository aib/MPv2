import numpy as np

import gfx
import objreader

SHAPE_VS = """
#version 130

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

in vec3 position;
in vec3 bary;
in vec3 wires;
in vec2 texUV;

out vec3 vf_bary;
out vec3 vf_wires;
out vec2 vf_texUV;

void main() {
	gl_Position = u_projection * u_view * u_model * vec4(position, 1);
	vf_bary = bary;
	vf_wires = wires;
	vf_texUV = texUV;
}
"""

SHAPE_FS = """
#version 130

in vec3 vf_bary;
in vec3 vf_wires;
in vec2 vf_texUV;

out vec4 fragColor;

void main() {
	vec3 wire_bary = (1 - vf_wires) + vf_bary;
	float edge_distance = min(wire_bary.x, min(wire_bary.y, wire_bary.z));
	float edge = 1 - step(.05, edge_distance);

	vec4 faceColor = vec4(0, 1, 0, .2);
	vec4 wireColor = vec4(0, 1, 0, .8);
	fragColor = mix(faceColor, wireColor, edge);
}
"""

class Shape:
	def __init__(self, scene):
		self.scene = scene
		self.faces = []
		self.program = gfx.Program(SHAPE_VS, SHAPE_FS)

	def load_file(self, filename):
		with open(filename, 'r') as f:
			vertices, texcoords, normals = objreader.read_obj_np(f)

		for i, vf in enumerate(vertices):
			tf, nf = texcoords[i], normals[i]
			face = Face(self, i, vf, tf, nf)
			self.faces.append(face)

	def update(self, dt):
		with self.program:
			self.program.set_uniform('u_model', self.scene.model)
			self.program.set_uniform('u_view', self.scene.view)
			self.program.set_uniform('u_projection', self.scene.projection)

class Face:
	def __init__(self, shape, index, vertices, texcoords, normals):
		self.shape = shape
		self.triangles = []
		self.midpoint = sum(vertices) / len(vertices)

		for i in range(1, len(vertices)-1):
			i0, i1, i2 = 0, i, i+1
			triangle = Triangle(vertices[[i0, i1, i2]], texcoords[[i0, i1, i2]], [True, i2==len(vertices)-1, i==1])
			self.triangles.append(triangle)

	def get_distance_to(self, target):
		return np.linalg.norm(self.midpoint - target)

	def update(self, dt):
		pass

	def render(self):
		with self.shape.program:
			for t in self.triangles:
				t.render()

class Triangle:
	def __init__(self, vertices, texcoords=None, wires=None):
		if texcoords is None: texcoords = [[0, 0], [0, 1], [1, 0]]
		if wires is None: wires = [True, True, True]

		self.vertices = vertices
		self.texcoords = texcoords
		self.wires = wires

		self.vao = gfx.VAO()
		self.vertices_vbo = gfx.VBO.create_with_data(self.vertices)
		self.tex_vbo = gfx.VBO.create_with_data(self.texcoords)
		self.bary_vbo = gfx.VBO.create_with_data([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
		self.wires_vbo = gfx.VBO.create_with_data([self.wires, self.wires, self.wires])

		with self.vao:
			self.vao.set_vbo_as_attrib(0, self.vertices_vbo)
			self.vao.set_vbo_as_attrib(1, self.bary_vbo)
			self.vao.set_vbo_as_attrib(2, self.wires_vbo)
			self.vao.set_vbo_as_attrib(3, self.tex_vbo)

	def render(self):
		self.vao.draw_triangles()
