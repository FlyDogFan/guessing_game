import pickle, os, copy
import datetime


class LeaderBoard():
	top = 10
	def __init__(self):
		self.database = []
		self.open()

	def create_entry(self, time, name, rounds):
		# 使用時間、使用者名稱，猜測次數建議一個新的entry
		timer = [int(time / 60), time % 60]
		new_time = datetime.time(hour=int(timer[0] / 60), minute=timer[0] % 60,
		                         second=timer[1])
		return {'time': new_time, 'name': name, 'rounds': rounds}
	# 提供interface 讓別人讀取database
	def get_score(self):
		return self.database

	def is_new_score(self, time):
		timer = [int(time / 60), time % 60]
		# 將秒數時間轉換為 datetime 物件
		new_time = datetime.time(hour=int(timer[0] / 60), minute=timer[0] % 60,
		                         second=timer[1]+1)
		if len(self.database) <= self.top - 1 or new_time < self.database[-1]['time']:
			return True
		return False

	'''
		針對排行榜做bubble sort
	'''
	def insert_and_sort(self, entry):
		self.database.append(entry)
		for i in range(len(self.database)):
			for j in range(len(self.database) - i - 1):
				if (self.database[j]['rounds'] > self.database[j + 1]['rounds']) \
					or (self.database[j]['rounds'] == self.database[j + 1]['rounds'] and \
						self.database[j]['time'] > self.database[j + 1]['time']):

					temp = copy.deepcopy(self.database[j])
					self.database[j] = copy.deepcopy(self.database[j + 1])
					self.database[j + 1] = temp

		self.database = self.database[:self.top]
		return self.database
	# 讀取資料庫
	def open(self):
		if os.path.exists("database.pkl"):
			self.database = pickle.load(open("database.pkl", "rb"))
	# 保存資料庫資料
	def close(self):
		pickle.dump(self.database, open("database.pkl", "wb"))
