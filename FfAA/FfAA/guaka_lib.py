"""
A collection of various useful stuff.
"""

import os
import scipy.xplt
import sys

from Numeric import *
import scipy.gplt
from scipy.cluster.vq import whiten



if sys.version_info[0] < 2:
	print "You're working with Python 1.x. Expect a lot of troubles!"
elif sys.version_info[1] < 2:
	print "You're working with a Python version below 2.2. Expect troubles!"
elif sys.version_info[2] < 2:
	False = 0
	True = 1


__imagesc_cb_ever_called_before = 0

def isarray(thing):
	try:
		thing.__class__.__name__
		return False
	except AttributeError:
		return thing.typecode() and True


def type(thing):
	"""Return type as string.

	Also tries to deal with Numeric arrays.
	numarray could be a problem here."""
	try:
		return thing.__class__.__name__
	except AttributeError:
		return thing.typecode() and "array"

def imagesc_cb(thing):
	global __imagesc_cb_ever_called_before
	if not __imagesc_cb_ever_called_before:
		print "The imagesc_cb is called twice the first time in order to avoid the buggy black spots."
		scipy.xplt.imagesc_cb(thing)
	scipy.xplt.imagesc_cb(thing)
	__imagesc_cb_ever_called_before = 1

def my_execute(command):
	"""Show and execute shell command."""
	print command
	os.system(command)

def show(a,
		 wait_when_imagesc_cb_ing = 0,
		 title = ''):
	"""Show array. Works for both 1D and 2D arrays."""

	if type(a) == "list":

		for e in a:
			print e

	elif type(a) == "array":
		
		l = len(shape(a))
		if l == 1:
			scipy.gplt.plot(a)
			title or scipy.gplt.title(title)
		elif l == 2:
			imagesc_cb(a)
			if wait_when_imagesc_cb_ing == 1:
				raw_input()
		else:
			print shape(a)

def normalize(arr):
	max = float(ravel(arr)[argmax(ravel(arr))])  # find maximum value
	min = float(ravel(arr)[argmin(ravel(arr))])
	dif = (max - min) or 1
	return (arr - min) / dif


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

def repeatedlyinvoke(func, n):
	"""Invoke func times times.

	Thanks to exarkun at #python."""
	
	def invoker(arg):
		for i in range(n):
			arg = func(arg)
		return arg
	return invoker




def delete_if_exists(file):
	if os.path.exists(file):
		os.remove(file)

