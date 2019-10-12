import numpy as np

import mp

class SphericalCamera:
	def __init__(self, pos, speed, target, up):
		self.pos = mp.array(pos)
		self.speed = mp.array(speed)
		self.target = mp.array(target)
		self.up = mp.array(up)

	def move(self, movedir):
		self.pos += self.speed * mp.asarray(movedir)

	def get_pos(self):
		return mp.spherical_to_cartesian(self.pos)

	def get_forward(self):
		return mp.normalize(self.target - self.get_pos())

	def get_right(self):
		return mp.normalize(np.cross(self.get_forward(), self.up))

	def get_up(self):
		return mp.normalize(np.cross(self.get_right(), self.get_forward()))

	def get_view_matrix(self):
		return mp.lookatM(self.get_pos(), self.target, self.get_up())

