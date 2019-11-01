import numpy as np
from OpenGL import GL

import mp

class ShaderError(Exception):
	def __init__(self, message, infoLog):
		super().__init__("%s: %s" % (message, infoLog))

class ProgramLinkError(ShaderError):
	def __init__(self, infoLog):
		super().__init__("Error linking program", infoLog)

class ShaderCompileError(ShaderError):
	def __init__(self, name, infoLog):
		super().__init__("Error compiling %s shader" % (name,), infoLog)

class UniformNotFound(Exception):
	def __init__(self, uniform_name):
		super().__init__("Uniform \"%s\" not found" % (uniform_name,))

def get_uniform_location(program_id, name, silent=False):
	location = GL.glGetUniformLocation(program_id, name)
	if location == -1:
		if not silent:
			raise UniformNotFound(name)
	return location

def set_uniform(program_id, name, value, silent=False):
	set_uniform_by_location(get_uniform_location(program_id, name, silent=silent), value)

def set_uniform_by_location(location, value):
	value = np.asarray(value)
	if value.shape == ():
		if value.dtype.kind == 'f':
			GL.glUniform1f(location, value)
		elif value.dtype.kind == 'i':
			GL.glUniform1i(location, value)
		else:
			raise NotImplementedError("I don't know how to process the dtype %s" % (value.dtype,))
	elif value.shape == (3,):
		if value.dtype.kind == 'f':
			GL.glUniform3fv(location, 1, value)
		else:
			raise NotImplementedError("I don't know how to process the dtype %s" % (value.dtype,))
	elif value.shape == (4,):
		if value.dtype.kind == 'f':
			GL.glUniform4fv(location, 1, value)
		else:
			raise NotImplementedError("I don't know how to process the dtype %s" % (value.dtype,))
	elif value.shape == (4, 4):
		GL.glUniformMatrix4fv(location, 1, GL.GL_TRUE, value)
	elif len(value.shape) == 2 and value.shape[1] == 4:
		GL.glUniform4fv(location, value.shape[0], value)
	else:
		raise NotImplementedError("I don't know how to process the shape %s" % (value.shape,))

class Program:
	def __init__(self, vert_shader, frag_shader):
		self.id = GL.glCreateProgram()
		self._uniform_locations = {}
		self._compile_program(vert_shader, frag_shader)

	def set_uniform(self, name, value, silent=False):
		if name not in self._uniform_locations:
			self._uniform_locations[name] = get_uniform_location(self.id, name, silent=silent)

		set_uniform_by_location(self._uniform_locations[name], value)

	def activate(self):
		GL.glUseProgram(self.id)

	def _compile_program(self, vert_shader, frag_shader):
		vs = self._compile_shader(vert_shader, GL.GL_VERTEX_SHADER, "vertex")
		fs = self._compile_shader(frag_shader, GL.GL_FRAGMENT_SHADER, "fragment")

		GL.glAttachShader(self.id, vs)
		GL.glAttachShader(self.id, fs)
		GL.glLinkProgram(self.id)

		if GL.glGetProgramiv(self.id, GL.GL_LINK_STATUS) == GL.GL_FALSE:
			infoLog = GL.glGetProgramInfoLog(self.id)
			if infoLog != '': infoLog = infoLog.decode('ascii')
			raise ProgramLinkError(infoLog)

	def _compile_shader(self, shaderSource, shaderType, shaderName):
		shader = GL.glCreateShader(shaderType)
		GL.glShaderSource(shader, shaderSource)
		GL.glCompileShader(shader)

		if GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS) == GL.GL_FALSE:
			infoLog = GL.glGetShaderInfoLog(shader)
			if infoLog != '': infoLog = infoLog.decode('ascii')
			raise ShaderCompileError(shaderName, infoLog)

		return shader

	def __enter__(self):
		self.activate()

	def __exit__(self, exc_type, exc_value, traceback):
		pass

class VAO:
	def __init__(self):
		self.id = GL.glGenVertexArrays(1)
		self.attribs = {}

	def activate(self):
		GL.glBindVertexArray(self.id)

	def set_vbo_as_attrib(self, index, vbo):
		if index not in self.attribs:
			GL.glEnableVertexAttribArray(index)

		with vbo:
			vbo.set_attrib_pointer(index)

		self.attribs[index] = vbo

	def draw_triangles(self, vbo_index=0):
		with self:
			GL.glDrawArrays(GL.GL_TRIANGLES, 0, np.prod(self.attribs[vbo_index].data.shape[:-1]))

	def __enter__(self):
		self.activate()

	def __exit__(self, exc_type, exc_value, traceback):
		pass

class VBO:
	@classmethod
	def create_with_data(cls, data, buffer_type=GL.GL_ARRAY_BUFFER, hint=GL.GL_STATIC_DRAW):
		vbo = cls(buffer_type)
		with vbo:
			vbo.set_data(data, hint)
		return vbo

	def __init__(self, buffer_type=GL.GL_ARRAY_BUFFER):
		self.id = GL.glGenBuffers(1)
		self.type = buffer_type
		self.data = None

	def activate(self):
		GL.glBindBuffer(self.type, self.id)

	def set_data(self, data, hint=GL.GL_STATIC_DRAW):
		self.data = mp.asarray(data)
		GL.glBufferData(self.type, self.data, hint)

	def set_attrib_pointer(self, index):
		GL.glVertexAttribPointer(index, self.data.shape[-1], GL.GL_FLOAT, False, self.data.shape[-1]*self.data.itemsize, None)

	def __enter__(self):
		self.activate()

	def __exit__(self, exc_type, exc_value, traceback):
		pass
