import math
import time

import numpy as np
from OpenGL import GL

class Program:
	def __init__(self, vert_shader, frag_shader):
		self.id = GL.glCreateProgram()
		self.prev_program = None

		self._compile_program(vert_shader, frag_shader)

	@staticmethod
	def set_program_uniform(program_id, name, utype, *params, silent=False):
		location = GL.glGetUniformLocation(program_id, name)
		if location == -1:
			if not silent:
				raise RuntimeError("Invalid uniform \"%s\"" % (name,))
		else:
			utype(location, *params)

	def set_uniform(self, name, utype, *params, silent=False):
		self.set_program_uniform(self.id, name, utype, *params, silent=silent)

	def set_texture(self, name, texture):
		self.set_uniform(name, GL.glUniform1i, texture.number)

	def _compile_program(self, vert_shader, frag_shader):
		vs = self._compile_shader(vert_shader, GL.GL_VERTEX_SHADER)
		fs = self._compile_shader(frag_shader, GL.GL_FRAGMENT_SHADER)

		GL.glAttachShader(self.id, vs)
		GL.glAttachShader(self.id, fs)
		GL.glLinkProgram(self.id)
		infoLog = GL.glGetProgramInfoLog(self.id)
		if infoLog != '':
			raise RuntimeError("Error in program: %s" % (infoLog.decode('ascii'),))

	def _compile_shader(self, shaderSource, shaderType):
		shader = GL.glCreateShader(shaderType)
		GL.glShaderSource(shader, shaderSource)
		GL.glCompileShader(shader)
		infoLog = GL.glGetShaderInfoLog(shader)
		if infoLog != '':
			raise RuntimeError("Error in shader: %s" % (infoLog.decode('ascii'),))
		return shader

	def __enter__(self):
		self.prev_program = GL.glGetInteger(GL.GL_CURRENT_PROGRAM)
		GL.glUseProgram(self.id)

	def __exit__(self, exc_type, exc_value, traceback):
		GL.glUseProgram(self.prev_program)
		self.prev_program = None

class VAO:
	def __init__(self):
		self.id = GL.glGenVertexArrays(1)
		self.attribs = {}

	def set_vbo_as_attrib(self, index, vbo):
		GL.glEnableVertexAttribArray(index)
		with vbo:
			vbo.set_attrib_pointer(index)
		self.attribs[index] = vbo

	def draw_triangles(self, vbo_index=0):
		with self:
			GL.glDrawArrays(GL.GL_TRIANGLES, 0, np.prod(self.attribs[vbo_index].data.shape[:-1]))

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

	def set_data(self, data, hint=GL.GL_STATIC_DRAW):
		self.data = data
		GL.glBufferData(self.type, self.data, hint);

	def set_attrib_pointer(self, index):
		GL.glVertexAttribPointer(index, self.data.shape[-1], GL.GL_FLOAT, False, self.data.shape[-1]*self.data.itemsize, None)

	def __enter__(self):
		GL.glBindBuffer(self.type, self.id)

	def __exit__(self, exc_type, exc_value, traceback):
		GL.glBindBuffer(self.type, 0)

def perspective_projection_matrix(fovy, size, zrange):
	aspect = size[0] / size[1]
	zNear, zFar = zrange
	f = 1 / math.tan(fovy / 2)

	mat = np.array([[f/aspect, 0,                    0,                 0],
	                [       0, f,                    0,                 0],
	                [       0, 0,   (zFar + zNear)   / (zNear - zFar), -1],
	                [       0, 0, (2 * zFar * zNear) / (zNear - zFar),  0]])

	return mat

def scaling_matrix(s):
	return np.array([[s, 0, 0, 0], [0, s, 0, 0], [0, 0, s, 0], [0, 0, 0, 1]])

def translation_matrix(tx, ty, tz):
	return np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [tx, ty, tz, 1]])

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
		self.elapsed = 0
		self.last_update_time = self.start_time
		self.do_init(size)

	def do_init(self):
		raise NotImplementedError()

	def do_update(self, dt):
		raise NotImplementedError()

	def do_render(self):
		raise NotImplementedError()

	def update(self):
		now = time.monotonic()
		self.elapsed = now - self.start_time
		dt = now - self.last_update_time
		self.do_update(dt)
		self.last_update_time = now

	def render(self):
		self.do_render()

	def update_uniforms(self):
		program_id = GL.glGetInteger(GL.GL_CURRENT_PROGRAM)
		if program_id == 0:
			raise RuntimeError("No active program")

		Program.set_program_uniform(program_id, 'u_model',      GL.glUniformMatrix4fv, 1, GL.GL_FALSE, self.model,      silent=True)
		Program.set_program_uniform(program_id, 'u_view',       GL.glUniformMatrix4fv, 1, GL.GL_FALSE, self.view,       silent=True)
		Program.set_program_uniform(program_id, 'u_projection', GL.glUniformMatrix4fv, 1, GL.GL_FALSE, self.projection, silent=True)
		Program.set_program_uniform(program_id, 'u_time', GL.glUniform1f, self.elapsed, silent=True)