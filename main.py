import logging
import sys

from OpenGL import GL
import pygame

import scene
import midi

TITLE = "MPv2"
SIZE = (int(1920*.8), int(1080*.8))

def main():
	if '-v' in sys.argv:
		sys.argv.remove('-v')
		loglevel = logging.DEBUG
	else:
		loglevel = logging.INFO

	outport_name = sys.argv[1] if len(sys.argv) > 1 else None
	inport_name  = sys.argv[2] if len(sys.argv) > 2 else None

	logging.basicConfig(level=loglevel)

	pygame.init()
	width, height = SIZE

	pygame.display.set_caption(TITLE)
	pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)

	fbo = create_multisampled_fbo(width, height, 0)

	midi_handler = midi.MidiHandler(inport_name, outport_name)
	main_scene = scene.Scene((width, height), midi_handler)
	clock = pygame.time.Clock()

	running = True
	while running:
		for ev in pygame.event.get():
			if ev.type == pygame.QUIT:
				running = False

			elif ev.type == pygame.KEYUP and ev.key == pygame.K_ESCAPE:
				running = False

			elif ev.type == pygame.KEYDOWN:
				main_scene.key_down(pygame.key.name(ev.key))

			elif ev.type == pygame.KEYUP:
				main_scene.key_up(pygame.key.name(ev.key))

			elif ev.type == pygame.MOUSEBUTTONDOWN:
				main_scene.mouse_down(ev.button, (ev.pos[0] / width, ev.pos[1] / height))

			elif ev.type == pygame.MOUSEBUTTONUP:
				main_scene.mouse_up(ev.button, (ev.pos[0] / width, ev.pos[1] / height))

		main_scene.update()
		main_scene.render()
		blit_multisampled_fbo(width, height, fbo)
		pygame.display.flip()
		pygame.display.set_caption("%s - %.2f FPS" % (TITLE, clock.get_fps()))
		clock.tick(120)

	main_scene.shutdown()

def create_multisampled_fbo(width, height, msaa):
	if msaa == 0: return 0

	fbotex = GL.glGenTextures(1);
	GL.glBindTexture(GL.GL_TEXTURE_2D_MULTISAMPLE, fbotex);
	GL.glTexImage2DMultisample(GL.GL_TEXTURE_2D_MULTISAMPLE, msaa, GL.GL_RGBA8, width, height, False);

	fbo = GL.glGenFramebuffers(1);
	GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, fbo);
	GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D_MULTISAMPLE, fbotex, 0);

	return fbo

def blit_multisampled_fbo(width, height, fbo):
	if fbo == 0: return

	GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, 0);
	GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, fbo);
	GL.glDrawBuffer(GL.GL_BACK);
	GL.glBlitFramebuffer(0, 0, width, height, 0, 0, width, height, GL.GL_COLOR_BUFFER_BIT, GL.GL_NEAREST)
	GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, fbo);

if __name__ == '__main__':
	main()
