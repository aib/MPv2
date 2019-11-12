import argparse
import logging
import time
import sys

from OpenGL import GL
import sdl2

import scene
import midi

TITLE = "MPv2"
FPS_PRINT_TIME = 10

def main():
	args = argparse.ArgumentParser(description="Run " + TITLE)
	args.add_argument('-i', '--midi-input',   help="connect to specified MIDI input port")
	args.add_argument('-o', '--midi-output',  help="connect to specified MIDI output port")
	args.add_argument('-c', '--debug-camera', action='store_true', help="use a controllable camera")
	args.add_argument('-s', '--vsync',        action='store_true', help="use vsync")
	args.add_argument('-v', '--verbose',      action='store_true', help="increase verbosity")
	args.add_argument('-w', '--windowed',     action='store_true', help="run in a window")
	args.add_argument('-3', '--stereoscopy', choices=[scene.STEREOSCOPY_OFF, scene.STEREOSCOPY_ANAGLYPH], help="stereoscopy mode")
	args.add_argument('-e', '--eye-separation', type=float, help="stereoscopic eye separation")
	opts = args.parse_args(sys.argv[1:])

	if opts.verbose:
		logging.basicConfig(level=logging.DEBUG)
	else:
		logging.basicConfig(level=logging.INFO)

	logger = logging.getLogger(__name__)

	logger.info("Initializing")
	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

	dm = sdl2.SDL_DisplayMode()
	sdl2.SDL_GetDesktopDisplayMode(0, dm)
	if not opts.windowed:
		width = dm.w
		height = dm.h
	else:
		width = round(dm.w * .8)
		height = round(dm.h * .8)

	window_flags = sdl2.SDL_WINDOW_OPENGL | (sdl2.SDL_WINDOW_FULLSCREEN if not opts.windowed else 0)
	window = sdl2.SDL_CreateWindow(TITLE.encode('utf-8'), sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED, width, height, window_flags)
	context = sdl2.SDL_GL_CreateContext(window)

	fbo = create_multisampled_fbo(width, height, 0)

	if opts.vsync:
		if sdl2.SDL_GL_SetSwapInterval(-1) == -1:
			logger.warning("Adaptive vsync not available")
			sdl2.SDL_GL_SetSwapInterval(1)

	midi_handler = midi.MidiHandler(opts.midi_input, opts.midi_output)
	main_scene = scene.Scene((width, height), midi_handler, debug_camera=opts.debug_camera)

	if opts.stereoscopy is not None:
		main_scene.set_stereoscopy(opts.stereoscopy)

	if opts.eye_separation is not None:
		main_scene.stereoscopy_eye_separation = opts.eye_separation

	frames = 0
	frame_count_time = time.monotonic()

	ev = sdl2.SDL_Event()
	running = True
	while running:
		while True:
			if (sdl2.SDL_PollEvent(ev) == 0):
				break

			if ev.type == sdl2.SDL_QUIT:
				running = False

			elif ev.type == sdl2.SDL_KEYUP and ev.key.keysym.sym == sdl2.SDLK_ESCAPE:
				running = False

			elif ev.type == sdl2.SDL_KEYDOWN:
				main_scene.key_down(sdl2.SDL_GetKeyName(ev.key.keysym.sym).decode('ascii').lower())

			elif ev.type == sdl2.SDL_KEYUP:
				main_scene.key_up(sdl2.SDL_GetKeyName(ev.key.keysym.sym).decode('ascii').lower())

			elif ev.type == sdl2.SDL_MOUSEBUTTONDOWN:
				main_scene.mouse_down(ev.button.button, (ev.button.x / width, ev.button.y / height))

			elif ev.type == sdl2.SDL_MOUSEBUTTONUP:
				main_scene.mouse_up(ev.button.button, (ev.button.x / width, ev.button.y / height))

		main_scene.update()
		main_scene.render()
		blit_multisampled_fbo(width, height, fbo)
		sdl2.SDL_GL_SwapWindow(window)

		frames += 1
		now = time.monotonic()
		if now - frame_count_time > FPS_PRINT_TIME:
			fps = frames / (now - frame_count_time)
			frames = 0
			frame_count_time = now
			logger.debug("%.3f FPS", fps)

	main_scene.shutdown()

	sdl2.SDL_GL_DeleteContext(context)
	sdl2.SDL_DestroyWindow(window)
	sdl2.SDL_Quit()

def create_multisampled_fbo(width, height, msaa):
	if msaa == 0: return 0

	fbotex = GL.glGenTextures(1)
	GL.glBindTexture(GL.GL_TEXTURE_2D_MULTISAMPLE, fbotex)
	GL.glTexImage2DMultisample(GL.GL_TEXTURE_2D_MULTISAMPLE, msaa, GL.GL_RGBA8, width, height, False)

	fbo = GL.glGenFramebuffers(1)
	GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, fbo)
	GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D_MULTISAMPLE, fbotex, 0)

	return fbo

def blit_multisampled_fbo(width, height, fbo):
	if fbo == 0: return

	GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, 0)
	GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, fbo)
	GL.glDrawBuffer(GL.GL_BACK)
	GL.glBlitFramebuffer(0, 0, width, height, 0, 0, width, height, GL.GL_COLOR_BUFFER_BIT, GL.GL_NEAREST)
	GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, fbo)

if __name__ == '__main__':
	main()
