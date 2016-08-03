#! /usr/bin/env python2.2

import copy
import random

random.seed()



def type(thing):
	return thing.__class__.__name__


def add(thing, val):
	"""
	>>> add('a', 3)
	'd'
	>>> add(10.1, -4) == 6.1
	1

	> >> add('abc', 1)
	bcd
	"""
	try:
		if len(thing) > 1:
			return map(lambda x: add(x, val), thing)
		thing = thing[0]
	except TypeError, s:
		if s.__str__() != ("len() of unsized object"):
			raise TypeError, s
	if isinstance(thing, str):
		return chr(min(ord(thing) + val,
					   255))
	return thing + val



def repeatedlyinvoke(func, n):
	"""Invoke func times times.

	Thanks to exarkun at #python."""
	
	def invoker(arg):
		for i in range(n):
			arg = func(arg)
		return arg
	return invoker



class function:
	def __init__(self, func, name = "noname"):
		self.name = name
		self.function = func
		self.__call__ = func

	def __repr__(self):
		return self.name

	def t__eq__(self):
		pass


id = function(lambda x: x, "id")
succ = function(lambda x: add(x, 1), "succ")
pred = function(lambda x: add(x, -1), "pred")

admissible_functions = [id, succ, pred]



class Data:
	"""
	>>> a, b = Data(1), Data(2)
	>>> a.complexity()
	1
	>>> a.string()
	'1'
	>>> a.random_subtree()
	Data(1)
	"""

	debug = False
	#__slots__ = []

	def __init__(self, value):
		self.value = value
		self.children = []

	def string(self):
		return str(self.value)

	def complexity(self):
		#if type(self) == Data:  doesn't work as expected.. type(Data('x')) == instance
		if type(self) == "Data":
			return 1
		else:
			return reduce(lambda x, y: x + y.complexity(),
						  self.children, 0)


	def __eq__(self, other):
		return type(self) == type(other) and \
			   self.value == other.value

	def __repr__(self):
		#return type(self) + "(" + repr(self.value) + ")"
		return repr(self.value)

	"""
	def __str__(self):
	"""

	#def children(self):
	#	return []

	def random_subtree(self, pick_chance = 0.3):
		if type(self) == "Data":
			return self
		if random.random() < pick_chance:
			return self
		c = self.children
		len_c = len(c)
		#return c[random_int(self.children())].random_subtree()
		#return c[random_int(len_c)].random_subtree()
		return random.choice(c).random_subtree()

	def _all_children_including_self(self):
		"""Get all childnodes from a node.

		Also sets the correct parent and child_number of the nodes, in
		order to do a nice crossover."""
		
		def un_list(ll): # this function should be refactored!
			new_list = []
			for l in ll:
				if isinstance(l, list):
					for el in l:
						new_list.append(el)
				else:
					new_list.append(l)
			return new_list
		
		if type(self) == "Data":
			return self
		else:
			for child, number in map(None, self.children, range(len(self.children))):
				child.parent = self
				child.child_number = number
			return [self] + un_list(map(lambda x: x._all_children_including_self(), self.children))

	def replace_by(self, new_self):
		if hasattr(self, "parent"):
			new_self.parent = self.parent
			new_self.child_number = self.child_number
			new_self.all_children()
			if False:
				print self.child_number, len(self.parent.children)
				print self.parent
				print new_self
				print
		
			self.parent.children[self.child_number] = new_self
		self = new_self

	def all_children(self):
		if hasattr(self, "children") and not len(self.children) == 0:
			l = self._all_children_including_self()
			l.remove(self)
			return l
		return []

	def optimize(self):
		return self

	def optimize_all_children(self):
		for child in (self.all_children()):
			optimized = child.optimize()
			#if not optimized is child:
			child.replace_by(optimized)
			#	break
		return self

	def check(self):
		pass
	
	check = classmethod(check)

	def node_repr_expanded(self):
		return repr(self.value)

	def node_repr_collapsed(self):
		return self.node_repr_expanded()

class codelist(list):
	def complexity(self):
		return reduce(lambda x,y: x+y.complexity(), self, 0)


class Operator(Data):
	def __repr__(self):
		return (self.__class__.__name__ + "(" + repr(self.children[0]) + ")")

	def __eq__(self, other):
		return (type(self) == type(other) and
				self.children == other.children)

	def node_repr_expanded(self):
		return self.__class__.__name__

	def node_repr_collapsed(self):
		return repr(self)


