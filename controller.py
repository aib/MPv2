import logging
import queue

class Controller:
	def __init__(self, scene, midi):
		self.scene = scene
		self.midi = midi

		self._logger = logging.getLogger(__name__)
		self._deferred_calls = queue.Queue()

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

	def _defer(self, func, *args, **kwargs):
		self._deferred_calls.put_nowait((func, args, kwargs))
