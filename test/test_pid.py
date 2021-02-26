import time
import matplotlib.pyplot as plt
from pid import *


class WaterBoiler:
	"""
	Simple simulation of a water boiler which can heat up water
	and where the heat dissipates slowly over time
	"""

	def __init__(self):
		self.water_temp = 20

	def update(self, boiler_power, dt):
		print("Before heating: " + str(self.water_temp))
		print("Power: " + str(boiler_power))
		if boiler_power > 0:
			# boiler can only produce heat, not cold
			self.water_temp += 1 * boiler_power * dt

		# some heat dissipation
		self.water_temp -= 0.02 * dt
		print("After heating: " + str(self.water_temp))
		print('')
		return self.water_temp


if __name__ == '__main__':
	boiler = WaterBoiler()
	water_temp = 20

	pid = PID(5, 0.01, 0.1, setpoint=40, sample_time=0.2, output_limits=(0, 5))

	start_time = time.time()
	last_time = start_time

	current_time = time.time()
	dt = current_time - last_time

	power = pid(water_temp)
	water_temp = boiler.update(power, dt)

	last_time = current_time

	while time.time() - start_time < 10:
		if time.time() - last_time >= 0.2:
			current_time = time.time()
			dt = current_time - last_time
	
			power = pid(water_temp)
			water_temp = boiler.update(power, dt)
	
			#x += [current_time - start_time]
			#y += [water_temp]
			#setpoint += [pid.setpoint]
	
			#if current_time - start_time > 1:
			#	pid.setpoint = 100
	
			last_time = current_time