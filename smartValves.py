from datetime import datetime

from http.server import HTTPServer

import threading
import signal
import sys

import re

#from thermostaticValve import *
from restApi import *

lock = threading.Lock()
terminate_flag = False


def httpHandler():
	server = ('192.168.1.210', 8080)
	httpd = HTTPServer(server, RequestHandler)

	while (1):
		httpd.handle_request()



def isTemperature(s):
	return re.fullmatch('^([1][6-9]|[2][0-6])([.][0-9])?$', s)

def setTemperature(cmd):
	global devices
	if (len(cmd) == 3):
		if (isTemperature(cmd[2]) != None):
			lock.acquire()
			devices[int(cmd[1])][0] = float(cmd[2])
			lock.release()
			return
	print("Syntax of temperature command is 'temp <device_id> <temperature>'.\nTemperature only acceptes numbers from 16 to 26.9.")

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

def setWeekProgram(cmd):
	global devices
	if (len(cmd) == 3):
		if (True):
			f = open(cmd[2])
			prg = f.read().split('\n')
			for d in prg:
				d = d.replace(' ', '')

				day, day_plan = d.split(':')
				day_index = getDayIndex(day)

				day_plan_parts = day_plan.split(';')
				for p in day_plan_parts:
					time, temp = p.split(',')
					time = time.split('-')
					for i in range(int(time[0]), int(time[1]) + 1):
						devices[int(cmd[2])][1][day_index][i] = temp

			return
	print("Syntax of week program set command is 'week_prg_set <device_id> <file_with_schedule>'.")



def run():

	thread = threading.Thread(target=httpHandler, args=())
	thread.daemon = True
	thread.start()

	while(1):
		print("Thread " + str(threading.current_thread().ident) + " running")
		print("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "")

		try:
			cmd_input = input()
		except KeyboardInterrupt:
			sys.exit(0)

		command = cmd_input.split(' ')
		print("Command: " + command)

		if (command[0] == "temp"):
			pass
		elif (command[0] == "week_prg_set"):
			pass
		elif (command[0] == "boost"):
			pass



if __name__ == "__main__":
	run()