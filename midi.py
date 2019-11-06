import logging
import threading
import time

import rtmidi

import scheduler

def get_note_name(note):
	octave = note // 12 - 1
	name = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"][note % 12]
	return "%s%s" % (name, octave)

class MidiHandler:
	def __init__(self, inport=None, outport=None):
		self._logger = logging.getLogger(__name__)
		self.controller = None
		self.notes = {}
		self.scheduled_notes = {}
		self.note_scheduler = scheduler.Scheduler()

		self.midi_in = rtmidi.MidiIn()
		self.midi_out = rtmidi.MidiOut()

		if inport is None:
			self.midi_in.open_virtual_port()
		else:
			for i, pname in enumerate(self.midi_in.get_ports()):
				if inport in pname:
					self.midi_in.open_port(i)
					break

		if not self.midi_in.is_port_open():
			self._logger.warning("Could not open MIDI IN port \"%s\"", inport)

		if outport is None:
			self.midi_out.open_virtual_port()
		else:
			for i, pname in enumerate(self.midi_out.get_ports()):
				if outport in pname:
					self.midi_out.open_port(i)
					break

		if not self.midi_out.is_port_open():
			self._logger.warning("Could not open MIDI OUT port \"%s\"", outport)

		threading.Thread(target=self.note_scheduler.run, name="MidiHandler note scheduler", daemon=True).start()
		self.midi_in.set_callback(self._midi_in_cb)

	def set_controller(self, controller):
		self.controller = controller

	def play_note(self, channel, note, duration, svel, evel):
		if (channel, note) in self.scheduled_notes:
			self.scheduled_notes[(channel, note)].cancel()

		def _note_off(channel, note, evel):
			del self.scheduled_notes[(channel, note)]
			self.send_note_up(channel, note, evel)

		self.send_note_down(channel, note, svel)
		ev = self.note_scheduler.enter(duration, _note_off, (channel, note, evel))
		self.scheduled_notes[(channel, note)] = ev

	def send_note_down(self, channel, note, svel):
		self.send_message([0x90 + channel, note, svel])

	def send_note_up(self, channel, note, evel):
		self.send_message([0x80 + channel, note, evel])

	def change_control(self, channel, control, value):
		self.send_message([0xb0 + channel, control, value])

	def change_program(self, channel, program):
		self.send_message([0xc0 + channel, program])

	def all_notes_off(self):
		for c in range(16):
			self.send_message([0xb0 + c, 0x7b, 00])

	def send_message(self, msg):
		self.midi_out.send_message(msg)

	def _midi_in_cb(self, message, user_data):
		now = time.monotonic()
		midimsg, timestamp = message
		event, channel = midimsg[0] & 0xF0, midimsg[0] & 0x0F

		if event == 0x90:
			note, velocity = midimsg[1], midimsg[2]
			if self.controller is not None:
				self.controller.note_down(channel, note, velocity)
			self.notes[(channel, note)] = (now, velocity)

		elif event == 0x80:
			note, velocity = midimsg[1], midimsg[2]
			if self.controller is not None:
				self.controller.note_up(channel, note, velocity)
			if (channel, note) in self.notes:
				stime, svel = self.notes[(channel, note)]
				if self.controller is not None:
					self.controller.note_play(channel, note, now - stime, svel, velocity)

		elif event == 0xb0:
			control, value = midimsg[1], midimsg[2]
			if self.controller is not None:
				self.controller.control_change(channel, control, value)
