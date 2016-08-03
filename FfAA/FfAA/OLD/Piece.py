
import FfAA
import Audio


class Piece(FfAA.Base):
	def __init__(self, parent):
		FfAA.Base.__init__(self, parent)

		if not isinstance(parent, Audio.Source):
			raise TypeError

		self.source = parent
		self.channels = FfAA.Mapping()
		



class Channel(FfAA.Base):
	def __init__(self, parent):
		FfAA.Base.__init__(self, parent)

		p = Processors.Audio_Processor(self)
		if len(p) > 512:
			p = Processors.Spectrogram(self)
			if len(p) > 512:
				p = Processors.PCofCepstrogram(self)

		self.similarity_relation = p.similarity_relation

		self.similar_parts = p.similar_parts
		self.borders = p.borders

		if isinstance(p, Processors.PCofCepstrogram):
			self.more_precise_borders = Relations.MorePreciseBorders(self.Spectrogram, self.borders)

