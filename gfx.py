import math
import time

import numpy as np
from OpenGL import GL
from OpenGL.GL import shaders

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

	return GL.shaders.compileProgram(vs, fs)

def get_perspective_projection(size, zrange):
	fovy = math.tau / 4
	aspect = size[0] / size[1]
	zNear, zFar = zrange
	f = 1 / math.tan(fovy / 2)

	mat = np.array([[f/aspect, 0,                    0,                 0],
	                [       0, f,                    0,                 0],
	                [       0, 0,   (zFar + zNear)   / (zNear - zFar), -1],
	                [       0, 0, (2 * zFar * zNear) / (zNear - zFar),  0]])

	return mat

class Scene:
	def __init__(self, size):
		GL.glClearColor(0, 0, 0, 1)
		self.model = np.eye(4)
		self.view = np.eye(4)
		self.projection = np.eye(4)
		self.start_time = time.monotonic()

	def set_uniforms(self, now):
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
			GL.glUniform1f(ul, now)
