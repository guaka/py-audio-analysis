import copy
import scipy
from numarray import *
from scipy import signal

def euclidean_distance(a, b):
	"""Calculate Euclidean distance between vectors a and b."""
	#print a,b
	diff = a - b
	return add.reduce(diff*diff, -1) # This does the equivalent of dot along the last axis

class Similarity_Relation:
	"""Similarity Relation class."""
	def __init__(self,
				 arr,
				 distance_function = euclidean_distance):
		"""Calculate similarity matrix, using
		* possibly conversion into 2 dimensions
		* distance matrix
		"""

		input_shape = arr.shape
		if len(input_shape) > 2:
			feature_vectors = reshape(feature_vectors,
									  (input_shape[0], input_shape[1] * input_shape[2]))
		distance_matrix = calculate_distance_matrix(arr, distance_function)
		self.arr = distance_matrix_to_similarity_matrix(distance_matrix)

	def calc_similar_parts(self):
		"""Find similar parts in the similarity matrix."""
		b = border_fir2d_filter(self.lag_matrix)
		self.similar_parts = Similar_Parts(self, b)

	def calc_borders(self):
		"""Find borders in the similarity matrix."""
		self.borders = Borders(self)
		if len(self.borders) == 0:
			print "No borders found. Probably strange bug, sepfir2d problem..."
			print "First (re)calculating similar_parts seems to resolve the problem %/"
			self.calc_similar_parts()
			self.borders = Borders(self)

def distance_matrix_to_similarity_matrix(D):
	max = ravel(D)[argmax(ravel(D))]  # find maximum value
	return 1.0 - (D/max)


def calculate_distance_matrix(W, distance_function = euclidean_distance):
	length = W.shape[0]
	S = zeros((length, length), W.typecode())
	for i in range(length):
		S[:i, i] = S[i, :i] = distance_function(W[i], W[:i])
	return S

def lag_matrix(arr):
	S = zeros(shape(arr), Float)
	l = len(arr)
	for i in arange(l):
		S[i, : l-i] = arr[i, i:]
	return S


def horizontal_fir2d_filter(arr,
							width = 10,
							factor = 10 / 12.0):
	fir2d = signal.sepfir2d(arr, [1] * width, [1])
	return greater(arr, fir2d / width * factor) * arr


def fast_horizontal_filter(arr, delta = 0.0001):
	l = len(arr)
		
	bigger_on_the_right = greater(arr[:, 1:], arr[:, :-1] + delta)
	bigger_on_the_left = greater(arr[:, :-1], arr[:, 1:] + delta)

	zero_column = zeros((l, 1))

	bigger_on_the_right = concatenate((bigger_on_the_right, zero_column), axis = 1)
	bigger_on_the_left = concatenate((zero_column, bigger_on_the_left), axis = 1)

	#crap!
	#result = arr * equal(bigger_on_the_left + bigger_on_the_left, 0)
	result = arr - arr * greater(bigger_on_the_left + bigger_on_the_right, 0)
	#assert doesn't work on matrices I guess
	return result
		

def border_fir2d_filter(arr, filter_x = [1] * 3, filter_y = [1] * 10):
	return greater(fast_horizontal_filter(signal.sepfir2d(arr, filter_x, filter_y)), 0) * arr


class Parts(list):
	def remove_overlaps(self):
		"""Remove overlapping parts."""
		
		self.sort(lambda a,b: cmp(a.end, b.end))
		i = 0
		while i < len(self) - 1:
			if self[i].end == self[i+1].end:
				if self[i].length() <= self[i+1].length():
					self.remove(self[i])
				else:
					self.remove(self[i+1])
			else:
				i += 1


