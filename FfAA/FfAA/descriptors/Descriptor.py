
import ZODB, ZODB.FileStorage

import FfAA
import my_show
from scipy import *


class Descriptor(FfAA.Calculation):
	"""Handle processing of data."""
	
	def __init__(self, parent, # pStructure
				 Default_Preprocessor = None,
				 reinit = False):

		FfAA.Calculation.__init__(self, parent)

		if Default_Preprocessor:
			if not reinit and not (Default_Preprocessor.__name__ in parent.__dict__.keys()):
				parent.__dict__[Default_Preprocessor.__name__] = Default_Preprocessor(parent)
			self.parent_processor = parent.__dict__[Default_Preprocessor.__name__]
			self.parent_processor.__dict__[self.name] = self
		else:
			self.parent_processor = None

		# self.children = FfAA.Mapping()

		#if hasattr(self.parent_processor, "segmentation"):
		#	self.segmentation = self.parent_processor.segmentation

		self._title()

	def __getitem__(self, key):
		return self.feature_vectors[key]

	def __len__(self):
		return len(self.feature_vectors)

	def __setitem__(self, key, value):
		self.feature_vectors[key] = value

	def _set_samplerate(self, hopsize):
		if self.parent_processor:
			self.samplerate = self.parent_processor.samplerate / hopsize
		else:
			self.samplerate = None

	def _delete_from_parents(self):
		del self.parent_processor.__dict__[self.name]
		del self.parent.__dict__[self.__class__.__name__]

	def reinit(self):
		self.parent.__dict__[self.__class__.__name__] = self.__class__(self.parent)
		for c in self.__dict__:
			if hasattr(c, "reinit"):
				print "reinit:", c, c.reinit
				# c.reinit()

	def _title(self, title = ""):
		title = title or type(self).__name__
		print title # "\n"

	def show(self):
		my_show.show(transpose(self.feature_vectors),
					 title = self.source.name + " - " + self.name)

	"""
	def calc_similarity_relation(self):
		feature_vectors = self.feature_vectors
		input_shape = shape(feature_vectors)
		self.similarity_relation = Relations.Similarity_Relation(self)

	def calc_borders(self):
		self.borders = self.similarity_relation.borders

	def calc_similar_parts(self):
		self.similar_parts = self.similarity_relation.similar_parts
	"""
