from pyclimate import svdeofs

import Relations

class MorePreciseSimilarParts(Relations.Parts): #Similar_Parts):
	def __init__(self, parent):
		Relations.Parts.__init__(self, parent)

		parent.sort(lambda x,y: cmp(x.start[1], y.start[1]))
		self.pcofcepstrogram = parent.parent.parent
		self.spectrogram = self.pcofcepstrogram.parent_processor

		for part in parent:
			self.analyse_part(part)


	def analyse_part(self, part):
		start, end = (part.start[0] * self.pcofcepstrogram.hopsize,
					  (part.end[0] + part.end[1]) * self.pcofcepstrogram.hopsize + self.pcofcepstrogram.framesize)
		print start, end
		
		self.append([self.spectrogram.feature_vectors[start : end]])
		
		eofs = svdeofs.SVDEOFs(self[-1][0])
		self[-1].append(eofs.pcs()[:,:10])


class Similarity_Band(Relations.Fuzzy_Relation):
	pass
