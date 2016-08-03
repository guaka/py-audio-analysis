#!/usr/bin/python

# (c) 2004 Guaka
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or (at
#  your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#  USA.

# standard python modules
import os
import commands
import wave
###############################
#
# numarray
import numarray
###############################


def decode_audio(source, dest = ""):
	def my_execute(command):
		print command
		os.system(command)

	if not dest:
		dest = os.path.split(source)[1] + ".wav"
	if not os.path.exists(dest):
		source_ext = os.path.splitext(source)[1]
		tmp2 = ""
		if source_ext == ".mp3":
			tmp2 = dest + "temp.wav"
			my_execute("mpg321 " + commands.mkarg(source) + " --wav " + commands.mkarg(tmp2))
			source = tmp2
		if source_ext == ".ogg":
			tmp2 = dest + "temp.wav"
			my_execute("ogg123 " + commands.mkarg(source) + " -d wav -f " + commands.mkarg(tmp2))
			source = tmp2
		command = "sox " + commands.mkarg(source) + " -c 1 -r 11025 " + commands.mkarg(dest)
		my_execute(command)
	return dest



class Soundfile:
	def __init__(self, filename):
		self.filename = os.path.expanduser(filename)
		self.wave_object = wave.open(self.filename, 'r')
		self.sampwidth = self.wave_object.getsampwidth() 
		self.framerate = self.wave_object.getframerate()
		self.number_of_frames = self.wave_object.getnframes()
		self.samplerate = float(11025) #self.framerate
		
	def calc_array(self):
		self.wave_object.setpos(0)
		self.frames = self.wave_object.readframes(self.number_of_frames)
		self.wave_object.close()
		w = self.wave_object.getsampwidth()
		if w == 2: #16 bits
			arr = numarray.fromstring(self.frames, numarray.Int16)

		#http://www.pythonapocrypha.com/Chapter32/Chapter32.shtml
		elif w == 1: #8 bits
			arr = numarray.array(self.frames, typecode = numarray.UnsignedInt8, savespace = 1)

		else:
			print "Not handled: samples are", w * 8, "bit"
			raise Error
		self.array = arr

