import time
import os

import sys
sys.path.append('./GraphEngine')

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import csv
import threading
from scipy.spatial import Voronoi
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import pprint

import console
import utils
import graph
import perlinNoise
import pathfinding
import parameters as params
import myglobals

from pygame import Rect

class SimThread(threading.Thread):

	def __init__(self, model):
		super(SimThread, self).__init__()
		self.model = model
		self._stop = False
		self._paused = False


		self.freq_list = [1, 7, 30, 90, 182, 365, -1]
		self.freq_index = 1
		self.freq = self.freq_list[self.freq_index]

		print("Creating SimThread")

	def increase_speed(self):
		self.freq_index = min(len(self.freq_list) - 1, self.freq_index + 1)
		self.freq = self.freq_list[self.freq_index]

	def decrease_speed(self):
		self.freq_index = max(0, self.freq_index - 1)
		self.freq = self.freq_list[self.freq_index]

	def run(self):
		while not self._stop:

			if not self._paused:
				self.model.loop()

			if self.freq > 0:
				time.sleep(1.0/float(self.freq))

	def stop(self):
		self._stop = True

	def pause(self, forced=None):
		if forced == None:
			self._paused = not self._paused
		else:
			self._paused = forced
		return self._paused

	def is_fastest_speed(self):
		return self.freq_index == (len(self.freq_list)-1)

class Map(object):

	class QuadTile(object):
		currID = 0
		def __init__(self):
			self.id = Map.QuadTile.currID
			Map.QuadTile.currID += 1
			self.type = None
			self.neighbours = []
			self.rect = None

		def set_type(self, t):
			self.type = t

		def addNeighbour(self, nid):
			self.neighbours.append(nid)

	class QuadMap(object):
		def __init__(self):
			self.qtiles = []

		def get_qtile_by_id(self, _id):
			for qt in self.qtiles:
				if qt.id == _id:
					return qt

	def __init__(self, width, height, nb_landmarks):
			
		self.width  = width
		self.height = height
		self.tiles  = []

		self.nb_landmarks = nb_landmarks
		self.landmarks = []

		for x in range(self.width):
			_rowx = []
			print("Creating tiles column {}".format(x), end='\r', flush=True)
			for y in range(self.height):
				_rowx.append(Tile(x, y))
			self.tiles.append(_rowx)
		print("")

		# self.tiles = [[Tile()] * self.height] * self.width

		self.generate_from_perlin_noise()
		self.smooth_map()

		self.quadmap = None
		# self.quadmap = self.generate_quadmap()

	def get_tile(self, x, y):
		return self.tiles[x][y]

	def generate_from_perlin_noise(self):
		PNFactory = perlinNoise.PerlinNoiseFactory(2, octaves=8, tile=(), unbias=True)
		PNFactoryForest = perlinNoise.PerlinNoiseFactory(2, octaves=8, tile=(), unbias=True)
		PNFactoryDesert = perlinNoise.PerlinNoiseFactory(2, octaves=8, tile=(), unbias=True)

		noise = []
		forest_noise = []
		desert_noise = []
		for x in range(self.width):
			print("Generating noise map column {}".format(x), end='\r', flush=True)

			noise.append([])
			forest_noise.append([])
			desert_noise.append([])
			
			for y in range(self.height):
				noise_value = PNFactory(float(x)/self.width,float(y)/self.height)
				noise[x].append(noise_value)

				noise_value = PNFactoryForest(float(x)/self.width,float(y)/self.height)
				forest_noise[x].append(noise_value)

				noise_value = PNFactoryDesert(float(x)/self.width,float(y)/self.height)
				desert_noise[x].append(noise_value)
		print("")

		new_noise = []
		flattened_noise = list(utils.flatten(noise))
		noise_min = min(flattened_noise)
		noise_max = max(flattened_noise)

		new_forest_noise = []
		flattened_forest_noise = list(utils.flatten(forest_noise))
		forest_noise_min = min(flattened_forest_noise)
		forest_noise_max = max(flattened_forest_noise)

		new_desert_noise = []
		flattened_desert_noise = list(utils.flatten(desert_noise))
		desert_noise_min = min(flattened_desert_noise)
		desert_noise_max = max(flattened_desert_noise)
		for x in range(len(noise)):
			print("Normalising noise column {}".format(x), end='\r', flush=True)
			new_noise.append(utils.normalise_list2(noise[x], noise_min, noise_max))
			new_forest_noise.append(utils.normalise_list2(forest_noise[x], forest_noise_min, forest_noise_max))
			new_desert_noise.append(utils.normalise_list2(desert_noise[x], desert_noise_min, desert_noise_max))
		noise = new_noise
		forest_noise = new_forest_noise
		desert_noise = new_desert_noise
		print("")

		for x in range(self.width):
			print("Setting noise for tile, column {}".format(x), end='\r', flush=True)
			for y in range(self.height):
				self.get_tile(x, y).info["noise"] = noise[x][y]
				self.get_tile(x, y).info["forest_noise"] = forest_noise[x][y]
				self.get_tile(x, y).info["desert_noise"] = desert_noise[x][y]
		print("")
			
		for x in range(self.width):
			print("Setting type for tile, column {}".format(x), end='\r', flush=True)
			for y in range(self.height):
				self.get_tile(x, y).set_type_from_noise()
		print("")

		print("Generate Landmarks and set their effect")

		self.landmarks = Landmark.generate(self.nb_landmarks, self.width, self.height)
		# for lm in _landmarks:
		# 	print(lm.to_string())

	def get_neighbours_of(self, pos, diag_neigh=False):
		res = []
		if pos[0] + 1 < self.width:
			res.append((pos[0] + 1, pos[1]))
		if pos[0] - 1 >= 0:
			res.append((pos[0] - 1, pos[1]))
		if pos[1] + 1 < self.height:
			res.append((pos[0], pos[1] + 1))
		if pos[1] - 1 >= 0:
			res.append((pos[0], pos[1] - 1))

		if diag_neigh:
			if pos[0] + 1 < self.width and pos[1] + 1 < self.height:
				res.append((pos[0] + 1, pos[1] + 1))
			if pos[0] - 1 >= 0 and pos[1] - 1 >= 0:
				res.append((pos[0] - 1, pos[1] - 1))
			if pos[0] - 1 >= 0 and pos[1] + 1 < self.height:
				res.append((pos[0] - 1, pos[1] + 1))
			if pos[0] + 1 < self.width and pos[1] - 1 >= 0:
				res.append((pos[0] + 1, pos[1] - 1))

		return res

	def get_circle_around(self, pos, rad):
		r = []
		for x in range(self.width):
			for y in range(self.height):
				if utils.distance2p(pos, (x,y)) <= rad:
					r.append((x,y))
		return r

	def smooth_map(self):
		for x in range(self.width):
			print("Smoothing map column {}".format(x), end='\r', flush=True)
			for y in range(self.height):
				t = self.get_tile(x, y)
				nposlis = self.get_neighbours_of((x, y))
				neigh_types = []
				for npos in nposlis:
					neigh_types.append(self.get_tile(npos[0], npos[1]).type)

				if len(neigh_types) > 0: 
					if len(set(neigh_types)) <= 1 and t.type != neigh_types[0]:
						t.type = neigh_types[0]
		print("")

	def generate_quadmap(self):
		quadmap = Map.QuadMap()

		# r1 = Rect((0, 0), (self.width//2, self.height//2))
		# r2 = Rect((self.width/2.0, 0), (self.width//2, self.height//2))
		# r3 = Rect((0, self.height/2.0), (self.width//2, self.height//2))
		# r4 = Rect((self.width/2.0, self.height/2.0), (self.width//2, self.height//2))

		base_rectangle = Rect((0,0), (self.width-1, self.height-1))

		def split(r):
			print("size="+str(r.size))
			r1 = Rect(r.topleft, (math.floor(r.size[0]/2), math.ceil(r.size[1]/2)))
			r2 = Rect((math.floor(r.size[0]/2), r.topleft[1]), (math.ceil(r.size[0]/2), math.ceil(r.size[1]/2)))
			r3 = Rect((r.topleft[0], math.floor(r.size[1]/2)), (math.ceil(r.size[0]/2), math.ceil(r.size[1]/2)))
			r4 = Rect((math.floor(r.size[0]/2), math.floor(r.size[1]/2)), (math.ceil(r.size[0]/2), math.ceil(r.size[1]/2)))			

			return [r1, r2, r3, r4]

		_start_set = split(base_rectangle)
		first = _start_set[0]
		for _r in split(first):
			_start_set.append(_r)
		_start_set.remove(first)

		quadmap.qtiles = []
		for r in _start_set:
			_t = Map.QuadTile()
			_t.rect = r
			quadmap.qtiles.append(_t)

		for r in _start_set:
			# print(self.get_tile(r.topleft[0], r.topleft[1]), self.get_tile(r.bottomright[0], r.bottomright[1]))
			print(r, r.topleft, r.topright, r.bottomleft, r.bottomright)

		return quadmap

class Tile(object):

	def __init__(self, x=-1, y=-1):
		self.x = x
		self.y = y

		self.type = params.rng.choice(params.TileParams.TYPES)

		self.info = {}
		self.info["color"] = (0,0,0)

		self.has_road = False

	def get_type(self):
		return self.type

	def set_type_from_noise(self):
		if not self.info["noise"]:
			return

		if self.info["noise"] < 0.05:
			self.type = params.TileParams.DEEPWATER
		elif self.info["noise"] < 0.17:
			self.type = params.TileParams.WATER
		elif self.info["noise"] < 0.19:
			self.type = params.TileParams.BEACH
		elif self.info["noise"] < 0.70:
			self.type = params.TileParams.PLAINS
		elif self.info["noise"] < 0.85:
			self.type = params.TileParams.HILLS
		elif self.info["noise"] < 0.95:
			self.type = params.TileParams.MOUNTAINS
		else:
			self.type = params.TileParams.PEAKS

		if self.type in [params.TileParams.PLAINS, params.TileParams.HILLS]:
			if self.info["forest_noise"] < 0.20:
				self.type = params.TileParams.FOREST
		if self.type in [params.TileParams.PLAINS, params.TileParams.HILLS]:
			if self.info["desert_noise"] < 0.20:
				self.type = params.TileParams.DESERT

