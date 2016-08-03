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

"""
SoundInfo can be used to find some information about sound, and more
specific, about musical pieces.
"""


# standard python modules
import sys
import math
###############################
#
# numarray
import numarray
import numarray.fft
import numarray.linear_algebra
###############################
# 
# pyclimate
from pyclimate import svdeofs
#
#stuff coming with audiorno
#import libedso
###############################
#
# adorno modules
#
import calcRelations
import Soundfile
###############################




class PCofCepstrogram:
	"""Find principal components of the cepstrogram."""
	def __init__(self, parent,
				 framesize = None,
	 			 hopsize = 100,
				 number_of_vectors_used = 15):
		if not framesize:
			lp = len(parent)
			#logfs = min(int(scipy.log2(lp / 32)), 10)
			log2 = lambda x: math.log(x) / math.log(2)
			logfs = min(int(log2(lp / 32)), 10)
			framesize = pow(2, logfs)
			print framesize
		if hopsize > framesize / 4:
			hopsize = framesize / 4

		self.hopsize = hopsize
		self.framesize = framesize

		#if len(parent) < framesize:
		#	self._delete_from_parents()
		#	raise UnderflowError, "Thingy is too small...\nHere I pull the plug in order to avoid a segfaulty thingy."

		input_array = parent
		
		self.feature_vectors = None
		interesting_parts = input_array[:, :number_of_vectors_used]
		interesting_parts = numarray.transpose(interesting_parts)

		for row in interesting_parts:
			specspectrum = calculate_spectrogram(row,
											  framesize = framesize,
											  hopsize = hopsize)
			import cPickle
			z, lambdas, EOFs = svdeofs.svdeofs(specspectrum)
			print ".",
			s = z[:, :15]
			svd_fft_fft_vectors = numarray.transpose(s)
			
			#print "svd_eofs ok!"
			if self.feature_vectors is None:
				self.feature_vectors = numarray.transpose(svd_fft_fft_vectors)
			else:
				self.feature_vectors = numarray.concatenate((self.feature_vectors,
															numarray.transpose(svd_fft_fft_vectors)), 1)
			#print "svd_fft_fft_vectors shapes:", shape(svd_fft_fft_vectors), shape(self.feature_vectors)

		z, lambdas, EOFs = svdeofs.svdeofs(self.feature_vectors)

		self.feature_vectors = z[:, :15]
		self.arr = self.feature_vectors



def calculate_spectrogram(input_array,
						  framesize,
						  hopsize,
						  window_function = numarray.linear_algebra.mlab.hanning,
						  keep_bands_until = 0,
						  axis = 0):
	"""Calculate the spectrogram."""

	do_fft = lambda arr: abs(numarray.fft.real_fft(arr, axis = axis))[:keep_bands_until]
	
	keep_bands_until = keep_bands_until or int(framesize / 2)
	input_shape = map(None, numarray.shape(input_array))

	window = window_function(framesize)
	if len(input_shape) > 1:
		window = transpose(array([list(window)] * input_shape[1]))
		
	# print "input_shape:", shape(input_array)
	zeros_shape = input_shape  # this allows for both 1 and 2 dim inputs
	zeros_shape[0] = framesize / 2
	input_array_plus_zeros = numarray.concatenate((numarray.zeros(zeros_shape), input_array, numarray.zeros(zeros_shape)))
	fft_range = range(0, len(input_array) - framesize, hopsize)

	fft_array = numarray.zeros(([len(fft_range)] + 
								map(None, numarray.shape(do_fft(window)))),
							   # do_fft(window) is used here because it gives the right shape
							   numarray.Float32) * 1.0  # this *1.0 is necessary!
	for result_counter, input_counter in enumerate(fft_range):
		frame = window * input_array_plus_zeros[input_counter : input_counter + framesize]
		fft_array[result_counter] = 10 * numarray.log10(0.1 + do_fft(frame))

	return fft_array

class SoundInfo:
	"""Find information about soundfiles.

	The Soundfile class, which is used, can decode both the MP3 and
	the OGG format.  WAV files are supported as well.
	"""
	def __init__(self, filename):
		self.filename = filename
		self.decoded_audio = Soundfile.decode_audio(filename)
		self.soundfile = Soundfile.Soundfile(self.decoded_audio)
		self.soundfile.calc_array()
		
		print "Calculate FFT..."
		self.fft = calculate_spectrogram(self.soundfile.array,
										 framesize = 512,
										 hopsize = 110)
		
		print "Calculate info about FFT..."
		# ** On entry to DGESDD parameter number 12 had an illegal value
		self.PC_cepstr = PCofCepstrogram(self.fft)

		self.simrel = calcRelations.Similarity_Relation(self.PC_cepstr.feature_vectors)
		self.simparts = calcRelations.Similar_Parts(self.simrel.arr)
		self.borders = calcRelations.Borders(self.simrel.arr)
		
if __name__ == "__main__":
	if len(sys.argv) > 1:
		f = sys.argv[1]
		si = SoundInfo(f)
	else:
		print "Give filename as argument"
		
		
