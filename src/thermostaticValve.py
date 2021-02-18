import time


"""
	Thermostatic valve
	@class
"""
class ThermostaticValve:
	week_prg_def = [None] * 7

	for i in range(7):
		week_prg_def[i] = [None] * 24
		for j in range(24):
			week_prg_def[i][j] = 21.0 if j > 5 and j < 22 else 17.0

	ids = []
	free_id = 0
	valves = []


	#constructor
	def __init__(self):
		self.id = ThermostaticValve.free_id
		print("New valve created: " + str(self.id))

		ThermostaticValve.getNewId()

		self.casual_tmp = 21.0
		self.eco_tmp = 17.0
		self.week_prg = ThermostaticValve.week_prg_def
		self.position = 1.0

		self.temperatures = [None] * 100 #list of temperature
		self.temperatures_index = 0
		self.positions = [None] * 50
		self.positions_index = 0

		self.open_window = False

		self.boost = False
		self.mode = 1

		self.falling = False
		self.recovering = False

		self.alias = ''

		ThermostaticValve.valves.append(self)

	#returns ids of all existing valves
	@staticmethod
	def getIds():
		return ThermostaticValve.ids

	#returns new id for new valve
	@staticmethod
	def getNewId():
		ThermostaticValve.ids.append(ThermostaticValve.free_id)
		ThermostaticValve.ids.sort()

		prev_id = ThermostaticValve.free_id
		for i in range(0, len(ThermostaticValve.ids)):
			if (i < ThermostaticValve.ids[i]):
				ThermostaticValve.free_id = i
				break
		if (prev_id == ThermostaticValve.free_id):
			ThermostaticValve.free_id = len(ThermostaticValve.ids)

	#returns valve id
	def getId(self):
		return self.id

	def setAlias(self, alias):
		self.alias = alias

	def getAlias(self):
		return self.alias

	#sets temperature
	def setTemperature(self, tmp):
		self.casual_tmp = tmp

	#returns set temperature
	def getTemperature(self):
		return self.casual_tmp

	#returns week program temperature at given time
	def getWeekProgramTemperature(self, day, hour):
		return self.week_prg[day][hour]

	#sets week program of valve
	def setWeekProgramTemperature(self, day, hour, tmp):
		self.week_prg[day][hour] = tmp
	#	self.week_prg = week_prg

	#sets position of valve
	def setPosition(self, position):
		self.position = position

	def getPosition(self):
		return self.position

	#sets current temperature and saves it to list for future use
	def setCurrentTemperature(self, tmp):
		self.current_temperature = tmp

		if (self.temperatures_index == 100):
			for i in range(0, len(self.temperatures)):
				if (i == 99):
					self.temperatures[i] = tmp
					break
				else:
					self.temperatures[i] = self.temperatures[i + 1]
		else:
			self.temperatures[self.temperatures_index] = tmp
			self.temperatures_index += 1

	#returns current temperature
	def getCurrentTemperature(self):
		return self.current_temperature

	#sets current position and saves it to list for future use
	def setCurrentPosition(self):
		pos = self.getPosition()

		if (self.positions_index == 50):
			for i in range(0, len(self.positions)):
				if (i == 49):
					self.positions[i] = pos
					break
				else:
					self.positions[i] = self.positions[i + 1]
		else:
			self.positions[self.positions_index] = pos
			self.positions_index += 1

	#helping function to get index of day
	@staticmethod
	def getDayIndex(day):
		return {
			'mon' : 0,
			'tue' : 1,
			'wed' : 2,
			'thu' : 3,
			'fri' : 4,
			'sat' : 5,
			'sun' : 6,
		}[day.lower()]

	#returns temperature according to selected mode
	def getDesiredTemperature(self):
		if (self.mode == 0):
			return self.week_prg[ThermostaticValve.getDayIndex(time.strftime("%a"))][int(time.strftime("%H")) - 1]
		elif (self.mode == 1):
			return self.casual_tmp
		elif (self.mode == 2):
			return self.eco_tmp

	def getMode(self):
		return self.mode

	def setMode(self, mode):
		self.mode = mode

	#returns valve object by id
	@staticmethod
	def getValve(id):
		if (isinstance(id, str) and id.isdigit()) or (isinstance(id, int)):
			for valve in ThermostaticValve.valves:
				if (int(id) == valve.getId()):
					return valve
					break

		return None

	#controls position of valve
	def controlValve(self):
		if (self.open_window):
			if(time.time() - self.open_window_time > 10*60):
				self.open_window = False
			else:
				return

		if (self.openWindowDetection()):
			self.open_window = True
			self.open_window_time = time.time()
			self.setPosition(1.0)
			return

		if (self.getBoostMode()):
			self.setPosition(5.0)
			return

		current_tmp = self.getCurrentTemperature()
		desired_tmp = self.getDesiredTemperature()
		difference_in_tmp = desired_tmp - current_tmp

		print(current_tmp)
		print(desired_tmp)
		print(difference_in_tmp)

		if ((difference_in_tmp > 0.5) or (self.recovering and difference_in_tmp > 0.1)):
			self.setPosition(5.0)

		elif (self.falling and difference_in_tmp > 0.3):
			self.setPosition(5.0)
			self.recovering = True
			self.falling = False

		else:
			self.setPosition(1.0)
			self.recovering = False
			self.falling = True

		"""elif (difference_in_tmp > 1):
			self.setPosition(4.0)
		elif (difference_in_tmp > 0.5):
			self.setPosition(3.0)
		elif (difference_in_tmp > 0):
			self.setPosition(2.0)
		else:
			self.setPosition(1.0)"""

		if (self.temperatures_index > 10):
			tmps = self.temperatures[:self.temperatures_index + 1 if self.temperatures_index != 100 else 100]
			poss = self.positions[:self.positions_index + 1 if self.positions_index != 50 else 50]

	#sets boost mode on
	def setBoostModeOn(self, t=time.time()):
		self.boost = True
		self.boost_time = t

	def setBoostModeOff(self):
		self.boost = False

	#returns True if boost mode is still on, otherwise False
	def getBoostMode(self, t=time.time()):
		if (self.boost):
			if (t - self.boost_time < 5*60):
				return True
			else:
				self.boost = False

		return False

	#detects open window by quick difference in temperature in humidity
	#TODO
	def openWindowDetection(self):
		if (self.temperatures_index == 100):
			tmps = self.temperatures[-5:]
			if (tmps[0] - tmps[4] > 1.5):
				return True

		return False

	#deletes valve from system
	@staticmethod
	def removeValve(id):
		del_valve = ThermostaticValve.getValve(id)

		if (del_valve is not None):
			ThermostaticValve.valves.remove(del_valve)
			del del_valve
			ThermostaticValve.ids.remove(int(id))
			#ThermostaticValve.getNewId()
			print("Valve " + id + " deleted")
			return True
		else:
			return False