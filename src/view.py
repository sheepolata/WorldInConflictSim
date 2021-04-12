import sys
sys.path.append('./GraphEngine')

import math
# from datetime import datetime, timedelta
import datetime
import random
import pygame
import numpy as np

from scipy.spatial import Voronoi
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import console
import ggraph
import graphdisplay as gd
import delaunaytriangulation as dt
import utils
import model
import parameters as params

class UserInterface(gd.GraphDisplay):

	def __init__(self, model, graph, fps=60):
		print("Creating UserInterface")

		super(UserInterface, self).__init__(graph, caption="A World in Conflict", logofile=None, fps=fps, screensize=params.UserInterfaceParams.SCREENSIZE, graph_surface_width_proportion=params.UserInterfaceParams.GRAPH_SURFACE_WIDTH_PROPORTION, info_surface_height_proportion=params.UserInterfaceParams.INFO_SURFACE_HEIGHT_PROPORTION, mbgc=params.UserInterfaceParams.MBGC, ibgc=params.UserInterfaceParams.IBGC, lbgc=params.UserInterfaceParams.LBGC)
		
		self.model = model

		self.selected = None

		self.map_image_file = "../data/fx/map.png"
		self.map_image = None
		self.map_image_rect = None

		self.voronoi_surface = pygame.Surface(self.graph_surface.get_size(), pygame.SRCALPHA)
		# self.voronoi_surface.set_alpha(200)

		self.voronoi = None
		self.voronoi_points = []

		self._draw_voronoi = True

		self.save_map_image()
		self.init_rect_for_nodes()
		self.set_node_graphic_info()
		self.compute_voronoi()

	def reset(self):
		self.save_map_image()
		self.init_rect_for_nodes()
		self.set_node_graphic_info()
		self.compute_voronoi()

	def reset_nodes_only(self):
		self.init_rect_for_nodes()
		self.set_node_graphic_info()
		self.compute_voronoi()

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

	def compute_voronoi(self):
		if self.graph == None:
			return

		self.voronoi_points = []

		for loc_node in self.graph.nodes:
			self.voronoi_points.append((loc_node.info["pos"][0], loc_node.info["pos"][1]))

		self.voronoi_points = np.array(self.voronoi_points)
		self.voronoi = Voronoi(self.voronoi_points)

		def voronoi_finite_polygons_2d(vor, radius=None):
			"""
			Reconstruct infinite voronoi regions in a 2D diagram to finite
			regions.
			Parameters
			----------
			vor : Voronoi
				Input diagram
			radius : float, optional
				Distance to 'points at infinity'.
			Returns
			-------
			regions : list of tuples


				Indices of vertices in each revised Voronoi regions.
			vertices : list of tuples
				Coordinates for revised Voronoi vertices. Same as coordinates
				of input vertices, with 'points at infinity' appended to the
				end.
			"""

			if vor.points.shape[1] != 2:
				raise ValueError("Requires 2D input")

			new_regions = []
			new_vertices = vor.vertices.tolist()

			center = vor.points.mean(axis=0)
			if radius is None:
				radius = vor.points.ptp().max()*2

			# Construct a map containing all ridges for a given point
			all_ridges = {}
			for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
				all_ridges.setdefault(p1, []).append((p2, v1, v2))
				all_ridges.setdefault(p2, []).append((p1, v1, v2))

			# Reconstruct infinite regions
			for p1, region in enumerate(vor.point_region):
				vertices = vor.regions[region]

				if all(v >= 0 for v in vertices):
					# finite region
					new_regions.append(vertices)
					continue

				# reconstruct a non-finite region
				ridges = all_ridges[p1]
				new_region = [v for v in vertices if v >= 0]

				for p2, v1, v2 in ridges:
					if v2 < 0:
						v1, v2 = v2, v1
					if v1 >= 0:
						# finite ridge: already in the region
						continue

					# Compute the missing endpoint of an infinite ridge

					t = vor.points[p2] - vor.points[p1] # tangent
					t /= np.linalg.norm(t)
					n = np.array([-t[1], t[0]])  # normal

					midpoint = vor.points[[p1, p2]].mean(axis=0)
					direction = np.sign(np.dot(midpoint - center, n)) * n
					far_point = vor.vertices[v2] + direction * radius

					new_region.append(len(new_vertices))
					new_vertices.append(far_point.tolist())

				# sort region counterclockwise
				vs = np.asarray([new_vertices[v] for v in new_region])
				c = vs.mean(axis=0)
				angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
				new_region = np.array(new_region)[np.argsort(angles)]

				# finish
				new_regions.append(new_region.tolist())

			return new_regions, np.asarray(new_vertices)

		self.voronoi_regions, self.voronoi_vertices = voronoi_finite_polygons_2d(self.voronoi)

		self.voronoi_draw_regions = []

		for reg in self.voronoi_regions:
			_draw_points = []
			for pi in reg:
				_draw_points.append(self.voronoi_vertices[pi])
			self.voronoi_draw_regions.append(_draw_points)

		# f = open("../data/Results/tmp.txt", 'w')
		# for p in self.voronoi_points:
		# 	f.write(str(p))
		# 	f.write('\n')
		# f.close()

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

	def draw_voronoi(self):
		if self.voronoi == None:
			return
		
		# First, the Voronoi vertices
		# for v in self.voronoi.vertices:
		# 	pygame.draw.circle(self.voronoi_surface, (255,0,0,255), v, 5)

		def centroid(vertexes):
			 _x_list = [vertex [0] for vertex in vertexes]
			 _y_list = [vertex [1] for vertex in vertexes]
			 _len = len(vertexes)
			 _x = sum(_x_list) / _len
			 _y = sum(_y_list) / _len
			 return(_x, _y)

		for dreg in self.voronoi_draw_regions:


			c = (0,0,0,0)
			transparency = 200
			node = None

			for loc_node in self.graph.nodes:
				if loc_node.info["rect"]:
					p = Point(loc_node.info["rect"].center[0], loc_node.info["rect"].center[1])
					poly = Polygon(dreg)
					if poly.contains(p):
						node = loc_node
						if loc_node.info["community"]:
							c = params.UserInterfaceParams.COLOR_LIST[params.UserInterfaceParams.KINGDOM_TO_COLOR[loc_node.info["community"].kingdom.name]]
							c = (c[0], c[1], c[2], transparency)

			if node != None:
				_centroid = node.info["rect"].center
			else:
				_centroid = centroid(dreg)

			dist = 15
			added_point = []
			for dreg_point in dreg:

				angle = math.atan2(_centroid[1]-dreg_point[1], _centroid[0]-dreg_point[0])

				_x = dreg_point[0] + (dist * math.cos(angle))
				_y = dreg_point[1] + (dist * math.sin(angle))
				new_p = (_x, _y)
				added_point.append(new_p)

			added_point.reverse()

			complex_polygon = dreg + [dreg[0]] + [added_point[-1]] + added_point

			pygame.draw.polygon(self.voronoi_surface, c, complex_polygon)


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

	def fill_surfaces(self):
		super(UserInterface, self).fill_surfaces()
		self.voronoi_surface.fill((0,0,0,0))

	def blit_surfaces(self):
		super(UserInterface, self).blit_surfaces()
		self.screen.blit(self.voronoi_surface, self.graph_surface_position)		

	def main_loop_end(self):
		self.update_node_info()

		self.fill_surfaces()

		self.draw_map()

		if self._draw_voronoi:
			self.draw_voronoi()

		super(UserInterface, self).main_loop_logic()

		self.blit_surfaces()

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


