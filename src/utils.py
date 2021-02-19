#returns True if value is float, otherwise returns False
def isFloat(value):
	try:
		float(value)
		return True
	except ValueError:
		return False