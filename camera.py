import numpy as np

import mp

class Camera:
	def get_pos(self):
		raise NotImplementedError()

	def get_forward(self):
		raise NotImplementedError()

	def _get_temp_up(self):
		raise NotImplementedError()

	def get_right(self):
		return mp.normalize(np.cross(self.get_forward(), self._get_temp_up()))

	def get_up(self):
		return mp.normalize(np.cross(self.get_right(), self.get_forward()))

	def get_view_matrix(self):
		return mp.lookatM(self.get_pos(), self.get_pos() + self.get_forward(), self.get_up())

class SphericalCamera(Camera):
	def __init__(self, scene, pos, speed, target, up):
		self.scene = scene
		self.pos = mp.array(pos)
		self.speed = mp.array(speed)
		self.target = mp.array(target)
		self.up = mp.array(up)

	def update(self, dt):
		if self.scene.keys['w']: self.move([ 0, -dt, 0 ])
		if self.scene.keys['a']: self.move([+dt, 0,  0 ])
		if self.scene.keys['s']: self.move([ 0, +dt, 0 ])
		if self.scene.keys['d']: self.move([-dt, 0,  0 ])
		if self.scene.keys['q']: self.move([ 0,  0, +dt])
		if self.scene.keys['e']: self.move([ 0,  0, -dt])

	def move(self, movedir):
		self.pos += self.speed * mp.asarray(movedir)

	def get_pos(self):
		return mp.spherical_to_cartesian(self.pos)

	def get_forward(self):
		return mp.normalize(self.target - self.get_pos())

	def _get_temp_up(self):
		return self.up
