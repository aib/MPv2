import math

import numpy as np
import pygame
import pygame.freetype

import gfx
import midi
import mp

HUD_VS = """
#version 130

in vec2 position;
in vec2 texUV;

out vec2 vf_texUV;

void main() {
	gl_Position = vec4(2*position.x - 1, -(2*position.y - 1), 0, 1);
	vf_texUV = vec2(texUV.x, 1 - texUV.y);
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

		self.enabled = True
		self.size = (rect[2], rect[3])

		self.program = gfx.Program(HUD_VS, HUD_FS)
		self.surface_buffer = bytearray(self.size[0] * self.size[1] * 4)
		self.surface = pygame.image.frombuffer(self.surface_buffer, self.size, 'RGBA')
		self.hudtex = self.scene.create_texture()
		self.hudtex.load_array(np.zeros((self.size[1], self.size[0], 4), dtype=np.uint8))

		self.vao = gfx.VAO()
		vert, texc = self._get_shape(self.scene.size, self.rect)
		with self.vao:
			self.vao.create_vbo_attrib(0, vert)
			self.vao.create_vbo_attrib(1, texc)

		with self.program:
			self.program.set_uniform('t_hud', self.hudtex.number)

		pygame.freetype.init()
		self.font = pygame.freetype.Font('font/Roboto-Regular.ttf')
		self.music_font = pygame.freetype.Font('font/NotoMusic-Regular.ttf')
		self.symbols_font = pygame.freetype.Font('font/NotoSansSymbols2-Regular.ttf')
		self.bright_color = (0, .75, .75, 1.)
		self.dim_color = (0, .5, .5, 1.)
		self.bg_color = (0, .25, .25, 1.)

		self.elements = [
			Channel(self, self._get_rect(.02, -.048, .2, .022)),
			NoteLength(self, self._get_rect(.25, -.07, .2, .05)),
			AssignmentStatus(self, self._get_rect(.45, -.05, .045, .035)),
			DynamicText(self, self._get_rect(.4, -.09, .2, .02), lambda: "%s (%d)" % (self.scene.active_shape.name, self.scene.active_symmetry)),
			FaceMapping(self, self._get_rect(.5, -.035, .49, .015)),
		]

		def _fit_sliders_with_labels(fit_rect, label_valgetters):
			elements = 3
			vspacing = 2
			height = (fit_rect[3] - ((elements-1) * vspacing)) // elements

			texts = []
			y = fit_rect[1]
			for label_valgetter in label_valgetters:
				r = (fit_rect[0], y+2, fit_rect[2] / 2, height-2)
				texts.append(Text(self, r, label_valgetter[0]))
				y += height + vspacing

			max_width = max([t.get_rect()[2] for t in texts])

			slider_x = max_width + 6

			sliders = []
			y = fit_rect[1]
			for label_valgetter in label_valgetters:
				r = (fit_rect[0] + slider_x, y, fit_rect[2] - slider_x, height)
				sliders.append(Slider(self, r, label_valgetter[1]))
				y += height + vspacing

			for t in texts:
				self.elements.append(t)
			for s in sliders:
				self.elements.append(s)

		_fit_sliders_with_labels(self._get_rect(.02, .84, .22, .075), [
			("Sphere Count:",  lambda: self.scene.controller.controls['ball_count'].get_fraction()),
			("Sphere Speed:",  lambda: self.scene.controller.controls['ball_speed'].get_fraction()),
			("Sphere Radius:", lambda: self.scene.controller.controls['ball_radius'].get_fraction()),
		])

		self.active_rect = self._find_bounding_int_rect([e.rect for e in self.elements])

	def _get_rect(self, x, y, w, h):
		if x < 0: x = 1 + x
		if y < 0: y = 1 + y
		return (x * self.rect[2], y * self.rect[3], w * self.rect[2], h * self.rect[3])

	def _get_shape(self, scene_size, rect):
		xmin = rect[0] / scene_size[0]
		ymin = rect[1] / scene_size[1]
		xmax = (rect[0] + rect[2]) / scene_size[0]
		ymax = (rect[1] + rect[3]) / scene_size[1]
		tw = rect[2] / self.size[0]
		th = rect[3] / self.size[1]

		return ([
			[[xmin, ymin], [xmax, ymin], [xmin, ymax]],
			[[xmin, ymax], [xmax, ymin], [xmax, ymax]]
		], [
			[[0,  0], [tw,  0], [ 0, th]],
			[[0, th], [tw,  0], [tw, th]]
		])

	def _find_bounding_int_rect(self, rects):
		xmin, ymin, xmax, ymax = None, None, None, None
		for rect in rects:
			xmin = mp.augmin(xmin, rect[0])
			ymin = mp.augmin(ymin, rect[1])
			xmax = mp.augmax(xmax, rect[0]+rect[2])
			ymax = mp.augmax(ymax, rect[1]+rect[3])
		xmin, ymin = math.floor(xmin), math.floor(ymin)
		xmax, ymax = math.ceil(xmax), math.ceil(ymax)
		return (xmin, ymin, xmax-xmin, ymax-ymin)

	def update(self, dt):
		for e in self.elements:
			e.update(dt)

	def pre_render(self, projection, view):
		pass

	def render(self):
		if not self.enabled: return

		self.surface.fill(pygame.Color(0, 0, 0, 0), self.active_rect)

		for e in self.elements:
			e.render()

		arr = np.frombuffer(self.surface_buffer, dtype=np.uint8).reshape(self.size[1], self.size[0], 4)
		self.hudtex.load_subarray(arr, self.active_rect[0], self.active_rect[1], self.active_rect[2], self.active_rect[3])

		with self.program:
			self.vao.draw_triangles()

class HudElement:
	def __init__(self, hud, rect):
		self.hud = hud
		self.rect = rect

	def update(self, dt):
		pass

	def render(self):
		self.draw_rect(0, 0, self.rect[2], self.rect[3], (1., 0, 1., 1.))

	def draw_rect(self, x, y, w, h, color=None):
		if color is None: color = self.hud.bg_color
		self.hud.surface.fill(self._pygame_color(color), (self.rect[0] + x, self.rect[1] + y, w, h))

	def get_text(self, text, x=0, y=0, font=None, color=None, halign='left', valign='top'):
		if font is None: font = self.hud.font
		if color is None: color = self.hud.bright_color

		surf, rect = font.render(text, size=self.rect[3], fgcolor=self._pygame_color(color))

		if halign == 'right':
			posx = self.rect[0] + self.rect[2] - rect[2]
		elif halign == 'center' or halign == 'middle':
			posx = self.rect[0] + (self.rect[2] - rect[2]) / 2
		else:
			posx = self.rect[0]

		if valign == 'bottom':
			posy = self.rect[1] + self.rect[3] - rect[3]
		elif valign == 'center' or valign == 'middle':
			posy = self.rect[1] + (self.rect[3] - rect[3]) / 2
		else:
			posy = self.rect[1]

		return surf, (posx + x, posy + y, rect[2], rect[3])

	def draw_text(self, *args, **kwargs):
		surf, rect = self.get_text(*args, **kwargs)
		self.hud.surface.blit(surf, (rect[0], rect[1]))

	def _pygame_color(self, color):
		return pygame.Color(round(color[0] * 255), round(color[1] * 255), round(color[2] * 255), round(color[3] * 255))

class Slider(HudElement):
	def __init__(self, hud, rect, value_getter, line_width=2, slider_width=4):
		super().__init__(hud, rect)
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
		self.draw_rect(0, 0, w, h, self.hud.dim_color)
		self.draw_rect(lw, lw, w - 2*lw, h - 2*lw, self.hud.bg_color)
		if self.slider_pos is not None:
			sx = lw + (w - 2*lw - self.slider_width) * self.slider_pos
			self.draw_rect(sx, lw, self.slider_width, h - 2*lw, self.hud.bright_color)

class Text(HudElement):
	def __init__(self, hud, rect, text, halign='left', valign='top'):
		super().__init__(hud, rect)
		self.text = text
		self.halign = halign
		self.valign = valign

	def get_rect(self):
		return self.get_text(self.text, halign=self.halign, valign=self.valign)[1]

	def render(self):
		self.draw_text(self.text, halign=self.halign, valign=self.valign)

class DynamicText(Text):
	def __init__(self, hud, rect, text_getter, halign='center', valign='center'):
		super().__init__(hud, rect, '', halign, valign)
		self.text_getter = text_getter

	def update(self, dt):
		self.text = self.text_getter()

class Channel(HudElement):
	def render(self):
		self.draw_text(self.hud.scene.controller.current_channel['name'])

class NoteLength(HudElement):
	SYMBOLS = ['𝅘𝅥𝅰', '𝅘𝅥𝅯', '𝅘𝅥𝅮', '𝅘𝅥', '𝅗𝅥', '𝅝', '𝅄']

	def update(self, dt):
		self.length_index = self.hud.scene.controller.controls['note_length'].get()

	def render(self):
		xoff = 0
		for i, symbol in enumerate(self.SYMBOLS):
			color = self.hud.bright_color if i == self.length_index else self.hud.bg_color
			self.draw_text(symbol, color=color, font=self.hud.music_font, x=xoff, valign='bottom')
			xoff += self.rect[2] / len(self.SYMBOLS)

class AssignmentStatus(HudElement):
	def update(self, dt):
		self.feedback_enabled = self.hud.scene.controller.get_feedback_enabled()
		self.assignment_enabled = self.hud.scene.controller.assignment_enabled

	def render(self):
		self.draw_text('◀', color=self.hud.bright_color if self.feedback_enabled else self.hud.bg_color, font=self.hud.symbols_font, valign='center')
		xoff = self.rect[2] / 2
		self.draw_text('▶', color=self.hud.bright_color if self.assignment_enabled else self.hud.bg_color, font=self.hud.symbols_font, x=xoff, valign='center')

class FaceMapping(HudElement):
	def __init__(self, hud, rect):
		super().__init__(hud, rect)
		self.max_notes = self.hud.scene.max_symmetries

	def update(self, dt):
		mappings = [self.hud.scene.get_face_mapping(face[0]) for face in reversed(self.hud.scene.face_queue)]
		self.names = ["%d·%s" % (mapping[0] + 1, midi.get_note_name(mapping[1]).replace('♯', '#')) if mapping is not None else "·" for mapping in mappings]

	def render(self):
		xoff = 0
		for name in self.names:
			self.draw_text(name, x=xoff, valign='center')
			xoff += self.rect[2] / self.max_notes
