"""

Processors.

- FFT,
- SVD EOF
- and more.


A Processor class should contain
 - the processing functionality,
 - (info about) its parent Processor
 - (info about) the music source
 - the calculated data
"""



import FfAA

import exceptions


import FFT  
import ZODB, ZODB.FileStorage

from scipy import *
from pyclimate import svdeofs

#
from text_output import print_color, Progressbar
import my_show


import Segmentations
import Relations



class Processor(FfAA.Calculation):
	"""Handle processing of data."""
	
	def __init__(self, parent, # pStructure
				 Default_Preprocessor = None,
				 reinit = False):

		FfAA.Calculation.__init__(self, parent)

		if Default_Preprocessor:
			if not reinit and not (Default_Preprocessor.__name__ in parent.__dict__.keys()):
				parent.__dict__[Default_Preprocessor.__name__] = Default_Preprocessor(parent)
			self.parent_processor = parent.__dict__[Default_Preprocessor.__name__]
			self.parent_processor.__dict__[self.name] = self
		else:
			self.parent_processor = None

		# self.children = FfAA.Mapping()

		#if hasattr(self.parent_processor, "segmentation"):
		#	self.segmentation = self.parent_processor.segmentation

		self._title()

	def __getitem__(self, key):
		return self.feature_vectors[key]

	def __len__(self):
		return len(self.feature_vectors)

	def __setitem__(self, key, value):
		self.feature_vectors[key] = value


	def _set_samplerate(self, hopsize):
		if self.parent_processor:
			self.samplerate = self.parent_processor.samplerate / hopsize
		else:
			self.samplerate = None

	def _delete_from_parents(self):
		del self.parent_processor.__dict__[self.name]
		del self.parent.__dict__[self.__class__.__name__]

	def reinit(self):
		self.parent.__dict__[self.__class__.__name__] = self.__class__(self.parent)
		for c in self.__dict__:
			if hasattr(c, "reinit"):
				print "reinit:", c, c.reinit
				# c.reinit()

	def _title(self, title = ""):
		title = title or type(self).__name__
		print_color(0xd, title + "\n")

	def show(self):
		my_show.show(transpose(self.feature_vectors),
					 title = self.source.name + " - " + self.name)
	
	def calc_similarity_relation(self):
		feature_vectors = self.feature_vectors
		input_shape = shape(feature_vectors)
		self.similarity_relation = Relations.Similarity_Relation(self)

	def calc_borders(self):
		self.borders = self.similarity_relation.borders

	def calc_similar_parts(self):
		self.similar_parts = self.similarity_relation.similar_parts


class Array(Processor):
	"""Dummy Processor class, to allow for arrays being used in this hierarchy."""
	
	def __init__(self, _array):
		self.feature_vectors = _array
		self.samplerate = 1
		self.source = None
		self._title()


class Marsyas(Processor):
	"""Uses executables from Marsyas, by George Tzanetakis."""

	def __init__(self, parent, type):
		if type(parent) == 'Source':
			self.source = parent
			parent = Audio_Processor(self.source)
		else:
			raise ValueError
		self._title()

		self.get_marsyas_data(type)

	def get_marsyas_data(self, type):
		self.source.decode_audio()
		marsyas_file = os.path.splitext(self.source.temp_audio)[0] + "." + type + ".mff"

		if not exists(marsyas_file):
			command = "extract " + type + " " + self.source.temp_audio
			my_execute(command)
		else:
			print marsyas_file, "already exists"

		self.feature_vectors = io.read_array(marsyas_file)



class Audio_Processor(Processor):

	def __init__(self, parent):

		Processor.__init__(self, parent)
		# self.start = start
		# self.soundfile = self.source.soundfile

		self.feature_vectors = self.source.soundfile.array 
		self.length = len(self.feature_vectors)
		self.samplerate = self.source.soundfile.samplerate

		Segmentations.Frames(self,
							 self.length,
							 self.samplerate)
							 
		# print "length of array:", len(self.feature_vectors)


