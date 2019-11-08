import json
import logging
import math
import threading
import time
import queue

import chordus
import midi
import params
import scheduler

IGNORE_PLAY_CHANNELS = [9]

def _get_controls():
	return [
		Control('ball_speed',  params.BALL_SPEED,   Control.fexprange()),
		Control('ball_radius', params.BALL_RADIUS,  Control.frange),
		Control('ball_count',  params.BALLS,        Control.irange),
		Control('shape',       params.SHAPES,       Control.enumindex),
		Control('note_length', params.NOTE_LENGTHS, Control.enumindex),
		Control('channel',     params.CHANNELS,     Control.enumindex),
		Control('assignment_feedback', params.ASSIGNMENT_FEEDBACK, Control.bool),
	]

def _get_cc_mapping():
	return {
		7: 'volume',
		21: 'ball_count',
		22: 'ball_speed',
		23: 'ball_radius',
		24: 'shape',
		25: 'note_length',
		27: 'reverb',
		28: 'chorus',
		102: 'chan_next',
		103: 'chan_prev',
		112: 'prev_symmetry',
		113: 'next_symmetry',
		114: 'disable_assignment',
		115: 'enable_assignment',
		116: 'shuffle',
		117: 'chordus',
	}

def _get_note_mapping():
	return {
		(9, 36): 'reset_balls',
		(9, 37): 'shuffle_faces',
		(9, 38): 'toggle_hud',
		(9, 39): 'toggle_assignment_feedback',
	}

class Controller:
	def __init__(self, scene, midi, save_file=None, channels_file=None):
		self.scene = scene
		self.midi = midi
		self.save_file = save_file
		self.channels_file = channels_file

		self._logger = logging.getLogger(__name__)
		self.note_player = NotePlayer(self)
		self.chordus = chordus.Chordus(self.note_player, allow_duplicates=True)
		self.controls = { c.name: c for c in _get_controls() }
		self.cc_mapping = _get_cc_mapping()
		self.note_mapping = _get_note_mapping()

		self.assignment_enabled = True

		self.controls['note_length'].on_change(self._on_note_length_change)
		self.controls['channel'].on_change(self._on_channel_change)

	def _on_note_length_change(self, control, nl):
		self.note_length = params.NOTE_LENGTHS[nl]

	def _on_channel_change(self, control, cn):
		self.current_channel = params.CHANNELS[cn]

	def initialize_controls(self):
		try:
			with open(self.channels_file, 'r') as f:
				for channel in params.CHANNELS:
					name = f.readline()
					if len(name) <= 0: break
					channel['name'] = name.strip()
		except FileNotFoundError:
			pass

		for channel in params.CHANNELS:
			if channel['program'] is not None:
				self.midi.change_program(channel['number'], channel['program'])

		self.load_controls()

		for control in self.controls.values():
			control.set(control.get(), fire_onchange=True)

	def shutdown(self):
		self.save_controls()
		self.midi.all_notes_off()

	def load_controls(self):
		if self.save_file is None: return

		try:
			with open(self.save_file, 'r') as f:
				valmap = json.load(f)
		except FileNotFoundError:
			return
		except json.decoder.JSONDecodeError:
			return

		for cname, cval in valmap.items():
			if cname in self.controls:
				self.controls[cname].set(cval, fire_onchange=False)
			else:
				self._logger.warning("Saved control \"%s\" not found", cname)

	def save_controls(self):
		if self.save_file is None: return

		valmap = { c.name: c.get() for c in self.controls.values() }
		with open(self.save_file, 'w') as f:
			json.dump(valmap, f, indent='\t')
			f.write('\n') # Bug in json

	def handle_event(self, event, arg):
		self._logger.debug("Event \"%s\" (arg: %s)", event, arg)

		if event == 'reset_balls':
			self.scene.defer(self.scene.balls.reset_balls)

		elif event == 'shuffle_faces':
			self.scene.defer(self.scene.shuffle_faces)

		elif event == 'chan_prev':
			if arg > 0:
				self.controls['channel'].set((self.controls['channel'].get() - 1) % params.CHANNELS.COUNT)

		elif event == 'chan_next':
			if arg > 0:
				self.controls['channel'].set((self.controls['channel'].get() + 1) % params.CHANNELS.COUNT)

		elif event == 'toggle_hud':
			self.scene.hud.enabled = not self.scene.hud.enabled

		elif event == 'toggle_assignment_feedback':
			self.controls['assignment_feedback'].set(not self.controls['assignment_feedback'].get())

		elif event == 'volume':
			self.midi.change_control(self.current_channel['number'], 7, arg)

		elif event == 'reverb':
			self.midi.change_control(self.current_channel['number'], 91, arg)

		elif event == 'chorus':
			self.midi.change_control(self.current_channel['number'], 93, arg)

		elif event == 'prev_symmetry':
			if arg > 0:
				self.scene.defer(self.scene.set_next_symmetry, +1)

		elif event == 'next_symmetry':
			if arg > 0:
				self.scene.defer(self.scene.set_next_symmetry, -1)

		elif event == 'disable_assignment':
			if arg > 0:
				self.assignment_enabled = False

		elif event == 'enable_assignment':
			if arg > 0:
				self.assignment_enabled = True

		elif event == 'shuffle':
			if arg > 0:
				self.scene.defer(self.scene.shuffle_faces)

		elif event == 'chordus':
			if arg > 0:
				self.chordus.start_recording()
			else:
				self.chordus.stop_recording()

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

		if channel in IGNORE_PLAY_CHANNELS:
			return

		self.chordus.note_down(channel, note, velocity)

	def note_up(self, channel, note, velocity):
		self._logger.debug("Note %d (%-3s)  UP  on channel %d with velocity %d", note, midi.get_note_name(note), channel, velocity)

		if channel in IGNORE_PLAY_CHANNELS:
			return

		self.chordus.note_up(channel, note, velocity)

	def note_play(self, channel, note, duration, svel, evel):
		self._logger.debug("Note %d (%-3s) PLAY on channel %d with duration %.2f (velocity %d ~ %d)", note, midi.get_note_name(note), channel, duration, svel, evel)

		if channel in IGNORE_PLAY_CHANNELS:
			return

	def control_change(self, channel, control, value):
		self._logger.debug("CC %d = %d on channel %d", control, value, channel)
		self._handle_mapping(self.cc_mapping.get(control, None), value)

