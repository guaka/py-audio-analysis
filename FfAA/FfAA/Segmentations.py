
"""Several forms of segmentation.

Time units are seconds, unless specified otherwise"""


import FfAA
import Relations

import ZODB
import ZODB.FileStorage

from Numeric import *


#import Convolve

from text_output import Progressbar

class Segment(FfAA.Base):
	"""A segment contains information about:

	 x The start time
	 x The end time
	 x The audiostructure it belongs to."""

	def __init__(self, parent, start, end):
		self.parent = parent
		self.start = start
		self.end = end

	def __getitem__(self, key):
		return [self.start, self.end][key]
	
	def __getattr__(self, name):
		if name == "length":
			return self.end - self.start
		raise(AttributeError)

	def __repr__(self):
		return self._my_repr(self.start, self.end)
	
class Segmentation(FfAA.Base): # TODO: (FfAA.Base)
	def __init__(self, parent):

		# TODO:
		# what if hasattr(parent, "segmentation")?
		# differentiate between Frames and Calculated?
		if parent:
			parent.segmentation = self

		self.parent = parent

	"""
	def spanned_time(self, a, b):
		#Calculate start and end times of segments.

		return None
	"""


class Frames(Segmentation):
	"""Evenly spaced segmentation.""" # Unit: second."""
	
	def __init__(self,
				 parent,
				 number_of_frames,
				 samplerate,
				 framesize = None,
				 hopsize = None,
				 window_function = None
				 ):

		Segmentation.__init__(self, parent)

		self.number_of_frames = number_of_frames

		self.samplerate = samplerate
		self.framesize = framesize
		self.hopsize = hopsize
		self.window_function = window_function

		self.parent_segmentation = parent.parent_processor and parent.parent_processor.segmentation
		
		print "Frames with framesize =", framesize, " hopsize =", hopsize

	def length(self):
		"""Length in seconds."""
		return self.number_of_frames * self.hopsize / self.samplerate

	def __len__(self):
		"""Length in number of segments."""
		return self.number_of_frames

	def window_for_segments(self, a, b):
		if a > b:
			a, b = b, a

		if a < 0:
			print "Warning: start of segment < 0"
		if b > len(self):
			print "Warning: end of segment > len(self)"

		w = self.window_function(self.framesize)
		impulses = zeros((self.parent_segmentation.number_of_frames))
		impulses[a * self.hopsize : b * self.hopsize : self.hopsize] = 1
		arr = convolve(impulses, w / sum(w) * self.hopsize)
		assert alltrue(greater_equal(arr, 0))
		return arr

	def parent_segments(self, a):
		return (a * self.hopsize, a * self.hopsize + self.framesize)

	def window_for_window(self, window):

		arr = zeros((self.parent_segmentation.number_of_frames), Float)

		a = 0
		b = len(window)

		w = self.window_function(self.framesize)
		w *= self.hopsize / sum(w)
		
		pb = Progressbar(len(window))
		for i in range(len(window)):
			# print len(arr[i * self.hopsize : (i + 1) * self.hopsize - 1]), len(window[i] * w)
			pb.update()
			part = arr[i * self.hopsize : i * self.hopsize + self.framesize]
			part += (window[i] * w)[:len(part)]
		pb.finish()
		# assert alltrue(greater_equal(arr, 0))
		return arr

	def starttime(self, frame):
		"""Starttime of framenumber"""

		return self.hopsize / self.samplerate * frame
		

	def OLD_window_for_window(self, window):

		w = self.window_function(self.framesize)
		impulses = zeros((self.parent_segmentation.number_of_frames), Float)

		a = 0
		b = len(window)
		print len(impulses[a * self.hopsize : b * self.hopsize : self.hopsize]), len(window)
		impulses[a * self.hopsize : b * self.hopsize : self.hopsize] = window
		arr = convolve(impulses, w / sum(w) * self.hopsize)
		assert alltrue(greater_equal(arr, 0))
		return arr


	#def segments_to_time(self, a, b, degree = 0.5):
		"""Calculate start and length of time spanned by segment number a to segment number b.

		if degree >= 0.5:
		    time is certainly being spanned by segments
		if degree == 0:
		    time is 'possibly' spanned by segments

		if a > b:
			a, b = b, a
		return (self.hopsize * a + self.framesize * (1 - degree),
				self.hopsize * b + self.framesize * degree)
				"""

class LabeledSegmentation(Segmentation):
	def __init__(self):
		pass
	
class CalculatedSegmentation(FfAA.List):
	def __init__(self, parent):
		if not isinstance(parent, Relations.Borders):
			raise TypeError

		# Segmentation.__init__(self, parent)
		FfAA.List.__init__(self, parent)

		start = 0
		for b in parent.get_border_points():
			end = b[0]
			self.append(Segment(self, start, end))
			start = end

		self.parent_similarity_relation = parent.parent

	def calc_similarity_relation(self):
		lol = []
		if False:
			for i in self:
				lol.append(map(lambda x: self.parent_similarity_relation.similarity_for_segments(i, x),
							   self))
				pass
			pass
		##		
		a = map(lambda i:
				(map(lambda j: self.parent_similarity_relation.similarity_for_segments(i, j),
					 self)),
				self)
			
		self.similarity_relation = array(a)
		
	def show(self):
		self.parent.show()
