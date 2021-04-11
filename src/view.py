import sys
sys.path.append('./GraphEngine')

import math
# from datetime import datetime, timedelta
import datetime
import random
import pygame
import numpy as np

import console
import ggraph
import graphdisplay as gd
import delaunaytriangulation as dt
import utils
import model
import parameters as params

class UserInterface(gd.GraphDisplay):

	def __init__(self, model, graph, fps=60):
		super(UserInterface, self).__init__(graph, caption="A World in Conflict", logofile=None, fps=fps, screensize=params.UserInterfaceParams.SCREENSIZE, graph_surface_width_proportion=params.UserInterfaceParams.GRAPH_SURFACE_WIDTH_PROPORTION, info_surface_height_proportion=params.UserInterfaceParams.INFO_SURFACE_HEIGHT_PROPORTION, mbgc=params.UserInterfaceParams.MBGC, ibgc=params.UserInterfaceParams.IBGC, lbgc=params.UserInterfaceParams.LBGC)
		self.model = model

		self.selected = None

		self.map_image_file = "../data/fx/map.png"
		self.map_image = None
		self.map_image_rect = None

		print("Creating UserInterface")

		self.save_map_image()
		self.init_rect_for_nodes()
		self.set_node_graphic_info()

	def reset(self):
		self.save_map_image()
		self.init_rect_for_nodes()
		self.set_node_graphic_info()

	def reset_nodes_only(self):
		self.init_rect_for_nodes()
		self.set_node_graphic_info()

	def set_node_graphic_info(self):
		if self.graph != None:
			for i, loc_node in enumerate(self.graph.nodes):
				print("Set node graphic info {}/{}".format(i,len(self.graph.nodes)), end='\r', flush=True)
				
				# _x = (self.graph_surface_position[0]+random.random()*self.graph_surface_size[0]*0.2) + random.random()*self.graph_surface_size[0]*0.8
				# _y = (self.graph_surface_position[1]+random.random()*self.graph_surface_size[0]*0.2) + random.random()*self.graph_surface_size[1]*0.8
				if loc_node.info["rect"] != None:
					_x = loc_node.info["rect"].center[0]
					_y = loc_node.info["rect"].center[1]
				else:
					_x = 0; _y = 0;
				loc_node.info["pos"] = (_x, _y)

				loc_node.info["color"] = params.LocationParams.LOCATION_COLORS[loc_node.info["location"].archetype]
			print("")

	def update_node_info(self):
		if self.graph != None:
			for loc_node in self.graph.nodes:
				if self.selected == loc_node:
					loc_node.info["outline_color"] = (255, 255, 255)
				else:
					loc_node.info["outline_color"] = (0, 0, 0)

				if loc_node.info["community"] != None:
					_rad_factor = utils.normalise(loc_node.info["community"].get_total_pop(), maxi=8000)
					_rad_min = 6
					_rad_max = 14
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
		self.graph_surface.blit(self.map_image, self.map_image_rect)
		
		if self.model.map.quadmap != None:
			for qt in self.model.map.quadmap.qtiles:
				_r = pygame.Rect(params.map_coord_to_screen_coord_centered(qt.rect.topleft), params.map_coord_to_screen_coord_centered(qt.rect.bottomright))
				pygame.draw.rect(self.graph_surface, (255,0,0), _r, width=1)

	def init_rect_for_nodes(self):
		ceiled_tw = math.ceil(self.graph_surface_size[0] / self.model.map.width)
		ceiled_th = math.ceil(self.graph_surface_size[1] / self.model.map.height)

		tw = self.graph_surface_size[0] / self.model.map.width
		th = self.graph_surface_size[1] / self.model.map.height

		tile_size = (ceiled_tw, ceiled_th)

		for n in self.graph.nodes:
			loc = n.info["location"]
			mp = loc.map_position
			_x = mp[0] * tw
			_y = mp[1] * th
			_pos = (_x, _y)
			n.info["rect"] = pygame.Rect(_pos, tile_size)

	def save_map_image(self):
		print("Save map_image")

		temp_surface = pygame.Surface(self.graph_surface_size)

		ceiled_tw = math.ceil(self.graph_surface_size[0] / self.model.map.width)
		ceiled_th = math.ceil(self.graph_surface_size[1] / self.model.map.height)

		tw = self.graph_surface_size[0] / self.model.map.width
		th = self.graph_surface_size[1] / self.model.map.height

		tile_size = (ceiled_tw, ceiled_th)

		# self.init_rect_for_nodes()

		for x in range(self.model.map.width):
			print("Draw to map image, column {}".format(x), end='\r', flush=True)
			for y in range(self.model.map.height):
				t = self.model.map.get_tile(x, y)
				if t.has_road:
					c = params.UserInterfaceParams.TILE_TYPE_COLORS[params.TileParams.ROADS]
				else:
					c = params.UserInterfaceParams.TILE_TYPE_COLORS[t.type]

				_x = x * tw
				_y = y * th
				_pos = (_x, _y)

				_rect = pygame.Rect(_pos, tile_size)

				pygame.draw.rect(temp_surface, c, _rect)
		print("")

		pygame.image.save(temp_surface, self.map_image_file)
		self.map_image = pygame.image.load(self.map_image_file)
		self.map_image_rect = self.map_image.get_rect()
		print("Map image saved to {}".format(self.map_image_file))

	def main_loop_end(self):
		self.update_node_info()

		super(UserInterface, self).fill_surfaces()

		self.draw_map()

		super(UserInterface, self).main_loop_logic()

		super(UserInterface, self).blit_surfaces()

		super(UserInterface, self).pygame_update_and_tick()

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

