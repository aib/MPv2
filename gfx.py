import math
import time

import numpy as np
from OpenGL import GL

class VAO:
	def __init__(self):
		self.id = GL.glGenVertexArrays(1)
		self.attribs = {}

	def set_vbo_as_attrib(self, index, vbo):
		GL.glEnableVertexAttribArray(index)
		with vbo:
			vbo.set_attrib_pointer(index)
		self.attribs[index] = vbo

	def __enter__(self):
		GL.glBindVertexArray(self.id)

	def __exit__(self, exc_type, exc_value, traceback):
		GL.glBindVertexArray(0)

class VBO:
	@classmethod
	def create(cls, data, hint=GL.GL_STATIC_DRAW):
		vbo = cls()
		with vbo:
			vbo.set_data(data, hint)
		return vbo

	def __init__(self):
		self.id = GL.glGenBuffers(1)
		self.type = GL.GL_ARRAY_BUFFER
		self.query_type = GL.GL_ARRAY_BUFFER_BINDING
		self.data = None
		self.prev_binding = None

	def set_data(self, data, hint=GL.GL_STATIC_DRAW):
		self.data = data
		GL.glBufferData(self.type, self.data, GL.GL_STATIC_DRAW);

	def set_attrib_pointer(self, index):
		GL.glVertexAttribPointer(index, self.data.shape[-1], GL.GL_FLOAT, False, self.data.shape[-1]*self.data.itemsize, None)

	def __enter__(self):
		self.prev_binding = GL.glGetInteger(self.query_type)
		GL.glBindBuffer(self.type, self.id)

	def __exit__(self, exc_type, exc_value, traceback):
		GL.glBindBuffer(self.type, self.prev_binding)
		self.prev_binding = None

def create_program(vertfile, fragfile):
	def _compile_shader(shaderSource, shaderType):
		shader = GL.glCreateShader(shaderType)
		GL.glShaderSource(shader, shaderSource)
		GL.glCompileShader(shader)
		infoLog = GL.glGetShaderInfoLog(shader)
		if infoLog != '':
			print(infoLog.decode('ascii'))
		return shader

	with open(vertfile, 'r') as f:
		vs = _compile_shader(f.read(), GL.GL_VERTEX_SHADER)

	with open(fragfile, 'r') as f:
		fs = _compile_shader(f.read(), GL.GL_FRAGMENT_SHADER)

	program = GL.glCreateProgram()
	GL.glAttachShader(program, vs)
	GL.glAttachShader(program, fs)
	GL.glLinkProgram(program)
	infoLog = GL.glGetProgramInfoLog(program)
	if infoLog != '':
		print(infoLog.decode('ascii'))

	return program

def get_perspective_projection(fovy, size, zrange):
	aspect = size[0] / size[1]
	zNear, zFar = zrange
	f = 1 / math.tan(fovy / 2)

	mat = np.array([[f/aspect, 0,                    0,                 0],
	                [       0, f,                    0,                 0],
	                [       0, 0,   (zFar + zNear)   / (zNear - zFar), -1],
	                [       0, 0, (2 * zFar * zNear) / (zNear - zFar),  0]])

	return mat

# https://en.wikipedia.org/wiki/Euler%E2%80%93Rodrigues_formula
def rotation_matrix(axis, theta):
	axis = np.asarray(axis)
	axis = axis / math.sqrt(np.dot(axis, axis))
	a = math.cos(theta / 2)
	b, c, d = -axis * math.sin(theta / 2)
	aa, bb, cc, dd = a * a, b * b, c * c, d * d
	bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
	return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac), 0],
	                 [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab), 0],
	                 [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc, 0],
	                 [0, 0, 0, 1]])

class Scene:
	def __init__(self, size):
		GL.glClearColor(0, 0, 0, 1)
		self.model = np.eye(4)
		self.view = np.eye(4)
		self.projection = np.eye(4)
		self.start_time = time.monotonic()
		self.last_render_time = self.start_time
		self.do_init(size)

	def do_init(self):
		raise NotImplementedError()

	def do_render(self, elapsed, dt):
		raise NotImplementedError()

	def render(self):
		now = time.monotonic()
		self.do_render(now - self.start_time, now - self.last_render_time)
		self.last_render_time = now

	def set_uniforms(self, elapsed):
		ul = GL.glGetUniformLocation(self.program, 'u_model')
		if ul != -1:
			GL.glUniformMatrix4fv(ul, 1, GL.GL_FALSE, self.model)

		ul = GL.glGetUniformLocation(self.program, 'u_view')
		if ul != -1:
			GL.glUniformMatrix4fv(ul, 1, GL.GL_FALSE, self.view)

		ul = GL.glGetUniformLocation(self.program, 'u_projection')
		if ul != -1:
			GL.glUniformMatrix4fv(ul, 1, GL.GL_FALSE, self.projection)

		ul = GL.glGetUniformLocation(self.program, 'u_time')
		if ul != -1:
			GL.glUniform1f(ul, elapsed)
