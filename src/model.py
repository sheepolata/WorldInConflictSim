import time
import os
import random

import utils

random.seed(1995)

# 0.01 consumed per week per pop
FOOD      = 0
# Used to build stuff
MATERIALS = 1
# Affect happiness; 0.01 consumed per month per pop
WEALTH    = 2

RESSOURCES = [FOOD, MATERIALS, WEALTH]

class Location(object):

	def __init__(self, archetype):
		# Base happiness for pops living here
		self.attractiveness = 0
		# Base space to welcome pops, 1 space <=> 100 pops
		self.space = 0

		self.base_production   = {}
		self.base_storage      = {}
		self.bonus_per_100_pop = {}

		self.archetype = archetype
		if self.archetype == "PLAINS":
			self.base_production[FOOD] = 0.15 * 10
			self.base_production[MATERIALS] = 1.0
			self.base_production[WEALTH] = 0.5

			self.base_storage[FOOD] = 250.0
			self.base_storage[MATERIALS] = 500.0
			self.base_storage[WEALTH] = 100.0

			self.bonus_per_100_pop[FOOD] = 0.1
			self.bonus_per_100_pop[MATERIALS] = 0.05
			self.bonus_per_100_pop[WEALTH] = 0.01

			self.attractiveness = 8 + random.random()*4
			self.space = 20 + random.random()*10


