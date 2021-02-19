import PySimpleGUI as sg

from http.server import HTTPServer
import threading
import time

from thermostaticValve import *
from restApi import *

#function for http handler thread
def httpHandler():
	server = ('192.168.1.210', 8080)
	httpd = HTTPServer(server, RequestHandler)

	while (1):
		httpd.handle_request()


def run():

	thread = threading.Thread(target=httpHandler, args=())#start http server
	thread.daemon = True
	thread.start()

	sg.theme('TealMono')

	#two columns for window
	first_col = [[sg.Listbox(key="valves", enable_events=True, values=([]), size=(30, 30))]]
	second_col = [[sg.Text("Input alias:"), sg.Input(key="in_alias", size=(20, 0))],
				[sg.Button(button_text="Set alias", key="set_alias")],
				[sg.HSeparator()],
				[sg.Text("Current temperature: "), sg.Text(key="cur_tmp", text="---")],
				[sg.Text("Current desired temperature: "), sg.Text(key="des_tmp", text="---")],
				[sg.Text("Input desired temperature: "), sg.Input(key="in_tmp", size=(10, 0))],
				[sg.Button(button_text="Update temperature", key="temp_up")],
				[sg.HSeparator()],
				[sg.Text("Day: "), sg.Combo(values=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], default_value="Mon", enable_events=True, key="day_change", size=(5, 0)),
				 sg.Text("Hour: "), sg.Combo(values=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], default_value=0, enable_events=True, key="hour_change", size=(5, 0))],
				[sg.Text("Input time temperature: "), sg.Input(key="in_hour_tmp", size=(10, 0))],
				[sg.Button(button_text="Update time temperature", key="time_temp_up")],
				[sg.HSeparator()],
				[sg.Text("Mode: "),
				 sg.Combo(values=["Temperature", "Week program", "Boost", "Eco"], default_value="Week program", key="mode_change", enable_events=True, size=(13, 0)),
				 sg.Button(button_text="Turn off boost", key="boost_button", visible=False)],
				[sg.Text(key="time", text=time.strftime("%H:%M:%S"))]]

	layout = [ [sg.Column(first_col), sg.VSeperator(), sg.Column(key="second_col", layout=second_col)] ]

	window = sg.Window(title='Smart thermostatic valves control', layout=layout, size=(800, 500))

	while (True):
		event, values = window.read(timeout=200)

		if (event == sg.WIN_CLOSED):
			break

		window["time"].update(time.strftime("%H:%M:%S"))

		#print([x.split(' ', 2)[1] for x in window["valves"].get_list_values()])
		#print(["ID: " + str(x) + "(" + ThermostaticValve.getValve(x).getAlias() + ")" for x in ThermostaticValve.getIds()])

		if (ThermostaticValve.getIds() != [int(x.split(' ', 2)[1]) for x in window["valves"].get_list_values()]):#changing lists on valves change
			print("list are not the same")
			print(ThermostaticValve.getIds())
			window["valves"].update(["ID: " + str(x) + " (" + ThermostaticValve.getValve(x).getAlias() + ")" for x in ThermostaticValve.getIds()])

		if (len(window["valves"].get()) != 0):#do if there are some valves in system
			valve = ThermostaticValve.getValve(window["valves"].get()[0].split(' ', 2)[1])
			window["set_alias"].update(disabled=False)
			window["temp_up"].update(disabled=False)
			window["time_temp_up"].update(disabled=False)
		else:
			valve = None
			window["set_alias"].update(disabled=True)
			window["temp_up"].update(disabled=True)
			window["time_temp_up"].update(disabled=True)

		if (event == "set_alias"):#if alias is to be updated
			alias = window["in_alias"].get()
			valve.setAlias(alias)
			window["valves"].update(["ID: " + str(x) + " (" + ThermostaticValve.getValve(x).getAlias() + ")" for x in
									 ThermostaticValve.getIds()])

		elif (event == "temp_up"):#if desired temperature is to be updated
			tmp_in = window["in_tmp"].get()
			window["in_tmp"].update("")
			valve.setTemperature(float(tmp_in))

		elif (event == "day_change" or event == "hour_change") and (valve is not None):#if change in week time, update value
			tmp = valve.getWeekProgramTemperature(ThermostaticValve.getDayIndex(window["day_change"].get()), window["hour_change"].get())
			window["in_hour_tmp"].update(tmp)

		elif (event == "time_temp_up"):#if updated value of week program
			tmp = window["in_hour_tmp"].get()
			valve.setWeekProgramTemperature(ThermostaticValve.getDayIndex(window["day_change"].get()), window["hour_change"].get(), tmp)

		elif (event == "mode_change" and valve is not None):#if mode changed
			val = window["mode_change"].get()
			if (val == "Temperature"):
				valve.setMode(1)
			elif (val == "Week program"):
				valve.setMode(0)
			elif (val == "Boost"):
				valve.setBoostModeOn()
				window["boost_button"].update(visible=True)
			elif (val == "Eco"):
				valve.setMode(2)

		elif (event == "boost_button"):#if button for turning off boost was clicked
			valve.setBoostModeOff()
			mode = valve.getMode()
			if (mode == 0):
				mode = "Week program"
			elif (mode == 1):
				mode = "Temperature"
			elif (mode == 2):
				mode = "Eco"
			window["boost_button"].update(visible=False)
			window["mode_change"].update(value=mode)

		if (valve is not None):#if valve is selected, update temperatures
			window["cur_tmp"].update(str(valve.getCurrentTemperature()))
			window["des_tmp"].update(str(valve.getDesiredTemperature()))
			tmp = valve.getWeekProgramTemperature(ThermostaticValve.getDayIndex(window["day_change"].get()), window["hour_change"].get())
			#window["in_hour_tmp"].update(tmp)