import matplotlib.pyplot as plt

if __name__=='__main__':
	# print("#### LogConsole TESTS ####")
	# log = LogConsole()

	# log.log("Hello", 0)
	# log.log("Hello", 28)
	# log.log("Hello", 365)
	# log.log("Hello", 365*3)
	# log.push_back("Hello", 365*12)
	# log.push_front("Hello", 10000)

	# log.print()

	# print("##########################\n")

	points = np.array([ [726, 404],
						[662, 559],
						[287, 222],
						[551,  64],
						[447, 372],
						[370,  58],
						[  8, 571],
						[683, 191],
						[158, 369],
						[100,  52],
						[745, 689],
						[121, 199],
						[447, 225],
						[708,  21],
						[124, 666]])

	vor = Voronoi(points)

	plt.plot(points[:, 0], points[:, 1], 'o')

	plt.plot(vor.vertices[:, 0], vor.vertices[:, 1], '*')

	plt.xlim(-200, 1200); plt.ylim(-200, 1200)


	for simplex in vor.ridge_vertices:

		simplex = np.asarray(simplex)

		if np.all(simplex >= 0):

			plt.plot(vor.vertices[simplex, 0], vor.vertices[simplex, 1], 'k-')


	center = points.mean(axis=0)

	for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):

		simplex = np.asarray(simplex)

		if np.any(simplex < 0):

			i = simplex[simplex >= 0][0] # finite end Voronoi vertex

			t = points[pointidx[1]] - points[pointidx[0]]  # tangent

			t = t / np.linalg.norm(t)

			n = np.array([-t[1], t[0]]) # normal

			midpoint = points[pointidx].mean(axis=0)

			far_point = vor.vertices[i] + np.sign(np.dot(midpoint - center, n)) * n * 1000

			plt.plot([vor.vertices[i,0], far_point[0]],

					 [vor.vertices[i,1], far_point[1]], 'k--')

	plt.show()
