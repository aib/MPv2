import math
import time

from OpenGL import GL

import gfx
import mp
import shape
import texture
import triangle

class Scene:
	def __init__(self, size):
		GL.glClearColor(.1, 0, .1, 1)

		self.switch_depth(False)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

		self.texture1 = texture.Texture2D.create_with_image('texture/test1.jpg')
		self.texture1_number = 0

		projection = mp.perspectiveM(math.tau/8, size[0] / size[1], .1, 100.)

		self.triangle_program = gfx.Program(triangle.TRIANGLE_VS, triangle.TRIANGLE_FS)
		with self.triangle_program:
			self.triangle_program.set_uniform('u_model', mp.identityM())
			self.triangle_program.set_uniform('u_view', mp.identityM())
			self.triangle_program.set_uniform('u_projection', projection)
			self.triangle_program.set_uniform_generic('t_face', GL.glUniform1i, self.texture1_number)

		GL.glActiveTexture(GL.GL_TEXTURE0 + self.texture1_number)
		self.texture1.activate()

		self.cam_theta = math.radians(41)
		self.cam_phi = math.radians(90 - 15)
		self.cam_r = 10

		self.shape = Hexahedron()

		now = time.monotonic()
		self.last_update_time = now

	def switch_depth(self, depth=None):
		if depth is not None:
			self.depth = depth
		else:
			self.depth = not self.depth

		if self.depth:
			GL.glEnable(GL.GL_DEPTH_TEST)
			GL.glDisable(GL.GL_BLEND)
		else:
			GL.glEnable(GL.GL_BLEND)
			GL.glDisable(GL.GL_DEPTH_TEST)

	def update(self, keys):
		now = time.monotonic()
		dt = now - self.last_update_time
		self.last_update_time = now

		if keys[0]: self.cam_phi   -= math.tau/2 * dt
		if keys[1]: self.cam_theta += math.tau/2 * dt
		if keys[2]: self.cam_phi   += math.tau/2 * dt
		if keys[3]: self.cam_theta -= math.tau/2 * dt
		if keys[4]: self.cam_r     += 2 * dt
		if keys[5]: self.cam_r     -= 2 * dt

		cam_pos = [
			self.cam_r * math.cos(self.cam_theta) * math.sin(self.cam_phi),
			self.cam_r *                            math.cos(self.cam_phi),
			self.cam_r * math.sin(self.cam_theta) * math.sin(self.cam_phi),
		]
		view = mp.lookatM(cam_pos, [0, 0, 0], [0, 1, 0])

		with self.triangle_program:
			self.triangle_program.set_uniform('u_view', view)

	def render(self):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

		with self.triangle_program:
			for t in self.shape.triangles:
				t.render()

class Hexahedron(shape.Shape):
	def __init__(self):
		super().__init__()
		self.load_file('obj/hexahedron2.obj')

	def get_wire(self, i, v, t, n):
		a2 = mp.angle_between(v[0]-v[2], v[1]-v[2])
		a0 = mp.angle_between(v[1]-v[0], v[2]-v[0])
		a1 = mp.angle_between(v[2]-v[1], v[0]-v[1])
		r45 = (math.tau/8) * 1.01
		return [1 if a0 < r45 else 0, 1 if a1 < r45 else 0, 1 if a2 < r45 else 0]
