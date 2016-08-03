
"""Several functions to deal with soundfiles.

Uses
- ecasound (http://eca.cx)
- libsamplefile aka Secret Rabbit Code)
- xmms


Also a class Soundfile that uses standard wave module at the moment.
Doesn't use libsndfile yet.
"""


import os
import commands

from text_output import print_color

# from scipy import *
from os.path import exists



def my_execute(command):
	# should check out Bio.Application
	print_color(0x03, command + "\n")
	#print command
	os.system(command)

def delete_if_exists(file):
	if exists(file):
		os.remove(file)


def decode_audio(source, dest):
	"""Copy part (start, start+length) from source into dest."""

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

	delete_if_exists(tmp2)

	#command = "sndfile-resample -to 11025 " + tmp + " " + dest

def listen(source, start = 0, length = 0, program = "", dsp = "/dev/dsp"):
	"""Listen to audio."""

	# if program == "xmms":
	
	# command = "xmms -p "

	command = "noatun "
	command += source
	command += " &"

	"""
	else: #  if program == "ecasound":
		command = "ecasound -i:" + source
	    #command += " -f:16,1,44100 "
		if length > 0:
			command += " -t:" + repr(length)
		command += " -y:" + repr(start)
		command += " -o:" + dsp
		command += "&"
	my_execute(command)
	print
	"""
		

#sf = Soundfile("audio/harry.ogg.0-90.wav")
#sf = Soundfile("audio/shorttest.wav")
#print sf.get_array()
