import logging
import math
import queue

import midi
import params

def get_cc_mapping():
	return {
		7: 'volume',
		21: ('ball_count', irange(params.BALLS)),
		22: ('ball_speed', fexprange(params.BALL_SPEED)),
		23: ('ball_radius', frange(params.BALL_RADIUS)),
		24: ('shape', irange(params.SHAPE_INDEX)),
	}

def get_note_mapping():
	return {
		(9, 36): 'reset_balls',
	}

def irange(r):
	return lambda val: round(r.map01(val / 127.))

def frange(r):
	return lambda val: r.map01(val / 127.)

def fexprange(r, exp=1.):
	return lambda val: r.map01((math.e ** (val * exp / 127.) - 1.) / (math.e ** exp - 1.))

class Controller:
	def __init__(self, scene, midi):
		self.scene = scene
		self.midi = midi

		self._logger = logging.getLogger(__name__)

	def handle_event(self, event, arg):
		self._logger.debug("Event \"%s\" (arg: %s)", event, arg)

		if event == 'volume':
			self.midi.change_control(0, 7, arg)

		elif event == 'ball_count':
			self.scene.defer(self.scene.balls.set_ball_count, arg)

		elif event == 'ball_speed':
			self.scene.defer(self.scene.balls.set_ball_speed, arg)

		elif event == 'ball_radius':
			self.scene.defer(self.scene.balls.set_ball_radius, arg)

		elif event == 'shape':
			self.scene.defer(self.scene.set_shape, arg)

		elif event == 'reset_balls':
			self.scene.defer(self.scene.balls.reset_balls)

		else:
			self._logger.warning("Unrecognized event \"%s\" (arg: %s)", event, arg)

	def _handle_mapping(self, mapping, value):
		if mapping is None: return

		if isinstance(mapping, tuple):
			self.handle_event(mapping[0], mapping[1](value))
		else:
			self.handle_event(mapping, value)

	def update(self, dt):
		pass

	def note_down(self, channel, note, velocity):
		self._logger.debug("Note %d (%-3s) DOWN on channel %d with velocity %d", note, midi.get_note_name(note), channel, velocity)
		self._handle_mapping(get_note_mapping().get((channel, note), None), velocity)

	def note_up(self, channel, note, velocity):
		self._logger.debug("Note %d (%-3s)  UP  on channel %d with velocity %d", note, midi.get_note_name(note), channel, velocity)

	def note_play(self, channel, note, duration, svel, evel):
		self._logger.debug("Note %d (%-3s) PLAY on channel %d with duration %.2f (velocity %d ~ %d)", note, midi.get_note_name(note), channel, duration, svel, evel)

	def control_change(self, channel, control, value):
		self._logger.debug("CC %d = %d on channel %d", control, value, channel)

		self._handle_mapping(get_cc_mapping().get(control, None), value)

