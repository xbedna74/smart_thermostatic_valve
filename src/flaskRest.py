import flask
from flask import request

from thermostaticValve import *

if __name__ == "__main__":
	app = flask.Flask(__name__)

	@app.route("/device/radiator-valve", methods=["GET"])
	def get_info():
		if "id" in request.args and "day" in request.args and "hour" in request.args:
			this_valve = ThermostaticValve.get_valve(request.args["id"])
			if this_valve is not None:
				info = {
					"temperature": this_valve.get_temperature(),
					"current": this_valve.get_current_temperature(),
					"desired": this_valve.get_desired_temperature(),
					"time_tmp": this_valve.get_week_program_temperature(int(request.args["day"]), int(request.args["hour"])),
					"mode": this_valve.get_mode()
				}
				return flask.jsonify(info), 200
			else:
				flask.abort(404)
		else:
			return '', 204

	@app.route("/device/radiator-valve/current-temperature", methods=["GET"])
	def get_current_temperature():
		if "id" in request.args:
			this_valve = ThermostaticValve.get_valve(request.args["id"])
			if this_valve is not None:
				return str(this_valve.get_current_temperature()), 200
			else:
				flask.abort(404)
		else:
			return '', 204


	@app.route("/device/radiator-valve/desired-temperature", methods=["GET"])
	def get_desired_temperature():
		if "id" in request.args:
			this_valve = ThermostaticValve.get_valve(request.args["id"])
			if this_valve is not None:
				return str(this_valve.get_desired_temperature()), 200
			else:
				flask.abort(404)
		else:
			return '', 204

	@app.route("/device/radiator-valve/position", methods=["GET"])
	def get_position():
		if "id" in request.args:
			this_valve = ThermostaticValve.get_valve(request.args["id"])
			if this_valve is not None:
				print("Current temperature: " + str(this_valve.get_current_temperature()))
				this_valve.set_current_position()
				this_valve.control_valve()
				p = this_valve.get_position()
				return str(p), 200
			else:
				flask.abort(404)
		else:
			return '', 204

	@app.route("/device/radiator-valve/ids", methods=["GET"])
	def get_ids():
		ids = ThermostaticValve.get_ids()
		if ids is None:
			return flask.jsonify([]), 200
		return flask.jsonify(ids), 200

	@app.route("/device/radiator-valve/time-temperature", methods=["GET"])
	def get_day_hour_temperature():
		if "id" in request.args and "day" in request.args and "hour" in request.args:
			this_valve = ThermostaticValve.get_valve(request.args["id"])
			if this_valve is not None:
				tmp = this_valve.get_week_program_temperature(int(request.args["day"]), int(request.args["hour"]))
				return str(tmp), 200
			else:
				flask.abort(404)
		else:
			return '', 204

	@app.route("/device/radiator-valve/mode", methods=["GET"])
	def get_mode():
		if "id" in request.args:
			this_valve = ThermostaticValve.get_valve(request.args["id"])
			if this_valve is not None:
				return str(this_valve.get_mode()), 200
			else:
				flask.abort(404)
		else:
			return '', 204


	@app.route("/device/radiator-valve/alias", methods=["GET"])
	def get_alias():
		if "id" in request.args:
			this_valve = ThermostaticValve.get_valve(request.args["id"])
			if this_valve is not None:
				alias = this_valve.get_alias()
				return alias, 200
			else:
				flask.abort(404)
		else:
			return '', 204

	@app.route("/device/radiator-valve", methods=["POST"])
	def post_new_valve():
		new_valve = ThermostaticValve()
		return str(new_valve.get_id()), 201

	@app.route("/device/radiator-valve/temperature", methods=["PUT"])
	def put_temperature():
		if "id" in request.args and "tmp" in request.args:
			this_valve = ThermostaticValve.get_valve(request.args["id"])
			if this_valve is not None:
				this_valve.set_temperature(float(request.args["tmp"]))
				return '', 200
			else:
				flask.abort(404)
		else:
			return '', 204

	@app.route("/device/radiator-valve/current-temperature", methods=["PUT"])
	def put_current_temperature():
		if "id" in request.args and "tmp" in request.args:
			this_valve = ThermostaticValve.get_valve(request.args["id"])
			if this_valve is not None:
				this_valve.set_current_temperature(float(request.args["tmp"]))
				return '', 200
			else:
				flask.abort(404)
		else:
			return '', 204

	@app.route("/device/radiator-valve/time-temperature", methods=["PUT"])
	def put_day_hour_temperature():
		if "id" in request.args and "day" in request.args and "hour" in request.args and "tmp" in request.args:
			this_valve = ThermostaticValve.get_valve(request.args["id"])
			if this_valve is not None:
				this_valve.set_week_program_temperature(int(request.args["day"]), int(request.args["hour"]), float(request.args["tmp"]))
				return '', 200
			else:
				flask.abort(404)
		else:
			return '', 204

	@app.route("/device/radiator-valve/mode-change", methods=["PUT"])
	def put_mode():
		if "mode" in request.args and "id" in request.args:
			this_valve = ThermostaticValve.get_valve(request.args["id"])
			if this_valve is not None:
				mode = int(request.args["mode"])
				if mode == 3:
					this_valve.set_boost_mode_on()
				elif mode == 4:
					this_valve.set_boost_mode_off()
				else:
					this_valve.set_mode(mode)
				return '', 200
			else:
				flask.abort(404)
		else:
			return '', 204

	@app.route("/device/radiator-valve/alias", methods=["PUT"])
	def put_alias():
		if "id" in request.args and "alias" in request.args:
			this_valve = ThermostaticValve.get_valve(request.args["id"])
			if this_valve is not None:
				this_valve.set_alias(request.args["alias"])
				return '', 200
			else:
				flask.abort(404)
		else:
			return '', 204

	@app.route("/device/radiator-valve", methods=["DELETE"])
	def delete_valve():
		if "id" in request.args:
			if ThermostaticValve.remove_valve(request.args["id"]):
				return '', 200
			else:
				flask.abort(404)
		else:
			return '', 204


	app.run(host="192.168.1.210", port="8080")