import mp

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

def tri(period, x):
	return abs((2/period) * ((x + period/2) % period) - 1)

def tri_wave(period, y0, y1, x):
	return mp.mix(y0, y1, tri(period, x))

class RedBlue(ColorPalette):
	def get_default_wire_color(self):
		return (1., 0., 0., 1.)

	def get_default_face_colors(self):
		return self.get_face_colors_for_note(0)

	def get_face_colors_for_note(self, note):
		return rgb_alphas(tri(12, note) * .4, 0., 1., 0., .8)
