"""

FfAA --- Framework for Audio Applications
=========================================


Available subpackages
---------------------

"""



#
# http://www.scipy.org
from scipy import *
from UserList import UserList


def load_settings():
	"""Try to load settings module.

	Some code taken from imp example in Python manual."""

	import imp, os

	s_path = os.path.expanduser("~/.FfAA/")
	s_file = "Settings.py"
	s_pathfile = os.path.join(s_path, s_file)

	if not os.path.exists(s_path):
		os.mkdir(s_path)
		print "Created", s_path

	if not os.path.exists(s_pathfile):
		from shutil import copyfile
		def_settings = "Default" + s_file
		copyfile(def_settings, s_pathfile)
		print "Copied", def_settings, "to", s_pathfile
	print

	fp, pathname, description = imp.find_module("Settings", [os.path.expanduser("~/.FfAA/")])
	# return imp.load_module("settings", fp, pathname, description)
	try:
		return imp.load_module("Settings", fp, pathname, description)
	    #except ImportError, s:
	finally:
		# Since we may exit via an exception, close fp explicitly.
		if fp:
			fp.close()


Settings = load_settings()



try:
	import ZODB, ZODB.FileStorage
	from Persistence import Persistent, PersistentMapping
	from ZODB.PersistentList import PersistentList
	_ZODB_available = True

except ImportError:
	print \
		  """ZODB is not installed, there will be no database.
		  
		  You might want to install ZODB, the Zope Object Database.
		  A standalone version can be found at:
		  
		  http://www.zope.org/Products/StandaloneZODB
		  """

	Persistent = object
	PersistentMapping = dict
	_ZODB_available = False



class Base(Persistent):
	"""An effort to a generic class that has all it takes to do this stuff.
	"""

	def __init__(self, parent):
		self.name = self.__class__.__name__
		self.debug = False
		self.set_parent(parent)

	def set_parent(self, parent):
		self.parent = parent
		if is_FfAA_instance(parent):
			parent.__dict__[self.__class__.__name__] = self

			if hasattr(parent, "segmentation"):
				self.segmentation = parent.segmentation

	def get_children(self):
		attrs = [attr for attr in dir(self)
				 if (is_FfAA_instance(attr) or
					 attr[0] != "_" and
					 not attr in ["parent", "name", "inheritedAttribute"] and
					 not 'func_name' in dir(getattr(self, attr))
					 )]
		d = Mapping()
		for i in attrs:
			d[i] = getattr(self, i)
		return d

    #children = property(get_children, None, None, "object's children")

	def __getattr__(self, name):
		# .__getattr__ is only called when hasattr(self, name) == False

		if name == "children":
			return self.get_children()
		
		fname = "calc_" + name
		if hasattr(self, fname):
			exec("self." + fname + "()")
			return getattr(self, name)

		if name == "source":
			return self.parent.source

		raise AttributeError


	def _my_repr(self, *r):
		return self.__class__.__name__ + \
			   '(' + string.join(map(repr, r), ', ') + ')'
	         # '("' + string.join(r, '", "') + '")'

	def debug_print(self, s):
		if self.debug:
			print s

if False:
	class Audio(Base):
		pass


class Calculation(Base):
	def __init__(self, parent):
		Base.__init__(self, parent)


"""
Using PersistentList results in errors:
"""
class List(Base):
	def __init__(self, parent):
		Base.__init__(self, parent)
		self.__pers_list = PersistentList()

	def show(self):
		for x in self:
			print x

	def __repr__(self):
		return self.__pers_list.__repr__()

	def __getitem__(self, key):
		return self.__pers_list.__getitem__(key)

	def __len__(self):
		return self.__pers_list.__len__()

	def __getattr__(self, name):
		if name in ["append", "extend", "insert", "pop", "remove", "reverse", "sort"]:
			return getattr(self.__pers_list, name)
		return Base.__getattr__(self, name)


class Mapping(PersistentMapping):
	"""An enhanced dict. Has some properties of list.

	This class is started from a little example given somewhere in
	the Python docs (guess it's where the built-in objects are
	declared to be subclassable).

	It is now something between a list and a dict.

	>>> a = mydict()
	>>> a['test'] = 'thingy'
	>>> a['zzz'] = 'aap'
	>>> print a[0]
	thingy
	>>> a['est']
	'aap'


	WARNING

	Though this would be extremely welcome, Mapping is not a subclass of Base.
	"""

	def keys(self):
		my_keys = PersistentMapping.keys(self)
		my_keys.sort()
		return my_keys

	def get_list(self):
		return map(lambda x: self[x], self.keys())

	list = property(get_list, None, None,
					"Get the PersistentMapping object as a list.")

	def show(self):
		for key in self.keys():
			print key + ":", self[key]

	def __setitem__ (self, key, value):
		PersistentMapping.__setitem__(self, key, value)

	def __getitem__ (self, key):
		try:
			return PersistentMapping.__getitem__(self, key)

		except KeyError:
			if type(key) == type(0):
				return self.get_list()[key]

   			if type(key) == type(""):
				keys = self.keys()

				l = self.__class__()
				# first check if key can be found in start of key-strings
				shortened_keys = map(lambda x: (x, x[:len(key)]), keys)
				for k, sk in shortened_keys:
					if key == sk:
						l[k] = self[k]

				if len(l) == 0:
					# then check if it can be found anywhere
					for k in keys:
						if k.find(key) > -1:
							l[k] = self[k]

				# return either 1 object or list of objects
				if len(l) == 1:
					return l[0]
				if l:
					return l

			# key not found, so
			raise KeyError



def is_FfAA_instance(obj):
	if not hasattr(obj, "__class__"):
		return False
	cl = obj.__class__
	return issubclass(cl, Base) or issubclass(cl, Mapping)

	
