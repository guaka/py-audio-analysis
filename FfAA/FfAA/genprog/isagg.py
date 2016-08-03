#! /usr/bin/env python2.2

import random
import copy

from Numeric import *

from data_structures import *




class Pool(list):
	def __init__(self,
				 string,
				 poolsize = 40,
				 survive_rate = 0.8,
				 mutate_rate = 0.3,
				 crossover_rate = 0.1,
				 debug = False):

		self.string = string
		self.debug = debug
		#self.number_of_survivors = int(survive_rate * poolsize + 0.5)
		self.mutate_rate = mutate_rate
		self.crossover_rate = crossover_rate
		self.generation = 0
		self.poolsize = poolsize
		
		while len(self) < poolsize:
			self.append(buildstruct(string))

	def nextGeneration(self, debug = 0):
		self.generation += 1
		self.nextGenerationActions()
		if self.debug:
			print self.generation
			show(self)

	def nextGenerationActions(self):
		pass

	def show(self):
		for p in self:
			print p.complexity(), p


class GenGA(Pool):
	"""Generational GA with roulette-wheel selection.
	
	>>> g = GenGA("aaaa bbbb")

	>> > orig = copy.deepcopy(g); g == orig
	1

	>>> g.makeSelection()
	>>> len(g) > 0 #nothing selected?
	1
	>>> #g == orig #selection
	>>> g.applyCrossovers()
	>>> len(g) >= 8  #something left from crossover?
	1
	>>> g.applyMutations()
	>>> len(g) >= 8
	1
	>>> g.nextGenerationActions()
	"""

	def nextGenerationActions(self):
		self.applyCrossovers()
		self.applyMutations()
		self.optimize()
		self.makeSelection()


	def assert_codes(self):
		for code in self:
			if self.debug:
				print len(code.string()), code
			assert code.string() == self.string
	
	def optimize(self):
		for code_number in range(len(self)):
			code = self[code_number]
			self[code_number] = code = code.optimize()
			code.optimize_all_children()

				
	def makeSelection(self):
		# give code a fitness value
		complexities = array([code.complexity() for code in self])
		fitnesses = max(complexities) - complexities + 1
		max_fitness = max(fitnesses)
		for (code, fitness) in map(None, self, fitnesses):
			code.fitness = fitness

		# max fit codes are to survive
		survivors = []
		fitnesses = list(fitnesses)
		for code in self:
			if code.fitness == max_fitness:
				self.remove(code)
				survivors.append(code)

		fitnesses = [code.fitness for code in self]
		while len(survivors) < self.poolsize:
			cum_fitnesses = cumsum(fitnesses)
			val = random.randint(0, cum_fitnesses[-1])
			chosen = argmin(less(val, cum_fitnesses))
			fitnesses.remove(fitnesses[chosen])
			survivors.append(self[chosen])
			self.remove(self[chosen])

		while len(self):
			self.pop()
		for code in survivors:
			self.append(code)

	def applyCrossovers(self):
		crossover_group = []

		for code in shuffled_copy(self):
			if random.random() < self.crossover_rate:
				crossover_group.append(code)

		if self.debug:
			show(crossover_group)

		for counter in range(len(crossover_group) - 1):
			code1, code2 = crossover_group[counter], crossover_group[counter+1]
			
			#self.append(copy.copy(code1))
			#self.append(copy.copy(code2))
			
			for node1 in shuffled_copy(code1.all_children()):
				for node2 in shuffled_copy(code2.all_children()):
					if node1.string() == node2.string():
						# this doesn't work:  node1, node2 = node2, node1
						# but...
						# (node1.parent.children[node1.child_number],
						#  node2.parent.children[node2.child_number]) = (node2, node1)
						node1.replace_by(node2)
						node2.replace_by(node1)

						# works!
						break
		if self.debug:
			show(self)

	def applyMutations(self):
		for code in self:
   			if random.random() < self.mutate_rate:
				#exec("code_copy = " + repr(code))  # problem with copy.deepcopy..
				#self.append(code_copy)
				subtree = random.choice(code.all_children())
				mutated = buildstruct(subtree.string())
				if self.debug:
					print "mutate", subtree, " -> ", mutated
				subtree.replace_by(mutated)



def runGenGA(string,
			 poolsize = 10,
			 iter = 30,
			 debug = False):
	
	g = GenGA(string, poolsize = poolsize, debug = debug)
	for i in range(iter):
		g.nextGeneration(1)


def viewRunGenGA(string,
				 poolsize = 20,
				 iter = 100,
				 debug = False):
	
	g = GenGA(string, mutate_rate = 0, poolsize = poolsize, debug = debug)

	for i in range(iter):
		g.nextGenerationActions()
	
	#treeview.view_population(g)



def split_randomly(p):
	"""Randomly split sequence."""
	if len(p) <= 1:
		raise IndexError
	splitpoint = random.randint(1, len(p) - 1)
	return (p[:splitpoint],
			p[splitpoint:])
	
def show(l):
	print
	for el in l:
		print el.complexity(), el


def shuffled_copy(l):
	"Shuffle copy of sequence"
	lc = copy.copy(l)
	random.shuffle(lc)
	return lc




if __name__ == "__main__":
	viewRunGenGA('a' * 40, debug = True)

	