class Landmark(object):

	globalID = 0

	def __init__(self, x, y, name, happiness_value):
		self.id = Landmark.globalID
		Landmark.globalID += 1
		self.x = x
		self.y = y

		self.name = name

		self.happiness_value = happiness_value

	def generate(number, map_w, map_h, min_happ=-10, max_happ=10):

		if min_happ >= max_happ:
			raise ValueError("min_happ ({}) greater or equal than max_happ ({})".format(min_happ, max_happ))

		res = []

		landmark_neutral_namelist = open("../data/namelists/landmarks_neutral.txt")
		landmark_neutral_names_from_file = landmark_neutral_namelist.readlines()
		landmark_neutral_namelist.close()
		landmark_neutral_names = params.rng.choice(landmark_neutral_names_from_file, number, replace=False)
		landmark_neutral_names = [s.title() for s in landmark_neutral_names]

		landmark_evil_namelist = open("../data/namelists/landmarks_evil.txt")
		landmark_evil_names_from_file = landmark_evil_namelist.readlines()
		landmark_evil_namelist.close()
		landmark_evil_names = params.rng.choice(landmark_evil_names_from_file, number, replace=False)
		landmark_evil_names = [s.title() for s in landmark_evil_names]

		_x_values = params.rng.choice(range(map_w), number, replace=False)
		_y_values = params.rng.choice(range(map_h), number, replace=False)

		for i in range(number):
			_x = _x_values[i]
			_y = _y_values[i]

			if min_happ >= 0:
				_hv = min_happ + (params.rng.random() * (max_happ - min_happ))
			else:
				_neg = params.rng.random() * abs(min_happ)
				_pos = params.rng.random() * abs(max_happ)
				_hv = _pos - _neg

			if _hv >= 0:
				_name = landmark_neutral_names[i][:-1] if landmark_neutral_names[i][-1] == '\n' else landmark_neutral_names[i]
			else:
				_name = landmark_evil_names[i][:-1] if landmark_evil_names[i][-1] == '\n' else landmark_evil_names[i]

			_lm = Landmark(_x, _y, _name, _hv)

			res.append(_lm)

		return res

	def to_string(self):
		return "{} ({:.02f} happ.)".format(self.name, self.happiness_value)

class Location(object):

	def __init__(self, archetype, name):

		self.name = name
		# Base happiness for pops living here
		self.base_attractiveness = 0
		self.attractiveness = 0
		# Base space to welcome pops, 1 space <=> 100 pops
		self.space = 0
		# Coordinates on a map
		self.map_position = (0, 0)

		self.community = None
		self.neighbouring_locations = []

		self.base_production   = {}
		self.base_storage      = {}
		self.bonus_per_100_pop = {}

		self.area_of_influence = []

		self.landmarks = []

		self.archetype = archetype

		if self.archetype == params.LocationParams.PLAINS:
			self.base_production[params.ModelParams.FOOD] = 1.0
			self.base_production[params.ModelParams.MATERIALS] = 0.05
			self.base_production[params.ModelParams.WEALTH] = 0.08

			self.bonus_per_100_pop[params.ModelParams.FOOD] = 0.08
			self.bonus_per_100_pop[params.ModelParams.MATERIALS] = 0.04
			self.bonus_per_100_pop[params.ModelParams.WEALTH] = 0.01
			
			self.base_storage[params.ModelParams.FOOD] = 300.0
			self.base_storage[params.ModelParams.MATERIALS] = 500.0
			self.base_storage[params.ModelParams.WEALTH] = 160.0

			self.trade_factor = params.rng.random()*0.05

			self.base_attractiveness = 8 + params.rng.random()*4
			self.attractiveness += self.base_attractiveness
			self.space = 20 + params.rng.random()*5

		elif self.archetype == params.LocationParams.MOUNTAINS:

			self.base_production[params.ModelParams.FOOD] = 0.25
			self.base_production[params.ModelParams.MATERIALS] = 0.35
			self.base_production[params.ModelParams.WEALTH] = 0.25

			self.bonus_per_100_pop[params.ModelParams.FOOD] = 0.075
			self.bonus_per_100_pop[params.ModelParams.MATERIALS] = 0.07
			self.bonus_per_100_pop[params.ModelParams.WEALTH] = 0.1
			
			self.base_storage[params.ModelParams.FOOD] = 350.0
			self.base_storage[params.ModelParams.MATERIALS] = 800.0
			self.base_storage[params.ModelParams.WEALTH] = 400.0

			self.trade_factor = 0.02 + params.rng.random()*0.08

			self.base_attractiveness = -10 - params.rng.random()*5
			self.attractiveness += self.base_attractiveness
			self.space = 12 + params.rng.random()*5

		elif self.archetype == params.LocationParams.SEASIDE:

			self.base_production[params.ModelParams.FOOD] = 1.2
			self.base_production[params.ModelParams.MATERIALS] = 0.05
			self.base_production[params.ModelParams.WEALTH] = 0.3

			self.bonus_per_100_pop[params.ModelParams.FOOD] = 0.1
			self.bonus_per_100_pop[params.ModelParams.MATERIALS] = 0.01
			self.bonus_per_100_pop[params.ModelParams.WEALTH] = 0.03
			
			self.base_storage[params.ModelParams.FOOD] = 400.0
			self.base_storage[params.ModelParams.MATERIALS] = 350.0
			self.base_storage[params.ModelParams.WEALTH] = 500.0

			self.trade_factor = 0.05 + params.rng.random()*0.07

			self.base_attractiveness = 15 + params.rng.random()*5
			self.attractiveness += self.base_attractiveness
			self.space = 10 + params.rng.random()*5

		elif self.archetype == params.LocationParams.DESERT:

			self.base_production[params.ModelParams.FOOD] = 0.25
			self.base_production[params.ModelParams.MATERIALS] = 0.25
			self.base_production[params.ModelParams.WEALTH] = 0.0

			self.bonus_per_100_pop[params.ModelParams.FOOD] = 0.03
			self.bonus_per_100_pop[params.ModelParams.MATERIALS] = 0.04
			self.bonus_per_100_pop[params.ModelParams.WEALTH] = 0.015
			
			self.base_storage[params.ModelParams.FOOD] = 600.0
			self.base_storage[params.ModelParams.MATERIALS] = 650.0
			self.base_storage[params.ModelParams.WEALTH] = 750.0

			self.trade_factor = 0.04 + params.rng.random()*0.04

			self.base_attractiveness = 0 - params.rng.random()*10
			self.attractiveness += self.base_attractiveness
			self.space = 40 + params.rng.random()*5

		elif self.archetype == params.LocationParams.FOREST:
			self.base_production[params.ModelParams.FOOD] = 0.75
			self.base_production[params.ModelParams.MATERIALS] = 0.15
			self.base_production[params.ModelParams.WEALTH] = 0.0

			self.bonus_per_100_pop[params.ModelParams.FOOD] = 0.05
			self.bonus_per_100_pop[params.ModelParams.MATERIALS] = 0.08
			self.bonus_per_100_pop[params.ModelParams.WEALTH] = 0.025
			
			self.base_storage[params.ModelParams.FOOD] = 400.0
			self.base_storage[params.ModelParams.MATERIALS] = 650.0
			self.base_storage[params.ModelParams.WEALTH] = 400.0

			self.trade_factor = 0.01 + params.rng.random()*0.02

			self.base_attractiveness = 12 + params.rng.random()*4
			self.attractiveness += self.base_attractiveness
			self.space = 12 + params.rng.random()*6

		elif self.archetype == params.LocationParams.HILL:
			self.base_production[params.ModelParams.FOOD] = 0.45
			self.base_production[params.ModelParams.MATERIALS] = 0.25
			self.base_production[params.ModelParams.WEALTH] = 0.1

			self.bonus_per_100_pop[params.ModelParams.FOOD] = 0.08
			self.bonus_per_100_pop[params.ModelParams.MATERIALS] = 0.04
			self.bonus_per_100_pop[params.ModelParams.WEALTH] = 0.01
			
			self.base_storage[params.ModelParams.FOOD] = 400.0
			self.base_storage[params.ModelParams.MATERIALS] = 550.0
			self.base_storage[params.ModelParams.WEALTH] = 350.0

			self.trade_factor = 0.01 + params.rng.random()*0.04

			self.base_attractiveness = -5 + params.rng.random()*10
			self.attractiveness += self.base_attractiveness
			self.space = 16 + params.rng.random()*5

		_p = [0] * len(params.RaceParams.RACES)
		for i, r in enumerate(params.RaceParams.RACES):
			if self.archetype in r.preferred_locations:
				_p[i] = 3.0
			elif self.archetype in r.hated_locations:
				_p[i] = 1.0
			else:
				_p[i] = 2.0

		self.base_population_distribution = {}
		for i, r in enumerate(params.RaceParams.RACES):
			self.base_population_distribution[r] = _p[i]/sum(_p)

	def add_landmark(self, lm):
		if lm in self.landmarks:
			return 
		
		self.landmarks.append(lm)
		self.attractiveness += lm.happiness_value

	def in_area_of_influence(self, map_pos):
		p = Point(map_pos[0], map_pos[1])
		poly = Polygon(self.area_of_influence)
		if poly.contains(p):
			return True
		return False

	def to_string_list(self):
		lines = []
		lines.append(self.name)
		lines.append("Attractiveness: {}; Space available: {}".format(self.attractiveness, self.space))
		for lm in self.landmarks:
			lines.append(lm.to_string())
		return lines

