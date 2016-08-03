
import FfAA

from Numeric import shape

#import imagesc
import scipy

from guaka_lib import isarray

def show(a, title = ''):
	"""Show function. Quite handy. :)"""

	if type(a) == list:
		for e in a:
			print e
	elif isarray(a):
		l = len(shape(a))
		if l == 1:
			scipy.gplt.plot(a)
			title or scipy.gplt.title(title)
		elif l == 2:
			imagesc.plot2d(a, palette = imagesc.brownish)
		else:
			print shape(a)

