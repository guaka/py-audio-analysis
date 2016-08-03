from __future__ import division


import ZODB, ZODB.FileStorage

from Descriptor import Descriptor
from scipy import *

import Segmentations
import my_show
from text_output import Progressbar

import audio

from RandomArray import normal
from scipy.signal import buttord, butter, lfilter
import Interactive



def bandpass_filter(s, freq1, freq2, Nyq):
	#dt = 0.001
	#t = arange(0.0, 10.0, dt)
	#nse = normal(0, 1.4, t.shape)
	#s = sin(2*pi*t) + nse
    #Nyq = 1/(2*dt)

	d = 1.1
	Wp = [freq1 / Nyq, freq2 / Nyq]
	Ws = [Wp[0] / d, Wp[1] * d]
	print Wp, Ws
	[n,Wn] = buttord(Wp, Ws, 3, 60)
	print "%ith order" % n
	[b,a] = butter(n,Wn)
	print [b,a]
	return lfilter(b,a,s)


class Chroma(Descriptor):
	"""FFT Processor. Calculate the log-spectrum.
	
	Works on 1 and 2 dimensional vectors.
	"""
	def __init__(self,
				 parent,
				 hopsize = 2200,
				 steps_per_octave = 12,
				 reinit = False,
				 ):

		Descriptor.__init__(self, parent,
							Default_Preprocessor = audio.Audio,
							reinit = reinit)

		a_sgn = self.parent_processor.feature_vectors
		Nyq = self.parent_processor.samplerate / 2.
		l = int(len(a_sgn) / hopsize)
		chroma = zeros((12, l), typecode = 'f') * 1.0
		self.bands = []

		note_to_freq = lambda n: pow(2, (n-69) / 12.) * 440

		for n in range(36, 36 + 12):
			f1 = note_to_freq(n)
			f2 = note_to_freq(n+1)
			print f1, f2
			band = bandpass_filter(a_sgn, f1, f2, Nyq)
			band = log(abs(band) + 1)
			print len(band), l
			band = reshape(band[:l * hopsize], (l, hopsize))
			print shape(band)
			print n % 12
			band = sum(band, 1)
			self.bands.append(band)
			chroma[n % 12] += band

		chroma = transpose(chroma) / (sum(chroma, 1) + 1)

		self.feature_vectors = chroma
