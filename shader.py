from OpenGL import GL

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

def set_uniform_generic(program_id, name, utype, *uparams):
	location = GL.glGetUniformLocation(program_id, name)
	if location == -1:
		raise UniformNotFound(name)
	utype(location, *uparams)

class Program:
	def __init__(self, vert_shader, frag_shader):
		self.id = GL.glCreateProgram()
		self._compile_program(vert_shader, frag_shader)

	def set_uniform_generic(self, name, utype, *uparams):
		set_uniform_generic(self.id, name, utype, *uparams)

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