class Similar_Parts(Parts):
	def __init__(self, arr,
				 minimal_length = 10,
				 maximal_angle = 20):

		l = lag_matrix(arr)
		b = border_fir2d_filter(l)
		similarity_lag_relation = b
		
		self.a = self.similarity_lag_relation = similarity_lag_relation
		self.minimal_length = minimal_length
		self.find_similarity_parts(minimal_length = minimal_length,
								   maximal_angle = maximal_angle)
		self.remove_overlaps()
		self.remove_diagonal_parts()
		self.sort(lambda x,y: cmp(y.length(), x.length()))

	def remove_diagonal_parts(self, diag_length = 2):
		i = 0
		while i < len(self):
			diag = self[i].has_diagonal_part(diag_length = diag_length)
			if diag:
				self.split_diagonal_part(self[i], diag)
			else:
				i += 1

	def split_diagonal_part(self, part, (diag_start, diag_length)):
		if diag_start > self.minimal_length:
			if len(part) - (diag_start + diag_length) > self.minimal_length:
				# split in two parts
				last_part = part.copy()
				last_part.delete_until(diag_start + diag_length)
				self.append(last_part)
				part.delete_from(diag_start)
			else:
				# first part remains
				part.delete_from(diag_start)
		else:
			if len(part) - (diag_start + diag_length) > self.minimal_length:
				# last part remains
				part.delete_until(diag_start + diag_length)
			else:
				# no part remains
				self.remove(part)
				
	def shape(self):
		arr = zeros(shape(self.a))
		for sp in self:
			arr = arr + sp.shape()
		return greater(arr, 0)
	
	def find_similarity_parts(self, x_delta = 1, height = 10,
							  minimal_length = 10,
							  maximal_angle = 20):
		l = len(self.a)
		new_arr = copy.copy(self.a)

		x = 2
		y = 0
		while x < l:
			# print x, y
			y = 0
			while sum(self.a[y:, x]) > 0:
				if self.a[y, x] > 0:
					sp = Similar_Part(self.a, (y, x))
					# print sp
					if (sp.length() > minimal_length and
						abs(sp.angle()) < maximal_angle):
						self.append(sp)
						y = sp.end[0]
				y += 1
			x += 1

class Similar_Part: #(FfAA.Base):
	def __init__(self, similarity_lag_relation, start, end = None):
		self.start = start
		self.pos_list = [start]
		self.end = end or start
		self.a = self.similarity_lag_relation = self.similarity_relation = similarity_lag_relation
		self._prolong()

	def length(self, axis = 0):
		return self.end[axis] - self.start[axis]

	def angle(self):
		"""Angle in degrees."""
		return arctan(1.0 * self.length(1) / self.length(0)) / pi * 180

	def delete_until(self, until):
		self.pos_list = self.pos_list[until :]
		self.start = self.pos_list[0]

	def delete_from(self, from_pos):
		self.pos_list = self.pos_list[: from_pos]
		self.end = self.pos_list[-1]

	def copy(self):
		return copy.copy(self)

	def __len__(self):
		return len(self.pos_list)

	def __repr__(self):
		return self.__class__.__name__ + "(" + "array_thing" + ", " + repr(self.start) + ", " + repr(self.end) + ")"

	def _next_pos(self, pos):
		next = (lambda d: (pos[0] + 1, pos[1] + d))

		if self.a[pos] < 1e-10:
			return False
		if self.a[next(0)] > 0:
			return next(0)
		elif self.a[next(1)] > self.a[next(-1)]:
			return next(1)
		elif self.a[next(-1)] > 0:
			return next(-1)
		return False
		
	def _prolong(self):
		end = self.start
		pos = self._next_pos(end)
		while pos:
			self.end = pos
			self.pos_list.append(pos)
			pos = self._next_pos(pos)

	def has_diagonal_part(self, diag_length = 3):
		curve = scipy.diff(array(self.pos_list)[:,1])
		diag = lambda pos, l: abs(sum(curve[pos : pos + l]))

		for pos in range(len(curve) - diag_length):
			if diag(pos, diag_length) >= diag_length:
				l = diag_length
				# prolong diagonal length
				while pos + l < len(curve) and diag(pos, l+1) > diag(pos, l):
					l += 1
				return pos, l
		return False

	def weight(self):
		return sum(sum(self.shape() * self.a))

	def shape(self):
		arr = zeros(shape(self.a))

		#pos = self.start
		#while pos: # and not pos == self.pos_list[-1]:
		#	# print pos
		#	arr[pos] = 1
		#	pos = self._next_pos(pos)

		for pos in self.pos_list:
			arr[pos] = 1
		return arr


def filter_vector_pos(l):
	k = range(1, l) + range(l, 0, -1)
	return array(k, Float32) / sqrt(sum(k))

def filter_vector_alt(l):
	k = range(1, l) + range(l - 1, 0, -1)
	for i in range(0, len(k), 2):
	    k[i] = -k[i]
	return k

def build_matrix(vec, func_vec, r):
	# _from_vectors_calculated_with_varying_parameter
	a = zeros((len(r), len(vec)), Float)
	for i in r:
		a[i] = func_vec(vec, i)
	return a