class Community(object):

	global_id = 0

	class CommunityLog(console.Console):
		class CommunityLogDatetime(object):
			def __init__(self, simu_day):
				self.simu_day = simu_day

				self.day   = ((self.simu_day % 365) % 30) + 1
				self.month = (((self.simu_day % 365) // 30) % 12) + 1
				self.year  = (self.simu_day // 365) + 1

		def __init__(self):
			super(Community.CommunityLog, self).__init__()
			self.max = -1

		def get_date_to_string(day):
			_year = math.floor(day/(12*28))
			_month = (math.floor(day/28))%12
			_day = day%28
			d = Community.CommunityLog.CommunityLogDatetime(day)
			h = "{:02d}/{:02d}/{:04d}".format(d.day, d.month, d.year)
			return h

		def set_head(self, day):
			self.line_head = "{} - ".format(Community.CommunityLog.get_date_to_string(day))

		def log(self, s, day):
			self.set_head(day)
			l = "{}{}{}".format(self.line_head, s, self.line_tail)
			self.lines.append(l)

		def push_back(self, s, day):
			self.log(s, day)

		def push_front(self, s, day):
			self.set_head(day)
			l = "{}{}{}".format(self.line_head, s, self.line_tail)
			self.lines.insert(0, l)

		def insert(self, s, pos, day):
			self.set_head(day)
			l = "{}{}{}".format(self.line_head, s, self.line_tail)
			_pos = utils.clamp(pos, 0, len(self.lines)-1)
			self.lines.insert(_pos, l)

	def __init__(self, name, location, kingdom, poparch):

		self.name = name
		self.id = Community.global_id
		Community.global_id += 1

		self.location = location
		self.location.community = self

		self.kingdom = kingdom

		self.model = None

		self.pop_archetype = poparch
		self.population = {}
		self.space_used = 0

		self.social_ascension_index = 1.0
		self.social_decay_index     = 1.0

		self.init_population()

		self.ressource_production_bonus = {}
		self.ressource_storage_bonus = {}
		self.ressource_stockpile = {}
		for r in set(params.ModelParams.RESSOURCES)-set([params.ModelParams.WEALTH]):
			self.ressource_production_bonus[r] = 0.0
			self.ressource_storage_bonus[r] = 0.0
			self.ressource_stockpile[r] = self.location.base_storage[r] / 8.0
		self.ressource_production_bonus[params.ModelParams.WEALTH] = 0.0
		self.ressource_storage_bonus[params.ModelParams.WEALTH] = 0.0
		self.ressource_stockpile[params.ModelParams.WEALTH] = 0.0

		self.actual_storage = {}
		self.actual_production = {}

		self.trade_factor = 0.05 + self.location.trade_factor

		self.effective_gain = {}
		self.effective_consumption = {}
		for r in params.ModelParams.RESSOURCES:
			self.effective_gain[r] = {}
		for r in params.ModelParams.RESSOURCES:
			self.effective_consumption[r] = {}

		self.ressources_prev_net_worth = {}
		for r in params.ModelParams.RESSOURCES:
			self.ressources_prev_net_worth[r] = 0

		self.happiness_details = {}
		self.happiness = 0
		self.happiness_from_surplus = {}
		for r in params.ModelParams.RESSOURCES:
			self.happiness_from_surplus[r] = 0
		self.net_growth_rate   = 0
		self.population_control = 0
		self.actual_birth_rate = 0
		self.actual_death_rate = 0

		self.food_shortage = 0
		self.food_consumption_per_pop_min = 0.005
		self.food_consumption_per_pop_max = 0.03
		self.food_consumption_per_pop_step = 0.001

		# self.food_consumption_per_pop = self.food_consumption_per_pop_min
		self.food_consumption_per_pop = self.food_consumption_per_pop_min

		self.food_consumption_from_pop = 0

		self.randomness_of_life = {}
		self.randomness_of_life["birth_rate_factor"] = {}
		self.randomness_of_life["death_rate_factor"] = {}
		for race in params.RaceParams.RACES:
			self.randomness_of_life["birth_rate_factor"][race] = 0
			self.randomness_of_life["death_rate_factor"][race] = 0
		self.race_growth_rate = {}

		self.caravan_arrived_countdown_max = 30
		self.caravan_arrived_countdown = 0	

		self.show_pop_details       = False
		self.show_happiness_details = False
		self.show_ressources        = False
		self.show_landmarks         = False
		self.show_events            = False
		self.show_kingdom           = False
		self.show_kingdom_details   = False

		self.event_log = Community.CommunityLog()

	def reset_show_booleans(self):
		self.show_pop_details       = False
		self.show_happiness_details = False
		self.show_ressources        = False
		self.show_landmarks         = False
		self.show_events            = False

	def init_population(self, pop_archetype=None):
		if pop_archetype != None:
			self.pop_archetype = pop_archetype

		self.kingdom.set_main_race(self.location)

		def get_class_dist(_race):
			class_dist = {}
			print(self.kingdom.main_race.name)
			if _race == self.kingdom.main_race and self.location.archetype in _race.preferred_locations:
				class_dist[params.SocialClassParams.NOBILITY]    = 0.35
				class_dist[params.SocialClassParams.BOURGEOISIE] = 0.30
				class_dist[params.SocialClassParams.MIDDLE]      = 0.20
				class_dist[params.SocialClassParams.POOR]        = 0.15
			elif _race == self.kingdom.main_race and self.location.archetype in _race.hated_locations:
				class_dist[params.SocialClassParams.NOBILITY]    = 0.70
				class_dist[params.SocialClassParams.BOURGEOISIE] = 0.20
				class_dist[params.SocialClassParams.MIDDLE]      = 0.10
				class_dist[params.SocialClassParams.POOR]        = 0.00
			elif _race == self.kingdom.main_race:
				class_dist[params.SocialClassParams.NOBILITY]    = 0.45
				class_dist[params.SocialClassParams.BOURGEOISIE] = 0.25
				class_dist[params.SocialClassParams.MIDDLE]      = 0.20
				class_dist[params.SocialClassParams.POOR]        = 0.10
			elif self.location.archetype in _race.preferred_locations:
				class_dist[params.SocialClassParams.NOBILITY]    = 0.08
				class_dist[params.SocialClassParams.BOURGEOISIE] = 0.20
				class_dist[params.SocialClassParams.MIDDLE]      = 0.42
				class_dist[params.SocialClassParams.POOR]        = 0.30
			elif self.location.archetype in _race.hated_locations:
				class_dist[params.SocialClassParams.NOBILITY]    = 0.00
				class_dist[params.SocialClassParams.BOURGEOISIE] = 0.15
				class_dist[params.SocialClassParams.MIDDLE]      = 0.25
				class_dist[params.SocialClassParams.POOR]        = 0.60
			else:
				class_dist[params.SocialClassParams.NOBILITY]    = 0.05
				class_dist[params.SocialClassParams.BOURGEOISIE] = 0.15
				class_dist[params.SocialClassParams.MIDDLE]      = 0.50
				class_dist[params.SocialClassParams.POOR]        = 0.30
			return class_dist

		total_pop = params.CommunityParams.BASE_POP_VALUE
		_dist = self.location.base_population_distribution

		for race in _dist:
			_total_pop_race = total_pop * _dist[race]
			self.population[race] = {}

			_class_dist = get_class_dist(race)
			for _class in _class_dist:
				self.population[race][_class] = round(_total_pop_race * _class_dist[_class])
				
		self.space_used = self.get_total_pop() / 100.0

	def get_total_pop(self):
		total = 0
		for race in self.population.keys():
			for _class in self.population[race].keys():
				total += math.floor(self.population[race][_class])

		return total

	def get_total_pop_race(self, race):
		total = 0
		for _class in self.population[race]:
			total += math.floor(self.population[race][_class])
		return total
	
	def get_total_pop_class(self, _class):
		total = 0
		for race in self.population.keys():
			total += math.floor(self.population[race][_class])
		return total

	def get_pop_proportion(self):
		pop_prop = {}

		total = self.get_total_pop()

		for race in self.population.keys():
			try:
				pop_prop[race] = int(self.get_total_pop_race(race)) / total
			except ZeroDivisionError:
				pop_prop[race] = 0

		return pop_prop

	def update_actual_prod_and_store(self):
		for r in params.ModelParams.RESSOURCES:
			self.actual_production[r] = self.location.base_production[r] + (self.ressource_production_bonus[r])
			# self.actual_production[r] = self.location.base_production[r] + (self.ressource_production_bonus[r])
			self.actual_storage[r] = self.location.base_storage[r] * (1.0 + self.ressource_storage_bonus[r])

	def update_production_bonus(self):
		for r in self.ressource_production_bonus.keys():
			self.ressource_production_bonus[r] = self.get_total_pop()/100.0 * self.location.bonus_per_100_pop[r]
	
	def update_pops(self):
		# Update pops
		
		# br increases as accumulated wealth decreases
		base_birth_rate = 1.0
		brf_space = 0
		if self.space_used < (self.location.space*0.75):
			brf_space = (1 - (self.space_used / self.location.space)) * 0.5
		brf_wealth = (self.ressource_stockpile[params.ModelParams.WEALTH]/1000.0)
		brf_happ = 0
		if self.happiness > 50:
			brf_happ = self.happiness / 100.0
		
		brf_food = self.ressource_stockpile[params.ModelParams.FOOD]/1000.0
		# brf_food = self.food_shortage

		self.actual_birth_rate = base_birth_rate * (1 + (brf_space + brf_wealth + brf_happ + brf_food))

		# dr increases as accumulated wealth decreases
		base_death_rate = base_birth_rate * 0.52
		drf_space = 0
		if self.space_used >= (self.location.space*0.5):
			drf_space = (self.space_used / self.location.space)
		drf_wealth = 1 - (self.ressource_stockpile[params.ModelParams.WEALTH]/self.actual_storage[params.ModelParams.WEALTH])
		drf_food = (self.food_shortage*7) * 0.1
		# drf_food = 0

		drf_happ = 0
		if self.happiness < 0:
			drf_happ = abs(self.happiness * 0.2)

		self.actual_death_rate = base_death_rate * (1 + drf_space + drf_wealth + drf_food + drf_happ)

		# self.population_control = 0
		# if self.actual_death_rate * 0.9 > self.actual_birth_rate:
		# 	net_food = sum(self.effective_gain[params.ModelParams.FOOD].values()) - sum(self.effective_consumption[params.ModelParams.FOOD].values())
		# 	# if(self.location.archetype==params.LocationParams.DESERT):
		# 	# 	print(net_food)
		# 	if net_food <= 0:
		# 		self.population_control = (self.actual_birth_rate-self.actual_death_rate)


		if self.get_total_pop() <= 0:
			self.net_growth_rate = 0

		self.net_growth_rate = (self.actual_birth_rate-self.actual_death_rate) + self.population_control

		for race in self.population.keys():

			_prefered_location_factor = 1.0
			if self.location.archetype in race.preferred_locations:
				_prefered_location_factor += params.RaceParams.RACE_PREFERRED_LOCATION_FACTOR
			elif self.location.archetype in race.hated_locations:
				_prefered_location_factor -= params.RaceParams.RACE_PREFERRED_LOCATION_FACTOR

			if self.kingdom.main_race == race:
				_prefered_location_factor += params.RaceParams.KINGDOM_MAIN_RACE_BOOST


			_race_birth_rate = (self.actual_birth_rate*race.positive_growth_rate_factor*_prefered_location_factor)
			_race_death_rate = (self.actual_death_rate*race.negative_growth_rate_factor)

			_avg_birth_rate_race = 0
			_avg_death_rate_race = 0

			for social_class in self.population[race].keys():

				_race_class_birth_rate = _race_birth_rate * social_class.birth_rate_factor
				_race_class_death_rate = _race_death_rate * social_class.death_rate_factor

				_race_class_birth_rate *= (1 + self.randomness_of_life["birth_rate_factor"][race])
				_race_class_death_rate *= (1 + self.randomness_of_life["death_rate_factor"][race])


				_avg_birth_rate_race += _race_class_birth_rate
				_avg_death_rate_race += _race_class_death_rate

				_race_class_growth_rate = _race_class_birth_rate - _race_class_death_rate
				_race_class_growth_rate += self.population_control


				self.population[race][social_class] = float(self.population[race][social_class]) + ((float(self.population[race][social_class]) * (_race_class_growth_rate/100.0))/4.0)
			
			# self.race_growth_rate[race] = (_race_birth_rate - _race_death_rate)
			self.race_growth_rate[race] = ((_avg_birth_rate_race/len(self.population[race].keys())) - (_avg_death_rate_race/len(self.population[race].keys())))
		
		self.space_used = self.get_total_pop() / 100.0

	def migration(self):
		return
		# pops = []
		# happ = []
		# for nl in self.location.neighbouring_locations:
		# 	ncomm = nl.community
		# 	if ncomm != None:
		# 		_data = {}
		# 		for r in params.RaceParams.RACES:
		# 			_data[r] = (ncomm.get_total_pop() * ncomm.get_pop_proportion()[r]) * (1.0-utils.normalise(ncomm.happiness, mini=-100, maxi=100)) * 0.01
		# 		pops.append(_data)
		# 		happ.append(ncomm.happiness)


		# total_pop = {}
		# for i, _d in enumerate(pops):
		# 	for k in _d:
		# 		try:
		# 			total_pop[k] += _d[k]
		# 		except KeyError:
		# 			total_pop[k] = _d[k]

		# # pp = pprint.PrettyPrinter(indent=4)
		# # pp.pprint(total_pop)

		# for r in params.RaceParams.RACES:
		# 	try:
		# 		self.population[r] += total_pop[r]
		# 	except KeyError:
		# 		self.population[r] = total_pop[r]

	def caravan(self):
		if self.model != None:
			_pop_number = (50 + params.rng.random()*100)
			_race = params.rng.choice(params.RaceParams.RACES)

			_nhapp = []
			for nl in self.location.neighbouring_locations:
				ncomm = nl.community
				if ncomm != None:
					_nhapp.append(ncomm.happiness)

			avg_surrounding_happ = np.mean(_nhapp)
			ash_factor = 1 - utils.normalise(avg_surrounding_happ, mini=-100, maxi=100)
			_pop_number = int(_pop_number * ash_factor)

			
			self.randomness_of_life["birth_rate_factor"][_race] += abs(self.randomness_of_life["birth_rate_factor"][_race]*0.2)

			random_proportion_noble_class       = params.rng.random()*0.05
			random_proportion_bourgeoisie_class = 0.1 + params.rng.random()*0.05
			random_proportion_middle_class      = 0.2 + params.rng.random()*0.3
			random_proportion_poor_class        = 1.0 - (random_proportion_middle_class+random_proportion_bourgeoisie_class+random_proportion_noble_class)
			
			noble_pop = _pop_number * random_proportion_noble_class
			self.population[_race][params.SocialClassParams.NOBILITY] += noble_pop
			
			bourgeois_pop = _pop_number * random_proportion_bourgeoisie_class
			self.population[_race][params.SocialClassParams.BOURGEOISIE] += bourgeois_pop

			middle_pop = _pop_number * random_proportion_middle_class
			self.population[_race][params.SocialClassParams.MIDDLE] += middle_pop

			poor_pop = _pop_number * random_proportion_poor_class
			self.population[_race][params.SocialClassParams.POOR] += poor_pop

			self.caravan_arrived_countdown = self.caravan_arrived_countdown_max
			myglobals.LogConsoleInst.log(f"A caravan of {_pop_number} {_race.name} arrived in {self.name}.", self.model.day)
			self.event_log.log(f"A caravan of {_pop_number} {_race.name} arrived ({int(noble_pop)} {params.SocialClassParams.NOBILITY.adjective_short}, {int(bourgeois_pop)} {params.SocialClassParams.BOURGEOISIE.adjective_short}, {int(middle_pop)} {params.SocialClassParams.MIDDLE.adjective_short} and {int(poor_pop)} {params.SocialClassParams.POOR.adjective_short}).", self.model.day)

	def update_social_indexes(self):
		nobility_prop = (self.get_total_pop_class(params.SocialClassParams.NOBILITY)/self.get_total_pop())
		wealth_factor  = self.ressource_stockpile[params.ModelParams.WEALTH] / self.actual_storage[params.ModelParams.WEALTH]

		self.social_ascension_index = (1.0 * ((1.0-nobility_prop) * wealth_factor)) + self.actual_production[params.ModelParams.WEALTH]

		poor_prop = (self.get_total_pop_class(params.SocialClassParams.POOR)/self.get_total_pop())

		self.social_decay_index = 1.0 + (poor_prop-nobility_prop) + (1.0-wealth_factor) + sum(list(self.effective_consumption[params.ModelParams.WEALTH].values()))

	def social_evolution(self):
		# Ascend
		for _race in params.RaceParams.RACES:
			if self.get_total_pop_race(_race) > 0:

				ascend_random_factor  = params.randrange(0.8, 1.2)
				descend_random_factor = params.randrange(0.8, 1.2)
				if self.kingdom.main_race == _race and self.location.archetype in _race.preferred_locations:
					ascend_random_factor  = params.randrange(1.2, 1.6)
					descend_random_factor = params.randrange(0.4, 0.8)
				elif self.kingdom.main_race == _race and self.location.archetype in _race.hated_locations:
					ascend_random_factor  = params.randrange(0.9, 1.3)
					descend_random_factor = params.randrange(0.7, 1.1)
				elif self.kingdom.main_race == _race:
					ascend_random_factor  = params.randrange(0.9, 1.2)
					descend_random_factor = params.randrange(0.8, 1.1)
				elif self.location.archetype in _race.preferred_locations:
					ascend_random_factor  = params.randrange(1.0, 1.1)
					descend_random_factor = params.randrange(0.9, 1.0)
				elif self.location.archetype in _race.hated_locations:
					ascend_random_factor  = params.randrange(0.9, 1.0)
					descend_random_factor = params.randrange(1.0, 1.1)

				_poors_ascend  = (self.population[_race][params.SocialClassParams.POOR] * ((self.social_ascension_index*ascend_random_factor)/100.0))

				_middle_ascend  = (self.population[_race][params.SocialClassParams.MIDDLE] * ((self.social_ascension_index*ascend_random_factor)/100.0))
				_middle_descent = (self.population[_race][params.SocialClassParams.MIDDLE] * ((self.social_decay_index*descend_random_factor)/100.0))

				_bourgeois_ascend  = (self.population[_race][params.SocialClassParams.BOURGEOISIE] * ((self.social_ascension_index*ascend_random_factor)/100.0))
				_bourgeois_descent = (self.population[_race][params.SocialClassParams.BOURGEOISIE] * ((self.social_decay_index*descend_random_factor)/100.0))

				_nobles_descend = self.population[_race][params.SocialClassParams.NOBILITY] * ((self.social_decay_index*descend_random_factor)/100.0)

				self.population[_race][params.SocialClassParams.POOR]        = max(0, self.population[_race][params.SocialClassParams.POOR]        + math.floor(_middle_descent - _poors_ascend))
				self.population[_race][params.SocialClassParams.MIDDLE]      = max(0, self.population[_race][params.SocialClassParams.MIDDLE]      + math.floor((_poors_ascend + _bourgeois_descent) - (_middle_ascend + _middle_descent)))
				self.population[_race][params.SocialClassParams.BOURGEOISIE] = max(0, self.population[_race][params.SocialClassParams.BOURGEOISIE] + math.floor((_middle_ascend + _nobles_descend) - (_bourgeois_ascend + _bourgeois_descent)))
				self.population[_race][params.SocialClassParams.NOBILITY]    = max(0, self.population[_race][params.SocialClassParams.NOBILITY]    + math.floor(_bourgeois_ascend - _nobles_descend))

				# print(math.floor(_middle_descent - _poors_ascend))
				# print(math.floor((_poors_ascend + _bourgeois_descent) - (_middle_ascend + _middle_descent)))
				# print(math.floor((_middle_ascend + _nobles_descend) - (_bourgeois_ascend + _bourgeois_descent)))
				# print(math.floor(_bourgeois_ascend - _nobles_descend))


		# Descend

	def get_trade_factor(self):
		trade_factor_list = []
		for nloc in self.location.neighbouring_locations:
			if nloc.community != None:
				trade_factor_list.append(nloc.community.trade_factor)

		return np.mean(trade_factor_list)

	def a_day_passed(self):
		if self.location == None:
			return

		for r in params.ModelParams.RESSOURCES:
			self.effective_gain[r] = {}
		for r in params.ModelParams.RESSOURCES:
			self.effective_consumption[r] = {}

		# Update production bonus

		self.update_production_bonus()

		self.update_actual_prod_and_store()

		# Consume food 

		self.food_consumption_from_pop = (self.get_total_pop() * self.food_consumption_per_pop) / 7.0
		self.effective_consumption[params.ModelParams.FOOD]["POP"] = self.food_consumption_from_pop

		# Production

		for r in params.ModelParams.RESSOURCES:
			self.effective_gain[r]["PRODUCTION"] = self.actual_production[r]

		for r in set(params.ModelParams.RESSOURCES)-set([params.ModelParams.WEALTH]):
			self.ressource_stockpile[r] = utils.clamp(self.ressource_stockpile[r] + sum(self.effective_gain[r].values()) - sum(self.effective_consumption[r].values()), 0, self.actual_storage[r])	
			if self.ressource_stockpile[r] >= self.actual_storage[r]:
				if r != params.ModelParams.FOOD:
					self.effective_gain[params.ModelParams.WEALTH]["SURPLUS_SELL"] = sum(self.effective_gain[r].values()) - sum(self.effective_consumption[r].values())*self.get_trade_factor()
					self.effective_consumption[r]["SURPLUS_SELL"] = sum(self.effective_gain[r].values())

		if self.ressource_stockpile[params.ModelParams.FOOD] <= 0:
			self.food_shortage += 1.0/7.0
		else:
			self.food_shortage = max(0, (self.food_shortage - 1.0))

		# Update food consumption
		fcpp_new_increased_value = min(self.food_consumption_per_pop + self.food_consumption_per_pop_step, self.food_consumption_per_pop_max)
		fcpp_new_decreased_value = max(self.food_consumption_per_pop - self.food_consumption_per_pop_step, self.food_consumption_per_pop_min)
		
		new_inc_fc = (self.get_total_pop() * fcpp_new_increased_value) / 7.0
		new_dec_fc = (self.get_total_pop() * fcpp_new_decreased_value) / 7.0

		new_consump_inc = self.effective_consumption[params.ModelParams.FOOD].copy()
		new_consump_inc["POP"] = new_inc_fc

		new_consump_dec = self.effective_consumption[params.ModelParams.FOOD].copy()
		new_consump_dec["POP"] = new_dec_fc

		if (sum(self.effective_gain[params.ModelParams.FOOD].values()) - sum(self.effective_consumption[params.ModelParams.FOOD].values())) > 0:
			if (sum(self.effective_gain[params.ModelParams.FOOD].values()) - sum(new_consump_inc.values())) > 0:
				self.food_consumption_per_pop = fcpp_new_increased_value
		else:
			self.food_consumption_per_pop = fcpp_new_decreased_value

		# Consume params.ModelParams.WEALTH
		wealth_consumption = (self.get_total_pop() * 0.01) / 30.0
		wc_happiness_factor = 0
		if self.happiness > 0:
			wc_happiness_factor = min(0, -1 * ((self.happiness - 25) / 100.0))
		elif self.happiness <= 0:
			wc_happiness_factor = abs(((self.happiness) / 100.0))
		# print(wc_happiness_factor)

		self.effective_consumption[params.ModelParams.WEALTH]["POP"] = wealth_consumption * (1 + wc_happiness_factor)
		
		# Calculate Wealth
		self.ressource_stockpile[params.ModelParams.WEALTH] = utils.clamp(self.ressource_stockpile[params.ModelParams.WEALTH] + sum(self.effective_gain[params.ModelParams.WEALTH].values()) - sum(self.effective_consumption[params.ModelParams.WEALTH].values()), 0, self.actual_storage[params.ModelParams.WEALTH])

		# CALCULATE HAPPINESS
		# Happ from location
		self.happiness = self.location.attractiveness
		self.happiness_details["LOCATION_ATTRACTIVENESS"] = self.location.attractiveness

		# Unrest from food shortage
		self.happiness -= self.food_shortage*2
		self.happiness_details["FOOD_SHORTAGE"] = -self.food_shortage*2

		# Happ from stockpiled wealth
		# _v = self.ressource_stockpile[params.ModelParams.WEALTH] * 0.2
		if self.ressource_stockpile[params.ModelParams.WEALTH] > 0:
			_v = math.log(self.ressource_stockpile[params.ModelParams.WEALTH]) * 5
		else:
			_v = 0
		self.happiness += _v
		self.happiness_details["STOCKPILES_WEALTH"] = _v

		# Unrest from overpopulation
		# overpop_unrest = self.location.space - self.space_used
		overpop_unrest = -(self.space_used / self.location.space)
		overpop_unrest *= 50
		self.happiness += overpop_unrest
		self.happiness_details["OVERPOPULATION"] = overpop_unrest

		# Happ from wealth consumption
		if self.ressource_stockpile[params.ModelParams.WEALTH] > 0:
			_v = sum(self.effective_consumption[params.ModelParams.WEALTH].values()) * 10
			self.happiness += _v
			self.happiness_details["WEALTH_CONSUMPTION"] = _v

		# Happiness from food situation
		happ_food_factor = (self.food_consumption_per_pop - self.food_consumption_per_pop_min) * 1000 * 2
		happ_food_factor = round(happ_food_factor)
		self.happiness += happ_food_factor
		self.happiness_details["FOOD_SITUATION"] = happ_food_factor

		# Unrest due to lack of stored food
		stored_food_unrest = (self.ressource_stockpile[params.ModelParams.FOOD] - self.actual_storage[params.ModelParams.FOOD])
		stored_food_unrest = stored_food_unrest*0.1
		self.happiness += stored_food_unrest
		self.happiness_details["STORED_FOOD_UNREST"] = stored_food_unrest

		# Clamp happiness
		self.happiness = utils.clamp(self.happiness, -100, 100)
		if self.get_total_pop() <= 0:
			self.happiness = 0

		
		# Save previous net worth
		for r in params.ModelParams.RESSOURCES:
			self.ressources_prev_net_worth[r] = sum(self.effective_gain[r].values()) - sum(self.effective_consumption[r].values())

		# Update misc. count down/up
		self.caravan_arrived_countdown = max(0, self.caravan_arrived_countdown - 1)

	def a_week_passed(self):
		self.update_pops()
		if params.rng.random() < (0.02/4.0):
			self.caravan()

	def a_month_passed(self):
		for race in params.RaceParams.RACES:
			main_race_influence = 0
			if race == self.kingdom.main_race:
				main_race_influence = 0

			self.randomness_of_life["birth_rate_factor"][race] += ((-0.03 + params.rng.random() * 0.06) + (0.03*main_race_influence)) / 3.0
			self.randomness_of_life["death_rate_factor"][race] += ((-0.03 + params.rng.random() * 0.06) - (0.00*main_race_influence)) / 3.0

			self.randomness_of_life["birth_rate_factor"][race] = utils.clamp(self.randomness_of_life["birth_rate_factor"][race], 0, 0.2)
			self.randomness_of_life["death_rate_factor"][race] = utils.clamp(self.randomness_of_life["death_rate_factor"][race], 0, 0.2)
		
		# self.migration()

	def a_quarter_passed(self):
		pass

	def a_semester_passed(self):
		self.update_social_indexes()
		self.social_evolution()

	def a_year_passed(self):
		pass

	def to_string(self):
		s = "{}\n".format(self.name)
		s += "{}\n".format(params.LocationParams.ARCHETYPES_STR[self.location.archetype])
		str_popprop = ""
		popprop = self.get_pop_proportion()
		for race in popprop:
			str_popprop += "{:.1f}% {} ({})".format(popprop[race]*100, race.name, int(self.get_total_pop_race(race)))
		s += "{} inhabitants : {}\n".format(self.get_total_pop(), str_popprop)
		s += "Happiness : {:.2f}; Growth rate : {:.2f}; Space : {:.2f}/{:.2f}\n".format(self.happiness, self.net_growth_rate, self.space_used, self.location.space)
		for r in self.ressource_stockpile:
			s += "{:.0f}/{:.0f} (+{:.3f}; {:.3f}+{:.3f}-{:.3f})\n".format(self.ressource_stockpile[r], self.actual_storage[r], sum(self.effective_gain[r].values())-sum(self.effective_consumption[r].values()), self.location.base_production[r], self.ressource_production_bonus[r], sum(self.effective_consumption[r].values()))

		s += "\nFood Shortage value:{}; Fcpp:{:.3f}\n".format(self.food_shortage, self.food_consumption_per_pop)

		return s

	def to_string_list(self, used_font=None):
		lines = []

		tab       = "      "
		small_tab = "   "

		def get_str_offset(_el, _list, _font):
			if _font == None:
				return ''
			_max_name_length = max([_font.size(e)[0] for e in _list])
			offset = ''
			tw, _ = _font.size(_el + offset)
			while tw <= _max_name_length:
				offset += ' '
				tw, _ = _font.size(_el + offset)
			return offset

		# lines.append("{}".format(self.name))
		lines.append("{} at {} ({}, {:.02f})".format(self.name, self.location.name, params.LocationParams.ARCHETYPES_STR[self.location.archetype].title(), self.location.base_attractiveness))
		lines.append(f"{'▼' if self.show_kingdom else '►'} {self.kingdom.name} (K to {'hide' if self.show_kingdom else 'show'})")
		if self.show_kingdom:
			lines.append(f"{tab}a{'' if self.kingdom.main_race.name_adjective.lower()[0] in ['d', 'h'] else 'n'} {self.kingdom.main_race.name_adjective} {self.kingdom.gov_type_str} {self.kingdom.governement_name} ({params.KingdomParams.POLITICS_STR[self.kingdom.main_politic]} {params.KingdomParams.POLITICS_STR[self.kingdom.secondary_politic]})")
			lines.append(f"{tab}Relations: (D to {'hide' if self.show_kingdom_details else 'show'} details)")
			for k in self.kingdom.relations:
				lines.append(f"{tab}{'▼' if self.show_kingdom_details else '►'} {k.name}: {sum(self.kingdom.relations[k].values())}")
				if self.show_kingdom_details:
					s = []
					max_details_per_line = 5
					for i, detail in enumerate(self.kingdom.relations[k]):
						_t = f"{tab}{small_tab}" if i%max_details_per_line == 0 else ", "
						_s = f"{_t}{detail}: {self.kingdom.relations[k][detail]}"

						if i == 0:
							s.append("")
							s[-1] += _s
						elif i%max_details_per_line == 0:
							s.append("")
							s[-1] += _s
						else:
							s[-1] += _s
					for _s in s:
						lines.append(_s)

		if self.show_happiness_details:
			lines.append(f"▼ Happiness: {self.happiness:.2f} (H to hide)")
			for k in self.happiness_details:
				lines.append(f"{tab}{k}: {self.happiness_details[k]:.2f}")
		else:
			lines.append(f"► Happiness: {self.happiness:.2f} (H to show)")

		if self.show_pop_details:
			lines.append("▼ Population: {} inhabitants (P to hide)".format(self.get_total_pop()))
			str_popprop = ""
			popprop = self.get_pop_proportion()
			for race in sorted(popprop, key=popprop.get, reverse=True):
				if popprop[race] != 0:
					# str_popprop += f"{popprop[race]*100:.1f}% {race.name} ({int(self.get_total_pop_race(race))}), "
					str_popprop += f"{popprop[race]*100:.1f}% {race.name}, "
			lines.append(f"{tab}{str_popprop[:-2]}")

			if used_font != None:
				_class_race_offset_pxvalue = (max([used_font.size(_class.name)[0] for _class in params.SocialClassParams.CLASSES]))
				_class_race_offset = ""
				while used_font.size(_class_race_offset)[0] < _class_race_offset_pxvalue:
					_class_race_offset += " "
				
				_race_header = f"{tab}{_class_race_offset}  " + str([_r.name for _r in params.RaceParams.RACES] + ['Total']).replace('\'', '').replace("[", '').replace("]",'').replace(",", " |")
				_race_value  = f"{tab}{_class_race_offset} " + str([f"{int(self.get_total_pop_race(_r))}{get_str_offset(str(int(self.get_total_pop_race(_r))), [_r.name], used_font)}" for _r in params.RaceParams.RACES] + [self.get_total_pop()]).replace('\'', '').replace("[", '').replace("]",'').replace(",", " |")
				
				_class_prop  = []
				for _sc in params.SocialClassParams.CLASSES:
					_class_name_offset = get_str_offset(_sc.name, [_c.name for _c in params.SocialClassParams.CLASSES], used_font)
					_s = f"{tab}{_sc.name}{_class_name_offset}:"
					for _race in params.RaceParams.RACES:
						value = self.population[_race][_sc]
						try:
							number_modf = math.modf((math.floor(value)/self.get_total_pop_race(_race))*100)
							_s += f" {int(number_modf[1]):02d}.{math.floor(number_modf[0]*10):01d}%     "
						except ZeroDivisionError:
							_s += f" N/A        "
						# _s += f" {math.floor(value)}    "
					_class_prop.append(_s)

				for _si, _c in zip(enumerate(_class_prop), params.SocialClassParams.CLASSES):
					_class_prop[_si[0]] += f"{(self.get_total_pop_class(_c)/self.get_total_pop())*100:.1f}%"
					# _class_prop[_si[0]] += f"{self.get_total_pop_class(_c)}%"

				lines.append(_race_header)
				lines.append(_race_value)
				for _s in _class_prop:
					lines.append(_s)

			lines.append(f"{tab}Social ascension: {self.social_ascension_index:.2f}, Social decay: {self.social_decay_index:.2f}")

			lines.append("{}Basic growth rate: {:+.2f} ({:.2f}-{:.2f})".format(tab, self.net_growth_rate, self.actual_birth_rate, self.actual_death_rate))
			s = ""
			for race in params.RaceParams.RACES:
				try:
					s += f"   {race.name}: {self.race_growth_rate[race]:.2f}, "
				except KeyError:
					pass
			if s != "":
				lines.append(f"{tab}GR/race: " + s[:-2])
			lines.append(f"{tab}Space used: {self.space_used:.2f}/{self.location.space:.2f}")
		else:
			lines.append("► Population: {} inhabitants (P to show)".format(self.get_total_pop()))
		
		# lines.append("Randomness of Life: {:+.2f}, Pop. control: {:+.2f}".format(np.mean(list(self.randomness_of_life["birth_rate_factor"].values())) - np.mean(list(self.randomness_of_life["death_rate_factor"].values())), self.population_control))
		if self.show_ressources:
			lines.append("▼ Ressources (R to hide)")
			for r in self.ressource_stockpile:
				try:
					lines.append("{}{} : {:.0f}/{:.0f} ({:+.3f}; {:.3f}+{:.3f}-{:.3f})".format(tab, params.ModelParams.RESSOURCES_STR[r].lower().title(), self.ressource_stockpile[r], self.actual_storage[r], sum(self.effective_gain[r].values())-sum(self.effective_consumption[r].values()), self.location.base_production[r], self.ressource_production_bonus[r], sum(self.effective_consumption[r].values())))
				except KeyError:
					pass
		else:
			lines.append("► Ressources (R to show)")

		# lines.append("Food Shortage :{:.3f}; Fcpp:{:.3f}".format(self.food_shortage, self.food_consumption_per_pop))

		if len(self.location.landmarks) > 0:
			if self.show_landmarks:
				lines.append("▼ Landmarks, happiness mod. {:+.02f}. (L to hide)".format(sum([lm.happiness_value for lm in self.location.landmarks])))
				for lm in sorted(self.location.landmarks, key=lambda x: x.happiness_value, reverse=True):
					lines.append(tab + lm.to_string())
			else:
				lines.append("► Landmarks, happiness mod. {:+.02f}. (L to show)".format(sum([lm.happiness_value for lm in self.location.landmarks])))


		nb_to_show = 5
		if self.show_events:
			lines.append(f"▼ Event log, entr{'y' if len(self.event_log.get_lines())<=1 else 'ies'} {max(0 if len(self.event_log.get_lines())==0 else 1, len(self.event_log.get_lines()) - nb_to_show + 1)} to {len(self.event_log.get_lines())}. (O to {'hide' if self.show_events else 'show'})")
			for l in self.event_log.get_lines()[-nb_to_show:]:
				lines.append(f"{tab}{l}")
		else:
			lines.append(f"► Event log, {len(self.event_log.get_lines())} entr{'y' if len(self.event_log.get_lines())<=1 else 'ies'}. (O to {'hide' if self.show_events else 'show'})")


		return lines

	def serialise(self, header=False):

		if header:
			s = "id, Total pop, Happiness, Net growth rate,"
			for r in self.ressource_stockpile:
				s += "stpl" + str(r) + ","
			for r in self.effective_gain:
				s += "ntpr" + str(r) + ","

			s += "% space used"

			return s

		s = ""

		s += "{},{},{},{},".format(self.id, self.get_total_pop(),self.happiness,self.net_growth_rate)
		for r in self.ressource_stockpile:
			tmp = "{},".format(self.ressource_stockpile[r])
			s += tmp
		for r in self.effective_gain:
			tmp = "{},".format(sum(self.effective_gain[r].values()) - sum(self.effective_consumption[r].values()))
			s += tmp
		
		s += str(self.space_used / self.location.space)

		return s

class Kingdom(object):

	global_id = 0

	def __init__(self, name):
		self.name = name
		self.id = Kingdom.global_id
		Kingdom.global_id += 1
		self.communities = []

		self.main_race = None

		self.governement       = params.KingdomParams.NOGOV
		self.governement_name  = params.rng.choice(params.KingdomParams.GOVERNEMENTS_STR[self.governement])

		self.main_politic      = params.KingdomParams.NOPOL
		self.secondary_politic = params.KingdomParams.NOPOL

		self.gov_type_str = "Empty gov. type"


		self.init_gov_and_politics()

		self.relations = {}

	def init_gov_and_politics(self):
		# self.governement  = params.rng.choice(params.KingdomParams.GOVERNEMENTS)

		self.main_politic      = params.rng.choice(params.KingdomParams.POLITICS)
		self.secondary_politic = params.rng.choice(list(set(params.KingdomParams.POLITICS)-set([self.main_politic])))

		try:
			self.gov_type_str = params.rng.choice(params.KingdomParams.GOVERNEMENT_TYPE_STR[(self.main_politic, self.secondary_politic)])
			self.governement = params.rng.choice(params.KingdomParams.GOVERNEMENT_FROM_POLICIES[(self.main_politic, self.secondary_politic)])
		except KeyError:
			self.gov_type_str = params.rng.choice(params.KingdomParams.GOVERNEMENT_TYPE_STR[(self.secondary_politic, self.main_politic)])
			self.governement = params.rng.choice(params.KingdomParams.GOVERNEMENT_FROM_POLICIES[(self.secondary_politic, self.main_politic)])

		self.governement_name = params.rng.choice(params.KingdomParams.GOVERNEMENTS_STR[self.governement])
		self.name = self.name.upper().replace("GOVNAME", params.rng.choice(params.KingdomParams.GOVERNEMENTS_STR[self.governement])).title()

	def generate_name(self):
		govtype = self.gov_type_str
		gov     = self.governement_name

		govadj  = params.rng.choice(["", params.rng.choice([self.main_race.name_adjective, params.rng.choice(params.KingdomParams.GLOBAL_KINGDOM_ADJ_ONLY), f"{self.main_race.name_adjective} {params.rng.choice(params.KingdomParams.GLOBAL_KINGDOM_ADJ_ONLY)}"], p=[0.3, 0.55, 0.15])], p=[0.5, 0.5])

		govname = params.rng.choice([params.rng.choice(self.communities).location.name, params.rng.choice(params.KingdomParams.GLOBAL_KINGDOM_NAMES_ONLY)], p=[0.3, 0.7])
		try:
			params.KingdomParams.GLOBAL_KINGDOM_NAMES_ONLY.remove(govname)
		except ValueError:
			pass

		self.name = f"The {govadj}{' ' if govadj != '' else ''}{govtype} {gov} of {govname}"

	def add_community(self, comm):
		if comm not in self.communities:
			self.communities.append(comm)

	def set_main_race(self, location):
		_dist = location.base_population_distribution
		total_pop = params.CommunityParams.BASE_POP_VALUE
		_data = {}
		for race in _dist:
			_total_pop_race = total_pop * _dist[race]
			_data[race] = _total_pop_race
		_prop = {}
		for k in _data:
			try:
				_prop[k] = _data[k] / total_pop
			except ZeroDivisionError:
				_prop[k] = 0
		_r = []
		_p = []
		for k in _prop:
			_r.append(k)
			_p.append(_prop[k])
		self.main_race = params.rng.choice(_r, p=_p)

	def get_neighbouring_kingdoms(self):
		res = set()
		for comm in self.communities:
			loc = comm.location
			for nloc in loc.neighbouring_locations:
				if nloc.community != None:
					res.add(nloc.community.kingdom)
		return list(res)

	def monthly_update(self):
		nkingdom = self.get_neighbouring_kingdoms()
		for k in nkingdom:
			try:
				self.relations[k]
			except KeyError:
				self.relations[k] = {}

			self.relations[k]["Aff.MP"] = params.KingdomParams.POLITICS_AFFINITY[self.main_politic][k.main_politic] + (params.KingdomParams.POLITICS_AFFINITY[self.main_politic][k.secondary_politic] / 2.0)
			self.relations[k]["Aff.SP"] = (params.KingdomParams.POLITICS_AFFINITY[self.secondary_politic][k.main_politic] / 2.0) + (params.KingdomParams.POLITICS_AFFINITY[self.secondary_politic][k.secondary_politic] / 4.0)
			self.relations[k]["Aff.Go"] = params.KingdomParams.GOVERNEMENTS_AFFINITY[self.governement][k.governement]

class Model(object):

	def __init__(self, map_size=20, max_location=20):
		self.is_init = False

		self.map_size = map_size

		self.nb_location  = 0
		self.nb_community = 0

		self.max_location = max_location

		self.locations   = []
		self.communities = []
		self.kingdoms    = []

		self.day = 0

		print("Creating model")

		self.map = Map(self.map_size, self.map_size, int(self.max_location*1.5))

		self.show_population = False
		self.show_race       = False
		self.show_happiness  = False

	def reset(self):
		self.nb_location  = 0
		self.nb_community = 0

		self.locations   = []
		self.communities = []
		self.kingdoms    = []

		self.day = 0

		for i in range(self.map.width):
			for j in range(self.map.height):
				self.map.get_tile(i, j).has_road = False

	def reset_show_booleans(self):
		self.show_population = False
		self.show_race       = False
		self.show_happiness  = False

	def set_map(self):
		self.map = Map(self.map_size, self.map_size, int(self.max_location*1.5))		

	def loop(self):
		if not self.is_init:
			return

		for kingdom in self.kingdoms:
			if self.day%30 == 0:
				kingdom.monthly_update()


		for community in self.communities:
			community.a_day_passed()
			if self.day%7 == 0:
				community.a_week_passed()
			if self.day%30 == 0:
				community.a_month_passed()
			if self.day%90 == 0:
				community.a_quarter_passed()
			if self.day%182 == 0:
				community.a_semester_passed()
			if self.day%365 == 0:
				community.a_year_passed()

		self.day += 1

	def random_model_map_basic(self, scale):
		# Scale indicate the highest coordinate value, so distance comparison are coherent

		#Function to check if new_pos is valid according to existing chosen positions
		def check_new_position(new_pos, pos_list, min_dist):
			for p in pos_list:
				d = utils.distance2p(new_pos, p)
				if d < min_dist:
					return False
			return True

		# Spot valid position on the map
		# Valid positions must on land, not too close to each other.

		chosen_positions = []

		flatten_tiles = list(utils.flatten(self.map.tiles))

		_continue = True

		while _continue and len(chosen_positions) < self.max_location:
			print("{} chosen positions".format(len(chosen_positions)), end='\r', flush=True)
			# Choose a random tile
			random_i = math.floor(params.rng.random() * len(flatten_tiles))
			new_pos = (flatten_tiles[random_i].x, flatten_tiles[random_i].y)
			# Get a new one until conditions are OK:
			# 		- Tile type is *not* WATER, DEEPWATER or PEAKS
			#		- New tile position is well positionned compared to chosen positions
			#		- Try x time until abandonning
			_try = 0; _max_try = 100
			while (	(
						flatten_tiles[random_i].type in [params.TileParams.WATER, params.TileParams.DEEPWATER, params.TileParams.PEAKS] 
						or not check_new_position(new_pos, chosen_positions, scale*0.05)
					)
					and _try < _max_try):
				# print("Trying for new pos... Attempt {}".format(_try), end='\r', flush=True)
				random_i = math.floor(params.rng.random() * len(flatten_tiles))
				new_pos = (flatten_tiles[random_i].x, flatten_tiles[random_i].y)
				_try += 1
			# print("")

			if _try < _max_try:
				# When tile chosen is OK, store it as 2D coordinates
				chosen_positions.append(new_pos)
			else:
				# Else break the loop
				_continue = False
		print("")

		# Generated one location per position
		# update params.LocationParams.map_position accordingly

		location_namelist = open("../data/namelists/locations.txt")
		location_names_from_file = location_namelist.readlines()
		location_namelist.close()

		location_names = params.rng.choice(location_names_from_file, len(chosen_positions), replace=False)
		location_names = [s.title() for s in location_names]

		for i, p in enumerate(chosen_positions):
			print("Set location archetype for position {}".format(i), end='\r', flush=True)

			pos_around = self.map.get_circle_around(p, self.map_size*0.02)

			data = {}
			for pa in pos_around:
				try:
					data[self.map.get_tile(pa[0], pa[1]).type] += 1
				except KeyError:
					data[self.map.get_tile(pa[0], pa[1]).type] = 1

			if params.TileParams.WATER in data.keys() or params.TileParams.DEEPWATER in data.keys():
				archetype = params.ModelParams.TILE_TYPE_TO_LOCATION_ARCHETYPE[params.TileParams.WATER]
			else:
				_t = max(data, key=data.get)
				archetype = params.ModelParams.TILE_TYPE_TO_LOCATION_ARCHETYPE[_t]
			# _t = self.map.get_tile(p[0], p[1]).type

			location = Location(archetype, location_names[i][:-1] if location_names[i][-1] == '\n' else location_names[i])
			location.map_position = p

			self.locations.append(location)
			self.nb_location += 1
		print("")

		print("Compute Voronoi to set aura of influence of each location")
		voronoi_points = []
		for loc in self.locations:
			voronoi_points.append((loc.map_position[0], loc.map_position[1]))
		voronoi_points = np.array(voronoi_points)
		voronoi = Voronoi(voronoi_points)

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

		voronoi_regions, voronoi_vertices = voronoi_finite_polygons_2d(voronoi)

		voronoi_actual_regions = []

		for reg in voronoi_regions:
			_actual_points = []
			for pi in reg:
				_actual_points.append(voronoi_vertices[pi])
			voronoi_actual_regions.append(_actual_points)

		for i, r in enumerate(voronoi_actual_regions):
			self.locations[i].area_of_influence = r

		# Set Landmarks
		print("Generate Landmarks and set their effect")

		# _landmarks = Landmark.generate(int(self.nb_location*1.5), self.map_size, self.map_size)
		# # for lm in _landmarks:
		# # 	print(lm.to_string())

		for _lm in self.map.landmarks:
			for loc in self.locations:
				if loc.in_area_of_influence((_lm.x, _lm.y)):
					loc.add_landmark(_lm)
					break


		# Generate communities
		city_namelist = open("../data/namelists/cities.txt")
		city_names_from_file = city_namelist.readlines()
		city_namelist.close()

		city_names = params.rng.choice(city_names_from_file, len(self.locations), replace=False)
		city_names = [s.title() for s in city_names]

		kingdom_namelist = open("../data/namelists/kingdoms.txt")
		kingdom_names_from_file = kingdom_namelist.readlines()
		kingdom_namelist.close()

		kingdom_names = params.rng.choice(kingdom_names_from_file, len(self.locations), replace=False)
		kingdom_names = [s.title() for s in kingdom_names]

		kingdom_colors = params.rng.choice(list(params.UserInterfaceParams.COLOR_LIST.keys()), len(self.locations), replace=False)

		for i, loc in enumerate(self.locations):
			print("Set Kingdom and create community for position {}".format(i), end='\r', flush=True)
			kingdom = Kingdom(kingdom_names[i][:-1] if kingdom_names[i][-1] == '\n' else kingdom_names[i])
			params.UserInterfaceParams.KINGDOM_TO_COLOR[kingdom.id] = kingdom_colors[i]
			community = Community(city_names[i][:-1] if city_names[i][-1] == '\n' else city_names[i], loc, kingdom, "HUMAN_CITY")
			community.model = self
			kingdom.add_community(community)
			kingdom.generate_name()
			
			self.communities.append(community)
			self.kingdoms.append(kingdom)
			self.nb_community += 1
		print("")

		self.is_init = True

	def get_kingdoms(self):
		kingdom_set = set()

		for comm in self.communities:
			kingdom_set.add(comm.kingdom)

		return list(kingdom_set)

	def to_string_summary(self, used_font=None):
		lines = []

		_total_pop = {}
		for comm in self.communities:
			for r in params.RaceParams.RACES:
				try:
					_total_pop[r] += comm.get_total_pop_race(r)
				except KeyError:
					_total_pop[r] = comm.get_total_pop_race(r)

		sum_all_pop = int(sum(list(_total_pop.values())))

		def get_str_offset(_el, _list, _font):
			if _font == None:
				return ''
			_max_name_length = max([_font.size(e)[0] for e in _list])
			offset = ''
			tw, _ = _font.size(_el + offset)
			while tw <= _max_name_length:
				offset += ' '
				tw, _ = _font.size(_el + offset)
			return offset

		lines.append(f"{'▼' if self.show_race else '►'} Races information (R to {'hide' if self.show_race else 'show'})")
		if self.show_race:
			s1 = "     "
			s2 = "     "
			for i, r in enumerate(params.RaceParams.RACES):
				if i == len(params.RaceParams.RACES)-1:
					s1 += r.name
				elif i == len(params.RaceParams.RACES)-2:
					s1 += r.name + " and "
				else:
					s1 += r.name + ", "
			lines.append(s1)

			for r in params.RaceParams.RACES:
				offset_name = get_str_offset(r.name, [_r.name for _r in params.RaceParams.RACES], used_font)
				offset_pref = get_str_offset(str([params.LocationParams.ARCHETYPES_STR[a] for a in r.preferred_locations]), [str([params.LocationParams.ARCHETYPES_STR[a] for a in r.preferred_locations]) for r in params.RaceParams.RACES], used_font)
				lines.append(f"     {r.name}{offset_name} prefs are {[params.LocationParams.ARCHETYPES_STR[a] for a in r.preferred_locations]}{offset_pref} and hated are {[params.LocationParams.ARCHETYPES_STR[a] for a in r.hated_locations]}")


		k_list = self.get_kingdoms()

		lines.append(f"{'▼' if self.show_population else '►'} Population: {sum_all_pop} inhabitants in {len(k_list)} Kingdom{'s' if len(k_list)>1 else ''} (P to {'hide' if self.show_population else 'show'})")
		if self.show_population:
			str_popprop = "     "
			for race in sorted(_total_pop, key=_total_pop.get, reverse=True):
				if _total_pop[race] != 0:
					str_popprop += "{:.0f}% {} ({:.1f}k), ".format((_total_pop[race]/sum_all_pop)*100, race.name, _total_pop[race]/1000)
			lines.append(str_popprop[:-2])
			lines.append(f"     Average population in Communities: {sum_all_pop/len(self.communities)}")
			lines.append(f"     Kingdoms:")
			data = {}
			for k in k_list:
				for c in k.communities:
					try:
						data[k] += c.get_total_pop()
					except KeyError:
						data[k] = c.get_total_pop()
			for k in data:
				offset = get_str_offset(k.name, [_k.name for _k in data.keys()], used_font)
				lines.append(f"        {k.name}{offset}: {data[k]/1000:.1f}k inhabitants")

		lines.append(f"{'▼' if self.show_happiness else '►'} Average happiness: {sum([c.happiness for c in self.communities])/len(self.communities):.2f} (H to {'hide' if self.show_happiness else 'show'})")
		if self.show_happiness:
			data = {}
			for k in k_list:
				for c in k.communities:
					try:
						data[k] += c.happiness
					except KeyError:
						data[k] = c.happiness
			for k in data:
				offset = get_str_offset(k.name, [_k.name for _k in data.keys()], used_font)
				lines.append(f"        {k.name}{offset}: {data[k]/len(k.communities):.1f} avg. happiness")

		return lines

	def get_location_by_position(self, pos):
		for l in self.locations:
			if l.map_position == pos:
				return l
		return None

	def generate_simple_connected_graph(self):
		print("Generating Graph")

		g = graph.CityGraph()

		nodes = []
		_id = 0
		for l in self.locations:
			# n = CityNode(_id)
			# n = graph.CityNode(l.name)
			n = graph.CityNode(_id)
			n.info["location"] = l

			nodes.append(n)

			_id += 1

		for c in self.communities:
			for n in nodes:
				if n.info["location"] == c.location:
					n.info["community"] = c

		for n in nodes:
			g.addNode(n)

		for n in g.nodes:
			if len(set(g.nodes)-set([n])) != 0:
				g.addEdge(n, params.rng.choice(list(set(g.nodes)-set([n]))), add_missing_nodes=False)
			g.addNode(n)

		return g

	def generate_graph_delaunay_basic(self, gen_roads):

		print("Generating Graph")

		g = graph.CityGraph()

		nodes = []
		_id = 0
		for l in self.locations:
			# n = CityNode(_id)
			# n = graph.CityNode(l.name)
			n = graph.CityNode(_id)
			n.info["location"] = l

			nodes.append(n)

			_id += 1

		for c in self.communities:
			for n in nodes:
				if n.info["location"] == c.location:
					n.info["community"] = c

		for n in nodes:
			g.addNode(n)

		g.setDelaunay(dcl=self.map_size*0.66)
		# g._draw_delaunay = True
		g.computeDelaunay()

		for ni in g.nodes:
			for j in g.triangulation.get_neighbours_of(ni.id):
				nj = g.getNodeByID(j)
				if ni.id != nj.id:
					g.addEdge(ni, nj, add_missing_nodes=False)

		for n in g.nodes:
			if len(n.getNeighbours()) == 0:
				data = {}
				for n2 in g.nodes:
					if n.id != n2.id:
						data[n2] = utils.distance2p(n.info["location"].map_position, n2.info["location"].map_position)
				m = min(data, key=data.get)
				g.addEdge(n, m, add_missing_nodes=False)

		for n in g.nodes:
			for e in n.edges:
				n.info["location"].neighbouring_locations.append(e.end.info["location"])


		# Generate roads between cities
		if gen_roads:
			_drawn = []
			for n in g.nodes:
				n.info["roads"] = {}
				n.info["dirt_roads"] = {}
				print("Generating roads for node {}".format(n.id), end='\n', flush=False)
				for e in n.edges:
					print("To node {}".format(e.end.id), end='\n', flush=False)
					if (n, e.end) in _drawn or (e.end, n) in _drawn:
						continue

					_start = self.map.get_tile(n.info["location"].map_position[0], n.info["location"].map_position[1])
					_end = self.map.get_tile(e.end.info["location"].map_position[0], e.end.info["location"].map_position[1])

					path = pathfinding.astar(_start, _end, self.map, dn=True)

					n.info["roads"][e.end.id] = path

					# for t in path:
					# 	t.has_road = True

					_drawn.append((n, e.end))

				for lm in n.info["location"].landmarks:
					print("To landmark {}".format(lm.name), end='\n', flush=False)
					_start = self.map.get_tile(n.info["location"].map_position[0], n.info["location"].map_position[1])
					_end   = self.map.get_tile(lm.x, lm.y)

					path = pathfinding.astar(_start, _end, self.map, dn=True)
					n.info["dirt_roads"][lm.name] = path


			print("")


		return g


if __name__=='__main__':

	clear = lambda: os.system('cls')

	nb_run = 1

	# for i, archetype in enumerate(params.LocationParams.ARCHETYPES):
	for i, archetype in enumerate(params.LocationParams.ARCHETYPES):

		run_id = i

		location_namelist = open("../data/namelists/locations.txt")

		location_name = params.rng.choice(location_namelist.readlines())[:-1]
		print(location_name)
		location1 = Location(archetype, location_name)

		location_namelist.close()


		city_namelist = open("../data/namelists/cities.txt")

		kingdom_namelist = open("../data/namelists/kingdoms.txt")
		kingdom_names_from_file = kingdom_namelist.readlines()
		kingdom_namelist.close()

		kingdom_names = params.rng.choice(kingdom_names_from_file, 1, replace=False)
		kingdom_names = [s.title() for s in kingdom_names]

		kingdom = Kingdom(kingdom_names)

		city_name = params.rng.choice(city_namelist.readlines())[:-1]
		print(city_name)
		community1 = Community(city_name, location1, kingdom, "HUMAN_CITY")

		city_namelist.close()


		filename = "../data/results/data{}{}".format(run_id, community1.location.archetype)
		data_file = open(filename+".csv", 'w')
		data_file.write("runID,day,"+community1.serialise(header=True)+"\n")

		pp = pprint.PrettyPrinter(indent=4)
		day = 1
		while day < 10000:
			community1.a_day_passed()
			if day%7 == 0:
				community1.a_week_passed()
			if day%30 == 0:
				community1.a_month_passed()
				data_file.write("{},{},{}\n".format(run_id, day, community1.serialise()))
			if day%91 == 0:
				community1.a_quarter_passed()
			if day%182 == 0:
				community1.a_semester_passed()
			if day%365 == 0:
				community1.a_year_passed()

			if day%500 == 0:
				clear()
				print("Day {}".format(day))
				print(community1.to_string())
				pp.pprint(community1.happiness_details)
				time.sleep(0.2)


			day += 1

		data_file.close()

	for i, archetype in enumerate(params.LocationParams.ARCHETYPES):

		filename = "../data/results/data{}{}".format(i, archetype)

		data_file = open(filename+".csv", 'r')
		csv_file = csv.reader(data_file, delimiter=",")

		_days = []
		_pop  = []
		_happ = []
		_ngr  = []
		_food = []
		_mat  = []
		_weal = []
		_spa  = []

		for i, row in enumerate(csv_file):
			if i > 1:
				_days.append(float(row[0+1]))
				_pop.append(float(row[1+2]))  
				_happ.append(float(row[2+2])) 
				_ngr.append(float(row[3+2]))  
				_food.append(float(row[4+2+3])) 
				_mat.append(float(row[5+2+3]))
				_weal.append(float(row[6+2+3])) 
				_spa.append(float(row[7+2+3])*100)

		fig, axes = plt.subplots(2, 1)

		fig.set_size_inches((14.96, 8.27), forward=False)

		fig.suptitle('Data plots')

		fig.subplots_adjust(right=0.8)

		## FIRST PLOT

		twin1 = axes[0].twinx()
		twin2 = axes[0].twinx()
		twin3 = axes[0].twinx()

		twin2.spines.right.set_position(("axes", 1.08))
		twin3.spines.right.set_position(("axes", 1.16))

		p0, = axes[0].plot(_days, _pop, label="Pop")
		p1, = twin1.plot(_days, _happ, 'tab:orange', label="Happ.")	
		p2, = twin2.plot(_days, _spa, 'tab:purple', label="%space")
		p3, = twin3.plot(_days, _ngr, 'tab:green', label="Net Growth")

		twin1.set_ylim(-110, 110)
		# twin2.set_ylim(-5, 200)
		twin2.set_ylim(-5, max(_spa)*1.2)

		axes[0].set(ylabel='Population')
		twin1.set_ylabel("Happiness")
		twin2.set_ylabel("% Space")
		twin3.set_ylabel("Net Growth Rate")

		axes[0].yaxis.label.set_color(p0.get_color())
		twin1.yaxis.label.set_color(p1.get_color())
		twin2.yaxis.label.set_color(p2.get_color())
		twin3.yaxis.label.set_color(p3.get_color())

		tkw = dict(size=4, width=1.5)
		axes[0].tick_params(axis='y', colors=p0.get_color(), **tkw)
		twin1.tick_params(axis='y', colors=p1.get_color(), **tkw)
		twin2.tick_params(axis='y', colors=p2.get_color(), **tkw)
		twin3.tick_params(axis='y', colors=p3.get_color(), **tkw)
		axes[0].tick_params(axis='x', **tkw)

		axes[0].legend(handles=[p0, p1, p2, p3])

		## SECOND PLOT

		twin1 = axes[1].twinx()
		twin2 = axes[1].twinx()

		twin2.spines.right.set_position(("axes", 1.08))

		p0, = axes[1].plot(_days, _food, 'tab:green', label="Food")
		p1, = twin1.plot(_days, _mat, 'tab:brown', label="Materials")
		p2, = twin2.plot(_days, _weal, 'tab:olive', label="Wealth")

		axes[1].set_ylim(1.2*min([min(_food),min(_mat),min(_weal)]), 1.2*max([max(_food),max(_mat),max(_weal)]))
		twin1.set_ylim  (1.2*min([min(_food),min(_mat),min(_weal)]), 1.2*max([max(_food),max(_mat),max(_weal)]))
		twin2.set_ylim  (1.2*min([min(_food),min(_mat),min(_weal)]), 1.2*max([max(_food),max(_mat),max(_weal)]))

		axes[1].set(ylabel='Food', xlabel='Days')
		twin1.set_ylabel("Materials")
		twin2.set_ylabel("Wealth")

		axes[1].yaxis.label.set_color(p0.get_color())
		twin1.yaxis.label.set_color(p1.get_color())
		twin2.yaxis.label.set_color(p2.get_color())

		tkw = dict(size=4, width=1.5)
		axes[1].tick_params(axis='y', colors=p0.get_color(), **tkw)
		twin1.tick_params(axis='y', colors=p1.get_color(), **tkw)
		twin2.tick_params(axis='y', colors=p2.get_color(), **tkw)
		axes[0].tick_params(axis='x', **tkw)
		
		axes[1].legend(handles=[p0, p1, p2])

		for ax in fig.get_axes():
			ax.label_outer()

		plt.savefig(filename+".png", dpi=500)
		# plt.show()

		data_file.close()



