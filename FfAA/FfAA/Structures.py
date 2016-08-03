#!/usr/bin/env python2.2

import FfAA
import Audio
import Processors
import Relations

import os
from struct import unpack


import ZODB
import ZODB.FileStorage  # still necessary...
try:
	import ID3
except:
	ID3 = None


from text_output import print_color
from my_show import show



class Structure(FfAA.Base):
	"""Contains information about musical structure."""

	def __init__(self, source, parent = None, reinit = 0):

		self.source = source
		self.name = source.name
		self.parent = parent
		
		# self.segmentations = FfAA.Mapping()
		# self.relations = FfAA.Mapping()
		# self.processors = FfAA.Mapping()
		
		return

		p = Processors.Audio_Processor(self)
		if len(p) > 512:
			p = Processors.Spectrogram(self)
			if len(p) > 512:
				#p = Processors.PCofCepstrogram(self)
				#p = Processors.PCofCepstrogram2(self)
				#p = Processors.PCofCepstrogram3(self)
				p = Processors.PCofCepstrogram(self)

		self.similarity_relation = p.similarity_relation

		self.similar_parts = p.similar_parts
		self.borders = p.borders

		if isinstance(p, Processors.PCofCepstrogram):
			self.more_precise_borders = Relations.MorePreciseBorders(self.Spectrogram, self.borders)

		import SongInfo
		if self.name in SongInfo.songinfo.keys():
			SongInfo.songinfo[self.name].set_parent(self)
		#SongInfo.songinfo


		save()

		# except Processors.UnderflowError:

	#def __repr__(self):
	#	return self._my_repr(self.source, self.parent)
			
	def reinit(self):
		self.parent.reinit_structure(self.source.name)

	def delete(self):
		self.parent.__delitem__(self.source.name)

	def __len__(self):
		return self.source.length
	
	def show(self):
		print_color(0x0f, self.source.name + "\n")
		print "  ", self.description()

	def description(self):
		return self.source.description()




class Structures(FfAA.Mapping):
	"""Store musical structures in one convenient class."""

	def init_structure(self, name, file = "", reinit = False):
		"""Initialize structure."""

		file = file or self[name].source.filename
		self[name] = Structure(Audio.Source(file, name),
							   parent = self,
							   reinit = reinit)
		save()
		return(self[name])

	def reinit_structure(self, key):
		"""Delete temporary files and start over again."""
		
		structure = self[key]
		name = structure.source.name
		file = structure.source.filename
		# self.init_structure(name, file,  reinit = True)
		self.init_structure(name, file,  reinit = False)

	def reinit_all_structures(self):
		for k in self.keys():
			self.reinit_structure(k)

	def reinit(self):
		self.reinit_all_structures()

	def remove(self, key):
		del self[key]
		save()

	def show(self):
		"""Show overview of structures."""

		for k in self.keys():
			self[k].show()
			print



class Initializer:
	def __init__(self, structures):
		self.structures = structures
		self.accepted_extensions = [".ogg", ".mp3", ".wav"]
		self.dir = ""
	
	def add_files(self, files_string, accepted_extensions = None, maximum = None):
		"""Initialize sound structures from directory or from glob.

		For example:

		add_files("/data/music/*/*")

		Only the files that have accepted_extensions are taken from
		the files that fulfill the pattern.

		Doesn't handle ~ directories yet.

		returns a list of the newly created or already existing structures
		"""

		from glob import glob

		new_structures = []
		accepted_extensions = accepted_extensions or self.accepted_extensions

		files_string = os.path.expanduser(files_string) # expand tilde

		if os.path.split(files_string)[1]:
			files = glob(files_string) # find files 
			files = filter(lambda x: os.path.splitext(x)[1] in accepted_extensions, 
						   files) # keep only files with accepted extensions

			print len(files), "files to add:"
			show(files)
			print

			for file in files:
				new_structures.append(self.add_file(file))
				if maximum and len(new_structures) >= maximum:
					break
			return new_structures

		else:
			files = glob(files_string + "/*") # find files 
			files = filter(lambda x: os.path.splitext(x)[1] in accepted_extensions, 
						   files) # keep only files with accepted extensions
			print len(files), "files in directory, none processed"
			return files
			

	def add_file(self, file):
		"""Create structure from file.
		returns the (possibly already existing) structure.
		"""
		name = os.path.basename(file)
		name, ext = os.path.splitext(name)
		file = os.path.expanduser(self.dir + file)
		
		if True: # ext == ".mp3":
			if ID3:
				id = ID3.ID3(file)
				k = id.keys()
				if "ARTIST" in k and "TITLE" in k:
					name = id["ARTIST"] + " - " + id["TITLE"]

		if not os.path.exists(file):
			print file, "does not exist!\n"
		else:
			if name in structures.keys():
				print "already in structures:", name
				return structures[name]
			else:
				print_color(0x09, "processing: " + name + "\n")
				new_structure = structures.init_structure(name, file)
				get_transaction().commit()
				return new_structure


def save():
	get_transaction().commit()

def close_db():
	save()
	_database.close()

def get_stored_structure_data():
	try:
		f = FfAA.Settings.file_for_storing_structures
		d = os.path.split(f)[0]
		if not os.path.exists(d):
			print "Creating directory", d
			os.mkdir(d)
		storage = ZODB.FileStorage.FileStorage(f)
	
		db = ZODB.DB(storage)
		conn = db.open()
	
		dbroot = conn.root()
		if not dbroot.has_key('structures'):
			print_color (3, "Add structures to database\n")
			dbroot['structures'] = Structures()

		structures = dbroot['structures']
		init = Initializer(structures)

	except ZODB.POSException.StorageSystemError:
		print "Sound Structure database already opened by another process."
		db = structures = init = None

	return db, structures, init


_database, structures, init = get_stored_structure_data()

if structures:
	print "structures = dbroot['structures']"
	print "init = Initializer(structures)"

