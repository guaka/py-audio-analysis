import ZODB, ZODB.FileStorage
from Descriptor import Descriptor
from scipy import *




import Segmentations

class Audio(Descriptor):
	def __init__(self, parent):
		Descriptor.__init__(self, parent)
		
		self.feature_vectors = self.source.soundfile.array
		self.length = len(self.feature_vectors)
		self.samplerate = self.source.soundfile.samplerate
		
		Segmentations.Frames(self,
							 self.length,
							 self.samplerate)

class RMS(Descriptor):
	def __init__(self, parent, N = 10000):
		Descriptor.__init__(self, parent,
							Default_Preprocessor = Audio)

		x = self.parent_processor.feature_vectors
		self.x_ms = x_ms = zeros((len(x) / N))
		mx = 1.0 * max(x)

		for i in range(0, len(x) / N):
			a = i * N
			b = a + N - 1
			r = x[a:b] / mx
			x_ms[i] = sum(r * r)
		self.feature_vectors = (1 / sqrt(N)) * sqrt(x_ms)
