import time

import mp

class Camera:
	def get_pos(self):
		raise NotImplementedError()

	def get_forward(self):
		raise NotImplementedError()

	def _get_temp_up(self):
		raise NotImplementedError()

	def get_right(self):
		return mp.normalize(mp.cross(self.get_forward(), self._get_temp_up()))

	def get_up(self):
		return mp.normalize(mp.cross(self.get_right(), self.get_forward()))

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

class WonderingSphericalCamera(Camera):
	def __init__(self, target, up, theta_eq, phi_eq, r_eq):
		self.target = mp.array(target)
		self.up = mp.array(up)
		self.theta_eq = theta_eq
		self.phi_eq = phi_eq
		self.r_eq = r_eq

		self.pos = mp.array([0, 0, 0])
		self.start_time = time.monotonic()

	def update(self, dt):
		elapsed = time.monotonic() - self.start_time
		theta = self.theta_eq(elapsed)
		phi = self.phi_eq(elapsed)
		r = self.r_eq(elapsed)
		self.pos = mp.spherical_to_cartesian([theta, phi, r])

	def get_pos(self):
		return self.pos

	def get_forward(self):
		return mp.normalize(self.target - self.get_pos())

	def _get_temp_up(self):
		return self.up
