import numpy as np
from OpenGL import GL

import mp

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
		GL.glBufferData(self.type, self.data, hint);

	def set_attrib_pointer(self, index):
		GL.glVertexAttribPointer(index, self.data.shape[-1], GL.GL_FLOAT, False, self.data.shape[-1]*self.data.itemsize, None)

	def __enter__(self):
		self.activate()

	def __exit__(self, exc_type, exc_value, traceback):
		pass
