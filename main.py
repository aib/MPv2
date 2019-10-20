import pygame

import mb2gfx
import midi

SIZE = (int(1920*.8), int(1080*.8))

def main():
	pygame.init()
	pygame.display.set_caption("MusicBalls v2")
	pygame.display.set_mode(SIZE, pygame.DOUBLEBUF | pygame.OPENGL)
	window_size = SIZE

	midi_handler = midi.MidiHandler()
	scene = mb2gfx.Scene(SIZE, midi_handler)
	clock = pygame.time.Clock()

	running = True
	while running:
		for ev in pygame.event.get():
			if ev.type == pygame.QUIT:
				running = False

			elif ev.type == pygame.KEYUP and ev.key == pygame.K_ESCAPE:
				running = False

			elif ev.type == pygame.KEYDOWN:
				scene.key_down(pygame.key.name(ev.key))

			elif ev.type == pygame.KEYUP:
				scene.key_up(pygame.key.name(ev.key))

			elif ev.type == pygame.MOUSEBUTTONDOWN:
				scene.mouse_down(ev.button, (ev.pos[0] / window_size[0], ev.pos[1] / window_size[1]))

			elif ev.type == pygame.MOUSEBUTTONUP:
				scene.mouse_up(ev.button, (ev.pos[0] / window_size[0], ev.pos[1] / window_size[1]))

		scene.update()
		scene.render()
		pygame.display.flip()
		pygame.display.set_caption("MusicBalls v2 - %.2f FPS" % (clock.get_fps(),))
		clock.tick(120)

if __name__ == '__main__':
	main()
