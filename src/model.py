import time
import os
import random

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import csv
import threading

import utils
import graph
import perlinNoise
import pathfinding
import parameters as params

# 0.01 consumed per week per pop
FOOD      = 0
# Used to build stuff
MATERIALS = 1
# Affect happiness; 0.01 consumed per month per pop
WEALTH    = 2

RESSOURCES = [FOOD, MATERIALS, WEALTH]
RESSOURCES_STR = {
	FOOD:"FOOD",
	MATERIALS:"MATERIALS",
	WEALTH:"WEALTH"
}

np.random.seed(1995)

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
				time.sleep(1.0/self.freq)

	def stop(self):
		self._stop = True

	def pause(self):
		self._paused = not self._paused

class Map(object):

	def __init__(self, width, height):
			
		self.width  = width
		self.height = height
		self.tiles  = []

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
		noise_min = min(utils.flatten(noise))
		noise_max = max(utils.flatten(noise))

		new_forest_noise = []
		forest_noise_min = min(utils.flatten(forest_noise))
		forest_noise_max = max(utils.flatten(forest_noise))

		new_desert_noise = []
		desert_noise_min = min(utils.flatten(desert_noise))
		desert_noise_max = max(utils.flatten(desert_noise))
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

class Tile(object):

	def __init__(self, x=-1, y=-1):
		self.x = x
		self.y = y

		self.type = np.random.choice(params.TileParams.TYPES)

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

class Location(object):

	def __init__(self, archetype, name):

		self.name = name
		# Base happiness for pops living here
		self.attractiveness = 0
		# Base space to welcome pops, 1 space <=> 100 pops
		self.space = 0
		# Coordinates on a map
		self.map_position = (0, 0)

		self.base_production   = {}
		self.base_storage      = {}
		self.bonus_per_100_pop = {}

		self.archetype = archetype
		if self.archetype == params.LocationParams.PLAINS:
			self.base_production[FOOD] = 1.0
			self.base_production[MATERIALS] = 0.1
			self.base_production[WEALTH] = 0.1

			self.bonus_per_100_pop[FOOD] = 0.08
			self.bonus_per_100_pop[MATERIALS] = 0.05
			self.bonus_per_100_pop[WEALTH] = 0.02
			
			self.base_storage[FOOD] = 250.0
			self.base_storage[MATERIALS] = 500.0
			self.base_storage[WEALTH] = 120.0

			self.trade_factor = np.random.random()*0.05

			self.attractiveness = 8 + np.random.random()*4
			self.space = 20 + np.random.random()*5

		elif self.archetype == params.LocationParams.MOUNTAINS:

			self.base_production[FOOD] = 0.5
			self.base_production[MATERIALS] = 0.3
			self.base_production[WEALTH] = 0.2

			self.bonus_per_100_pop[FOOD] = 0.05
			self.bonus_per_100_pop[MATERIALS] = 0.08
			self.bonus_per_100_pop[WEALTH] = 0.12
			
			self.base_storage[FOOD] = 350.0
			self.base_storage[MATERIALS] = 800.0
			self.base_storage[WEALTH] = 300.0

			self.trade_factor = 0.02 + np.random.random()*0.08

			self.attractiveness = -10 - np.random.random()*5
			self.space = 12 + np.random.random()*5

		elif self.archetype == params.LocationParams.SEASIDE:

			self.base_production[FOOD] = 1.2
			self.base_production[MATERIALS] = 0.1
			self.base_production[WEALTH] = 0.3

			self.bonus_per_100_pop[FOOD] = 0.1
			self.bonus_per_100_pop[MATERIALS] = 0.01
			self.bonus_per_100_pop[WEALTH] = 0.03
			
			self.base_storage[FOOD] = 400.0
			self.base_storage[MATERIALS] = 350.0
			self.base_storage[WEALTH] = 600.0

			self.trade_factor = 0.05 + np.random.random()*0.07

			self.attractiveness = 10 + np.random.random()*5
			self.space = 10 + np.random.random()*5

	def to_string_list(self):
		lines = []
		lines.append(self.name)
		lines.append("Attractiveness: {}; Space available: {}".format(self.attractiveness, self.space))
		return lines

