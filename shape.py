import colorsys

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

out vec3 vf_position;
out vec3 vf_bary;
out vec3 vf_wires;
out vec2 vf_texUV;

void main() {
	gl_Position = u_projection * u_view * u_model * vec4(position, 1);
	vf_position = position;
	vf_bary = bary;
	vf_wires = wires;
	vf_texUV = texUV;
}
"""

SHAPE_FS = """
#version 130

#define MAX_BALLS 16

uniform vec4 u_balls[MAX_BALLS];
uniform float u_excitation;
uniform vec3 u_faceColor;

uniform sampler2D t_face;

in vec3 vf_position;
in vec3 vf_bary;
in vec3 vf_wires;
in vec2 vf_texUV;

out vec4 fragColor;

float ball_dist() {
	float minDist = 1. / 0.;

	for (int i = 0; i < MAX_BALLS; i++) {
		float radius = u_balls[i].w;
		if (radius == 0.0) continue;

		float dist = distance(vf_position, u_balls[i].xyz);
		float sparkle = dist * dist * radius;
		minDist = min(sparkle, minDist);
	}
	return clamp(1 - sqrt(minDist / 10), 0, 1);
}

void main() {
	float excitation = (u_excitation/4);
	vec3 wire_bary = (1 - vf_wires) + vf_bary;
	float edge_distance = min(wire_bary.x, min(wire_bary.y, wire_bary.z));
	float edge_distance_delta = fwidth(edge_distance);
//	float edge = 1 - smoothstep(edge_distance_delta * .5, edge_distance_delta * 2, edge_distance);
	float edge = 1 - step(.005, edge_distance);

	vec4 texColor = texture2D(t_face, vf_texUV) + vec4(.1, .1, .1, 0);
	texColor.a = max(texColor.r, max(texColor.g, texColor.b));
	vec4 faceColor = texColor * vec4(u_faceColor, 1) + (vec4(u_faceColor, 1) * u_excitation/5);
//	vec4 faceColor = texColor + vec4(u_faceColor*texColor.a, texColor.a) + (vec4(u_faceColor, 1) * u_excitation/5);
//	vec4 faceColor = vec4(vf_texUV.st, 0, .4);
//	vec4 faceColor = vec4(dFdx, 0, 0, .4);
	faceColor.a = .2;
	vec4 highlight = vec4(ball_dist(), ball_dist(), ball_dist(), ball_dist());
	faceColor += highlight;

	vec4 wireColor = vec4(0, .2, 1, 1);
	fragColor = mix(faceColor, wireColor, edge);
	fragColor.a = max(fragColor.a, excitation);
}
"""

class Shape:
	def __init__(self, scene, radius):
		self.scene = scene
		self.radius = radius

		self.faces = []
		self.program = gfx.Program(SHAPE_VS, SHAPE_FS)

	def load_file(self, filename):
		with open(filename, 'r') as f:
			vertices, texcoords, normals = objreader.read_obj_np(f)

		for i, vf in enumerate(vertices):
			tf, nf = texcoords[i], normals[i]
			face = Face(self, i, vf * self.radius, tf, nf)
			self.faces.append(face)

	def update(self, dt):
		with self.program:
			self.program.set_uniform('u_model', self.scene.model)
			self.program.set_uniform('u_view', self.scene.view)
			self.program.set_uniform('u_projection', self.scene.projection)

		for f in self.faces:
			f.update(dt)

class Face:
	def __init__(self, shape, index, vertices, texcoords, normals):
		self.shape = shape
		self.index = index
		self.triangles = []
		self.midpoint = sum(vertices) / len(vertices)
		self.highlight_time = 0.
		self.color = colorsys.hsv_to_rgb(index/20*2*np.pi, 1, 1)
		self.color = colorsys.hsv_to_rgb(.5 + (1/6)*(index/20), 1, 1)

		for i in range(1, len(vertices)-1):
			i0, i1, i2 = 0, i, i+1
			triangle = Triangle(self, vertices[[i0, i1, i2]], texcoords[[i0, i1, i2]], [True, i2==len(vertices)-1, i==1])
			self.triangles.append(triangle)

	def get_distance_to(self, target):
		return np.linalg.norm(self.midpoint - target)

	def ball_collision(self, ball):
#		self.highlight_time = 3.
#		self.shape.scene.midi.play_note(0, [60, 64, 67, 70, 72, 73, 76, 78, 82, 83, 86, 88, 60, 64, 70, 72, 60, 64, 70, 72][self.index], 1*(self.index//3)/7, 100, 0)
		pass

	def update(self, dt):
		if self.highlight_time > 0:
			self.highlight_time -= dt
		if self.highlight_time < 0:
			self.highlight_time = 0.

	def render(self):
		with self.shape.program:
			self.shape.program.set_uniform('u_excitation', self.highlight_time)
			self.shape.program.set_uniform('u_faceColor', self.color, silent=True)
			for t in self.triangles:
				t.render()

class Triangle:
	def __init__(self, face, vertices, texcoords=None, wires=None):
		if texcoords is None: texcoords = [[0, 0], [0, 1], [1, 0]]
		if wires is None: wires = [True, True, True]

		self.face = face
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

	def __repr__(self):
		return "<T@f=(%d)>" % (self.face.index,)
