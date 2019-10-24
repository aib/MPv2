import logging
import math
import queue

import midi
import params

def _get_controls():
	return [
		Control('volume',      params.VOLUME,      Control.irange()),
		Control('ball_speed',  params.BALL_SPEED,  Control.fexprange()),
		Control('ball_radius', params.BALL_RADIUS, Control.frange()),
		Control('ball_count',  params.BALLS,       Control.irange()),
		Control('shape',       params.SHAPES,      Control.enumindex()),
	]

def _get_cc_mapping():
	return {
		7: 'volume',
		21: 'ball_count',
		22: 'ball_speed',
		23: 'ball_radius',
		24: 'shape',
	}

def _get_note_mapping():
	return {
		(9, 36): 'reset_balls',
		(9, 37): 'reset_faces',
	}

class Controller:
	def __init__(self, scene, midi):
		self.scene = scene
		self.midi = midi

		self._logger = logging.getLogger(__name__)
		self.controls = { c.name: c for c in _get_controls() }
		self.cc_mapping = _get_cc_mapping()
		self.note_mapping = _get_note_mapping()

		self.controls['volume'].on_change(lambda _, vol: self.midi.change_control(0, 7, vol))

	def load_controls(self):
		for control in self.controls.values():
			control.set(control.get(), True)

	def handle_event(self, event, arg):
		self._logger.debug("Event \"%s\" (arg: %s)", event, arg)

		if event == 'reset_balls':
			self.scene.defer(self.scene.balls.reset_balls)

		elif event == 'reset_faces':
			self.scene.defer(self.scene.reset_faces)

		else:
			self._logger.warning("Unrecognized event \"%s\" (arg: %s)", event, arg)

	def _handle_mapping(self, mapping, value):
		if mapping is None: return

		if mapping in self.controls:
			self.controls[mapping].set_with_mapping(value / 127)
		else:
			self.handle_event(mapping, value)

	def update(self, dt):
		pass

	def note_down(self, channel, note, velocity):
		self._logger.debug("Note %d (%-3s) DOWN on channel %d with velocity %d", note, midi.get_note_name(note), channel, velocity)
		self._handle_mapping(self.note_mapping.get((channel, note), None), velocity)

	def note_up(self, channel, note, velocity):
		self._logger.debug("Note %d (%-3s)  UP  on channel %d with velocity %d", note, midi.get_note_name(note), channel, velocity)

	def note_play(self, channel, note, duration, svel, evel):
		self._logger.debug("Note %d (%-3s) PLAY on channel %d with duration %.2f (velocity %d ~ %d)", note, midi.get_note_name(note), channel, duration, svel, evel)

		faces = self.scene.get_next_faces_and_rotate()
		for f in faces:
			self.scene.face_mapping[f.index] = (channel, note, duration, svel, evel)

	def control_change(self, channel, control, value):
		self._logger.debug("CC %d = %d on channel %d", control, value, channel)
		self._handle_mapping(self.cc_mapping.get(control, None), value)

class Control:
	def __init__(self, name, range_, mapping):
		self.name = name
		self.range = range_
		self.mapping = mapping

		self._logger = logging.getLogger(__name__)
		self.current_value = range_.DEFAULT
		self._on_change = None

	def set_with_mapping(self, val, force_onchange=False):
		mapped = self.mapping(self.range, val)
		self.set(mapped, force_onchange=force_onchange)

	def set(self, val, force_onchange=False):
		if val == self.current_value and not force_onchange:
			return

		self.current_value = val
		self._fire_on_change()

	def get(self):
		return self.current_value

	def get_fraction(self):
		return (self.current_value - self.range.MIN) / (self.range.MAX - self.range.MIN)

	def on_change(self, f):
		self._on_change = f

	def _fire_on_change(self):
		self._logger.debug("%s changed to %s", self.name, self.current_value)
		if self._on_change is not None:
			self._on_change(self, self.current_value)

	@staticmethod
	def map01(range_, val):
		return range_.MIN + ((range_.MAX - range_.MIN) * val)

	@staticmethod
	def irange():
		return lambda range_, val: round(Control.map01(range_, val))

	@staticmethod
	def frange():
		return lambda range_, val: Control.map01(range_, val)

	@staticmethod
	def fexprange(exp=1.):
		return lambda range_, val: Control.map01(range_, (math.e ** (val * exp) - 1.) / (math.e ** exp - 1.))

	@staticmethod
	def enumindex():
		return lambda enum_, val: round(Control.map01(enum_, val))