class Iter(Operator):
	def __init__(self, child, n = 1, function = id):
		self.n = n
		self.children = [child]
		self.function = function

	def string(self):
		def str(s, n):
			if n > 1:
				return s + str(self.function(s), n-1)
			else:
				return s
		return str(self.children[0].string(), self.n)

	def __eq__(self, other):
		return Operator.__eq__(self, other) and \
			   self.n == other.n

	def __repr__(self):
		return self.__class__.__name__ + "(" + (repr(self.children[0]) + ", " +
												repr(self.n) + ", " + 
												repr(self.function)
												) + ")"

	#def children(self):
	#	return [self.X]

	def node_repr_expanded(self):
		return Operator.node_repr_expanded(self) + " " + repr(self.n) + " " + repr(self.function)

	def optimize(self):
		if isinstance(self.children[0], Iter):
			self.n = self.n * self.children[0].n
			self.children[0] = self.children[0].children[0]
		return self

	def check(self, left, right):
		"""Check if left and right can be made into a nice Iter."""
		types = map(type, (left, right))
		if types == ["Iter", "Iter"] and left.children[0] == right.children[0] and left.function == right.function:
			return Iter(left.children[0], left.n + right.n)
		elif types == ["Data", "Data"] and left.value == right.value:
			return Iter(left, 2)
		elif types == ["Iter", "Data"] and left.children[0] == right:
			return Iter(left.children[0], left.n + 1)
		elif types == ["Data", "Iter"] and left.value == right.children[0]:
			return Iter(right.children[0], right.n + 1)

	check = classmethod(check)

class SymEven(Operator):
	def __init__(self, t):
		self.children = [t]
		
	def string(self):
		#str = reduce(lambda x, y: x + y.string(), self.children[0], "")
		#print self.children[0]
		str = "".join([x.string() for x in [self.children[0]]])
		l = map(lambda x: x, str)
		l.reverse()
		return str + "".join(l)

	#def children(self):
	#	return self.X

	def _reversed(self):
		to_reverse = self.children[0]
		if not type(to_reverse) == "Con":
			#print "_reversed: adding Con"
			#print to_reverse
			to_reverse = Con(to_reverse)
			#print to_reverse
		l = map(None, copy.copy(to_reverse))
		l.reverse()
		return l
	
	def check(self, left, right):
		types = map(type, (left, right))
		if types == ["Con", "Con"] and len(left) == len(right):
			# Cannot handle Con(Con(x)) structures
			l = copy.copy(right)
			l.reverse()
			if l == left:
				return SymEven(left)

	check = classmethod(check)


class SymOdd(SymEven):
	def __init__(self, t, pivot):
		self.children = [t, pivot]
		
	def string(self):
	    #return reduce(lambda x, y: x + y.string(), self.children + self._reversed(), "")	
		return "".join([x.string() for x in self.children + self._reversed()])

	def __repr__(self):
		return self.__class__.__name__ + "(" + repr(self.children[0]) + ", " + repr(self.children[1]) + ")"

	def check(self, left, right):
		if map(type, (left, right)) == ["Con", "Con"]:
			if len(left) < len(right):
				r = copy.copy(right[-len(left):])
				r.reverse()
				if r == left:
					return SymOdd(left, Con(right[:len(right) - len(left)]))

			if len(right) < len(left):
				l = copy.copy(left[:len(right)])
				l.reverse()
				if l == right:
					return SymOdd(Con(left[:len(right)]),
								  Con(left[len(right):]))

	check = classmethod(check)


class AltLeft(Operator, codelist):
	def __init__(self,
				 t,
				 t_list,
				 function = id):

		self.function = function
		self.Xrep = self.t = t
		if len(t_list) == 1:
			if type(t_list[0]) == list:
				t_list = t_list[0]
			if type(t_list[0]) == tuple:
				t_list = map(None, t_list[0])
		for el in t_list:
			self.append(el)
		
		self.children = self.X + [self.Xrep]

	def get_X(self):
		return codelist(self)

	X = property(get_X, None)

	def string(self):
		s = self.t.string()
		string_list = map(lambda x: x.string(), self)
		return self.t.string() + s.join(string_list)

	def __repr__(self):
		return self.__class__.__name__ + "(" + repr(self.Xrep) + ", <" + ", ".join(map(repr, self)) + ">)"

	def __eq__(self, other):
		return Operator.__eq__(self, other) and \
			   self.Xrep == other.Xrep

	def check(self, left, right):
		types = map(type, (left, right))
		if types == ("Con", "Con") and left[0] == right[0]:
			return AltLeft(left[0], [left[1:], right[1:]])
		if types == ("Con", "AltLeft") and left[0] == right.Xrep:
			l = map(lambda x: x, right)
			l.insert(0, Con(left[1:]))
			return AltLeft(right.Xrep, l)
		if types == ("AltLeft", "Con") and left.Xrep == right[0]:
			l = map(lambda x: x, left)
			l.append(Con(right[1:]))
			return AltLeft(left.Xrep, l)
		if types == ("AltLeft", "AltLeft") and left.Xrep == right.Xrep:
			l = map(lambda x: x, left) + \
				map(lambda x: x, right)
			return AltLeft(left.Xrep, l)

	check = classmethod(check)

