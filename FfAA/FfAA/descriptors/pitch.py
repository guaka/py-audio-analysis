from __future__ import division


import ZODB, ZODB.FileStorage

from Descriptor import Descriptor
#from scipy import *

import Segmentations
import my_show
from text_output import Progressbar

import audio
import spectral

from RandomArray import normal
from scipy.signal import buttord, butter, lfilter
import Interactive

import Relations


class PitchesFromSpectrogram(Descriptor):
	def __init__(self,
				 parent,
				 reinit = False,
				 ):

		Descriptor.__init__(self, parent,
							Default_Preprocessor = spectral.Spectrogram,
							reinit = reinit)
		
		spectrum = self.parent_processor.feature_vectors
		self.feature_vectors = Relations.border_fir2d_filter(spectrum, filter_x = [1] * 20, filter_y = [1] * 40)


class Pitch(Descriptor):
	def __init__(self,
				 parent,
				 hopsize = 2200,
				 steps_per_octave = 12,
				 reinit = False,
				 ):

		Descriptor.__init__(self, parent,
							Default_Preprocessor = spectral.Spectrogram,
							reinit = reinit)


		#pitch = 

		#self.feature_vectors = chroma
