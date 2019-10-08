import pygame

import mb2gfx

SIZE = (int(1920*.8), int(1080*.8))

def main():
	pygame.init()
	pygame.display.set_caption("MusicBalls v2")
	pygame.display.set_mode(SIZE, pygame.DOUBLEBUF | pygame.OPENGL)
	scene = mb2gfx.Scene(SIZE)

	clock = pygame.time.Clock()

	running = True
	while running:
		for ev in pygame.event.get():
			if ev.type == pygame.QUIT:
				running = False

			elif ev.type == pygame.KEYDOWN:
				if ev.key == pygame.K_ESCAPE:
					running = False

				elif ev.key == pygame.K_f:
					scene.switch_depth()

		kp = pygame.key.get_pressed()
		arrows = kp[pygame.K_w], kp[pygame.K_a], kp[pygame.K_s], kp[pygame.K_d], kp[pygame.K_q], kp[pygame.K_e]

		scene.update(arrows)
		scene.render()
		pygame.display.flip()
		pygame.display.set_caption("MusicBalls v2 - %.2f FPS" % (clock.get_fps(),))
		clock.tick(120)

if __name__ == '__main__':
	main()
