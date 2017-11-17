from threading import Thread
from time import sleep

class TimerThread(Thread):
	callback = None
	timer = 0
	flag = True

	def __init__(self,callback):
		super(TimerThread, self).__init__()
		self.callback = callback
		print("Start thread")

	def run(self):
		self.timer = 0
		# 方一個flag 讓timer 暫停
		while self.flag:
			sleep(1)
			self.timer += 1
			self.callback(self.timer)

	def start(self):
		super(TimerThread, self).start()
		self.flag = True
		self.timer = 0

	def stop_thread(self):
		print("Stop here")
		self.restart()
		self.flag = False
		self.timer = 0

	def restart(self):
		print("Restart")
		self.timer = 0

	def reset_time(self):
		self.timer = 0