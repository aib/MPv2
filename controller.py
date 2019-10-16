import logging
import queue

def get_cc_mapping():
	return {
		7: 'volume',
	}

class Controller:
	def __init__(self, scene, midi):
		self.scene = scene
		self.midi = midi

		self._logger = logging.getLogger(__name__)
		self._deferred_calls = queue.Queue()

	def handle_event(self, event, arg):
		self._logger.debug("Event \"%s\" (arg: %s)", event, arg)

		if event == 'volume':
			self.midi.change_control(0, 7, arg)

		else:
			self._logger.warn("Unrecognized event \"%s\" (arg: %s)", event, arg)

	def _handle_mapping(self, mapping, value):
		if mapping is None: return

		self.handle_event(mapping, value)

	def update(self, dt):
		while True:
			try:
				item = self._deferred_calls.get_nowait()
				item[0](*item[1], **item[2])
			except queue.Empty:
				break

	def note_down(self, channel, note, velocity):
		self._logger.debug("Note %d DOWN on channel %d with velocity %d", note, channel, velocity)

	def note_up(self, channel, note, velocity):
		self._logger.debug("Note %d  UP  on channel %d with velocity %d", note, channel, velocity)

	def note_play(self, channel, note, duration, svel, evel):
		self._logger.debug("Note %d PLAY on channel %d with duration %.2f (velocity %d ~ %d)", note, channel, duration, svel, evel)

	def control_change(self, channel, control, value):
		self._logger.debug("CC %d = %d on channel %d", control, value, channel)

		self._handle_mapping(get_cc_mapping().get(control, None), value)

	def _defer(self, func, *args, **kwargs):
		self._deferred_calls.put_nowait((func, args, kwargs))
