import numpy as np
from OpenGL import GL
from PIL import Image

_nextTextureUnit = 0 # race condition below, but you should not be playing with multiple threads around OpenGL

class Texture2D:
	def __init__(self):
		global _nextTextureUnit
		self.id = GL.glGenTextures(1)
		self.number = _nextTextureUnit
		_nextTextureUnit += 1
		self.prev_active_texture = None
		self.prev_binding = None

	def load(self, image_file):
		with Image.open(image_file) as img:
			arr = np.asarray(img)

		if arr.shape[2] == 3:
			informat = GL.GL_RGB
		elif arr.shape[2] == 4:
			informat = GL.GL_RGBA
		else:
			raise NotImplementedError("I don't know how to process an image of shape %s" % (arr.shape,))

		with self:
			GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, arr.shape[1], arr.shape[0], 0, informat, GL.GL_UNSIGNED_BYTE, arr)
			GL.glGenerateMipmap(GL.GL_TEXTURE_2D);

	def __enter__(self):
		self.prev_active_texture = GL.glGetInteger(GL.GL_ACTIVE_TEXTURE)
		self.prev_binding = GL.glGetInteger(GL.GL_TEXTURE_BINDING_2D)
		GL.glActiveTexture(GL.GL_TEXTURE0 + self.number)
		GL.glBindTexture(GL.GL_TEXTURE_2D, self.id)

	def __exit__(self, exc_type, exc_value, traceback):
		GL.glActiveTexture(self.prev_active_texture)
		GL.glBindTexture(GL.GL_TEXTURE_2D, self.prev_binding)
		self.prev_number = None
		self.prev_binding = None
