import numpy as np

import gfx
import mp
import objreader

HIGHLIGHT_FALLOFF_TIME = .5
WIREFRAME_LINE_WIDTH = 2.

SHAPE_VS = """
#version 130

uniform mat4 u_view;
uniform mat4 u_projection;

in vec3 position;
in vec3 bary;
in vec2 texUV;
in vec3 normal;
in vec3 wires;

out vec3 vf_position;
out vec2 vf_texUV;

void main() {
	gl_Position = u_projection * u_view * vec4(position, 1);
	vf_position = position;
	vf_texUV = texUV;
}
"""

SHAPE_FS = """
#version 130

#define MAX_BALLS 16

uniform vec4 u_balls[MAX_BALLS];
uniform vec4 u_faceColorNormal;
uniform vec4 u_faceColorHighlighted;
uniform float u_faceHighlight;

in vec3 vf_position;
in vec2 vf_texUV;

out vec4 fragColor;

float ball_highlight_factor() {
	float maxHighlight = -1. / 0.;

	for (int i = 0; i < MAX_BALLS; i++) {
		float radius = u_balls[i].w;
		if (radius == 0.0) continue;

		float dist = max(distance(vf_position, u_balls[i].xyz) - radius, 0.);
		float light_radius = radius * 4;

		// f(lr)=0, f(0)=1
		float hf = (-1 / light_radius) * (dist - light_radius);
		hf = pow(clamp(hf, 0, 1), 2);

		maxHighlight = max(maxHighlight, hf);
	}

	return clamp(maxHighlight, 0, 1);
}

void main() {
	vec4 faceColor = mix(u_faceColorNormal, u_faceColorHighlighted, u_faceHighlight);
	vec4 ball_highlight = vec4(1, 1, 1, ball_highlight_factor());

	fragColor = mix(faceColor, ball_highlight, ball_highlight.a);
}
"""

WIRE_FS = """
#version 130

uniform vec4 u_wireColor;

out vec4 fragColor;

void main() {
	fragColor = u_wireColor;
}
"""

class Shape:
	def __init__(self, scene, name, radius):
		self.scene = scene
		self.name = name
		self.radius = radius

		self.faces = []
		self.symmetries = {}
		self.program = gfx.Program(SHAPE_VS, SHAPE_FS)
		self.wire_program = gfx.Program(SHAPE_VS, WIRE_FS)

	def load_file(self, filename, default_symmetry=True):
		with open(filename, 'r') as f:
			vertices, texcoords, normals = objreader.read_obj_map(f, vec_cls=mp.array)

		bsrad = max(map(lambda fvs: max(map(mp.norm, fvs)), vertices))

		for i, vf in enumerate(vertices):
			tf, nf = texcoords[i], normals[i]
			vf_scaled = list(map(lambda v: v / bsrad * self.radius, vf))
			face = Face(self, i, vf_scaled, tf, nf)
			self.faces.append(face)

		if default_symmetry:
			self.symmetries[len(self.faces)] = [(f.index,) for f in self.faces]

	def update(self, dt):
		with self.program:
			balls = [[b.pos[0], b.pos[1], b.pos[2], b.radius * b.opacity if b.enabled else 0.] for b in self.scene.balls.balls]
			self.program.set_uniform('u_balls', balls)
			self.program.set_uniform('u_view', self.scene.view)
			self.program.set_uniform('u_projection', self.scene.projection)

		with self.wire_program:
			self.wire_program.set_uniform('u_view', self.scene.view)
			self.wire_program.set_uniform('u_projection', self.scene.projection)

		for f in self.faces:
			f.update(dt)

class Face:
	def __init__(self, shape, index, vertices, texcoords, normals):
		self.shape = shape
		self.index = index

		self.triangles = []
		self.midpoint = sum(vertices) / len(vertices)
		self.normal = mp.triangle_normal(vertices[0:3])
		self.wire_color = mp.array([1, 1, 1, 1])
		self.face_color_normal = mp.array([1, 1, 1, .1])
		self.face_color_highlighted = mp.array([1, 1, 1, 1])
		self.highlight_time = 0.

		self.wire_vao = gfx.VAO()
		with self.wire_vao:
			self.wire_vao.create_vbo_attrib(0, vertices)

		for i in range(1, len(vertices)-1):
			i0, i1, i2 = 0, i, i+1
			_triplet = lambda arr: [arr[i0], arr[i1], arr[i2]]
			triangle = Triangle(self, _triplet(vertices), _triplet(texcoords), _triplet(normals), [True, i2==len(vertices)-1, i==1])
			self.triangles.append(triangle)

	def set_wire_color(self, color):
		self.wire_color = color

	def set_face_colors(self, normal_color, highlighted_color):
		self.face_color_normal = normal_color
		self.face_color_highlighted = highlighted_color

	def highlight(self, highlight_time, force=False):
		highlight_time = float(highlight_time) + HIGHLIGHT_FALLOFF_TIME
		if force:
			self.highlight_time = highlight_time
		else:
			self.highlight_time = max(self.highlight_time, highlight_time)

	def update(self, dt):
		self.highlight_time -= dt
		self.face_highlight = mp.clamp(self.highlight_time / HIGHLIGHT_FALLOFF_TIME, 0., 1.)

	def render(self):
		with self.shape.program:
			self.shape.program.set_uniform('u_faceColorNormal', self.face_color_normal)
			self.shape.program.set_uniform('u_faceColorHighlighted', self.face_color_highlighted)
			self.shape.program.set_uniform('u_faceHighlight', self.face_highlight)
			for t in self.triangles:
				t.render()

		with self.shape.wire_program:
			self.shape.wire_program.set_uniform('u_wireColor', self.wire_color)
			self.wire_vao.draw_line_loop()

	def __repr__(self):
		return "<Face %d>" % (self.index,)

class Triangle:
	def __init__(self, face, vertices, texcoords=None, normals=None, wires=None):
		if texcoords is None: texcoords = [[0, 0], [0, 1], [1, 0]]
		if normals is None: normals = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
		if wires is None: wires = [True, True, True]

		self.face = face
		self.vertices = vertices
		self.texcoords = texcoords
		self.normals = normals
		self.wires = wires
		self.normal = mp.triangle_normal(self.vertices)

		self.vao = gfx.VAO()
		with self.vao:
			self.vao.create_vbo_attrib(0, self.vertices)
			self.vao.create_vbo_attrib(1, self.texcoords)

	def render(self):
		self.vao.draw_triangles()
