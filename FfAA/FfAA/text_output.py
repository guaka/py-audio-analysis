"""Colorized text."""

import sys


try:
	from ll import ansistyle
	text_output = ansistyle.Stream(sys.__stdout__)
	ansistyle_working = 1
except ImportError:
	ansistyle_working = 0

def print_color(color, text):
	if ansistyle_working:
		text_output.pushColor(color)
		text_output.write(text)
		text_output.popColor()
		text_output.finish()
	else:
		print text



class Progressbar:
	def __init__(self, total):
		self.total = total
		self.barwidth = 70
		self.barmask = "[%-" + str(self.barwidth) + "s]"
		self.update(0)

	def finish(self):
		self.update(self.total)
		print

	def update(self, count = None):
		"""Draw nice progress bars."""
		if count == None:
			count = self.current + 1
		self.current = count
		bardown = int(self.barwidth * (float(count) / max(1, float(self.total))))
		bar = self.barmask % ("=" * bardown)
		sys.stdout.write("\r%s %i : %i\r" % (bar, count, self.total))

