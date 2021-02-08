from http.server import BaseHTTPRequestHandler

from thermostaticValve import *

class RequestHandler(BaseHTTPRequestHandler):
	def _send_response(self, payload, code):
		payload = str(payload)
		self.protocol_version = "HTTP/1.1"
		self.send_response(code)
		if (len(payload) > 0):
			self.send_header("Content-type", "text/plain")
			self.send_header("Content-Length", len(payload))
		self.end_headers()
		if (len(payload) > 0):
			self.wfile.write(bytes(payload, "ascii"))

	def do_GET(self):

		print(self.path)

		path_parts = self.path.split('/')
		path_parts = path_parts[1:]
		if (path_parts[0] == "device"):
			if (path_parts[1] == "radiator-valve"):
				this_valve = ThermostaticValve.getValve(path_parts[2])
				if (this_valve is not None):
					if (path_parts[3] == "position"):
						this_valve.controlValve()
						this_valve.setCurrentPosition()
						self._send_response(this_valve.getPosition(), 200)
				else:
					self._send_response('', 404)


	def do_POST(self):

		print(self.path)

		path_parts = self.path.split('/')
		path_parts = path_parts[1:]
		if (path_parts[0] == "device"):
			if (path_parts[1] == "radiator-valve"):
				if (len(path_parts) == 2):
					new_valve = ThermostaticValve()
					print("New valve registered: " + str(new_valve.getId()))
					self._send_response(str(new_valve.getId()), 201)

				elif (path_parts[2].isdigit() and path_parts[3] == "current-temperature"):#add control if temperature is float (fifth part(forth index))
					this_valve = ThermostaticValve.getValve(path_parts[2])

					if (len(path_parts) < 5):
						self._send_response('', 204)#no content
					elif (this_valve is not None):
						print("Valves " + str(path_parts[2]) + " temperature is " + str(path_parts[4]))
						this_valve.setCurrentTemperature(float(path_parts[4]))
						self._send_response('', 200)
					else:
						self._send_response('', 404)#id not found


	def do_PUT(self):
		self.do_POST()

	def do_DELETE(self):
		
		print(self.path)

		path_parts = self.path.split('/')
		path_parts = path_parts[1:]

		if (path_parts[0] == "device"):
			if (path_parts[1] == "radiator-valve"):
				if (path_parts[2].isdigit()):
					if (ThermostaticValve.removeValve(path_parts[2])):
						self._send_response('', 200)
					else:
						self._send_response('', 404)
					#this_valve = ThermostaticValve.getValve(path_parts[2])

					#if (this_valve is not None):
					#	ThermostaticValve.removeValve(int(path_parts[2]))
					#	self._send_response('', 200)
					#else:
					#	self._send_response('', 404)