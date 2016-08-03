
import Image

from Numeric import *
import MLab

import Image

from scipy import pilutil

def normalize_rows(arr):
	min = zeros(len(arr), Float32)
	max = zeros(len(arr), Float32)
	dif = zeros(len(arr), Float32)
	for r in arange(len(arr)):
		max[r] = arr[r, argmax(arr[r])]
		min[r] = arr[r, argmin(arr[r])]
		dif[r] = max[r] - min[r]
		if dif[r] == 0:
			dif[r] = 1
	return (arr - outerproduct(min, [1] * shape(arr)[1])) / outerproduct(dif, [1] * shape(arr)[1])


a = arange(0, 1., 1/256.)


palfuncs = lambda f,g,h: transpose(normalize_rows(concatenate((f(a)[NewAxis,:],
															   g(a)[NewAxis,:],
															   h(a)[NewAxis,:]))) * 255).astype('b')


id = lambda x: x

# (lambda x:25 * sqrt(x) + 0.8*x + (x+1)*(0.4*x-1)

(lambda x: 1.01 * x*x*x - 2.1 * x*x + 1.4 * x)

gray = palfuncs(id, id, id)
brownish = palfuncs(sin, exp, lambda x: x*x*x)

p2 = palfuncs(sin, exp, lambda x: sqrt(x))
p3 = palfuncs(sin,
			  lambda x: 1.01 * x*x*x - 2.1 * x*x + 1.4 * x,
			  lambda x: sqrt(x))


def plot2d(arr, size = (700, 600), palette = gray, dontscale = False):

	if dontscale:
		im = pilutil.toimage(MLab.flipud(arr), pal = palette, cmin = 0., cmax = 1.)
	else:
		im = pilutil.toimage(MLab.flipud(arr), pal = palette)

	if size:
		im = im.resize(size)

	
	im.show()