class Spectrogram(Processor):
	"""FFT Processor. Calculate the log-spectrum.

	Works on 1 and 2 dimensional vectors.
	"""
	def __init__(self,
				 parent,
				 hopsize = 110,
				 framesize = None,
				 keep_bands_until = 0,
				 window_function = signal.hanning,
				 Default_Preprocessor = Audio_Processor,
				 show_progressbar = True,
				 reinit = False,
				 ):

		Processor.__init__(self, parent,
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



class Cepstrogram(Spectrogram):
	"""
	Cepstrogram Processor. Calculate the log-spectrum.
	"""
	
	def __init__(self,
				 parent,
				 hopsize = 100,
				 framesize = 512,
				 keep_bands_until = 0,
				 window_function = signal.hanning,
				 show_progressbar = True,
				 reinit = False,
				 ):

		Processor.__init__(self, parent,
						   Default_Preprocessor = Spectrogram,
						   reinit = reinit)

		if not framesize:
			lp = len(self.parent_processor)
			logfs = min(int(log2(lp / 32)), 10)
			framesize = pow(2, logfs)

		if hopsize > framesize / 3:
			hopsize = framesize / 3

		self._set_samplerate(hopsize)
		self.hopsize = hopsize
		self.framesize = framesize

		Spectrogram.__init__(self, parent,
							 hopsize = hopsize, framesize = framesize, window_function = window_function,
							 keep_bands_until = keep_bands_until,
							 Default_Preprocessor = Spectrogram)

class SVDEOFs(Processor):
	def __init__(self,
				 parent,
				 reinit = False):
		Processor.__init__(self, parent,
						   Default_Preprocessor = Cepstrogram,
						   reinit = reinit)

		self.svdeofs = svdeofs.SVDEOFs(parent.feature_vectors)
	


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



class Linear_Transform(Processor):
	def __init__(self, parent,
				 number_of_bands_to_keep = 10,
				 reinit = False,
				 ):

		Processor.__init__(self, parent,
						   Default_Preprocessor = Spectrogram,
						   reinit = reinit)

		orig_bands = shape(self.parent_processor.feature_vectors)[1]
		print orig_bands

		width = number_of_bands_to_keep
		self.where_to_put_1_list = range(width)
		unit_row = lambda x: ([0.0] * x +
							  [1.0] +
							  [0.0] * (width - x - 1))
		zero_row = [0.0] * width

		if False:
			breakpoint = 9
			self.where_to_put_1_list = range(breakpoint) + \
									   reduce(lambda x,y: x+y,
											  map(lambda x: [breakpoint + x] * (1+x), range(10)))
			
		#self.where_to_put_1_list = self.where_to_put_1_list[:orig_bands]
		self.transform_list = map(unit_row, self.where_to_put_1_list) + [zero_row] * (orig_bands - len(self.where_to_put_1_list))
		
		### self.transform_matrix = array(self.transform_list)[:, :self.where_to_put_1_list[-1]]
		self.transform_matrix = array(self.transform_list)

		self.transform_matrix
			
		
		for row in range(shape(self.transform_matrix)[1]):
			self.transform_matrix[:, row] = (self.transform_matrix[:, row]
												 / max(sum(self.transform_matrix[:, row]), 1))
		

			
		print map(shape, (self.parent_processor.feature_vectors, self.transform_matrix))
		self.feature_vectors = matrixmultiply(self.parent_processor.feature_vectors, self.transform_matrix)
		#print transform_matrix


class SVDEOF_Processor(Processor):
	def __init__(self, parent,
				 dump_vectors_beyond = 20,
				 lambda_border = 0,
				 two_dim_mode = 'separate',
				 reinit = False,
				 ):

		Processor.__init__(self, parent,
						   Default_Preprocessor = Cepstrogram,
						   reinit = reinit)

		input_vectors = self.parent_processor.feature_vectors
		input_shape = shape(input_vectors)

		if len(input_shape) > 2:
			if False and two_dim_mode == 'separate':

				print "mode:", two_dim_mode
				keep_from_band_variations = 3
				svd_input_vectors = zeros((input_shape[0], input_shape[1] * keep_from_band_variations), Float)
				counter = 0
				for spectrum_of_band in parent.feature_vectors:
					print counter
					svd_input_vectors[:, counter : counter + keep_from_band_variations - 1] = \
									 svdeofs.svdeofs(input_vectors)[0][:, :keep_from_band_variations]
					counter += keep_from_band_variations
				input_vectors = svd_input_vectors
			else:
				input_vectors = reshape(input_vectors, (input_shape[0], input_shape[1] * input_shape[2]))

		print shape(input_vectors)
		
		(z, self.lambdas, self.EOFs) = svdeofs.svdeofs(input_vectors)

		if not dump_vectors_beyond:
			if lambda_border:
				dump_vectors_beyond = argmin(greater(self.lambdas, lambda_border))

		if dump_vectors_beyond:
			self.feature_vectors = z[:, :dump_vectors_beyond]
		else:
			self.feature_vectors = z


def svd_eofs(feature_vectors, number_of_vectors_to_keep = 15, show_lambdas = 0):
	# Should be using svd_eofs.SVDEOFs here
	
	z, lambdas, EOFs = svdeofs.svdeofs(feature_vectors)
	if show_lambdas:
		my_show.show(lambdas)
	return (z[:, :number_of_vectors_to_keep], lambdas)


class UnderflowError(exceptions.OverflowError):
	pass


class PCofCepstrogram(Spectrogram):
	def __init__(self, parent,
				 framesize = None,
	 			 hopsize = 100,
				 window_function = signal.hanning,
				 number_of_vectors_used = 15,
				 reinit = False,
				 ):

		Processor.__init__(self, parent,
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



class PCofCepstrogram2(PCofCepstrogram):
	def __init__(self, parent,
				 framesize = None,
	 			 hopsize = 100,
				 window_function = signal.hanning,
				 number_of_vectors_used = 15,
				 reinit = False,
				 ):

		Processor.__init__(self, parent,
						   #  Default_Preprocessor = Cepstrogram,
						   Default_Preprocessor = Spectrogram,
						   reinit = reinit)
		if not framesize:
			lp = len(self.parent_processor)
			logfs = min(int(log2(lp / 32)), 10)
			framesize = pow(2, logfs)

		if hopsize > framesize / 16:
			hopsize = framesize / 16

		print "hopsize: ", hopsize

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

class PCofCepstrogram3(PCofCepstrogram):
	def __init__(self, parent):
		PCofCepstrogram.__init__(self, parent,
								 framesize = None,
								 window_function = signal.hanning,
								 number_of_vectors_used = 60,
								 reinit = False,
								 )

class PCofCepstrogram4(PCofCepstrogram):
	def __init__(self, parent):
		PCofCepstrogram.__init__(self, parent,
								 framesize = None,
								 window_function = signal.hanning,
								 number_of_vectors_used = 90,
								 reinit = False,
								 )


class WTFBTF(PCofCepstrogram):
	def __init__(self, parent, 
				 framesize = 32,
	 			 hopsize = 8,
				 window_function = signal.hanning,
				 number_of_vectors_used = 15,
				 reinit = False,
				 ):

		window_function = signal.hanning

		Processor.__init__(self, parent,
						   #  Default_Preprocessor = Cepstrogram,
						   Default_Preprocessor = Spectrogram,
						   reinit = reinit)

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

		self.test = self.feature_vectors
		z, lambdas, EOFs = svdeofs.svdeofs(self.feature_vectors)
		self.feature_vectors = z[:, :15]

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
	


class KMeans(Processor):
	def __init__(self,
				 parent,
				 states = 6,
				 number_of_iterations = 20,
				 reinit = False):

		Processor.__init__(self, parent,
						   Default_Preprocessor = PCofCepstrogram,
						   reinit = reinit)

		(self.codebook, self.avg_dist) = cluster.vq.kmeans(self.parent_processor.feature_vectors,
														   states,
														   number_of_iterations)
		
		print self.codebook, self.avg_dist

		(self.code, self.dist) = cluster.vq.vq(self.parent_processor.feature_vectors, self.codebook)
		self.feature_vectors = self.code

		return
		
		l = len(code)
		Z = zeros((l, l))
		for i in range(l):
			for j in range(i):
				if code[i] == code[j]:
					Z[i, j] = Z[j, i] = 1
		



		


"""
Move old stuff beyond this line
===============================
"""

class OLD_Similarity_Parts(Processor):
	def __init__(self, parent):

		Processor.__init__(self, parent,
						   Default_Preprocessor = PCofCepstrogram)

		self.parent_processor.feature_vectors


def OLD_calc_fft(input_array, hopsize, framesize,
				 window_function = signal.hanning):

	keep_bands_until = keep_bands_until or int(framesize / 2)

	do_fft = lambda arr: abs(FFT.real_fft(arr))[:keep_bands_until]

	input_shape = map(None, shape(input_array))

	window = window_function(framesize)
	if len(input_shape) > 1:
		window = transpose(array([list(window)] * input_shape[1]))

	print "input_shape:", shape(input_array)

	zeros_shape = input_shape  # this allows for both 1 and 2 dim inputs
	zeros_shape[0] = framesize
	input_array_plus_zeros = concatenate((input_array, zeros(zeros_shape)))
	fft_range = range(0, len(input_array) - framesize, hopsize)
	if show_progressbar:
		pbar = Progressbar(len(fft_range))
		output_counter = 0

	fft_array = zeros(([len(fft_range)] + 
					   map(None, shape(do_fft(window)))),
					  Float32) * 1.0  # this *1.0 is necessary!

	print shape(fft_array)
	
	for i in fft_range:
   		frame = window * input_array_plus_zeros[i : i + framesize]
		fft_array[output_counter] = 10 * log10(0.1 + do_fft(frame))

		if show_progressbar:
	   		divmod(output_counter, 128)[1] or pbar.update(output_counter)
	   		output_counter += 1

	if show_progressbar:
	   	pbar.finish()

	return fft_array


#import psyco
#psyco.bind(calculate_spectrogram)
#psyco.profile(0.2)
