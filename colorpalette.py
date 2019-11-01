class ColorPalette:
	def get_default_wire_color(self):
		return (1., 1., 1., 1.)

	def get_default_face_colors(self):
		return rgb_alphas(1., 1., 1., .1, 1.)

	def get_wire_color_for_note(self, note):
		return self.get_default_wire_color()

	def get_face_colors_for_note(self, note):
		return self.get_default_face_colors()

	def update(self, dt):
		pass

def rgb_alphas(r, g, b, an, ah):
	return ((r, g, b, an), (r, g, b, ah))

def tri(note):
	return abs(((note + 6) % 12) - 6) / 6.

class RedBlue(ColorPalette):
	def get_default_wire_color(self):
		return (1., 0., 0., 1.)

	def get_default_face_colors(self):
		return self.get_face_colors_for_note(0)

	def get_face_colors_for_note(self, note):
		return rgb_alphas(tri(note) * .4, 0., 1., 0., .8)
