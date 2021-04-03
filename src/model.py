import time
import os
import random

import utils

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
			self.base_production[FOOD] = 1.0
			self.base_production[MATERIALS] = 0.1
			self.base_production[WEALTH] = 0.1

			self.bonus_per_100_pop[FOOD] = 0.08
			self.bonus_per_100_pop[MATERIALS] = 0.05
			self.bonus_per_100_pop[WEALTH] = 0.02
			
			self.base_storage[FOOD] = 250.0
			self.base_storage[MATERIALS] = 500.0
			self.base_storage[WEALTH] = 120.0

			self.trade_factor = random.random()*0.05

			self.attractiveness = 8 + random.random()*4
			self.space = 20 + random.random()*10

		elif self.archetype == "MOUNTAINS":

			self.base_production[FOOD] = 1.0
			self.base_production[MATERIALS] = 2.0
			self.base_production[WEALTH] = 1.0

			self.bonus_per_100_pop[FOOD] = 0.12
			self.bonus_per_100_pop[MATERIALS] = 0.08
			self.bonus_per_100_pop[WEALTH] = 0.12
			
			self.base_storage[FOOD] = 300.0
			self.base_storage[MATERIALS] = 800.0
			self.base_storage[WEALTH] = 250.0

			self.trade_factor = 0.05 + random.random()*0.05

			self.attractiveness = -10 - random.random()*5
			self.space = 15 + random.random()*8

		elif self.archetype == "SEASIDE":

			self.base_production[FOOD] = 2.0
			self.base_production[MATERIALS] = 0.5
			self.base_production[WEALTH] = 0.8

			self.bonus_per_100_pop[FOOD] = 0.12
			self.bonus_per_100_pop[MATERIALS] = 0.04
			self.bonus_per_100_pop[WEALTH] = 0.08
			
			self.base_storage[FOOD] = 250.0
			self.base_storage[MATERIALS] = 300.0
			self.base_storage[WEALTH] = 500.0

			self.trade_factor = 0.1 + random.random()*0.1

			self.attractiveness = 15 + random.random()*5
			self.space = 20 + random.random()*15



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
			self.effective_gain[r] = 0
		for r in RESSOURCES:
			self.effective_consumption[r] = 0

		self.happiness = 0
		self.happiness_from_surplus = {}
		for r in RESSOURCES:
			self.happiness_from_surplus[r] = 0
		self.net_growth_rate = 0

		self.food_shortage = 0

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
			if self.ressource_stockpile[r] >= self.actual_storage[r]:
				if r != FOOD:
					self.effective_gain[WEALTH] += (self.effective_gain[r] - self.effective_consumption[r])*self.trade_factor
					self.effective_consumption[r] += self.effective_gain[r]

		if self.ressource_stockpile[FOOD] <= 0:
			# self.food_shortage += self.effective_gain[FOOD] - self.effective_consumption[FOOD]
			# self.food_shortage += abs(self.effective_gain[FOOD] - self.effective_consumption[FOOD])
			self.food_shortage += 1.0/7.0
		else:
			# self.food_shortage = round(self.food_shortage * 0.9, 1)
			# self.food_shortage = round(self.food_shortage * 0.5)
			self.food_shortage = max(0, self.food_shortage - 1)

		# print(self.food_shortage)
		# print(abs(self.effective_gain[FOOD] - self.effective_consumption[FOOD]))

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

		# print(self.food_shortage)
		# Unrest from food shortage
		self.happiness -= self.food_shortage

		# Happ from raw production
		for r in set(RESSOURCES):
			r_net_worth = self.effective_gain[r] - self.effective_consumption[r]
			self.happiness += r_net_worth * 2

		# Happ from surplus ressources
		for r in set(RESSOURCES) - set([WEALTH]):
			r_net_worth = self.effective_gain[r] - self.effective_consumption[r]
			if self.ressource_stockpile[r] >= self.actual_storage[r]:
				# self.happiness += r_net_worth * 5
				self.happiness_from_surplus[r] = min(self.happiness_from_surplus[r] + (r_net_worth * 0.01), r_net_worth*5)
			else:
				self.happiness_from_surplus[r] = max(self.happiness_from_surplus[r] - (r_net_worth*5*0.1), 0)

		self.happiness += sum(self.happiness_from_surplus.values())

		# Happ from net wealth production
		wealth_net_worth = self.effective_gain[WEALTH] - self.effective_consumption[WEALTH]
		if wealth_net_worth > 0:
			self.happiness += wealth_net_worth * 10

		# Happ from stockpiled wealth
		self.happiness += self.ressource_stockpile[WEALTH] * 0.1

		# Unrest from overpopulation
		overpop_unrest = self.location.space - self.space_used
		self.happiness += overpop_unrest

		# Happ from wealth consumption
		if self.ressource_stockpile[WEALTH] > 0:
			self.happiness += self.effective_consumption[WEALTH] * 5

		# Clamp happiness
		self.happiness = utils.clamp(self.happiness, -100, 100)
		if self.get_total_pop() <= 0:
			self.happiness = 0

		# Calculate Wealth
		self.ressource_stockpile[WEALTH] = utils.clamp(self.ressource_stockpile[WEALTH] + self.effective_gain[WEALTH] - self.effective_consumption[WEALTH], 0, self.actual_storage[WEALTH])
		

	def a_week_passed(self):
		
		# Update pops
		
		# br increases as accumulated wealth decreases
		# base_birth_rate = 3.69
		base_birth_rate = 1.0
		try:
			brf_space = ((self.location.space*0.5) / self.space_used)
		except ZeroDivisionError:
			brf_space = 0
		brf_wealth = (self.ressource_stockpile[WEALTH]/100.0)
		brf_happ = 0
		if self.happiness > 50:
			brf_happ = self.happiness / 100.0
		
		# if self.food_shortage > 0:
		# 	actual_birth_rate = 0
		brf_food = 0
		# brf_food = self.food_shortage

		actual_birth_rate = base_birth_rate * (1 + (brf_space + brf_wealth + brf_happ + brf_food))


		# dr increases as accumulated wealth decreases
		# base_death_rate = 1.91
		base_death_rate = 1.0
		# drf_space = max(0, self.space_used - self.location.space) / 100.0
		drf_space = self.space_used / self.location.space
		drf_wealth = 1 - (self.ressource_stockpile[WEALTH]/self.actual_storage[WEALTH])
		drf_food = (self.food_shortage*7) * 0.1
		drf_happ = 0
		if self.happiness < 0:
			drf_happ = abs(self.happiness * 0.1)
		actual_death_rate = base_death_rate * (1 + drf_space + drf_wealth + drf_food + drf_happ)

		# print(actual_birth_rate, actual_death_rate)

		self.net_growth_rate = (actual_birth_rate-actual_death_rate)
		if self.get_total_pop() <= 0:
			self.net_growth_rate = 0

		for race in self.population.keys():
			self.population[race] = (float(self.population[race]) * (1 + (self.net_growth_rate/100.0)))
		
		self.space_used = self.get_total_pop() / 100.0


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
			s += "{:.0f}/{:.0f} (+{:.3f}; {:.3f}+{:.0f}%-{:.3f})\n".format(self.ressource_stockpile[r], self.actual_storage[r], self.effective_gain[r]-self.effective_consumption[r], self.location.base_production[r], self.ressource_production_bonus[r]*100, self.effective_consumption[r])

		return s

	def serialise(self, header=False):

		if header:
			s = "Total pop, Happiness, Net growth rate,"
			for r in self.ressource_stockpile:
				s += "stpl" + str(r) + ","
			for r in self.effective_gain:
				s += "ntpr" + str(r) + ","

			s += "% space used"

			return s

		s = ""

		s += "{},{},{},".format(self.get_total_pop(),self.happiness,self.net_growth_rate)
		for r in self.ressource_stockpile:
			tmp = "{},".format(self.ressource_stockpile[r])
			s += tmp
		for r in self.effective_gain:
			tmp = "{},".format(self.effective_gain[r] - self.effective_consumption[r])
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

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import csv

