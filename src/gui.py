import PySimpleGUI as sg

import json
import requests

from thermostaticValve import *

from utils import *

address = "http://192.168.1.210:8080"

def get_valve_list(ids):
	valves_list = []
	for valve in ids:
		alias = requests.get(address + "/device/radiator-valve/alias?id=" + str(valve))
		valves_list.append("ID: " + str(valve) + " (" + alias.text + ")")
	return valves_list

def run():

	sg.theme('TealMono')

	#two columns for window
	first_col = [[sg.Listbox(key="valves", enable_events=True, values=([]), size=(30, 30))]]
	second_col = [[sg.Text("Current temperature: "), sg.Text(key="cur_tmp", text="---")],
	            [sg.Text("Desired temperature: "), sg.Text(key="des_tmp", text="---")],
	            [sg.HSeparator()],
				[sg.Text("Input alias:"), sg.Input(key="in_alias", size=(20, 0))],
				[sg.Button(button_text="Set alias", key="set_alias", disabled=True)],
				[sg.HSeparator()],
				[sg.Text("Selected temperature: "), sg.Text(key="sel_tmp", text="---")],
				[sg.Text("Input temperature: "), sg.Input(key="in_tmp", size=(10, 0))],
				[sg.Button(button_text="Update temperature", key="tmp_up", disabled=True)],
				[sg.HSeparator()],
				[sg.Text("Day: "), sg.Combo(values=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], default_value="Mon", enable_events=True, key="day_change", size=(5, 0)),
				 sg.Text("Hour: "), sg.Combo(values=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], default_value=0, enable_events=True, key="hour_change", size=(5, 0))],
				[sg.Text("Selected time temperature: "), sg.Text(key="sel_time_tmp", text="---")],
				[sg.Text("Input time temperature: "), sg.Input(key="in_time_tmp", size=(10, 0))],
				[sg.Button(button_text="Update time temperature", key="time_tmp_up", disabled=True)],
				[sg.HSeparator()],
				[sg.Text("Mode: "),
				 sg.Combo(values=["Temperature", "Week program", "Boost", "Eco"], default_value="Week program", key="mode_change", enable_events=True, size=(13, 0)),
				 sg.Button(button_text="Turn off boost", key="boost_button", visible=False)],
				[sg.Text(key="time", text=time.strftime("%H:%M:%S"))]]

	layout = [ [sg.Column(first_col), sg.VSeperator(), sg.Column(key="second_col", layout=second_col)] ]

	window = sg.Window(title='Smart thermostatic valves control', layout=layout, size=(800, 500))

	while True:
		event, values = window.read(timeout=10000)

		if event == sg.WIN_CLOSED:
			break

		window["time"].update(time.strftime("%H:%M"))

		#print([x.split(' ', 2)[1] for x in window["valves"].get_list_values()])
		#print(["ID: " + str(x) + "(" + ThermostaticValve.getValve(x).getAlias() + ")" for x in ThermostaticValve.getIds()])

		valve_ids = requests.get(address + "/device/radiator-valve/ids")
		valve_ids = json.loads(valve_ids.text)

		if valve_ids != [int(x.split(' ', 2)[1]) for x in window["valves"].get_list_values()]:#changing lists on valves change
			print("list are not the same")
			print(valve_ids)
			valves_list = get_valve_list(valve_ids)

			if window["valves"].get():
				old_id = window["valves"].get()[0].split(' ', 2)[1]
				new_id = None
				for i in range(0, len(valves_list)):
					if old_id == valves_list[i].split(' ', 2)[1]:
						new_id = i
						break
				window["valves"].update(valves_list)
				window["valves"].update(set_to_index=new_id) if new_id is not None else None
			else:
				window["valves"].update(valves_list)


		#if len(window["valves"].get()) != 0:#do if there are some valves in system
		if window["valves"].get():
			v = window["valves"].get()[0].split(' ', 2)[1]
			window["set_alias"].update(disabled=False)
			window["tmp_up"].update(disabled=False)
			window["time_tmp_up"].update(disabled=False)
		else:
			v = None
			window["set_alias"].update(disabled=True)
			window["tmp_up"].update(disabled=True)
			window["time_tmp_up"].update(disabled=True)

		if event == "valves" and v is not None:
			req = requests.get(
				address + "/device/radiator-valve?id=" + v + "&day=" +
				str(get_day_index(window["day_change"].get())) + "&hour=" + str(window["hour_change"].get()))
			valve_info = json.loads(req.text)

			window["cur_tmp"].update(valve_info["current"])
			window["des_tmp"].update(valve_info["desired"])
			window["sel_time_tmp"].update(valve_info["time_tmp"])

			m = int(valve_info["mode"])
			if m == 0:
				m = "Week program"
			elif m == 1:
				m = "Temperature"
			elif m == 2:
				m = "Eco"
			elif m == 3:
				m = "Boost"
			window["mode_change"].update(m)

		elif event == "set_alias" and v is not None:#if alias is to be updated
			alias = window["in_alias"].get()
			requests.put(address + "/device/radiator-valve/alias?id=" + v + "&alias=" + alias)
			valves_list = get_valve_list(valve_ids)
			window["valves"].update(valves_list)
			window["in_alias"].update('')
			#window["valves"].update(["ID: " + str(x) + " (" + ThermostaticValve.getValve(x).getAlias() + ")" for x in
			#						 ThermostaticValve.getIds()])


		elif event == "tmp_up" and v is not None:#if desired temperature is to be updated
			tmp_in = window["in_tmp"].get()
			window["in_tmp"].update('')
			requests.put(address + "/device/radiator-valve/temperature?id=" + v + "&tmp=" + str(tmp_in))
			#valve.setTemperature(float(tmp_in))

		elif (event == "day_change" or event == "hour_change") and v is not None:#if change in week time, update value
			req = requests.get(
				address + "/device/radiator-valve/time-temperature?id=" + v + "&day=" +
				str(get_day_index(window["day_change"].get())) + "&hour=" + str(window["hour_change"].get()))

			#tmp = valve.getWeekProgramTemperature(getDayIndex(window["day_change"].get()), window["hour_change"].get())
			tmp = req.text
			window["sel_time_tmp"].update(tmp)

		elif event == "time_tmp_up" and v is not None:#if updated value of week program
			tmp = window["in_time_tmp"].get()
			window["in_time_tmp"].update('')
			requests.put(
				address + "/device/radiator-valve/time-temperature?id=" + v + "&day=" +
				str(get_day_index(window["day_change"].get())) + "&hour=" + str(window["hour_change"].get()) + "&tmp=" + str(tmp))

			#valve.setWeekProgramTemperature(getDayIndex(window["day_change"].get()), window["hour_change"].get(), tmp)

		elif event == "mode_change" and v is not None:#if mode changed
			mode = window["mode_change"].get()
			val = 0
			if (mode == "Temperature"):
				val = 1
			elif (mode == "Week program"):
				val = 0
			elif (mode == "Boost"):
				val = 3
				window["boost_button"].update(visible=True)
			elif (mode == "Eco"):
				val = 2
			requests.put(address + "/device/radiator-valve/mode-change?id=" + v + "&mode=" + str(val))

		elif event == "boost_button":#if button for turning off boost was clicked
			requests.put(address + "/device/radiator-valve/mode-change?id=" + v + "&mode=" + str(4))
			req = requests.get(address + "/device/radiator-valve/mode?id=" + v)

			m = int(req.text)
			if m == 0:
				m = "Week program"
			elif m == 1:
				m = "Temperature"
			elif m == 2:
				m = "Eco"

			window["boost_button"].update(visible=False)
			window["mode_change"].update(value=m)
			#valve.setBoostModeOff()
			#mode = valve.getMode()
			#if (mode == 0):
			#	mode = "Week program"
			#elif (mode == 1):
			#	mode = "Temperature"
			#elif (mode == 2):
			#	mode = "Eco"

		if v is not None:#if valve is selected, update temperatures
			req = requests.get(
				address + "/device/radiator-valve?id=" + v + "&day=" +
				str(get_day_index(window["day_change"].get())) + "&hour=" + str(window["hour_change"].get()))
			valve_info = json.loads(req.text)

			window["sel_tmp"].update(valve_info["temperature"])
			window["cur_tmp"].update(valve_info["current"])
			window["des_tmp"].update(valve_info["desired"])
			window["sel_time_tmp"].update(valve_info["time_tmp"])

			m = int(valve_info["mode"])
			if m == 0:
				m = "Week program"
			elif m == 1:
				m = "Temperature"
			elif m == 2:
				m = "Eco"
			elif m == 3:
				m = "Boost"
			window["mode_change"].update(m)
			#req = requests.get(address + "/device/radiator-valve/current-temperature?id=" + v)
			#window["cur_tmp"].update(req.text)
			#req = requests.get(address + "/device/radiator-valve/desired-temperature?id=" + v)
			#window["des_tmp"].update(req.text)
			#window["cur_tmp"].update(str(valve.getCurrentTemperature()))
			#window["des_tmp"].update(str(valve.getDesiredTemperature()))
			#tmp = valve.getWeekProgramTemperature(getDayIndex(window["day_change"].get()), window["hour_change"].get())
			#window["sel_time_tmp"].update(tmp)
		else:
			window["sel_tmp"].update("---")
			window["cur_tmp"].update("---")
			window["des_tmp"].update("---")
			window["sel_time_tmp"].update("---")


if __name__ == "__main__":
	run()