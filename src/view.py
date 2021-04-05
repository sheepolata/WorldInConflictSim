import sys
sys.path.append('./GraphEngine')

import math
from datetime import datetime

import console

class LogConsole(console.Console):

	def __init__(self):
		super(LogConsole, self).__init__()

	def set_head(self, day):
		_year = math.floor(day/(12*28))
		_month = (math.floor(day/28))%12
		_day = day%28
		d = datetime.fromtimestamp(day*24*60*60)
		d = d.replace(year=(d.year-1969))
		h = "{:02d}/{:02d}/{:04d} - ".format(d.day, d.month, d.year)
		self.line_head = h

	def log(self, s, day):
		self.set_head(day)
		super(LogConsole, self).log(s)

	def push_back(self, s, day):
		self.log(s, day)

	def push_front(self, s, day):
		self.set_head(day)
		super(LogConsole, self).push_front(s)


if __name__=='__main__':
	log = LogConsole()

	log.log("Hello", 0)
	log.log("Hello", 28)
	log.log("Hello", 365)
	log.log("Hello", 365*3)
	log.push_back("Hello", 365*12)
	log.push_front("Hello", 10000)

	log.print()