import sys
sys.path.append('./GraphEngine')

import math
from datetime import datetime

import console
import ggraph

class CityNode(ggraph.gNode):

	def __init__(self, _id):
		super(CityNode, self).__init__(_id)

		self.info["pos"]    = (0, 0)
		self.info["radius"] = 8

		

class CityGraph(ggraph.gGraph):

	def __init__(self):
		super(CityGraph, self).__init__(node_type=CityNode, oriented=False)

		self._draw_delaunay = False

class LogConsole(console.Console):

	def __init__(self):
		super(LogConsole, self).__init__()

	def get_date_to_string(day):
		_year = math.floor(day/(12*28))
		_month = (math.floor(day/28))%12
		_day = day%28
		d = datetime.fromtimestamp(day*24*60*60)
		# d = d.replace(year=(d.year-1969))
		h = "{:02d}/{:02d}/{:04d}".format(d.day, d.month, d.year-1969)
		return h

	def set_head(self, day):
		self.line_head = "{} - ".format(LogConsole.get_date_to_string(day))

	def log(self, s, day):
		self.set_head(day)
		super(LogConsole, self).log(s)

	def push_back(self, s, day):
		self.log(s, day)

	def push_front(self, s, day):
		self.set_head(day)
		super(LogConsole, self).push_front(s)


if __name__=='__main__':
	print("#### LogConsole TESTS ####")
	log = LogConsole()

	log.log("Hello", 0)
	log.log("Hello", 28)
	log.log("Hello", 365)
	log.log("Hello", 365*3)
	log.push_back("Hello", 365*12)
	log.push_front("Hello", 10000)

	log.print()

	print("##########################\n")

