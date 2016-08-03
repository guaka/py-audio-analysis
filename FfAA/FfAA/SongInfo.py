
import FfAA
import ZODB, ZODB.FileStorage
import Structures


class SongInfo(FfAA.Base):
	"""Entered information
	and mechanisms to compare it to the calculated information."""
	
	def __init__(self, parent, name, borderinfo = None):
		FfAA.Base.__init__(self, parent)
		self.name = name

	def __repr__(self):
		return self._my_repr(self.name, self.BorderInfo)

	def calc_score(self):
		self.score = self.BorderInfo.score

	def calc_structure(self):
		if self.name in Structures.structures.keys():
			self.structure = Structures.structures[self.name]
			self.set_parent(self.structure)
		else:
			self.structure = False
			raise KeyError, self.name + " not in structures, cannot compare entered and calculated data"

		
class BorderInfo(FfAA.List):
	"""Human entered border information."""

	def __init__(self, parent, borderlist = []):
		FfAA.List.__init__(self, parent)
		self.debug = False
		for b in borderlist:
			if type(b) in [int, float]:
				b = (b,)
			self.append(b)

	def test(self):
		self.calculated = self.parent.structure.more_precise_borders
		self.dist = self.parent.structure.source.length / 100.0

		self.good = {}
		self.not_found = []
		self.miscalculated = []

		cntr = 0
		l = len(self.calculated)

		for h in self:
			if self.debug:
				print "cntr: ", cntr
			c = self.calculated[cntr]
			while h[0] - c[0] > self.dist:
				if not c in self.good.values():
					self.debug_print("bad: " + repr(c))
					self.miscalculated.append(c)

				cntr += 1
				if cntr < l:
					c = self.calculated[cntr]
				else:
					break
			if abs(h[0] - c[0]) <= self.dist:
				self.debug_print("good: " + repr(h) + repr(c))
				self.good[h] = c

				cntr += 1
			if h not in self.good.keys():
				self.debug_print("not found: " + repr(h))
				self.not_found.append(h)

			if cntr < l:
				c = self.calculated[cntr]
			else:
				break

		self.tested = True

	def calc_score(self):
		"""Evaluate border information. .. How?"""
		
		if hasattr(self.parent.structure, "more_precise_borders"):
			if not hasattr(self, "tested") or not self.tested:
				self.test()

			self.score = -len(self.not_found)
			self.score -= len(self.miscalculated)
			d = self.dist
			good_scores = map(lambda a: 2 - abs(a[0][0] - a[1][0]) / d, self.good.items())
			self.debug_print (repr(good_scores))
			self.score += reduce(lambda x,y: x+y, good_scores)


songinfo = FfAA.Mapping()

def add_info(name, borderinfolist):
	if Structures.structures:
		parent = None
		if name in Structures.structures.keys():
			parent = Structures.structures[name]
		songinfo[name] = SongInfo(parent, name)
		BorderInfo(songinfo[name], borderinfolist)


add_info("iriXx-AltDamagedGoods",
		 [(32, "noise"),
		  (58, "end of noise"),
		  (79, "melodic thingy"),
		  (126, "filter thingy"),
		  (144, "just some rattle"),
		  (183, "rhythm thingy again"),
		  (359, "voice"),
		  (363, "non-beat"),
		  (368, "beat again")])
		  
		  



add_info("Guaka-IdLikeAShower",
		 [(24, "we are lonely"),
		  (30, "beatblip start"),
		  (40, "other tones start"),
		  (54, "change of tonality"),
		  (62, "back"),
		  (77, "xmas snares and bells"),
		  (92, "peep bleep"),
		  (109, "drop beat"),
		  (115, "beat again, high pitched sounds"),
		  (146, "we are lonely"),
		  (177, "verse"),
		  (200, "drop beat"),
		  (207, "outro")
		  ])

add_info("TWISTED HELICES - Oppression: the thought police",
		 [(4.5, "change"),
		  (13.1, "voice 'first they came'"),
		  (40.4, ""),
		  (60, "end of voice"),
		  (68, "voice: 'police..'"),
		  (88, "female voice"),
		  (90, "male voice again"),
		  (132, "no voice"),
		  (138, "guitar"),
		  (158, "high pitched thing"),
		  (166, ""),
		  (228, ""),
		  (251, ""),
		  (248, "voice")
		  ])

add_info("guaka-gtrshv",
		 [2,
		  4.6,
		  26.2,
		  55.0,
		  60 * 1+55,
		  60 * 2+11,
		  60 * 2+23,
		  ])

add_info("BeastieBoys-InAWorldGoneMad",
		 [(10.7, "start of snare"),
		  (19.6, "'world gone mad..'"),
		  (29.0, "break, yeah"),
		  (31.5, "high pitched voice"),
		  (40.8, "raw voice"),
		  (50.2, "now, voice"),
		  (60.0, "verse"),
		  (69.8, "break, yeah"),
		  (72.4, "break thingy"),
		  (77.1, "add hats"),
		  (79.7, "add snares"),
		  (81.8, "raw voice"),
		  (91.3, ""),
		  (100.8, "verse"),
		  (111.1, ""),
		  (119.8, ""),
		  (127.5, ""),
		  (129.8, ""),
		  (180.8, "outro, low profile"),
		  (189.9, "outro, high profile"),
		  (207.7, "end")
		  ])

add_info("wox-morceau1",
		 [(8, "thingy"),
		  (36, "fm start"),
		  (180 + 51, "higher pitched thingy"),
		  (245, ".."),
		  (304, "piano intermezzo"),
		  (315, "piano intermezzo"),
		  (332, "final piano chord")
		  ])


"""
BeastieBoys-InAWorldGoneMad 9.04592660127
Guaka-IdLikeAShower 9.30176767677
TWISTED HELICES - Oppression: the thought police 1.66801400362
guaka-gtrshv -0.826543670407
iriXx-AltDamagedGoods -28.3289350188
wox-morceau1 -1.19749933097

using 30 dimensions of EOF vectors:
BeastieBoys-InAWorldGoneMad 9.04592660127
Guaka-IdLikeAShower 9.30176767677
TWISTED HELICES - Oppression: the thought police 1.66801400362
guaka-gtrshv -0.826543670407
iriXx-AltDamagedGoods -23.704119738
wox-morceau1 -1.51501976882

"""	  


def evaluater():
	for i in songinfo:
		if hasattr(i, "score"):
			print i.name + " " + str(i.score) #evaluate()

#evaluater()
