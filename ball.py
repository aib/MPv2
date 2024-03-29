import numpy as np

import gfx
import mp
import params

GRAPHICS_SCALE = 2.

BALL_VS = """
#version 130

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

in vec3 position;
in vec2 texUV;

out vec2 vf_texUV;

void main() {
	mat4 billboard_view = transpose(mat4(u_view[0], u_view[1], u_view[2], vec4(0, 0, 0, 1)));
	gl_Position = u_projection * u_view * u_model * billboard_view * vec4(position, 1);
	vf_texUV = texUV;
}
"""

BALL_FS = """
#version 130

uniform sampler2D t_ball;
uniform float u_opacity;

in vec2 vf_texUV;

out vec4 fragColor;

void main() {
	vec4 color = texture2D(t_ball, vf_texUV);
	fragColor = vec4(color.rgb, color.a * u_opacity);
}
"""

class Balls:
	def __init__(self, scene, ball_textures):
		self.scene = scene

		self.ball_textures = ball_textures
		self.balls = [Ball(self.scene, self, i) for i in range(params.BALLS.MAX)]

		self.program = gfx.Program(BALL_VS, BALL_FS)

		self._next_ball_index = 0

		self.scene.controller.controls['ball_radius'].on_change(lambda _, radius: self.scene.defer(self.set_ball_radius, radius))
		self.scene.controller.controls['ball_speed'].on_change(lambda _, speed: self.scene.defer(self.set_ball_speed, speed))
		self.scene.controller.controls['ball_count'].on_change(lambda _, count: self.scene.defer(self.set_ball_count, count))

	def enabled_balls(self):
		return [b for b in self.balls if b.enabled]

	def send_next_to(self, face):
		ball = self.balls[self._next_ball_index]
		self._next_ball_index = (self._next_ball_index + 1) % len(self.balls)

		dir_ = face.midpoint
		self._reset_ball(ball, dir=dir_)
		ball.fade_rate_after_collision = 2.
		ball.enabled = True

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

	def pre_render(self, projection, view):
		with self.program:
			self.program.set_uniform('u_view', view)
			self.program.set_uniform('u_projection', projection)

	def _reset_ball(self, ball, dir=None):
		if dir is None: dir = mp.normalize(np.random.standard_normal(3))
		ball.init(
			pos=[0, 0, 0],
			dir=dir,
			speed=self._ball_speed,
			radius=self._ball_radius,
			texture=np.random.choice(self.ball_textures)
		)

class Ball:
	VERTICES = [
		[[-1, -1, 0], [+1, -1, 0], [-1, +1, 0]],
		[[-1, +1, 0], [+1, -1, 0], [+1, +1, 0]]
	]
	TEXCOORDS = [
		[[0, 0], [1, 0], [0, 1]],
		[[0, 1], [1, 0], [1, 1]]
	]

	def __init__(self, scene, manager, index):
		self.scene = scene
		self.manager = manager
		self.index = index

		self.enabled = False
		self.fade_rate_after_collision = 0

		self.vao = gfx.VAO()
		with self.vao:
			self.vao.create_vbo_attrib(0, self.VERTICES)
			self.vao.create_vbo_attrib(1, self.TEXCOORDS)

		self.init([0, 0, 0], [0, 0, 0], 0, 0, None)

	def init(self, pos, dir, speed, radius, texture):
		self.pos = mp.array(pos)
		self.dir = mp.array(dir)
		self.speed = speed
		self.radius = radius
		self.texture = texture

		self.opacity = 1.
		self.fading = False

	def get_distance_to(self, target):
		return mp.norm(self.pos - target)

	def _update_physics(self, dt):
		collision_blacklist = []

		while dt > 0:
			col_tri, col_time, col_pos = self.scene.pick_triangle(self.pos, self.dir*self.speed, self.radius, maxtime=dt, blacklist=collision_blacklist)
			if col_tri is None:
				break

			if not self.fading:
				self.scene.ball_face_collision(self, col_tri.face, col_pos)

			collision_blacklist.append(col_tri)

			if self.fade_rate_after_collision:
				self.fading = True

			self.dir = mp.reflect(-col_tri.normal, self.dir)
			self.pos += self.dir * self.speed * col_time
			dt -= col_time

		self.pos += self.dir * self.speed * dt

	def update(self, dt):
		self._update_physics(dt)

		if self.fading:
			self.opacity -= dt * self.fade_rate_after_collision
			if self.opacity < 0:
				self.enabled = False

	def render(self):
		model = mp.translateM(self.pos) @ mp.scaleM(self.radius * GRAPHICS_SCALE)
		with self.manager.program:
			self.manager.program.set_uniform('t_ball', self.texture.number)
			self.manager.program.set_uniform('u_model', model)
			self.manager.program.set_uniform('u_opacity', self.opacity)
			self.vao.draw_triangles()

	def __repr__(self):
		return "<Ball %d>" % (self.index,)
