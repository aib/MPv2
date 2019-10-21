import numpy as np

import ball
import mp
import params

class Balls:
	def __init__(self, scene, ball_textures):
		self.scene = scene

		self.ball_textures = ball_textures
		self.balls = [ball.Ball(self.scene, i) for i in range(params.BALLS.MAX)]

		self.set_ball_speed(params.BALL_SPEED.DEFAULT)
		self.set_ball_radius(params.BALL_RADIUS.DEFAULT)
		self.set_ball_count(params.BALLS.DEFAULT)

	def enabled_balls(self):
		return [b for b in self.balls if b.enabled]

	def set_ball_count(self, count):
		for i in range(params.BALLS.MAX):
			if i >= count:
				self.balls[i].enabled = False
			elif not self.balls[i].enabled:
				self._reset_ball(self.balls[i])
				self.balls[i].enabled = True

	def set_ball_speed(self, speed):
		self._ball_speed = speed
		for b in self.enabled_balls():
			b.speed = speed

	def set_ball_radius(self, radius):
		self._ball_radius = radius
		for b in self.enabled_balls():
			b.radius = radius

	def reset_balls(self):
		for b in self.enabled_balls():
			self._reset_ball(b)

	def update(self, dt):
		for b in self.enabled_balls():
			b.update(dt)

		for b in self.enabled_balls():
			if b.get_distance_to(mp.array([0, 0, 0])) > self.scene.active_shape.radius:
				self._reset_ball(b)

	def _reset_ball(self, ball):
		ball.init(
			pos=[0, 0, 0],
			dir=mp.normalize(np.random.standard_normal(3)),
			speed=self._ball_speed,
			radius=self._ball_radius,
			texture=np.random.choice(self.ball_textures)
		)
