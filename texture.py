import numpy as np
from OpenGL import GL
from PIL import Image

class Texture2D:
	@classmethod
	def create_with_image(cls, number, image_file):
		tex = cls(number)
		with tex:
			tex.load_image(image_file)
		return tex

	def __init__(self, number):
		self.number = number
		self.id = GL.glGenTextures(1)

	def activate(self):
		GL.glActiveTexture(GL.GL_TEXTURE0 + self.number)
		GL.glBindTexture(GL.GL_TEXTURE_2D, self.id)

	def load_image(self, image_file):
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
			GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
			GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

	def __enter__(self):
		self.activate()

	def __exit__(self, exc_type, exc_value, traceback):
		pass