class Community(object):

	global_id = 0

	def __init__(self, name, location, poparch):

		self.name = name
		self.id = Community.global_id
		Community.global_id += 1

		self.location = location

		self.pop_archetype = poparch
		self.population = {}
		self.space_used = 0

		self.init_population()

		self.ressource_production_bonus = {}
		self.ressource_storage_bonus = {}
		self.ressource_stockpile = {}
		for r in set(RESSOURCES)-set([WEALTH]):
			self.ressource_production_bonus[r] = 0.0
			self.ressource_storage_bonus[r] = 0.0
			self.ressource_stockpile[r] = self.location.base_storage[r] / 8.0
		self.ressource_production_bonus[WEALTH] = 0.0
		self.ressource_storage_bonus[WEALTH] = 0.0
		self.ressource_stockpile[WEALTH] = 0.0

		self.actual_storage = {}
		self.actual_production = {}

		self.trade_factor = 0.05 + self.location.trade_factor

		self.effective_gain = {}
		self.effective_consumption = {}
		for r in RESSOURCES:
			self.effective_gain[r] = {}
		for r in RESSOURCES:
			self.effective_consumption[r] = {}

		self.ressources_prev_net_worth = {}
		for r in RESSOURCES:
			self.ressources_prev_net_worth[r] = 0

		self.happiness = 0
		self.happiness_from_surplus = {}
		for r in RESSOURCES:
			self.happiness_from_surplus[r] = 0
		self.net_growth_rate = 0

		self.food_shortage = 0
		self.food_consumption_per_pop_min = 0.005
		self.food_consumption_per_pop_max = 0.03
		self.food_consumption_per_pop_step = 0.001

		# self.food_consumption_per_pop = self.food_consumption_per_pop_min
		self.food_consumption_per_pop = self.food_consumption_per_pop_min

		self.food_consumption_from_pop = 0

		self.randomness_of_life = {}
		self.randomness_of_life["birth_rate_factor"] = 0
		self.randomness_of_life["death_rate_factor"] = 0

	def init_population(self, pop_archetype=None):
		if pop_archetype != None:
			self.pop_archetype = pop_archetype

		if self.pop_archetype == "HUMAN_CITY":
			base_pop_factor = 0.2 + np.random.random()*0.2
			total_pop = int(self.location.space * base_pop_factor * 100)

			self.population[HUMAN] = total_pop

		self.space_used = self.get_total_pop() / 100.0


	def get_total_pop(self):
		total = 0
		for race in self.population.keys():
			total += int(self.population[race])

		return total

	def get_pop_proportion(self):
		pop_prop = {}

		total = self.get_total_pop()

		for race in self.population.keys():
			try:
				pop_prop[race] = int(self.population[race]) / total
			except ZeroDivisionError:
				pop_prop[race] = 0

		return pop_prop


	def update_actual_prod_and_store(self):
		for r in RESSOURCES:
			self.actual_production[r] = self.location.base_production[r] + (self.ressource_production_bonus[r])
			# self.actual_production[r] = self.location.base_production[r] + (self.ressource_production_bonus[r])
			self.actual_storage[r] = self.location.base_storage[r] * (1.0 + self.ressource_storage_bonus[r])

	def update_production_bonus(self):
		for r in self.ressource_production_bonus.keys():
			self.ressource_production_bonus[r] = self.get_total_pop()/100.0 * self.location.bonus_per_100_pop[r]
			

	def a_day_passed(self):
		if self.location == None:
			return

		for r in RESSOURCES:
			self.effective_gain[r] = {}
		for r in RESSOURCES:
			self.effective_consumption[r] = {}

		# Update production bonus

		self.update_production_bonus()

		self.update_actual_prod_and_store()

		# Consume FOOD 

		self.food_consumption_from_pop = (self.get_total_pop() * self.food_consumption_per_pop) / 7.0
		self.effective_consumption[FOOD]["POP"] = self.food_consumption_from_pop

		# Production

		for r in RESSOURCES:
			self.effective_gain[r]["PRODUCTION"] = self.actual_production[r]

		for r in set(RESSOURCES)-set([WEALTH]):
			self.ressource_stockpile[r] = utils.clamp(self.ressource_stockpile[r] + sum(self.effective_gain[r].values()) - sum(self.effective_consumption[r].values()), 0, self.actual_storage[r])	
			if self.ressource_stockpile[r] >= self.actual_storage[r]:
				if r != FOOD:
					self.effective_gain[WEALTH]["SURPLUS_SELL"] = sum(self.effective_gain[r].values()) - sum(self.effective_consumption[r].values())*self.trade_factor
					self.effective_consumption[r]["SURPLUS_SELL"] = sum(self.effective_gain[r].values())

		if self.ressource_stockpile[FOOD] <= 0:
			self.food_shortage += 1.0/7.0
		else:
			self.food_shortage = max(0, (self.food_shortage - 1.0))

		# Update food consumption
		fcpp_new_increased_value = min(self.food_consumption_per_pop + self.food_consumption_per_pop_step, self.food_consumption_per_pop_max)
		fcpp_new_decreased_value = max(self.food_consumption_per_pop - self.food_consumption_per_pop_step, self.food_consumption_per_pop_min)
		
		new_inc_fc = (self.get_total_pop() * fcpp_new_increased_value) / 7.0
		new_dec_fc = (self.get_total_pop() * fcpp_new_decreased_value) / 7.0

		new_consump_inc = self.effective_consumption[FOOD].copy()
		new_consump_inc["POP"] = new_inc_fc

		new_consump_dec = self.effective_consumption[FOOD].copy()
		new_consump_dec["POP"] = new_dec_fc

		if (sum(self.effective_gain[FOOD].values()) - sum(self.effective_consumption[FOOD].values())) > 0:
			if (sum(self.effective_gain[FOOD].values()) - sum(new_consump_inc.values())) > 0:
				self.food_consumption_per_pop = fcpp_new_increased_value
		else:
			self.food_consumption_per_pop = fcpp_new_decreased_value

		# Consume WEALTH
		wealth_consumption = (self.get_total_pop() * 0.01) / 30.0
		wc_happiness_factor = 0
		if self.happiness > 0:
			wc_happiness_factor = min(0, -1 * ((self.happiness - 25) / 100.0))
		elif self.happiness <= 0:
			wc_happiness_factor = abs(((self.happiness) / 100.0))
		# print(wc_happiness_factor)

		self.effective_consumption[WEALTH]["POP"] = wealth_consumption * (1 + wc_happiness_factor)
		
		# Calculate Wealth
		self.ressource_stockpile[WEALTH] = utils.clamp(self.ressource_stockpile[WEALTH] + sum(self.effective_gain[WEALTH].values()) - sum(self.effective_consumption[WEALTH].values()), 0, self.actual_storage[WEALTH])

		# CALCULATE HAPPINESS
		# Happ from location
		self.happiness = self.location.attractiveness

		# Unrest from food shortage
		self.happiness -= self.food_shortage

		# Happ from stockpiled wealth
		self.happiness += self.ressource_stockpile[WEALTH] * 0.2

		# Unrest from overpopulation
		# overpop_unrest = self.location.space - self.space_used
		overpop_unrest = -(self.space_used / self.location.space)
		self.happiness += overpop_unrest * 50

		# Happ from wealth consumption
		if self.ressource_stockpile[WEALTH] > 0:
			self.happiness += sum(self.effective_consumption[WEALTH].values()) * 10

		# Happiness from food situation
		happ_food_factor = (self.food_consumption_per_pop - self.food_consumption_per_pop_min) * 1000 * 2
		happ_food_factor = round(happ_food_factor)
		self.happiness += happ_food_factor

		# Clamp happiness
		self.happiness = utils.clamp(self.happiness, -100, 100)
		if self.get_total_pop() <= 0:
			self.happiness = 0

		
		# Save previous net worth
		for r in RESSOURCES:
			self.ressources_prev_net_worth[r] = sum(self.effective_gain[r].values()) - sum(self.effective_consumption[r].values())

	def a_week_passed(self):
		
		# Update pops
		
		# br increases as accumulated wealth decreases
		# base_birth_rate = 3.69
		base_birth_rate = 1.0
		brf_space = 0
		if self.space_used < (self.location.space*0.75):
			brf_space = (1 - (self.space_used / self.location.space)) * 0.5
		brf_wealth = (self.ressource_stockpile[WEALTH]/1000.0)
		brf_happ = 0
		if self.happiness > 50:
			brf_happ = self.happiness / 100.0
		
		brf_food = self.ressource_stockpile[FOOD]/1000.0
		# brf_food = self.food_shortage

		self.actual_birth_rate = base_birth_rate * (1 + (brf_space + brf_wealth + brf_happ + brf_food + self.randomness_of_life["birth_rate_factor"]))

		# dr increases as accumulated wealth decreases
		# base_death_rate = 1.91
		base_death_rate = 0.52
		# drf_space = max(0, self.space_used - self.location.space) / 100.0
		drf_space = 0
		if self.space_used >= (self.location.space*0.5):
			drf_space = (self.space_used / self.location.space)
		drf_wealth = 1 - (self.ressource_stockpile[WEALTH]/self.actual_storage[WEALTH])
		drf_food = (self.food_shortage*7) * 0.1
		# drf_food = 0
		
		drf_happ = 0
		if self.happiness < 0:
			drf_happ = abs(self.happiness * 0.1)

		self.actual_death_rate = base_death_rate * (1 + drf_space + drf_wealth + drf_food + drf_happ + self.randomness_of_life["death_rate_factor"])

		# print(actual_birth_rate, actual_death_rate)

		self.net_growth_rate = (self.actual_birth_rate-self.actual_death_rate)
		if self.get_total_pop() <= 0:
			self.net_growth_rate = 0

		for race in self.population.keys():
			self.population[race] = (float(self.population[race]) * (1 + (self.net_growth_rate/100.0)))
		
		self.space_used = self.get_total_pop() / 100.0

	def a_month_passed(self):
		pass

	def a_quarter_passed(self):
		self.randomness_of_life["birth_rate_factor"] += -0.1 + np.random.random() * 0.2
		self.randomness_of_life["death_rate_factor"] += -0.1 + np.random.random() * 0.2

		self.randomness_of_life["birth_rate_factor"] = utils.clamp(self.randomness_of_life["birth_rate_factor"], 0, 1)
		self.randomness_of_life["death_rate_factor"] = utils.clamp(self.randomness_of_life["death_rate_factor"], 0, 1)
		pass

	def a_semester_passed(self):
		pass

	def a_year_passed(self):
		pass


	def to_string(self):
		s = "{}\n".format(self.name)
		s += "{}\n".format(params.LocationParams.ARCHETYPES_STR[self.location.archetype])
		str_popprop = ""
		popprop = self.get_pop_proportion()
		for race in popprop:
			str_popprop += "{:.1f}% {} ({})".format(popprop[race]*100, race.name, int(self.population[race]))
		s += "{} inhabitants : {}\n".format(self.get_total_pop(), str_popprop)
		s += "Happiness : {:.2f}; Growth rate : {:.2f}; Space : {:.2f}/{:.2f}\n".format(self.happiness, self.net_growth_rate, self.space_used, self.location.space)
		for r in self.ressource_stockpile:
			s += "{:.0f}/{:.0f} (+{:.3f}; {:.3f}+{:.0f}%-{:.3f})\n".format(self.ressource_stockpile[r], self.actual_storage[r], sum(self.effective_gain[r].values())-sum(self.effective_consumption[r].values()), self.location.base_production[r], self.ressource_production_bonus[r]*100, sum(self.effective_consumption[r].values()))

		s += "\nFood Shortage value:{}; Fcpp:{:.3f}\n".format(self.food_shortage, self.food_consumption_per_pop)

		return s

	def to_string_list(self):
		lines = []

		lines.append("{}".format(self.name))
		lines.append("at {} ({})".format(self.location.name, params.LocationParams.ARCHETYPES_STR[self.location.archetype].title()))
		str_popprop = ""
		popprop = self.get_pop_proportion()
		for race in popprop:
			str_popprop += "{:.1f}% {} ({})".format(popprop[race]*100, race.name, int(self.population[race]))
		lines.append("{} inhabitants : {}".format(self.get_total_pop(), str_popprop))
		lines.append("Happiness : {:.2f}; Growth rate : {:.2f} ({:.2f}-{:.2f}); Space : {:.2f}/{:.2f}".format(self.happiness, self.net_growth_rate, self.actual_birth_rate, self.actual_death_rate, self.space_used, self.location.space))
		for r in self.ressource_stockpile:
			lines.append("{} : {:.0f}/{:.0f} (+{:.3f}; {:.3f}+{:.0f}%-{:.3f})".format(RESSOURCES_STR[r].lower().title(), self.ressource_stockpile[r], self.actual_storage[r], sum(self.effective_gain[r].values())-sum(self.effective_consumption[r].values()), self.location.base_production[r], self.ressource_production_bonus[r]*100, sum(self.effective_consumption[r].values())))

		lines.append("Food Shortage value:{}; Fcpp:{:.3f}".format(self.food_shortage, self.food_consumption_per_pop))

		lines.append("{}".format(self.randomness_of_life))

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

