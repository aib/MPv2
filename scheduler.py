import queue
import time

class Scheduler:
	class StopItem:
		pass

	class CancelItem:
		def __init__(self, event):
			self.event = event

	def __init__(self):
		self._entry_queue = queue.Queue()
		self._queue = []

	def enterabs(self, time_, action, args=(), kwargs={}):
		event = Event(self, time_, action, args, kwargs)
		self._entry_queue.put(event)
		return event

	def enter(self, delay, action, args=(), kwargs={}):
		return self.enterabs(time.monotonic() + delay, action, args, kwargs)

	def stop(self):
		self._entry_queue.put(self.StopItem())

	def cancel(self, event):
		self._entry_queue.put(self.CancelItem(event))

	def run(self):
		while True:
			now = time.monotonic()
			if len(self._queue) == 0:
				next_event = None
			else:
				next_event = self._queue[0]

			if next_event is None:
				sleep_time = None
			else:
				if next_event.time < now:
					self._queue.remove(next_event)
					next_event.fire()
					sleep_time = 0
				else:
					sleep_time = next_event.time - now

			try:
				new_item = self._entry_queue.get(timeout=sleep_time)

				if isinstance(new_item, self.StopItem):
					break
				elif isinstance(new_item, self.CancelItem):
					try:
						self._queue.remove(new_item.event)
					except ValueError: pass
				else:
					self._queue.append(new_item)
					self._queue.sort(key=lambda e: e.time)
			except queue.Empty: pass

class Event:
	def __init__(self, scheduler, time_, action, args, kwargs):
		self.scheduler = scheduler
		self.time = time_
		self.action = action
		self.args = args
		self.kwargs = kwargs

	def fire(self):
		try:
			self.action(*self.args, **self.kwargs)
		except Exception: pass

	def cancel(self):
		self.scheduler.cancel(self)