class NotePlayer:
	def __init__(self, controller):
		self.controller = controller

		self._logger = logging.getLogger(__name__)
		self._notes_down = []
		self._note_up_scheduler = scheduler.Scheduler()
		threading.Thread(target=self._note_up_scheduler.run, name="NotePlayer scheduler", daemon=True).start()

	def note_down(self, channel, note, velocity):
		now = time.monotonic()
		down_channel = self.controller.current_channel['number']
		custom_length = (self.controller.note_length == params.CUSTOM_NOTE_LENGTH)
		assignment_enabled = self.controller.assignment_enabled

		down_data = self._note_play_down(down_channel, note, velocity, assignment_enabled)
		self._notes_down.append(((channel, note), now, down_channel, down_data, custom_length, assignment_enabled))

		if not custom_length:
			self._note_up_scheduler.enter(self.controller.note_length, self.note_up, (channel, note, 0), { 'scheduled': True })

	def note_up(self, channel, note, velocity, scheduled=False):
		now = time.monotonic()

		for i, nd in enumerate(self._notes_down):
			if nd[0] == (channel, note):
				down_time, down_channel, down_data, custom_length, assignment_enabled = nd[1:]
				if not custom_length and not scheduled:
					continue

				self._notes_down.pop(i)
				self._note_play_up(down_channel, note, velocity, now - down_time, down_data, assignment_enabled)
				break

	def _note_play_down(self, channel, note, velocity, assignment_enabled):
		self._logger.debug("NotePlayer %d (%-3s) DOWN on channel %d with velocity %d", note, midi.get_note_name(note), channel, velocity)

		if assignment_enabled:
			faces = self.controller.scene.get_next_faces_and_rotate()
			if self.controller.controls['assignment_feedback'].get():
				self.controller.midi.send_note_down(channel, note, velocity)
		else:
			faces = self.controller.scene.get_next_faces()
			self.controller.midi.send_note_down(channel, note, velocity)

		for f in faces:
			f.set_wire_color(self.controller.scene.color_palette.get_wire_color_for_note(note))
			f.set_face_colors(*self.controller.scene.color_palette.get_face_colors_for_note(note))
			f.highlight(math.inf)
		return { 'faces': faces, 'svel': velocity }

	def _note_play_up(self, channel, note, velocity, duration, down_data, assignment_enabled):
		self._logger.debug("NotePlayer %d (%-3s)  UP  on channel %d after %.3f with velocity %d (down data: %s)", note, midi.get_note_name(note), channel, duration, velocity, down_data)

		if assignment_enabled:
			if self.controller.controls['assignment_feedback'].get():
				self.controller.midi.send_note_up(channel, note, velocity)
		else:
			self.controller.midi.send_note_up(channel, note, velocity)

		for f in down_data['faces']:
			if self.controller.assignment_enabled:
				self.controller.scene.set_face_mapping(f, (channel, note, duration, down_data['svel'], velocity))
			f.highlight(0., force=True)

class Control:
	def __init__(self, name, range_, mapping):
		self.name = name
		self.range = range_
		self.mapping = mapping

		self._logger = logging.getLogger(__name__)
		self.current_value = range_.DEFAULT
		self._on_change_handlers = []

	def set_with_mapping(self, val, fire_onchange=None):
		mapped = self.mapping(self.range, val)
		self.set(mapped, fire_onchange=fire_onchange)

	def set(self, val, fire_onchange=None):
		if val == self.current_value:
			if fire_onchange is True:
				self._fire_on_change()
			return

		self.current_value = val
		if fire_onchange is not False:
			self._fire_on_change()

	def get(self):
		return self.current_value

	def get_fraction(self):
		return (self.current_value - self.range.MIN) / (self.range.MAX - self.range.MIN)

	def on_change(self, f):
		self._on_change_handlers.append(f)

	def _fire_on_change(self):
		self._logger.debug("%s changed to %s", self.name, self.current_value)
		for handler in self._on_change_handlers:
			handler(self, self.current_value)

	@staticmethod
	def map01(range_, val):
		return range_.MIN + ((range_.MAX - range_.MIN) * val)

	@staticmethod
	def irange(range_, val):
		return round(Control.map01(range_, val))

	@staticmethod
	def frange(range_, val):
		return Control.map01(range_, val)

	@staticmethod
	def fexprange(exp=1.):
		return lambda range_, val: Control.map01(range_, (math.e ** (val * exp) - 1.) / (math.e ** exp - 1.))

	@staticmethod
	def enumindex(enum_, val):
		return Control.irange(enum_, val)

	@staticmethod
	def bool(bool_, val):
		return False if val < .5 else True
