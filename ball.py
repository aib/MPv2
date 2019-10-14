import numpy as np

import gfx
import mp

BALL_VS = """
#version 130

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

in vec3 position;
in vec2 texUV;

out vec2 vf_texUV;

void main() {
	gl_Position = u_projection * u_view * u_model * vec4(position, 1);
	vf_texUV = texUV;
}
"""

BALL_FS = """
#version 130

in vec2 vf_texUV;

out vec4 fragColor;

void main() {
	fragColor = vec4(1, 1, 1, 1);
}
"""

class Ball:
	VERTICES = [
		[[-1, -1, 0], [+1, -1, 0], [-1, +1, 0]],
		[[-1, +1, 0], [+1, -1, 0], [+1, +1, 0]]
	]
	TEXCOORDS = [
		[[0, 0], [1, 0], [0, 1]],
		[[0, 1], [1, 0], [1, 1]]
	]

	def __init__(self, scene, pos, vel):
		self.scene = scene
		self.pos = mp.array(pos)
		self.vel = mp.array(vel)

		self.program = gfx.Program(BALL_VS, BALL_FS)

		self.vao = gfx.VAO()
		self.vertices_vbo = gfx.VBO.create_with_data(self.VERTICES)
		self.texcoords_vbo = gfx.VBO.create_with_data(self.TEXCOORDS)

		with self.vao:
			self.vao.set_vbo_as_attrib(0, self.vertices_vbo)
			self.vao.set_vbo_as_attrib(1, self.texcoords_vbo)

	def get_distance_to(self, target):
		return np.linalg.norm(self.pos - target)

	def _update_physics(self, dt):
		class Collision:
			def __init__(self, triangle, time_position):
				self.triangle = triangle
				self.time = time_position[0]
				self.position = time_position[1]

		all_triangles = [t for face in self.scene.get_all_faces() for t in face.triangles]
		collision_blacklist = []

		while dt > 0:
			triangles = filter(lambda t: t not in collision_blacklist, all_triangles)
			intersections = map(lambda t: Collision(t, mp.intersect_plane_sphere(t.vertices, self.pos, self.vel, 0)), triangles)
			intersections_now = filter(lambda c: np.isfinite(c.time) and c.time > 0 and c.time <= dt, intersections)
			collisions = filter(lambda c: mp.triangle_contains_point(c.triangle.vertices, c.position), intersections_now)
			collisions = list(collisions)

			if len(collisions) == 0:
				break

			first_collision = sorted(collisions, key=lambda c: c.time)[0]
			collision_blacklist.append(first_collision.triangle)

			self.vel = mp.reflect(mp.triangle_normal(first_collision.triangle.vertices), self.vel)
			self.pos += self.vel * first_collision.time
			dt -= first_collision.time

		self.pos += self.vel * dt

	def update(self, dt):
		self._update_physics(dt)

		# Rotate so basis matches that of the eye
		billboard_rot = mp.from3vecM(
			self.scene.camera.get_right(),
			self.scene.camera.get_up(),
			self.scene.camera.get_forward()
		)

		model = billboard_rot @ mp.translateM(self.pos)
		with self.program:
			self.program.set_uniform('u_model', model)
			self.program.set_uniform('u_view', self.scene.view)
			self.program.set_uniform('u_projection', self.scene.projection)

	def render(self):
		with self.program:
			self.vao.draw_triangles()