class Community(object):

	global_id = 0

	def __init__(self, name, location, poparch):

		self.name = name
		self.id = Community.global_id
		Community.global_id += 1

		self.location = location

		self.pop_archetype = poparch
		self.population = {}

		self.init_population()

		self.ressource_production_bonus = {}
		self.ressource_storage_bonus = {}
		self.ressource_stockpile = {}
		for r in RESSOURCES:
			self.ressource_production_bonus[r] = 0.0
			self.ressource_storage_bonus[r] = 0.0
			self.ressource_stockpile[r] = self.location.base_storage[r] / 8.0

		self.actual_storage = {}
		self.actual_production = {}

		self.trade_factor = 0.05

		self.effective_gain = {}
		self.effective_consumption = {}
		for r in RESSOURCES:
			self.effective_gain[r] = 0
		for r in RESSOURCES:
			self.effective_consumption[r] = 0

		self.happiness = 0
		self.net_growth_rate = 0

		self.space_used = 0

	def init_population(self, pop_archetype=None):
		if pop_archetype != None:
			self.pop_archetype = pop_archetype

		if self.pop_archetype == "HUMAN_CITY":
			base_pop_factor = 0.2 + random.random()*0.2
			total_pop = int(self.location.space * base_pop_factor * 100)

			self.population[HUMAN] = total_pop

		self.space_used = self.get_total_pop() / 100.0

	def get_total_pop(self):
		total = 0
		for race in self.population.keys():
			total += self.population[race]

		return total

	def get_pop_proportion(self):
		pop_prop = {}

		total = self.get_total_pop()

		for race in self.population.keys():
			pop_prop[race] = self.population[race] / total

		return pop_prop


	def update_actual_prod_and_store(self):
		for r in RESSOURCES:
			self.actual_production[r] = self.location.base_production[r] * (1.0 + self.ressource_production_bonus[r])
			self.actual_storage[r] = self.location.base_storage[r] * (1.0 + self.ressource_storage_bonus[r])

	def update_production_bonus(self):
		for r in self.ressource_production_bonus.keys():
			self.ressource_production_bonus[r] = self.get_total_pop()/100.0 * self.location.bonus_per_100_pop[r]
			

	def a_day_passed(self):
		if self.location == None:
			return

		for r in RESSOURCES:
			self.effective_gain[r] = 0
		for r in RESSOURCES:
			self.effective_consumption[r] = 0

		# Update production bonus

		self.update_production_bonus()

		self.update_actual_prod_and_store()

		# Consume FOOD
		food_consumption = (self.get_total_pop() * 0.01) / 7.0
		self.effective_consumption[FOOD] += food_consumption

		# Production

		for r in RESSOURCES:
			self.effective_gain[r] += self.actual_production[r]

		for r in set(RESSOURCES)-set([WEALTH]):
			self.ressource_stockpile[r] = utils.clamp(self.ressource_stockpile[r] + self.effective_gain[r] - self.effective_consumption[r], 0, self.actual_storage[r])
			if r != WEALTH:
				if self.ressource_stockpile[r] >= self.actual_storage[r]:
					self.effective_gain[WEALTH] += (self.effective_gain[r] - self.effective_consumption[r])*self.trade_factor

		# Consume WEALTH

		wealth_consumption = (self.get_total_pop() * 0.01) / 30.0
		wc_happiness_factor = 0
		if self.happiness >= 50:
			wc_happiness_factor = -1 * ((self.happiness - 50) / 100.0)
		elif self.happiness <= 0:
			wc_happiness_factor = -1 * ((self.happiness) / 100.0)
		# print(wc_happiness_factor)

		self.effective_consumption[WEALTH] += wealth_consumption * (1 + wc_happiness_factor)

		# Calculate Happiness
		# Happ from location
		self.happiness = self.location.attractiveness

		# Happ from raw production
		for r in set(RESSOURCES):
			r_net_worth = self.effective_gain[r] - self.effective_consumption[r]
			self.happiness += r_net_worth * 2

		# Happ from surplu ressources
		for r in set(RESSOURCES) - set([WEALTH]):
			if self.ressource_stockpile[r] >= self.actual_storage[r]:
				r_net_worth = self.effective_gain[r] - self.effective_consumption[r]
				self.happiness += r_net_worth * 5

		# Happ from net wealth production
		wealth_net_worth = self.effective_gain[WEALTH] - self.effective_consumption[WEALTH]
		if wealth_net_worth > 0:
			self.happiness += wealth_net_worth * 10

		# Happ from stockpiled wealth
		self.happiness += self.ressource_stockpile[WEALTH] * 0.1

		# Unrest from overpopulation
		overpop_unrest = self.location.space - self.space_used
		self.happiness += overpop_unrest
		
		# Calculate Wealth
		self.ressource_stockpile[WEALTH] = utils.clamp(self.ressource_stockpile[WEALTH] + self.effective_gain[WEALTH] - self.effective_consumption[WEALTH], 0, self.actual_storage[WEALTH])

	def a_week_passed(self):
		
		# Update pops
		
		# br increases as wealth decreases
		base_birth_rate = 3.69
		# dr increases as wealth decreases
		base_death_rate = 1.91

		self.net_growth_rate = (base_birth_rate-base_death_rate)

		for race in self.population.keys():
			self.population[race] = int(self.population[race] * (1 + (self.net_growth_rate/100.0)))
		
		self.space_used = self.get_total_pop() / 100.0


	def serialise(self):
		s = "{}\n".format(self.name)
		s += "{}\n".format(self.location.archetype)
		str_popprop = ""
		popprop = self.get_pop_proportion()
		for race in popprop:
			str_popprop += "{:.1f}% {} ({})".format(popprop[race]*100, race.name, int(self.population[race]))
		s += "{} inhabitants : {}\n".format(self.get_total_pop(), str_popprop)
		s += "Happiness : {:.2f}; Growth rate : {:.2f}; Space : {:.2f}/{:.2f}\n".format(self.happiness, self.net_growth_rate, self.space_used, self.location.space)
		for r in self.ressource_stockpile:
			s += "{:.0f}/{:.0f} (+{:.3f}; {:.3f}+{:.0f}%-{:.3f})\n".format(self.ressource_stockpile[r], self.actual_storage[r], self.effective_gain[r]-self.effective_consumption[r], self.location.base_production[r], self.ressource_production_bonus[r]*100, self.effective_consumption[r])

		return s



class Race(object):

	def __init__(self, name):
		self.name = name

		self.affinities = {}


	def set_affinity(self, other_race, aff):
		self.affinities[other_race] = aff

HUMAN = Race("Humans")

RACES = [HUMAN]

class Population(object):
	global_id = 0

	def __init__(self):
		self.id = Population.global_id
		Population.global_id += 1

		self.name = "pop"
		self.age = 0

		self.happiness = 50

		self.race = Race("race")

		self.community = None

		self.job = None

	def day(self):
		### Every day behaviour

		# Produce and/or consume ressources from job

		# Consume ressources

		# Update values (age, happiness, etc)

		pass

if __name__=='__main__':
	location1 = Location("PLAINS")

	community1 = Community("Saint Just", location1, "HUMAN_CITY")

	clear = lambda: os.system('cls')

	day = 0
	while True:
		clear()

		if day%7 == 0:
			community1.a_week_passed()

		community1.a_day_passed()

		day += 1

		print("Day {}".format(day))
		print(community1.serialise())

		time.sleep(0.05)