if __name__=='__main__':

	random.seed(1995)

	clear = lambda: os.system('cls')

	nb_run = 1

	for i in range(nb_run):

		run_id = i

		location1 = Location("PLAINS")
		# location1 = Location("MOUNTAINS")
		# location1 = Location("SEASIDE")

		city_namelist = open("../data/namelists/cities.txt")

		city_name = random.choice(city_namelist.readlines())[:-1]
		print(city_name)
		community1 = Community(city_name, location1, "HUMAN_CITY")

		city_namelist.close()

		data_file = open("../data/results/data{}.csv".format(run_id), 'w')
		data_file.write("runID,day,"+community1.serialise(header=True)+"\n")

		day = 1
		while day < 10000:

			if day%7 == 0:
				community1.a_week_passed()
				
				data_file.write("{},{},{}\n".format(run_id, day, community1.serialise()))

			# if day%30 == 0:
			# 	clear()
			# 	print("Day {}".format(day))
			# 	print(community1.to_string())
			# 	time.sleep(0.1)

			community1.a_day_passed()

			day += 1

		data_file.close()

	data_file = open("../data/results/data0.csv", 'r')
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
			_pop.append(float(row[1+1]))  
			_happ.append(float(row[2+1])) 
			_ngr.append(float(row[3+1]))  
			_food.append(float(row[4+1+3])) 
			_mat.append(float(row[5+1+3]))
			_weal.append(float(row[6+1+3])) 
			_spa.append(float(row[7+1+3])*100)

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

	twin1.set_ylim(-100, 100)
	twin2.set_ylim(0, 200)

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

	plt.savefig("../data/results/data_fig.png", dpi=500)
	plt.show()

	data_file.close()