class AltRight(AltLeft):
	def string(self):
		s = self.t.string()
		string_list = map(lambda x: x.string(), self)
		return s.join(string_list) + self.t.string()
	

	def check(self, left, right):
		types = map(type, (left, right))
		if types == ("Con", "Con") and left[-1] == right[-1]:
			return AltRight(left[-1], (Con(left[:-1]), Con(right[:-1])))
		if types == ("Con", "AltRight") and left[-1] == right.Xrep:
			l = map(lambda x: x, right)
			l.insert(0, Con(left[:-1]))
			return AltRight(right.Xrep, l)
		if types == ("AltRight", "Con") and left.Xrep == right[-1]:
			l = map(lambda x: x, left)
			l.append(Con(right[:-1]))
			return AltRight(left.Xrep, l)
		if types == ("AltRight", "AltRight") and left.Xrep == right.Xrep:
			l = map(lambda x: x, left) + \
				map(lambda x: x, right)
			return AltRight(left.Xrep, l)

	check = classmethod(check)


class Unit(Operator):
	def __init__(self, t):
		self.t = t
		self.children = [self.t]

	def string(self):
		return self.t.string()

	def complexity(self):
		return self.t.complexity() + 1

	#def children(self):
	#	return [self.t]
	
class Con(Operator, list):
	def __init__(self, *t_list):
		if len(t_list) == 1:
			if type(t_list[0]) == "list":
				t_list = t_list[0]
			if type(t_list[0]) == "tuple":
				t_list = map(None, t_list[0])
		for el in t_list:
			self.append(el)
		#self.X = self.t_list = map(None, t_list)
		self.children = self #map(None, self)

	def __repr__(self):
		return (self.__class__.__name__ + "(" + ", ".join(map(repr, self)) + ")")

	def __eq__(self, other):
		return isinstance(self, list) and \
			   isinstance(other, list) and \
			   map(None, self) == map(None, other)

	def string(self):
		# print "Con.string():", self
		return "".join([x.string() for x in self.children])
	
	def check(self, left, right):
		types = map(type, (left, right))
		if types == ("Con", "Con"):
			return Con(left + right)
		if types[1] == "Con":
			return Con(Con(left) + right)
		if types[0] == "Con":
			return Con(left + Con(right))
		#return Con(Con(left, right))  #SymEven.check couldn't handle this
		return Con(left, right)

	check = classmethod(check)


	def optimize(self):
		if len(self) == 1:
			# self.replace_by(self[0])
			return self[0]

		if self.debug:
			print "Con.optimize", self

		for counter in range(len(self) - 2):
			current = self[counter]
			next = self[counter+1]

			if self.debug:
				print counter, current, next, current == next
			# print isinstance(current, Iter), isinstance(next, Iter) #, current.children[0] == next.children[0]
			
			if isinstance(current, Iter) and isinstance(next, Iter) and current.children[0] == next.children[0]:
				self[counter].n += next.n
				self.pop(counter+1)
				return self
			
			if current == next:
				self[counter + 1] = Iter(current, 2)
				self.pop(counter)
				return self

			if isinstance(current, Iter) and current.children[0] == next:
				self[counter].n += 1
				self.pop(counter+1)
				return self
			
			if isinstance(next, Iter) and current == next.children[0]:
				next.n += 1
				self.pop(counter)
				return self
			
			if ((isinstance(current, AltLeft) and isinstance(next, AltLeft)) or
				(isinstance(current, AltRight) and isinstance(next, AltRight))) and current.Xrep == next.Xrep:
				current += next
				self.pop(counter+1)
				return self
		
		sym_length = 0
		length = len(self)
		while sym_length * 2 < length - 1 and self[sym_length] == self[length - sym_length - 1]:
			sym_length += 1
		if sym_length * 2 == length:
			self = SymEven(Con(self[:sym_length]))
			return self
		elif sym_length > 0:
			self = SymOdd(Con(self[:sym_length]), Con(self[sym_length:length-sym_length]))
			return self
		return self



def split_randomly(p):
	"""Randomly split sequence."""
	if len(p) <= 1:
		raise IndexError
	splitpoint = random.randint(1, len(p) - 1)
	return (p[:splitpoint],
			p[splitpoint:])


def buildstruct(p):
	"""Build a tree structure from a sequence."""
	if len(p) > 1:
		t1, t2 = map(buildstruct, split_randomly(p))
		return combine_trees(t1, t2)
	else:
		return Data(p)

operators = [Iter, SymOdd, SymEven, AltRight, AltLeft, Con]

def combine_trees(t1, t2):
	"""Combine two tree structures into one."""
	found = False
	while not found:
		found = random.choice(operators).check(t1, t2)
	return found



def _test():
	import doctest
	import data_structures
	return doctest.testmod(data_structures)

if __name__ == "__main__":
	_test()
