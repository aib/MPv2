import numpy as np
from OpenGL import GL
from PIL import Image

class Texture:
	@classmethod
	def create_with_image(cls, number, image_file):
		tex = cls(number)
		with tex:
			tex.load_image(image_file)
		return tex

	def __init__(self, number, type):
		self.number = number
		self.type = type
		self.id = GL.glGenTextures(1)

	def activate(self):
		GL.glActiveTexture(GL.GL_TEXTURE0 + self.number)
		GL.glBindTexture(self.type, self.id)

	def _read_image(self, image_file):
		with Image.open(image_file) as img:
			arr = np.asarray(img)

		if arr.shape[2] == 3:
			informat = GL.GL_RGB
		elif arr.shape[2] == 4:
			informat = GL.GL_RGBA
		else:
			raise NotImplementedError("I don't know how to process an image of shape %s" % (arr.shape,))

		return (informat, arr)

	def _set_params_and_generate_mipmap(self):
		GL.glTexParameteri(self.type, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
		GL.glTexParameteri(self.type, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
		GL.glGenerateMipmap(self.type)

	def __enter__(self):
		self.activate()

	def __exit__(self, exc_type, exc_value, traceback):
		pass

class Texture2D(Texture):
	def __init__(self, number):
		super().__init__(number, GL.GL_TEXTURE_2D)

	def load_image(self, image_file):
		informat, arr = self._read_image(image_file)

		arr = np.flip(arr, axis=0)

		with self:
			GL.glTexImage2D(self.type, 0, GL.GL_RGBA, arr.shape[1], arr.shape[0], 0, informat, GL.GL_UNSIGNED_BYTE, arr)
			self._set_params_and_generate_mipmap()

class CubeMap(Texture):
	def __init__(self, number):
		super().__init__(number, GL.GL_TEXTURE_CUBE_MAP)

	def load_image(self, image_file):
		informat, arr = self._read_image(image_file)

		sidelen = arr.shape[1] // 4

		if arr.shape[0] // 3 == sidelen: # Standard 4:3 cube map
			slicer = lambda x, y: arr[y:y+sidelen, x:x+sidelen, ...]

		elif arr.shape[0] == arr.shape[1]: # Square texture; take a centered 4x3 portion
			yoff = arr.shape[0] // 8
			slicer = lambda x, y: arr[yoff+y:yoff+y+sidelen, x:x+sidelen, ...]

		else:
			raise NotImplementedError("I don't know how to use a cube map of shape %s" % (arr.shape,))

		with self:
			def _teximage(side, arr):
				GL.glTexImage2D(side, 0, GL.GL_RGBA, arr.shape[1], arr.shape[0], 0, informat, GL.GL_UNSIGNED_BYTE, arr)

			_teximage(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X, slicer(2*sidelen,   sidelen))
			_teximage(GL.GL_TEXTURE_CUBE_MAP_NEGATIVE_X, slicer(        0,   sidelen))
			_teximage(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_Y, slicer(  sidelen,         0))
			_teximage(GL.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y, slicer(  sidelen, 2*sidelen))
			_teximage(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_Z, slicer(  sidelen,   sidelen))
			_teximage(GL.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z, slicer(3*sidelen,   sidelen))

			self._set_params_and_generate_mipmap()
