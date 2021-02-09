import PySimpleGUI as sg

from http.server import HTTPServer
import threading
import time

from thermostaticValve import *
from restApi import *

def httpHandler():
	server = ('192.168.1.210', 8080)
	httpd = HTTPServer(server, RequestHandler)

	while (1):
		httpd.handle_request()


def run():

	thread = threading.Thread(target=httpHandler, args=())
	thread.daemon = True
	thread.start()

	sg.theme('TealMono')

	first_col = [[sg.Listbox(key="valves", enable_events=True, values=([]), size=(30, 30))]]
	second_col = [  [sg.Text("Current temperature: "), sg.Text(key="cur_tmp", text="---")],
	                [sg.Text("Current desired temperature: "), sg.Text(key="des_tmp", text="---")],
	                [sg.Text("Input desired temperature: "), sg.Input(key="in_tmp")],
	                [sg.Button("Update"), sg.Text(key="time", text=time.strftime("%H:%M:%S"))] ]
	layout = [ [sg.Column(first_col), sg.VSeperator(), sg.Column(key="second_col", layout=second_col)] ]

	window = sg.Window(title='Smart thermostatic valves control', layout=layout, size=(800, 500))
	while (True):
		event, values = window.read(timeout=200)

		window["time"].update(time.strftime("%H:%M:%S"))

		new_valves = ThermostaticValve.getIds()
		old_valves = window["valves"].get_list_values()
		if (new_valves != old_valves):
			window["valves"].update(new_valves)

		if (len(window["valves"].get()) != 0):
			valve = ThermostaticValve.getValve(window["valves"].get()[0])
		else:
			valve = None

		if (valve is not None):
			current = str(valve.getCurrentTemperature())
			window["cur_tmp"].update(current)

		if (event == "Update"):
			tmp_in = window["in_tmp"].get()
			window["in_tmp"].update("")

			if (valve is not None):
				valve.setTemperature(float(tmp_in))

				window["cur_tmp"].update(str(valve.getCurrentTemperature()))
				window["des_tmp"].update(str(valve.getDesiredTemperature()))

		elif (event == sg.WIN_CLOSED):
			break
		elif (event == "valves"):
			if (valve is not None):
				window["cur_tmp"].update(str(valve.getCurrentTemperature()))
				window["des_tmp"].update(str(valve.getDesiredTemperature()))


if __name__ == "__main__":
	run()