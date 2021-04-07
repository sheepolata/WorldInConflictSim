import sys
sys.path.append('./GraphEngine')

import math
# from datetime import datetime, timedelta
import datetime
import random
import pygame

import console
import ggraph
import graphdisplay as gd
import utils
import model

LOCATION_COLORS = {
	"PLAINS"    : (86, 125, 70),
	"MOUNTAINS" : (139,69,19),
	"SEASIDE"   : (15,94,156)
}

class UserInterface(gd.GraphDisplay):

	TILE_TYPE_COLORS = {
		model.Tile.WATER     : (0, 0, 255),
		model.Tile.PLAINS    : (0, 168, 0),
		model.Tile.MOUNTAINS : (128, 0, 0)
	}

	def __init__(self, model, graph, fps=60):
		super(UserInterface, self).__init__(graph, caption="A World in Conflict", fps=fps)
		self.model = model

		self.selected = None

		for loc_node in self.graph.nodes:
			_x = (self.graph_surface_position[0]+random.random()*self.graph_surface_size[0]*0.2) + random.random()*self.graph_surface_size[0]*0.8
			_y = (self.graph_surface_position[1]+random.random()*self.graph_surface_size[0]*0.2) + random.random()*self.graph_surface_size[1]*0.8
			loc_node.info["pos"] = (_x, _y)

			loc_node.info["color"] = LOCATION_COLORS[loc_node.info["location"].archetype]

	def update_node_info(self):
		for loc_node in self.graph.nodes:
			if self.selected == loc_node:
				loc_node.info["outline_color"] = (0, 255, 0)
			else:
				loc_node.info["outline_color"] = (0, 0, 0)

			if loc_node.info["community"] != None:
				_rad_factor = utils.normalise(loc_node.info["community"].get_total_pop(), maxi=10000)
				_rad_min = 10
				_rad_max = 50
				loc_node.info["radius"] = _rad_min + (_rad_factor*(_rad_max-_rad_min))

	def update_info_tab(self):
		self.info_console.log("{}".format(LogConsole.get_date_to_string(self.model.day)))

		if self.selected == None:
			model_summary = self.model.to_string_summary()
			for l in model_summary:
				self.info_console.log(l)
		else:
			if self.selected.info["community"] != None:
				comm_info = self.selected.info["community"].to_string_list()
				for l in comm_info:
					self.info_console.log(l)
			elif self.selected.info["location"] != None:
				loc_info = self.selected.info["location"].to_string_list()
				for l in loc_info:
					self.info_console.log(l)

		self.info_console.push_front("{:.1f} FPS".format(self.clock.get_fps()))

	def insert_info_console(self, s, pos):
		self.info_console.insert(s, pos)

	def draw_map(self):

		tw = self.graph_surface_size[0] // self.model.map.width
		th = self.graph_surface_size[1] // self.model.map.height

		tw = int(tw)
		th = int(th)

		# print("{}/{}={}".format(self.graph_surface_size[0], self.model.map.width, self.graph_surface_size[0] / self.model.map.width))
		# print("{}/{}={}".format(self.graph_surface_size[1], self.model.map.height, self.graph_surface_size[1] / self.model.map.height))
		# print(self.graph_surface_size)

		tile_size = (tw, th)

		width_r  = list(range(0, int(self.graph_surface_size[0]), tw))
		height_r = list(range(0, int(self.graph_surface_size[1]), th))

		pygame.draw.rect(self.graph_surface, (0,0,0), pygame.Rect((0,0), self.graph_surface_size))

		for x, posx in enumerate(width_r[:-1]):
			for y, posy in enumerate(height_r[:-1]):

				t = self.model.map.tiles[x][y]
				c = UserInterface.TILE_TYPE_COLORS[t.type]

				# _x = x * tile_size[0]
				# _y = y * tile_size[1]
				_pos = (posx, posy)

				pygame.draw.rect(self.graph_surface, c, pygame.Rect(_pos, tile_size), 1)



	def main_loop_end(self):
		self.update_node_info()

		super(UserInterface, self).fill_surfaces()

		self.draw_map()

		super(UserInterface, self).main_loop_logic()

		super(UserInterface, self).blit_surfaces()

		super(UserInterface, self).pygame_update_and_tick()

class CityNode(ggraph.gNode):

	def __init__(self, _id):
		super(CityNode, self).__init__(_id)

		self.info["pos"]    = (0, 0)
		self.info["radius"] = 8
		self.info["color"] = (255, 255, 255)

		self.info["location"] = None
		self.info["community"] = None

class CityGraph(ggraph.gGraph):

	def __init__(self, model):
		super(CityGraph, self).__init__(node_type=CityNode, oriented=False)

		self._draw_delaunay = False

		self.model = model

	def generate_graph_from_model(self):
		if self.model == None:
			return

		nodes = []
		_id = 0
		for l in self.model.locations:
			# n = CityNode(_id)
			n = CityNode(l.name)
			n.info["location"] = l

			nodes.append(n)

			_id += 1

		for c in self.model.communities:
			for n in nodes:
				if n.info["location"] == c.location:
					n.info["community"] = c

		for n in nodes:
			self.addNode(n)

		for n in self.nodes:
			for n2 in self.nodes:
				if n != n2:
					self.addEdge(n, n2)

class myDatetime(object):

	def __init__(self, simu_day):
		self.simu_day = simu_day

		self.day   = ((self.simu_day % 365) % 30) + 1
		self.month = (((self.simu_day % 365) // 30) % 12) + 1
		self.year  = (self.simu_day // 365) + 1

class LogConsole(console.Console):

	def __init__(self):
		super(LogConsole, self).__init__()

	def get_date_to_string(day):
		_year = math.floor(day/(12*28))
		_month = (math.floor(day/28))%12
		_day = day%28
		d = myDatetime(day)
		h = "{:02d}/{:02d}/{:04d}".format(d.day, d.month, d.year)
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

