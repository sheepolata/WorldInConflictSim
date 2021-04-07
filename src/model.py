import time
import os
import random

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import csv

import utils
import threading

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
LOCATION_ARCHETYPES = ["PLAINS", "MOUNTAINS", "SEASIDE"]

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

class Model(object):

	def __init__(self):
		self.is_init = False

		self.nb_location  = 0
		self.nb_community = 0

		self.locations   = []
		self.communities = []

		self.day = 0

		self.map = Map(20, 20)

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

		city_names = np.random.choice(city_names_from_file, len(LOCATION_ARCHETYPES), replace=False)
		location_names = np.random.choice(location_names_from_file, len(LOCATION_ARCHETYPES), replace=False)

		city_names = [s.title() for s in city_names]
		location_names = [s.title() for s in location_names]

		for i, archetype in enumerate(LOCATION_ARCHETYPES):
			location = Location(archetype, location_names[i][:-1])
			city_name = city_names[i][:-1]
			community = Community(city_name, location, "HUMAN_CITY")

			self.locations.append(location)
			self.communities.append(community)

		self.is_init = True

	def to_string_summary(self):
		lines = []
		for comm in self.communities:
			s = "{} at {}, {} inh.; Happ. {:0.0f}".format(comm.name, comm.location.name, comm.get_total_pop(), comm.happiness)
			lines.append(s)
		return lines

class Map(object):

	def __init__(self, width, height):
			
		self.width  = width
		self.height = height
		self.tiles  = []

		for x in range(width):
			_rowx = []
			for y in range(height):
				_rowx.append(Tile(x, y))
			self.tiles.append(_rowx)


class Tile(object):

	WATER     = 0
	PLAINS    = 1
	MOUNTAINS = 2
	TYPES = [WATER, PLAINS, MOUNTAINS]
	TYPES_STR = {
		WATER:"WATER",
		PLAINS:"PLAINS",
		MOUNTAINS:"MOUNTAINS"
	}

	def __init__(self, x, y):
		self.x = x
		self.y = y

		self.type = np.random.choice(Tile.TYPES)

class Location(object):

	def __init__(self, archetype, name):

		self.name = name
		# Base happiness for pops living here
		self.attractiveness = 0
		# Base space to welcome pops, 1 space <=> 100 pops
		self.space = 0

		self.base_production   = {}
		self.base_storage      = {}
		self.bonus_per_100_pop = {}

		self.archetype = archetype
		if self.archetype == "PLAINS":
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

		elif self.archetype == "MOUNTAINS":

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

		elif self.archetype == "SEASIDE":

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


		# print(self.food_consumption_per_pop)

	def a_week_passed(self):
		
		# Update pops
		
		# br increases as accumulated wealth decreases
		# base_birth_rate = 3.69
		base_birth_rate = 1.0
		brf_space = 0
		if self.space_used < (self.location.space*0.75):
			brf_space = (1 - (self.space_used / self.location.space)) * 0.5
		# try:
		# 	brf_space = ((self.location.space*0.5) / self.space_used)
		# except ZeroDivisionError:
		# 	brf_space = 0
		brf_wealth = (self.ressource_stockpile[WEALTH]/1000.0)
		brf_happ = 0
		if self.happiness > 50:
			brf_happ = self.happiness / 100.0
		
		brf_food = self.ressource_stockpile[FOOD]/1000.0
		# brf_food = self.food_shortage

		self.actual_birth_rate = base_birth_rate * (1 + (brf_space + brf_wealth + brf_happ + brf_food + self.randomness_of_life["birth_rate_factor"]))

		# if self.food_shortage > 0:
		# 	actual_birth_rate = actual_birth_rate * (1.0/self.food_shortage)


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

		# if self.ressources_prev_net_worth[FOOD] > 0:
		# 	self.food_consumption_per_pop = min(self.food_consumption_per_pop + self.food_consumption_per_pop_step, self.food_consumption_per_pop_max)
		# elif self.ressources_prev_net_worth[FOOD] <= 0:		
		# 	self.food_consumption_per_pop = max(self.food_consumption_per_pop - self.food_consumption_per_pop_step, self.food_consumption_per_pop_min)


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
		s += "{}\n".format(self.location.archetype)
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
		lines.append("at {} ({})".format(self.location.name, self.location.archetype))
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

if __name__=='__main__':

	# random.seed(1995)

	clear = lambda: os.system('cls')

	nb_run = 1

	for i, archetype in enumerate(LOCATION_ARCHETYPES):

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

	for i, archetype in enumerate(LOCATION_ARCHETYPES):

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



