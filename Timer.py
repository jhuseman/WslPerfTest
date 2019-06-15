import time

class Timer(object):
	def __init__(self):
		self.nulled = False
	def __enter__(self):
		self.start_time = time.clock()
	def __exit__(self, type, value, tb):
		self.end_time = time.clock()
	def get_delta(self):
		if self.nulled:
			return None
		return self.end_time - self.start_time
	def nullify(self):
		self.nulled = True