import FfAA

import ZODB, ZODB.FileStorage
# from Persistence import Persistent

import os
import wave
import commands

import Numeric
#
# pyao: http://www.andrewchatham.com/pyogg/
import ao


import soundfile
from text_output import print_color




class Source(FfAA.Base):
	"""The audio source.

	s = Source(filename, name)
	"""
	
	def __init__(self, filename, name):
		self.filename = filename
		self.name = name
		self.temp_audio = None

		self.decode_audio()

	def __repr__(self):
		return self._my_repr(self.filename, self.name)

	def description(self):
		return self.filename

	def listen(self, startPos = 0):
		"""Listen to filex, startPos in milliseconds"""
		soundfile.my_execute("noatun&")
		soundfile.my_execute("dcop noatun Noatun addFile " + commands.mkarg(self.filename) + " 1")
		soundfile.my_execute("dcop noatun Noatun skipTo " + str(int(round(startPos))))

	def open_with(self, program):
		# program = FfAA.Settings.preferred_program
		# dsp = FfAA.Settings.preferred_dsp

		#	sf = Soundfile(self.filename)
		#	sf.listen()

		# command = "xmms -p "
		command = program + " "
		command += commands.mkarg(self.filename)
		command += " &"

		print_color(0x03, command + "\n")
		os.system(command)

	def decode_audio(self):
		"""Decode selected part of file."""

		temp_dir = FfAA.Settings.temp_dir
		if not os.path.exists(temp_dir):
			os.mkdir(temp_dir)
		
		#self.temp_audio = temp_dir + os.path.basename(self.filename) + ".wav"
		self.temp_audio = os.path.join(temp_dir, os.path.basename(self.filename) + ".wav")
		print "decode_audio:", self.temp_audio
		if not os.path.exists(self.temp_audio):
			soundfile.decode_audio(self.filename, self.temp_audio)
		else:
			print_color(0x06, self.temp_audio + " already exists\n")
	
	def calc_soundfile(self):
		os.path.exists(self.temp_audio) or self.decode_audio()
		self.soundfile = Soundfile(self.temp_audio)

	def calc_length(self):
		self.length = self.soundfile.length



class Soundfile(FfAA.Base):
	def __init__(self, filename, mode = 'r'):
		self.filename = filename
		w = self._get_wave(filename, mode)

		if 1:  # wave_object is read_object
			self.channels = w.getnchannels() 
			self.sampwidth = w.getsampwidth() 
			self.framerate = w.getframerate()
			self.number_of_frames = w.getnframes()
			#print self.framerate, self.sampwidth
			self.samplerate = float(11025) #self.framerate
			
	def _get_wave(self,
				  filename = "",
				  mode = 'r'):
		if filename == "":
			filename = self.filename
		return wave.open(filename, mode)

	def listen(self,
			   start = 0,
			   length = 0,
			   dsp = "/dev/dsp"):


		device = ao.AudioDevice("oss",
								bits = 16,
								rate = self.framerate,
								channels = self.channels)
		wave_object = self._get_wave()

		startframe = int(start * self.framerate)
		if length == 0:
			length = self.number_of_frames -  startframe
		else:
			length = int(length * self.framerate)
		wave_object.setpos(startframe)

		print "start, length:", start, length
		print startframe, length
		
		frames = wave_object.readframes(length)

		try:
			device.play(frames)
		except KeyboardInterrupt:
			pass
		del device


	def calc_array(self):
		#fr = self.wave_object.readframes(self.number_of_frames)
		length = self.number_of_frames

		wave_object = self._get_wave()
		
		wave_object.setpos(0)
		self.frames = wave_object.readframes(length)
		wave_object.close()

		w = wave_object.getsampwidth()

		if w == 2: #16 bits
			arr = Numeric.fromstring(self.frames, Numeric.Int16)

		#http://www.pythonapocrypha.com/Chapter32/Chapter32.shtml
		elif w == 1: #8 bits
			arr = Numeric.array(self.frames, typecode = Numeric.UnsignedInt8, savespace = 1)

		else:
			print "Not handled: samples are", w * 8, "bit"
			raise Error

		self.array = arr

	def calc_length(self):
		self.length = len(self.array) / self.samplerate
