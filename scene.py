import collections
import glob
import itertools as it
import logging
import math
import queue
import random
import time

import numpy as np
from OpenGL import GL

import ball
import camera
import colorpalette
import controller
import hud
import mp
import params
import shape
import shapes
import skybox
import texture

class Scene:
	def __init__(self, size, midi):
		self.size = size
		self.keys = collections.defaultdict(lambda: False)
		self.midi = midi

		self._logger = logging.getLogger(__name__)
		self._deferred_calls = queue.Queue()
		self._next_free_texture = 1
		self.controller = controller.Controller(self, midi, 'controls.json')
		self.midi.set_controller(self.controller)
		self.color_palette = colorpalette.RedBlue()

		self.camera = camera.SphericalCamera(
			self,
			pos=[math.radians(41), math.radians(90 - 15), 10],
			speed=[math.tau/2, math.tau/2, 2],
			target=[0, 0, 0],
			up=[0, 1, 0]
		)

		GL.glClearColor(.1, 0, .1, 1)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
		GL.glEnable(GL.GL_BLEND)
		GL.glEnable(GL.GL_TEXTURE_CUBE_MAP_SEAMLESS)

		skybox_texture = None
		self.skybox = skybox.SkyBox(self, params.DEPTH.MAX / 4, skybox_texture)

		self.shapes = [shape(self) for shape in params.SHAPES]
		self.balls = ball.Balls(self, list(map(self.load_texture, glob.glob('texture/ball*.png'))))

		self.hud = hud.Hud(self, (0, 0, size[0], size[1]))

		self._symmetry_map = []
		self.controller.controls['shape'].on_change(lambda _, index: self.defer(self.set_shape, index))

		self.controller.initialize_controls()

		now = time.monotonic()
		self.last_update_time = now

	def set_shape(self, i, symmetry=None):
		self.active_shape = self.shapes[i]

		if symmetry is None:
			symmetry = len(self.active_shape.faces)

		self.active_symmetry = symmetry

		self._logger.debug("Changing shape to %s (%d)", self.active_shape.name, self.active_symmetry)

		sym_map = self.active_shape.symmetries[self.active_symmetry]
		self._symmetry_id_count = len(sym_map)
		self._symmetry_ids = { face_index: i for i, faces in enumerate(sym_map) for face_index in faces }

		if len(self._symmetry_map) < self._symmetry_id_count:
			self._symmetry_map.extend([None] * (self._symmetry_id_count - len(self._symmetry_map)))

		self.face_queue = [[self.active_shape.faces[fi] for fi in sym] for sym in sym_map]
		self._reset_faces()

	def get_next_faces_and_rotate(self):
		faces = self.face_queue.pop(0)
		self.face_queue.append(faces)
		return faces

	def shuffle_faces(self):
		active_map, inactive_map = self._symmetry_map[0:self._symmetry_id_count], self._symmetry_map[self._symmetry_id_count:]
		random.shuffle(active_map)
		self._symmetry_map = active_map + inactive_map
		self._reset_faces()

	def _reset_faces(self):
		random.shuffle(self.face_queue)
		for face in self.active_shape.faces:
			if self.get_face_mapping(face) is None:
				face.set_wire_color(self.color_palette.get_default_wire_color())
				face.set_face_colors(*self.color_palette.get_default_face_colors())
			else:
				note = self.get_face_mapping(face)[1]
				face.set_wire_color(self.color_palette.get_wire_color_for_note(note))
				face.set_face_colors(*self.color_palette.get_face_colors_for_note(note))

	def get_face_mapping(self, face):
		return self._symmetry_map[self._symmetry_ids[face.index]]

	def set_face_mapping(self, face, mapping):
		self._symmetry_map[self._symmetry_ids[face.index]] = mapping

	def update(self):
		now = time.monotonic()
		dt = now - self.last_update_time
		self.last_update_time = now

		while True:
			try:
				item = self._deferred_calls.get_nowait()
				item[0](*item[1], **item[2])
			except queue.Empty:
				break

		self.controller.update(dt)

		self.camera.update(dt)

		self.view = self.camera.get_view_matrix()
		self.projection = mp.perspectiveM(math.tau/8, self.size[0] / self.size[1], params.DEPTH.MIN, params.DEPTH.MAX)

		self.skybox.update(dt)

		self.balls.update(dt)
		self.active_shape.update(dt)

		self.hud.update(dt)

	def render(self):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT)

		self.skybox.render()

		drawables = it.chain(self.active_shape.faces, self.balls.enabled_balls())

		def _drawable_sort_key(drawable):
			if isinstance(drawable, shape.Face):
				if mp.dot(drawable.normal, drawable.midpoint - self.camera.get_pos()) <= 0:
					return -2 * params.DEPTH.MAX
				else:
					return +2 * params.DEPTH.MAX
			return drawable.get_distance_to(self.camera.get_pos())

		for drawable in sorted(drawables, key=_drawable_sort_key, reverse=True):
			drawable.render()

		self.hud.render()

	def shutdown(self):
		self.controller.shutdown()

	def key_down(self, key):
		self.keys[key] = True

	def key_up(self, key):
		self.keys[key] = False

	def mouse_down(self, button, pos):
		unp_n, unp_f = mp.unproject(pos, self.view, self.projection)
		tri, time, pos = self.pick_triangle(unp_n, unp_f - unp_n)
		if tri is not None:
			self._logger.debug("Picked face %d with button %d", tri.face.index, button)

	def mouse_up(self, button, pos):
		pass

	def ball_face_collision(self, ball, face, pos):
		mapping = self.get_face_mapping(face)
		if mapping is not None:
			self.midi.play_note(*mapping)
			face.highlight(0)

	def create_texture(self, cls=texture.Texture2D, **kwargs):
		tex = cls(self._next_free_texture, **kwargs)
		self._next_free_texture += 1
		return tex

	def load_texture(self, filename, cls=texture.Texture2D, **kwargs):
		tex = self.create_texture(cls, **kwargs)
		with tex:
			tex.load_image(filename)
		return tex

	def pick_triangle(self, start, forward, ray_radius=0, maxtime=None, blacklist=None):
		intersections = []
		for f in self.active_shape.faces:
			for t in f.triangles:
				if blacklist is not None and t in blacklist:
					continue

				behind = mp.dot(t.normal, forward) > 0
				closest = start - (-t.normal if behind else t.normal) * ray_radius

				distproj = mp.project(t.normal, closest - t.vertices[0])
				if distproj == 0:
					continue

				velproj = mp.project(t.normal, forward)
				if velproj == 0:
					continue

				intersection_time = distproj / -velproj

				if intersection_time < 0:
					continue

				if maxtime is not None and intersection_time > maxtime:
					continue

				intersection_point = closest + forward * intersection_time

				if mp.dot(intersection_point - t.vertices[0], mp.cross(t.vertices[1] - t.vertices[0], t.normal)) > 0:
					continue

				if mp.dot(intersection_point - t.vertices[1], mp.cross(t.vertices[2] - t.vertices[1], t.normal)) > 0:
					continue

				if mp.dot(intersection_point - t.vertices[2], mp.cross(t.vertices[0] - t.vertices[2], t.normal)) > 0:
					continue

				intersections.append((t, intersection_time, intersection_point))

		if len(intersections) == 0:
			return (None, None, None)

		first = sorted(intersections, key=lambda i: i[1])[0]
		return (first[0], first[1], first[2])

	def defer(self, func, *args, **kwargs):
		self._deferred_calls.put_nowait((func, args, kwargs))
