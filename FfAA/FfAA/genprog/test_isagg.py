#!/usr/bin/env python

import unittest

from isagg import *


def random_string(len = 25, r = 26):
	return "".join([chr(random.randint(65, 64 + r)) for x in xrange(len)])
	


class FunctionTestCase(unittest.TestCase):
	def testShuffledCopy(self):
		self.assertEqual(len(shuffled_copy(range(100))), 100)


class PoolTestCase(unittest.TestCase):
	size = 20
	s = random_string(30)
	p = Pool(s, poolsize = size)

	def testPool(self):
		self.assertEqual(len(self.p), self.size)
		for e in self.p:
			self.assertEqual(e.string(), self.s)
		
	def testNG(self):
		for i in xrange(20):
			self.p.nextGeneration()
			self.testPool()

class GenGATestCase(unittest.TestCase):
	def newG(self):
		size = 20
		self.s = random_string(10, 4)
		self.p = GenGA(self.s, poolsize = size)

	def testPoolSize(self):
		self.newG()
		self.assertEqual(len(self.p), self.p.poolsize)

	def testPoolStrings(self):
		self.newG()
		for e in self.p:
			self.assertEqual(e.string(), self.s)

class GenGACrossoverTestCase(GenGATestCase):
	def testCrossovers(self):
		self.newG()
		for i in xrange(20):
			self.p.applyCrossovers()
			self.testPoolStrings()

class GenGAMutationsTestCase(GenGATestCase):
	def testMutations(self):
		self.newG()
		for i in xrange(2):
			self.p.applyMutations()
			self.testPoolStrings()

class GenGASelectionTestCase(GenGATestCase):
	def testSelection(self):
		self.newG()
		for i in xrange(5):
			self.p.makeSelection()
			self.testPoolStrings()
			self.testPoolSize()

class GenGANGSelectionTestCase(GenGATestCase):
	def testNG(self):
		self.newG()
		for i in xrange(20):
			self.p.nextGeneration()
			self.testPoolStrings()



if __name__ == '__main__':
    unittest.main()
