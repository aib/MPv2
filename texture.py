import numpy as np
from OpenGL import GL
from PIL import Image

class Texture:
	@classmethod
	def create_with_image(cls, number, image_file, **kwargs):
		tex = cls(number, **kwargs)
		with tex:
			tex.load_image(image_file)
		return tex

	def __init__(self, number, texture_type):
		self.number = number
		self.type = texture_type
		self.id = GL.glGenTextures(1)

	def load_image(self, image_file):
		raise NotImplementedError()

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
	def __init__(self, number, inverted=True):
		super().__init__(number, GL.GL_TEXTURE_CUBE_MAP)
		self.inverted = inverted

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
			def _teximage(side, arr, flipx=False):
				if flipx:
					GL.glTexImage2D(side, 0, GL.GL_RGBA, arr.shape[1], arr.shape[0], 0, informat, GL.GL_UNSIGNED_BYTE, np.flip(arr, axis=1))
				else:
					GL.glTexImage2D(side, 0, GL.GL_RGBA, arr.shape[1], arr.shape[0], 0, informat, GL.GL_UNSIGNED_BYTE, arr)

			right  = slicer(2*sidelen,   sidelen)
			left   = slicer(        0,   sidelen)
			top    = slicer(  sidelen,         0)
			bottom = slicer(  sidelen, 2*sidelen)
			front  = slicer(  sidelen,   sidelen)
			back   = slicer(3*sidelen,   sidelen)

			if self.inverted:
				_teximage(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X, left,   flipx=True)
				_teximage(GL.GL_TEXTURE_CUBE_MAP_NEGATIVE_X, right,  flipx=True)
				_teximage(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_Y, top,    flipx=True)
				_teximage(GL.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y, bottom, flipx=True)
				_teximage(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_Z, front,  flipx=True)
				_teximage(GL.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z, back,   flipx=True)
			else:
				_teximage(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X, right)
				_teximage(GL.GL_TEXTURE_CUBE_MAP_NEGATIVE_X, left)
				_teximage(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_Y, top)
				_teximage(GL.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y, bottom)
				_teximage(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_Z, front)
				_teximage(GL.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z, back)

			GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE)
			GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
			GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)

			self._set_params_and_generate_mipmap()
