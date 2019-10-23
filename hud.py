import gfx

import numpy as np
import pygame

HUD_VS = """
#version 130

in vec2 position;
in vec2 texUV;

out vec2 vf_texUV;

void main() {
	gl_Position = vec4(2*position.x - 1, -(2*position.y - 1), 0, 1);
	vf_texUV = texUV;
}
"""

HUD_FS = """
#version 130

uniform sampler2D t_hud;

in vec2 vf_texUV;

out vec4 fragColor;

void main() {
	fragColor = texture2D(t_hud, vf_texUV);
}
"""

class Hud:
	def __init__(self, scene, rect):
		self.scene = scene
		self.rect = rect

		surface_size = (2048, 2048)

		self.program = gfx.Program(HUD_VS, HUD_FS)
		self.surface = pygame.Surface(surface_size, flags=pygame.SRCALPHA, depth=32)
		self.hudtex = self.scene.create_texture()

		self.vao = gfx.VAO()
		vert, texc = self._get_shape(self.scene.size, self.rect)
		self.vertices_vbo = gfx.VBO.create_with_data(vert)
		self.texcoords_vbo = gfx.VBO.create_with_data(texc)

		with self.vao:
			self.vao.set_vbo_as_attrib(0, self.vertices_vbo)
			self.vao.set_vbo_as_attrib(1, self.texcoords_vbo)

		with self.program:
			self.program.set_uniform('t_hud', self.hudtex.number)

		self.elements = []

	def _get_shape(self, scene_size, rect):
		xmin = rect[0] / scene_size[0]
		ymin = rect[1] / scene_size[1]
		xmax = (rect[0] + rect[2]) / scene_size[0]
		ymax = (rect[1] + rect[3]) / scene_size[1]
		tw = rect[2] / self.surface.get_width()
		th = rect[3] / self.surface.get_height()

		return ([
			[[xmin, ymin], [xmax, ymin], [xmin, ymax]],
			[[xmin, ymax], [xmax, ymin], [xmax, ymax]]
		], [
			[[0,  0], [tw,  0], [ 0, th]],
			[[0, th], [tw,  0], [tw, th]]
		])

	def update(self, dt):
		for e in self.elements:
			e.update(dt)

	def render(self):
		for e in self.elements:
			e.render()

		with self.hudtex:
			arr = np.flip(np.frombuffer(self.surface.get_view().raw, dtype=np.uint8).reshape(self.surface.get_width(), self.surface.get_height(), 4), axis=0)
			self.hudtex.load_array(arr, bgr=True)

		with self.program:
			self.vao.draw_triangles()

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
