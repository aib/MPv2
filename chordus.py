class Chordus:
	def __init__(self, midi, allow_duplicates=False):
		self.midi = midi
		self.allow_duplicates = allow_duplicates

		self.recording = False
		self.record_center = None
		self.reset()

	def note_down(self, channel, note, velocity):
		self.midi.note_down(channel, note, velocity)

		if self.recording:
			if self.record_center is None:
				self.record_center = note
			else:
				delta = note - self.record_center
				if self.allow_duplicates or (delta != 0 and delta not in self.deltas):
					self.deltas.append(delta)

		else:
			for delta in self.deltas:
				hnote = note + delta
				if 0 <= hnote <= 127:
					self.midi.note_down(channel, hnote, velocity)

	def note_up(self, channel, note, velocity):
		self.midi.note_up(channel, note, velocity)

		if self.recording:
			pass
		else:
			for delta in self.deltas:
				hnote = note + delta
				if 0 <= hnote <= 127:
					self.midi.note_up(channel, note + delta, velocity)

	def reset(self):
		self.deltas = []

	def start_recording(self):
		self.reset()
		self.record_center = None
		self.recording = True

	def stop_recording(self):
		self.recording = False
