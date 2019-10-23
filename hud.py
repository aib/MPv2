class Slider:
	def __init__(self, surface, bg_color, outline_color, slider_color, rect, value_getter, line_width=2, slider_width=4):
		self.surface = surface
		self.bg_color = bg_color
		self.outline_color = outline_color
		self.slider_color = slider_color
		self.x, self.y, self.width, self.height = rect
		self.value_getter = value_getter
		self.line_width = line_width
		self.slider_width = slider_width

		self.slider_pos = None

	def update(self, dt):
		val = self.value_getter()
		if val is None or val < 0. or val > 1.:
			self.slider_pos = None
		else:
			self.slider_pos = val

	def render(self):
		w, h, lw = self.width, self.height, self.line_width
		self._rect(0, 0, w, h, self.outline_color)
		self._rect(lw, lw, w - 2*lw, h - 2*lw, self.bg_color)
		if self.slider_pos is not None:
			sx = lw + (w - 2*lw - self.slider_width) * self.slider_pos
			self._rect(sx, lw, self.slider_width, h - 2*lw, self.slider_color)

	def _rect(self, x, y, w, h, color):
		self.surface.fill(color, (self.x + x, self.y + y, w, h))
