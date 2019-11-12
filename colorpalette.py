import colorsys

import mp

class ColorPalette:
	def get_default_wire_color(self):
		return (1., 1., 1., 1.)

	def get_default_face_colors(self):
		return rgb_alphas(1., 1., 1., .1, 1.)

	def get_hud_colors(self):
		return ((1., 1., 1., 1.), (.5, .5, .5, 1.), (.25, .25, .25, 1.))

	def get_wire_color_for_note(self, note):
		return self.get_default_wire_color()

	def get_face_colors_for_note(self, note):
		return self.get_default_face_colors()

	def update(self, dt):
		pass

def hsva(h, s, v, a):
	rgb = colorsys.hsv_to_rgb(h, s, v)
	return (rgb[0], rgb[1], rgb[2], a)

def rgb_alphas(r, g, b, a1, a2):
	return ((r, g, b, a1), (r, g, b, a2))

def hsv_alphas(h, s, v, a1, a2):
	return (hsva(h, s, v, a1), hsva(h, s, v, a2))

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

class Shifting(ColorPalette):
	def __init__(self):
		self.elapsed = 0
		self.update(0)

	def update(self, dt):
		self.elapsed += dt
		self.hue = tri_wave(199, .5, .833, self.elapsed)

	def get_default_wire_color(self):
		return hsva(self.hue, 1., 1., 1.)

	def get_default_face_colors(self):
		return hsv_alphas(self.hue, 1., .5, 0., 1.)

class HueRotation(ColorPalette):
	def __init__(self):
		self.elapsed = 0

	def update(self, dt):
		self.elapsed += dt

	def get_default_wire_color(self):
		return hsva((self.elapsed / 31) % 1., 1., 1., 1.)

	def get_default_face_colors(self):
		return hsv_alphas((self.elapsed / 29) % 1., 1., .5, 0., 1.)
