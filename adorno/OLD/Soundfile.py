
# standard python modules
import wave
###############################
#
# numarray
import numarray
###############################

class Soundfile:
	def __init__(self, filename):
		self.filename = filename
		w = wave.open(filename, 'r')
		self.sampwidth = w.getsampwidth() 
		self.framerate = w.getframerate()
		self.number_of_frames = w.getnframes()
		self.samplerate = float(11025) #self.framerate
		
	def calc_array(self):
		wave_object = self._get_wave()
		wave_object.setpos(0)
		self.frames = wave_object.readframes(self.number_of_frames)
		wave_object.close()
		w = wave_object.getsampwidth()
		if w == 2: #16 bits
			arr = numarray.fromstring(self.frames, numarray.Int16)

		#http://www.pythonapocrypha.com/Chapter32/Chapter32.shtml
		elif w == 1: #8 bits
			arr = numarray.array(self.frames, typecode = numarray.UnsignedInt8, savespace = 1)

		else:
			print "Not handled: samples are", w * 8, "bit"
			raise Error
		self.array = arr

