import time

from OpenGL import GL

class Scene:
	def __init__(self, size):
		GL.glClearColor(.1, 0, .1, 1)

		now = time.monotonic()
		self.last_update_time = now

	def update(self):
		now = time.monotonic()
		dt = now - self.last_update_time
		self.last_update_time = now

	def render(self):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT)
