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
import skybox
import texture

CAMERA_DISTANCE = 9.

STEREOSCOPY_OFF = 'off'
STEREOSCOPY_ANAGLYPH = 'anaglyph'

class Scene:
	def __init__(self, size, midi_handler, debug_camera=False):
		self.size = size
		self.keys = collections.defaultdict(lambda: False)
		self.midi = midi_handler

		self._logger = logging.getLogger(__name__)
		self._deferred_calls = queue.Queue()
		self._next_free_texture = 1
		self.controller = controller.Controller(self, self.midi, 'controls.json', 'channels.txt')
		self.midi.set_controller(self.controller)

		self.set_stereoscopy(STEREOSCOPY_OFF)
		self.stereoscopy_eye_separation = .5

		if debug_camera:
			self.camera = camera.SphericalCamera(
				self,
				target=[0, 0, 0],
				up=[0, 1, 0],
				pos=[0, math.tau/4, CAMERA_DISTANCE],
				speed=[math.tau/16, math.tau/16, 2.],
			)
		else:
			self.camera = camera.WanderingSphericalCamera(
				target=[0, 0, 0],
				up=[0, 1, 0],
				theta_eq=lambda elapsed: (elapsed * math.tau / 499) % math.tau,
				phi_eq=lambda elapsed: math.tau/4 - math.sin(elapsed / 131) * (math.tau/16),
				r_eq=lambda elapsed: CAMERA_DISTANCE
			)
		self.fov_y = math.tau / 8

		GL.glClearColor(.1, 0, .1, 1)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
		GL.glEnable(GL.GL_BLEND)
		GL.glEnable(GL.GL_TEXTURE_CUBE_MAP_SEAMLESS)

		GL.glEnable(GL.GL_LINE_SMOOTH)
		GL.glLineWidth(shape.WIREFRAME_LINE_WIDTH)

		try:
			skybox_texture = self.load_texture('texture/skybox.png', cls=texture.CubeMap)
		except FileNotFoundError:
			skybox_texture = None

		self.skybox = skybox.SkyBox(self, params.DEPTH.MAX / 4, skybox_texture)

		self.shapes = [shape(self) for shape in params.SHAPES]
		self.balls = ball.Balls(self, list(map(self.load_texture, glob.glob('texture/ball*.png'))))

		self.max_symmetries = max([max(shape.symmetries.keys()) for shape in self.shapes])
		self._symmetry_map = [None] * self.max_symmetries

		self.hud = hud.Hud(self, (0, 0, size[0], size[1]))

		self.controller.controls['shape'].on_change(lambda _, index: self.defer(self._set_shape, index))

		self.controller.initialize_controls()

		now = time.monotonic()
		self.last_update_time = now

	def _set_shape(self, index):
		shape = self.shapes[index]
		default_symmetry = next(iter(shape.symmetries.keys()))
		self._set_shape_and_symmetry(shape, default_symmetry)

	def _set_shape_and_symmetry(self, shape, symmetry):
		self.active_shape = shape
		self.active_symmetry = symmetry

		self._logger.debug("Changing shape to %s (%d)", self.active_shape.name, self.active_symmetry)

		sym_map = self.active_shape.symmetries[self.active_symmetry]
		self._symmetry_id_count = len(sym_map)
		self._symmetry_ids = { face_index: i for i, faces in enumerate(sym_map) for face_index in faces }

		self.face_queue = [[self.active_shape.faces[fi] for fi in sym] for sym in sym_map]
		self._reset_faces()

	def set_next_symmetry(self, delta=+1):
		symmetries = list(self.active_shape.symmetries.keys())
		cur_sym_index = symmetries.index(self.active_symmetry)
		next_symmetry = symmetries[(cur_sym_index + delta) % len(symmetries)]
		self._set_shape_and_symmetry(self.active_shape, next_symmetry)

	def get_next_faces_and_rotate(self):
		faces = self.face_queue.pop(0)
		self.face_queue.append(faces)
		self._next_faces_index = 0
		return faces

	def get_next_faces(self):
		faces = self.face_queue[self._next_faces_index]
		self._next_faces_index = (self._next_faces_index + 1) % len(self.face_queue)
		return faces

	def shuffle_faces(self):
		active_map, inactive_map = self._symmetry_map[0:self._symmetry_id_count], self._symmetry_map[self._symmetry_id_count:]
		random.shuffle(active_map)
		self._symmetry_map = active_map + inactive_map
		self._reset_faces()

	def _reset_faces(self):
		random.shuffle(self.face_queue)
		self._next_faces_index = 0
		self._update_face_colors()

	def _update_face_colors(self):
		for face in self.active_shape.faces:
			if self.get_face_mapping(face) is None:
				face.set_wire_color(self.color_palette.get_default_wire_color())
				face.set_face_colors(*self.color_palette.get_default_face_colors())
			else:
				note = self.get_face_mapping(face)[1]
				face.set_wire_color(self.color_palette.get_wire_color_for_note(note))
				face.set_face_colors(*self.color_palette.get_face_colors_for_note(note))

	def get_face_mapping(self, face):
		if face.index in self._symmetry_ids:
			symmetry_id = self._symmetry_ids[face.index]
			return self._symmetry_map[symmetry_id]

		return None

	def set_face_mapping(self, face, mapping):
		self._symmetry_map[self._symmetry_ids[face.index]] = mapping

	def set_stereoscopy(self, mode):
		if mode == STEREOSCOPY_OFF:
			self.color_palette = colorpalette.Shifting()
		elif mode == STEREOSCOPY_ANAGLYPH:
			self.color_palette = colorpalette.Anaglyph()
		else:
			raise ValueError("Invalid stereoscopy mode \"%s\"" % (mode,))

		self.stereoscopy = mode

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
		self.projection = mp.perspectiveM(self.fov_y, self.size[0] / self.size[1], params.DEPTH.MIN, params.DEPTH.MAX)

		self.skybox.update(dt)

		self.color_palette.update(dt)
		self._update_face_colors()
		self.hud.set_colors(self.color_palette.get_hud_colors())

		self.balls.update(dt)
		self.active_shape.update(dt)

		self.hud.update(dt)

		if self.keys['p']:
			self.stereoscopy_eye_separation += .05 * dt
			self._logger.debug("Eye separation set to %f", self.stereoscopy_eye_separation)
		if self.keys['o']:
			self.stereoscopy_eye_separation -= .05 * dt
			self._logger.debug("Eye separation set to %f", self.stereoscopy_eye_separation)

	def render(self):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT)

		self.skybox.pre_render(self.projection, self.view)
		self.skybox.render()

		drawables = list(it.chain(self.active_shape.faces, self.balls.enabled_balls()))

		def _drawable_sort_key(drawable):
			if isinstance(drawable, shape.Face):
				if mp.dot(drawable.normal, drawable.midpoint - self.camera.get_pos()) <= 0:
					return -2 * params.DEPTH.MAX
				else:
					return +2 * params.DEPTH.MAX
			return drawable.get_distance_to(self.camera.get_pos())

		if self.stereoscopy == STEREOSCOPY_OFF:
			self.balls.pre_render(self.projection, self.view)
			self.active_shape.pre_render(self.projection, self.view)

			GL.glColorMaski(0, 1, 1, 1, 1)

			for drawable in sorted(drawables, key=_drawable_sort_key, reverse=True):
				drawable.render()

		elif self.stereoscopy == STEREOSCOPY_ANAGLYPH:
			lview = mp.translateM([-self.stereoscopy_eye_separation / 2, 0, 0]) @ self.view
			self.balls.pre_render(self.projection, lview)
			self.active_shape.pre_render(self.projection, lview)

			GL.glColorMaski(0, 0, 1, 1, 1)

			for drawable in sorted(drawables, key=_drawable_sort_key, reverse=True):
				drawable.render()

			rview = mp.translateM([+self.stereoscopy_eye_separation / 2, 0, 0]) @ self.view

			self.balls.pre_render(self.projection, rview)
			self.active_shape.pre_render(self.projection, rview)

			GL.glColorMaski(0, 1, 0, 0, 1)

			for drawable in sorted(drawables, key=_drawable_sort_key, reverse=True):
				drawable.render()

			GL.glColorMaski(0, 1, 1, 1, 1)

		self.hud.pre_render(self.projection, self.view)
		self.hud.render()

	def shutdown(self):
		self.controller.shutdown()

	def key_down(self, key):
		if key == 'h':
			self.hud.enabled = not self.hud.enabled
		if key == 'x':
			if self.stereoscopy == STEREOSCOPY_OFF:
				self.set_stereoscopy(STEREOSCOPY_ANAGLYPH)
			elif self.stereoscopy == STEREOSCOPY_ANAGLYPH:
				self.set_stereoscopy(STEREOSCOPY_OFF)
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
		tex.load_image(filename)
		return tex

	def pick_triangle(self, start, forward, ray_radius=0, maxtime=None, blacklist=None):
		# Vectorized bit basically doing mp.intersect_plane_sphere on all triangles
		triangles = [t for f in self.active_shape.faces for t in f.triangles]
		normals = np.array([t.normal for t in triangles])
		vert0 = np.array([t.vertices[0] for t in triangles])
		velproj = np.dot(normals, forward)
		negs = np.repeat(((velproj > 0).astype(np.float32) * 2 - 1), 3).reshape(normals.shape[0], 3)
		closest = start + (normals * negs) * ray_radius
		distproj = np.sum(normals * (closest - vert0), axis=1)
		intersection_times = distproj / -velproj
		intersection_points = closest + np.outer(intersection_times, forward)

		intersections = []
		for t, intersection_time, intersection_point in zip(triangles, intersection_times, intersection_points):
			if blacklist is not None and t in blacklist:
				continue

			if math.isinf(intersection_time) or math.isnan(intersection_time) or intersection_time < 0:
				continue

			if maxtime is not None and intersection_time > maxtime:
				continue

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
