#returns True if value is float, otherwise returns False
def isFloat(value):
	try:
		float(value)
		return True
	except ValueError:
		return False

#returns index of day of the week
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