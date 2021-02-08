import requests
import time
import json

r = requests.post("http://192.168.1.210:8080/device/radiator-valve")
identifier = r.text
tmp = 20.0
prev_pos = 0.0
pos = 1.0
weather = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat=49.86&lon=18.15&exclude=minutely,daily,alerts&units=metric&appid=3988c69d554f40acae644bde23b1838a")

cur = json.loads(weather.text)["current"]["temp"]

heating = [-0.2, 0.4, 0.6, 0.9, 1.5]
colding = 0.0

nowtime = None

try:
	while (1):
		if (nowtime is None):
			print(time.strftime("%c"))
			nowtime = time.time()
			x = requests.post("http://192.168.1.210:8080/device/radiator-valve/" + identifier + "/current-temperature/" + str(tmp))
			y = requests.get("http://192.168.1.210:8080/device/radiator-valve/" + identifier + "/position")
			pos = float(y.text)
			print("Temperature: " + str(tmp))
			print("Position: " + str(pos))

			weather = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat=49.86&lon=18.15&exclude=minutely,daily,alerts&units=metric&appid=3988c69d554f40acae644bde23b1838a")
			cur = json.loads(weather.text)["current"]["temp"]
			if (float(cur) > 12):
				colding = 0.0
			elif (float(cur) < 2):
				colding = 0.9
			elif (float(cur) < 7):
				colding = 0.6
			elif (float(cur) < 12):
				colding = 0.3

			time.sleep(60 - (time.time() - nowtime) - 5)


		if (time.time() - nowtime > 60):
			print(time.strftime("%c"))
			nowtime = time.time()
			if (prev_pos == 5.0 and pos == 1.0):
				tmp += heating[int(prev_pos) - 1] - colding
			else:
				tmp += heating[int(pos) - 1] - colding
			x = requests.post("http://192.168.1.210:8080/device/radiator-valve/" + identifier + "/current-temperature/" + str(tmp))
			y = requests.get("http://192.168.1.210:8080/device/radiator-valve/" + identifier + "/position")
			print(y.text)
			prev_pos = pos
			pos = float(y.text)
			print("Temperature: " + str(tmp))
			print("Position: " + str(pos))
			print("Colding: " + str(colding))
	
			weather = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat=49.86&lon=18.15&exclude=minutely,daily,alerts&units=metric&appid=3988c69d554f40acae644bde23b1838a")
			cur = json.loads(weather.text)["current"]["temp"]
			print("Outside temperature: " + str(cur))
			if (float(cur) > 12):
				colding = 0.0
			elif (float(cur) < 2):
				colding = 0.9
			elif (float(cur) < 7):
				colding = 0.6
			elif (float(cur) < 12):
				colding = 0.3

			time.sleep(60 - (time.time() - nowtime) - 5)


except KeyboardInterrupt:
	requests.delete("http://192.168.1.210:8080/device/radiator-valve/" + identifier)
	exit(0)