import ZODB, ZODB.FileStorage

from Descriptor import Descriptor
from scipy import *
import FFT
from pyclimate import svdeofs

import Segmentations

import my_show

from text_output import Progressbar


import audio
import spectral


class Onsets(Descriptor):
	def __init__(self,
				 parent,
				 reinit = False):

		Descriptor.__init__(self, parent,
							Default_Preprocessor = spectral.Spectrogram,
							reinit = reinit)

		
		spec = self.parent_processor.feature_vectors #[3000:5000]

		a = signal.sepfir2d(diff(transpose(spec)), [1], [.1] * 10)
		b = (where(a > 10, a, 0.))
		c = sum(b)
		d = where(c > 100.0, c, 0.)
		self.feature_vectors = d


	
