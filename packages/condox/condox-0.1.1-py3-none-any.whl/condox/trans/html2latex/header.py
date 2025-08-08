from .util import headers
from condox import config

class Header(object):
	def sectionize(self, line, dpref):
		for flag in headers["section"]:
			if line.startswith(flag):
				return "%s%s"%(dpref, line)
		return line

	def section(self, h, depth):
		dpref = depth * "#"
		lines = h.split("\n")
		return "\n".join([self.sectionize(line, dpref) for line in lines])

	def biggerize(self, line):
		hflags = headers["section"]
		lahead = headers["latex"]
		for i in range(6):
			flag = hflags[i]
			if line.startswith(flag):
				return "\n%s %s \\normalsize\n"%(lahead[i], line[len(flag):])
		return line

	def upsize(self, h):
		return "\n".join(map(self.biggerize, h.split("\n")))

	def __call__(self, h, depth):
		if config.toc.secheaders:
			return self.section(h, depth)
		return self.upsize(h)

