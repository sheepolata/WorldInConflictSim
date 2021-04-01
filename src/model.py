
class Race(object):

	def __init__(self, name):
		self.name = name


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

if __name__=='__main__':
	p = []
	for i in range(10):
		p.append(Population())

	for pop in p:
		print(pop.id)