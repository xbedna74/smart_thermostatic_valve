import time
from utils import *


"""
	Thermostatic valve
	@class
"""
class ThermostaticValve:
	week_prg_def = [None] * 7

	for i in range(7):
		week_prg_def[i] = [None] * 24
		for j in range(24):
			week_prg_def[i][j] = 21.0 if 5 < j < 22 else 17.0

	ids = []
	free_id = 0
	valves = []

	#constructor
	def __init__(self):

		self.id = ThermostaticValve.free_id
		print("New valve created: " + str(self.id))

		ThermostaticValve.get_new_id()

		self.casual_tmp = 21.0
		self.eco_tmp = 17.0
		self.week_prg = ThermostaticValve.week_prg_def
		self.position = 1.0

		self.current_temperature = None
		self.temperatures = [None] * 100 #list of temperature
		self.temperatures_index = 0
		self.positions = [None] * 50
		self.positions_index = 0

		self.open_window = False
		self.open_window_time = None

		self.boost = False
		self.boost_time = None
		self.mode = 1

		self.falling = False
		self.recovering = False

		self.alias = ''

		ThermostaticValve.valves.append(self)

	#returns ids of all existing valves
	@staticmethod
	def get_ids():
		return ThermostaticValve.ids

	#returns new id for new valve
	@staticmethod
	def get_new_id():
		ThermostaticValve.ids.append(ThermostaticValve.free_id)
		ThermostaticValve.ids.sort()

		prev_id = ThermostaticValve.free_id
		for i in range(0, len(ThermostaticValve.ids)):
			if i < ThermostaticValve.ids[i]:
				ThermostaticValve.free_id = i
				break
		if prev_id == ThermostaticValve.free_id:
			ThermostaticValve.free_id = len(ThermostaticValve.ids)

	#returns valve id
	def get_id(self):
		return self.id

	def set_alias(self, alias):
		self.alias = alias

	def get_alias(self):
		return self.alias

	#sets temperature
	def set_temperature(self, tmp):
		self.casual_tmp = tmp

	#returns set temperature
	def get_temperature(self):
		return self.casual_tmp

	#returns week program temperature at given time
	def get_week_program_temperature(self, day, hour):
		return self.week_prg[day][hour]

	#sets week program of valve
	def set_week_program_temperature(self, day, hour, tmp):
		self.week_prg[day][hour] = tmp
	#	self.week_prg = week_prg

	#sets position of valve
	def set_position(self, position):
		self.position = position

	def get_position(self):
		return self.position

	#sets current temperature and saves it to list for future use
	def set_current_temperature(self, tmp):
		self.current_temperature = tmp

		if self.temperatures_index == 100:
			for i in range(0, len(self.temperatures)):
				if i == 99:
					self.temperatures[i] = tmp
					break
				else:
					self.temperatures[i] = self.temperatures[i + 1]
		else:
			self.temperatures[self.temperatures_index] = tmp
			self.temperatures_index += 1

	#returns current temperature
	def get_current_temperature(self):
		return self.current_temperature

	#sets current position and saves it to list for future use
	def set_current_position(self):
		pos = self.get_position()

		if self.positions_index == 50:
			for i in range(0, len(self.positions)):
				if i == 49:
					self.positions[i] = pos
					break
				else:
					self.positions[i] = self.positions[i + 1]
		else:
			self.positions[self.positions_index] = pos
			self.positions_index += 1

	#returns temperature according to selected mode
	def get_desired_temperature(self):
		if self.mode == 0:
			return self.week_prg[get_day_index(time.strftime("%a"))][int(time.strftime("%H"))]
		elif self.mode == 1:
			return self.casual_tmp
		elif self.mode == 2:
			return self.eco_tmp

	def get_mode(self):
		if self.get_boost_mode():
			return 3
		return self.mode

	def set_mode(self, mode):
		self.mode = mode

	#returns valve object by id
	@staticmethod
	def get_valve(identifier):
		if (isinstance(identifier, str) and identifier.isdigit()) or isinstance(identifier, int):
			for valve in ThermostaticValve.valves:
				if int(identifier) == valve.get_id():
					return valve

		return None

	#controls position of valve
	def control_valve(self):
		if self.open_window:
			if time.time() - self.open_window_time > 10*60:
				self.open_window = False
			else:
				return

		if self.open_window_detection():
			self.open_window = True
			self.open_window_time = time.time()
			self.set_position(1.0)
			return

		if self.get_boost_mode():
			self.set_position(5.0)
			return

		current_tmp = self.get_current_temperature()
		desired_tmp = self.get_desired_temperature()
		difference_in_tmp = desired_tmp - current_tmp

		print(current_tmp)
		print(desired_tmp)
		print(difference_in_tmp)

		if (difference_in_tmp > 0.5) or (self.recovering and difference_in_tmp > 0.1):
			self.set_position(5.0)

		elif self.falling and difference_in_tmp > 0.3:
			self.set_position(5.0)
			self.recovering = True
			self.falling = False

		else:
			self.set_position(1.0)
			self.recovering = False
			self.falling = True

		if self.temperatures_index > 100:
			tmps = self.temperatures[:self.temperatures_index + 1 if self.temperatures_index != 100 else 100]
			poss = self.positions[:self.positions_index + 1 if self.positions_index != 50 else 50]

	#sets boost mode on
	def set_boost_mode_on(self, t=time.time()):
		self.boost = True
		self.boost_time = t

	def set_boost_mode_off(self):
		self.boost = False

	#returns True if boost mode is still on, otherwise False
	def get_boost_mode(self, t=time.time()):
		if self.boost:
			if t - self.boost_time < 5*60:
				return True
			else:
				self.boost = False

		return False

	#detects open window by quick difference in temperature in humidity
	#TODO
	def open_window_detection(self):
		if self.temperatures_index == 100:
			tmps = self.temperatures[-5:]
			if tmps[0] - tmps[4] > 1.5:
				return True

		return False

	#deletes valve from system
	@staticmethod
	def remove_valve(identifier):
		del_valve = ThermostaticValve.get_valve(identifier)

		if del_valve is not None:
			ThermostaticValve.valves.remove(del_valve)
			del del_valve
			ThermostaticValve.ids.remove(int(identifier))
			#ThermostaticValve.get_new_id()
			print("Valve " + identifier + " deleted")
			return True
		else:
			return False
