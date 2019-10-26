import logging
import sys

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
	pygame.display.set_caption(TITLE)
	pygame.display.set_mode(SIZE, pygame.DOUBLEBUF | pygame.OPENGL)
	window_size = SIZE

	midi_handler = midi.MidiHandler(inport_name, outport_name)
	main_scene = scene.Scene(SIZE, midi_handler)
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
				main_scene.mouse_down(ev.button, (ev.pos[0] / window_size[0], ev.pos[1] / window_size[1]))

			elif ev.type == pygame.MOUSEBUTTONUP:
				main_scene.mouse_up(ev.button, (ev.pos[0] / window_size[0], ev.pos[1] / window_size[1]))

		main_scene.update()
		main_scene.render()
		pygame.display.flip()
		pygame.display.set_caption("%s - %.2f FPS" % (TITLE, clock.get_fps()))
		clock.tick(120)

	main_scene.shutdown()

if __name__ == '__main__':
	main()
