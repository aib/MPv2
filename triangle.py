import gfx

TRIANGLE_VS = """
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

TRIANGLE_FS = """
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

class Triangle:
	def __init__(self, vertices, texcoords=None, wires=None):
		if texcoords is None: texcoords = [[0, 0], [0, 1], [1, 0]]
		if wires is None: wires = [[1, 1, 1]] * 3

		self.vertices = vertices
		self.texcoords = texcoords
		self.wires = wires

		self.vao = gfx.VAO()
		self.vertices_vbo = gfx.VBO.create_with_data(self.vertices)
		self.tex_vbo = gfx.VBO.create_with_data(self.texcoords)
		self.bary_vbo = gfx.VBO.create_with_data([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
		self.wires_vbo = gfx.VBO.create_with_data(self.wires)

		with self.vao:
			self.vao.set_vbo_as_attrib(0, self.vertices_vbo)
			self.vao.set_vbo_as_attrib(1, self.bary_vbo)
			self.vao.set_vbo_as_attrib(2, self.wires_vbo)
			self.vao.set_vbo_as_attrib(3, self.tex_vbo)

	def update(self, dt):
		pass

	def render(self):
		self.vao.draw_triangles()
