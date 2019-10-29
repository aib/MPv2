class ColorPalette:
	def get_default_wire_color(self):
		return (1., 1., 1., 1.)

	def get_default_face_colors(self):
		return rgb_alphas(1., 1., 1., .1, 1.)

	def get_wire_color_for_note(self, note):
		return self.get_default_wire_color()

	def get_face_colors_for_note(self, note):
		return self.get_default_face_colors()

def rgb_alphas(r, g, b, an, ah):
	return ((r, g, b, an), (r, g, b, ah))