def find_borders_from_band(band):
	return build_matrix(sum(band, -1),
						lambda v, i: (signal.lfilter(filter_vector_pos(i), [1], v)),
						range(30))



def sim_matrix_find_segments(arr,
							 length1 = 10,
							 length2 = 10):
	length1 = max(length1, 1)
	length2 = max(length2, 2)

	length1 = min(length1, (len(arr) / 2) - 1)
	length2 = min(length2, (len(arr) / 2) - 1)

	k1 = range(1, length1) + range(length1, 0, -1)
	k2 = range(1, length2) + range(length2 - 1, 0, -1)

	k1 = array(k1, Float32) / sqrt(sum(k1))

	#print k1

	for i in range(0, len(k2)/2):
	#for i in range(0, len(k2), 2):
	    k2[i] = -k2[i]

	#print k1, type(k1)
	#print k2, type(k2)
	k2 = array(k2)
	#print "fuck signal.sepfir2d"
	#print arr
	res1 = signal.sepfir2d(arr, k1, k1)
	#print res1
	res2 = signal.sepfir2d(res1, k2, k2)
	#print shape(res2)
	return abs(res2)


class Borders(Parts):
	def __init__(self, arr):
		self.similarity_matrix = arr
		
		self.kerneled_sim_matrix = self.different_kernel_sizes(self.similarity_matrix)

		self.a = self.basic_border_info = border_fir2d_filter(self.kerneled_sim_matrix)
		self.find_borders()
		self.remove_overlaps()

	def remove_subsequents(self):
		i = 0
		while i < len(self):
			#if (self[i].pos == self[i+1][0] and
			#	self[i][1] < self[i+1][1])
			pass

	def find_borders(self):
		# very similar to Similar_Parts.find_similarity_parts()
		ly, lx = shape(self.basic_border_info)

		x = 0
		while x < lx:
			y = 0
			# print x, y
			while y < ly and sum(self.basic_border_info[y:, x]) > 0:
				if self.basic_border_info[y, x] > 0:
					b = Border(self.basic_border_info, (y, x))
					if b and b.is_sufficient():
						self.append(b)
						y = ly
				y += 1
			x += 1

	def get_border_points(self):
		return map(lambda x: (x.pos_list[-1][1], x.weight()), self)

	def different_kernel_sizes(self, arr, l = 20):
		a = zeros((l, len(arr)), Float)
		#print "b"
		for i in range(0, l):
			# a[l - 1 - i] = diag(sim_matrix_find_segments(arr, i, 2))
			a[l - 1 - i] = scipy.diag(sim_matrix_find_segments(arr, i, 2))
			#print "b"
		#print "c"
		return a

	def shape1d(self):
		a = zeros((shape(self.a)[1]), Float)
		for b in self:
			a[b.pos_list[-1][1]] = b.weight()
		return a

	def calc_imposed_segmentation(self):
		self.imposed_segmentation = Segmentations.CalculatedSegmentation(self)


class Border(Similar_Part):
	def __init__(self, matrix, start):
		self.start = start
		self.pos_list = [start]
		self.a = self.matrix = matrix
		self._prolong()

	def __repr__(self):
		return str((self.pos_list[-1][1], self.weight()))

	def __getitem__(self, key):
		return [self.pos_list[-1][1], self.weight()][key]

	def is_sufficient(self, minimum_sum = 1, minimum_length = 4):
		return self.pos_list[-1][0] == len(self.a) - 1 and \
			   self.sum() >= minimum_sum and \
			   len(self) >= minimum_length

	def listen(self):
		#TODO
		self.source.listen(map(lambda x: structures["Th"].more_precise_borders.segmentation.starttime(x[0]), structures["Th"].more_precise_borders)[6] * 1000 - 1000)

	def _next_pos(self, pos):
		next = lambda d: (pos[0] + 1, pos[1] + d)

		if len(self.a) == pos[0] + 1:
			return False

		# print next(0),
		# print self.a[next(0)]
		if self.a[next(0)] > 0:
			return next(0)
		elif self.a[next(1)] > self.a[next(-1)]:
			return next(1)
		elif self.a[next(-1)] > 0:
			return next(-1)
		return False
		
	def _prolong(self):
		end = self.start
		pos = self._next_pos(end)
		while pos:
			# print pos, self.a[pos]
			self.end = pos
			self.pos_list.append(pos)
			pos = self._next_pos(pos)

	def sum(self):
		return reduce(lambda s, p: s + self.a[p], self.pos_list, 0)
		
