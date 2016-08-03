
import ZODB, ZODB.FileStorage

from Descriptor import Descriptor
from scipy import *
import FFT
from pyclimate import svdeofs

import Segmentations

import my_show

from text_output import Progressbar


import audio

class Spectrogram(Descriptor):
	"""FFT Processor. Calculate the log-spectrum.
	
	Works on 1 and 2 dimensional vectors.
	"""
	def __init__(self,
				 parent,
				 hopsize = 110,
				 framesize = None,
				 keep_bands_until = 0,
				 window_function = signal.hanning,
				 Default_Preprocessor = audio.Audio,
				 show_progressbar = True,
				 reinit = False,
				 ):

		Descriptor.__init__(self, parent,
							Default_Preprocessor = Default_Preprocessor,
							reinit = reinit)

		self._set_samplerate(hopsize)

		if not framesize:
			lp = len(self.parent_processor)
			logfs = min(int(log2(lp / 32)), 8)
			framesize = pow(2, logfs)

		self.framesize = framesize
		self.hopsize = hopsize

		self.feature_vectors = calculate_spectrogram(self.parent_processor.feature_vectors,
												  framesize = framesize,
												  hopsize = hopsize,
												  keep_bands_until = keep_bands_until,
												  window_function = window_function,
												  show_progressbar = 1)

		self.segmentation = Segmentations.Frames(self,
												 len(self.feature_vectors),
												 self.parent_processor.samplerate,
												 framesize = framesize,
												 hopsize = hopsize,
												 window_function = window_function)


def calculate_spectrogram(input_array,
						  framesize,
						  hopsize,
						  window_function,
						  keep_bands_until = 0,
						  axis = 0,
						  show_progressbar = 0
						  ):

	# TODO Segmentation should be determined here!
	
	#Segmentations.Frames(self,
	#					 len(self.
	
	
	# print "Calculating FFT..."
	do_fft = lambda arr: abs(FFT.real_fft(arr, axis = axis))[:keep_bands_until]
	
	keep_bands_until = keep_bands_until or int(framesize / 2)
	input_shape = map(None, shape(input_array))

	window = window_function(framesize)
	if len(input_shape) > 1:
		window = transpose(array([list(window)] * input_shape[1]))
		
	# print "input_shape:", shape(input_array)
	zeros_shape = input_shape  # this allows for both 1 and 2 dim inputs
	zeros_shape[0] = framesize / 2
	input_array_plus_zeros = concatenate((zeros(zeros_shape), input_array, zeros(zeros_shape)))
	fft_range = range(0, len(input_array) - framesize, hopsize)

	fft_array = zeros(([len(fft_range)] + 
					   map(None, shape(do_fft(window)))),
					  # do_fft(window) is used here because it gives the right shape
					  Float32) * 1.0  # this *1.0 is necessary!
	
	# print shape(fft_array)
	if show_progressbar:
		pbar = Progressbar(len(fft_range))

	output_counter = 0
	for i in fft_range:
		frame = window * input_array_plus_zeros[i : i + framesize]
		fft_array[output_counter] = 10 * log10(0.1 + do_fft(frame))
		output_counter += 1
			
		if show_progressbar:
			divmod(output_counter, 128)[1] or pbar.update(output_counter)

	if show_progressbar:
		pbar.finish()
	# print "outputshape:", shape(fft_array)
	return fft_array




class PCofCepstrogram(Spectrogram):
	def __init__(self, parent,
				 framesize = None,
	 			 hopsize = 100,
				 window_function = signal.hanning,
				 number_of_vectors_used = 15,
				 reinit = False,
				 ):

		Descriptor.__init__(self, parent,
						   #  Default_Preprocessor = Cepstrogram,
						   Default_Preprocessor = Spectrogram,
						   reinit = reinit)

		if not framesize:
			lp = len(self.parent_processor)
			logfs = min(int(log2(lp / 32)), 10)
			framesize = pow(2, logfs)

		if hopsize > framesize / 4:
			hopsize = framesize / 4

		self._set_samplerate(hopsize)
		self.hopsize = hopsize
		self.framesize = framesize


		print "EOF..."

		if len(self.parent_processor) < framesize:
			self._delete_from_parents()
			raise UnderflowError, "Thingy is too small...\nHere I pull the plug in order to avoid a segfaulty thingy."

		self.svd_fft_fft(self.parent_processor.feature_vectors,
						 framesize = framesize,
						 hopsize = hopsize,
						 window_function = window_function,
						 number_of_vectors_used = number_of_vectors_used)

		z, lambdas, EOFs = svdeofs.svdeofs(self.feature_vectors)
		self.feature_vectors = z[:, :15]

		#self.feature_vectors, self.lambdas = svd_eofs(self.feature_vectors,
		#											  number_of_vectors_to_keep = 15)
		
		Segmentations.Frames(self,
							 len(self.feature_vectors),
							 self.parent_processor.samplerate,
							 framesize,
							 hopsize,
							 window_function = window_function,
							 )

	def svd_fft_fft(self, input_array,
					framesize,
					hopsize,
					window_function = signal.hanning,
					number_of_vectors_used = 256):
		pbar = Progressbar(number_of_vectors_used)
		self.feature_vectors = None
		interesting_parts = input_array[:, :number_of_vectors_used]
		interesting_parts = transpose(interesting_parts)

		for row in interesting_parts:
			# print "row shape:", shape(row)
			pbar.update()
			#fft = parent.feature_vectors
			specspectrum = calculate_spectrogram(row,
											  framesize = framesize,
											  hopsize = hopsize,
											  window_function = window_function,
											  show_progressbar = 0)
			#z, lambdas, EOFs = svdeofs.svdeofs(fft)
			#svd_fft_fft_vectors = transpose(z[:, :15])
			svd_fft_fft_vectors = transpose(svd_eofs(specspectrum)[0])
			
			if self.feature_vectors is None:
				self.feature_vectors = transpose(svd_fft_fft_vectors)
			else:
				self.feature_vectors = concatenate((self.feature_vectors,
													transpose(svd_fft_fft_vectors)), 1)
			#print "svd_fft_fft_vectors shapes:", shape(svd_fft_fft_vectors), shape(self.feature_vectors)
		pbar.finish()
		#self.show()

def svd_eofs(feature_vectors, number_of_vectors_to_keep = 15, show_lambdas = 0):
	# Should be using svd_eofs.SVDEOFs here
	
	z, lambdas, EOFs = svdeofs.svdeofs(feature_vectors)
	if show_lambdas:
		my_show.show(lambdas)
	return (z[:, :number_of_vectors_to_keep], lambdas)



