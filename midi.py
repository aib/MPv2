import threading
import time

import rtmidi

import scheduler

class MidiHandler:
	def __init__(self, scene, inport=None, outport=None):
		self.scene = scene

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

		if outport is None:
			self.midi_out.open_virtual_port()
		else:
			for i, pname in enumerate(self.midi_out.get_ports()):
				if outport in pname:
					self.midi_out.open_port(i)
					break

		threading.Thread(target=self.note_scheduler.run, name="MidiHandler note scheduler", daemon=True).start()
		self.midi_in.set_callback(self._midi_in_cb)
		self.scene.midi_connected(self)

	def play_note(self, channel, note, duration, svel, evel):
		if (channel, note) in self.scheduled_notes:
			self.scheduled_notes[(channel, note)].cancel()

		def _note_off(channel, note, evel):
			del self.scheduled_notes[(channel, note)]
			self.midi_out.send_message([0x80 + channel, note, evel])

		self.midi_out.send_message([0x90 + channel, note, svel])
		ev = self.note_scheduler.enter(duration, _note_off, (channel, note, evel))
		self.scheduled_notes[(channel, note)] = ev

	def _midi_in_cb(self, message, user_data):
		now = time.monotonic()
		midimsg, timestamp = message
		event, channel = midimsg[0] & 0xF0, midimsg[0] & 0x0F

		if event == 0x90:
			note, velocity = midimsg[1], midimsg[2]
			self.scene.note_down(channel, note, velocity)
			self.notes[(channel, note)] = (now, velocity)

		elif event == 0x80:
			note, velocity = midimsg[1], midimsg[2]
			self.scene.note_up(channel, note, velocity)
			if (channel, note) in self.notes:
				stime, svel = self.notes[(channel, note)]
				self.scene.note_play(channel, note, now - stime, svel, velocity)