class Race(object):

	def __init__(self, name):
		self.name = name

		self.affinities = {}


	def set_affinity(self, other_race, aff):
		self.affinities[other_race] = aff

HUMAN = Race("Humans")

RACES = [HUMAN]

class Model(object):

	def __init__(self, map_size=20):
		self.is_init = False

		self.map_size = map_size

		self.nb_location  = 0
		self.nb_community = 0

		self.locations   = []
		self.communities = []

		self.day = 0

		print("Creating model")

		self.map = Map(self.map_size, self.map_size)

	def reset(self):
		self.nb_location  = 0
		self.nb_community = 0

		self.locations   = []
		self.communities = []

		self.day = 0

		for i in range(self.map.width):
			for j in range(self.map.height):
				self.map.get_tile(i, j).has_road = False

	def set_map(self):
		self.map = Map(self.map_size, self.map_size)		

	def loop(self):
		if not self.is_init:
			return

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


	def test_model_init(self):
		self.nb_location  = 3
		self.nb_community = 3

		city_namelist = open("../data/namelists/cities.txt")
		city_names_from_file = city_namelist.readlines()
		city_namelist.close()

		location_namelist = open("../data/namelists/locations.txt")
		location_names_from_file = location_namelist.readlines()
		location_namelist.close()

		city_names = np.random.choice(city_names_from_file, len(params.LocationParams.ARCHETYPES), replace=False)
		location_names = np.random.choice(location_names_from_file, len(params.LocationParams.ARCHETYPES), replace=False)

		city_names = [s.title() for s in city_names]
		location_names = [s.title() for s in location_names]

		for i, archetype in enumerate(params.LocationParams.ARCHETYPES):
			location = Location(archetype, location_names[i][:-1])
			city_name = city_names[i][:-1]
			community = Community(city_name, location, "HUMAN_CITY")

			self.locations.append(location)
			self.communities.append(community)

		self.is_init = True

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
		max_location = 15

		# i = x + width*y
		# x = i % width
		# y = i // width
		flatten_tiles = list(utils.flatten(self.map.tiles))

		_continue = True

		while _continue and len(chosen_positions) < max_location:
			print("{} chosen positions".format(len(chosen_positions)), end='\r', flush=True)
			# Choose a random tile
			random_i = np.random.randint(0, len(flatten_tiles))
			new_pos = (flatten_tiles[random_i].x, flatten_tiles[random_i].y)
			# Get a new one until conditions are OK:
			# 		- Tile type is *not* WATER, DEEPWATER or PEAKS
			#		- New tile position is well positionned compared to chosen positions
			#		- Try x time until abandonning
			_try = 0; _max_try = 100
			while (	(
						flatten_tiles[random_i].type in [params.TileParams.WATER, params.TileParams.DEEPWATER, params.TileParams.PEAKS] 
						or not check_new_position(new_pos, chosen_positions, scale/5)
					)
					and _try < _max_try):
				# print("Trying for new pos... Attempt {}".format(_try), end='\r', flush=True)
				random_i = np.random.randint(0, len(flatten_tiles))
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

		location_names = np.random.choice(location_names_from_file, len(chosen_positions), replace=False)
		location_names = [s.title() for s in location_names]

		for i, p in enumerate(chosen_positions):
			print("Set city archetype for position {}".format(i), end='\r', flush=True)

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

			location = Location(archetype, location_names[i][:-1])
			location.map_position = p

			self.locations.append(location)
			self.nb_location += 1
		print("")


		# Generate communities
		city_namelist = open("../data/namelists/cities.txt")
		city_names_from_file = city_namelist.readlines()
		city_namelist.close()

		city_names = np.random.choice(city_names_from_file, len(self.locations), replace=False)
		city_names = [s.title() for s in city_names]

		for i, loc in enumerate(self.locations):
			community = Community(city_names[i][:-1], loc, "HUMAN_CITY")

			self.communities.append(community)
			self.nb_community += 1


		self.is_init = True

	def to_string_summary(self):
		lines = []
		for comm in self.communities:
			s = "{} at {}, {} inh.; Happ. {:0.0f}".format(comm.name, comm.location.name, comm.get_total_pop(), comm.happiness)
			lines.append(s)
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
				g.addEdge(n, np.random.choice(list(set(g.nodes)-set([n]))), add_missing_nodes=False)
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


		# Generate roads between cities
		if gen_roads:
			_drawn = []
			for n in g.nodes:
				n.info["roads"] = {}
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
			print("")


		return g



if __name__=='__main__':

	# random.seed(1995)

	clear = lambda: os.system('cls')

	nb_run = 1

	for i, archetype in enumerate(params.LocationParams.ARCHETYPES):

		run_id = i

		location_namelist = open("../data/namelists/locations.txt")

		location_name = random.choice(location_namelist.readlines())[:-1]
		print(location_name)
		location1 = Location(archetype, location_name)

		location_namelist.close()


		city_namelist = open("../data/namelists/cities.txt")

		city_name = random.choice(city_namelist.readlines())[:-1]
		print(city_name)
		community1 = Community(city_name, location1, "HUMAN_CITY")

		city_namelist.close()

		filename = "../data/results/data{}{}".format(run_id, community1.location.archetype)

		data_file = open(filename+".csv", 'w')
		data_file.write("runID,day,"+community1.serialise(header=True)+"\n")


		day = 1
		while day < 50000:
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
				time.sleep(0.1)


			day += 1

		data_file.close()

	for i, archetype in enumerate(p.LocationParams.ARCHETYPES):

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



