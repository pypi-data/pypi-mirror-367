from condox.util import getstart
from .html2latex.rules import flags, styles, cstyles
from .fragment import Fragment

#
# misc
#

def nextlast(h, flagz):
	f = None
	i = -1
	for flag in flagz:
		startflag = flagz[flag].get("start")
		if startflag:
			sflags = [startflag]
		else:
			sflags = ["<%s "%(flag,), "<%s>"%(flag,)]
		for sflag in sflags:
			fi = getstart(h, sflag)
			if fi > i:
				i = fi
				f = flag
	return f

def trans(h, flag, rules=None, flags=flags, styles=styles, cstyles=cstyles, listed=False, loud=False):
	rules = rules or flags[flag]
#	sflag = rules.get("start", "<%s"%(flag,))
	sflag = rules.get("start")
	altstart = None
	if not sflag:
		sflag = "<%s>"%(flag,)
		altstart = "<%s "%(flag,)
	seflag = rules.get("startend", ">")
	aseflag = rules.get("altstartend")
	esflag = rules.get("endstart")
	eflag = rules.get("end", "</%s>"%(flag,))
	tex = rules.get("tex")
	fragset = []
	while sflag in h or altstart and altstart in h:
		start = getstart(h, sflag)
		if altstart:
			start = max(start, getstart(h, altstart))
		startend = seflag and h.find(seflag, start)
		selen = len(seflag or sflag)
		if aseflag:
			altstartend = h.find(aseflag, start)
			if altstartend != -1 and (startend == -1 or altstartend < startend):
				startend = altstartend
				selen = len(aseflag)
		if startend == -1:
			end = h.index(eflag, start)
			seg = h[start:end + len(eflag)]
			print("discarding bad node: %s"%(seg,))
			h = h[:start] + h[end + len(eflag):]
		else:
			startender = (startend or start) + selen
			endstart = esflag and h.index(esflag, startender)
			end = h.index(eflag, startender or start)
			starter = h[start : startender]
			seg = h[startender : (endstart or end)]
			frag = Fragment(seg, starter, rules, styles, cstyles, loud).translate()
			fragset.insert(0, frag)
			h = h[:start] + frag + h[end + len(eflag):]
	return listed and fragset or h

class Converter(object):
	def __init__(self, fragment, depth=0, swappers={}, flaggers={}, styles={}, cstyles={}, linestrips=[], postswaps={}, ifswaps={}, notswaps={}, loud=False):
		self.fragment = fragment
		self.depth = depth
		self.swappers = swappers
		self.flaggers = flaggers
		self.styles = styles
		self.cstyles = cstyles
		self.linestrips = linestrips
		self.postswaps = postswaps
		self.ifswaps = ifswaps
		self.notswaps = notswaps
		self.loud = loud
		self.uncomment()
		linestrips and self.striplines()

	def log(self, *msg):
		self.loud and print(*msg)

	def striplines(self):
		lines = []
		for line in self.fragment.split("\n"):
			for flag in self.linestrips:
				if flag in line:
					lines.append(flag)
				else:
					lines.append(line)
		self.fragment = "\n".join(lines)

	def uncomment(self):
		cs = "<!--"
		ce = "-->"
		while cs in self.fragment:
			start = self.fragment.index(cs)
			end = self.fragment.index(ce, start)
			self.fragment = self.fragment[:start] + self.fragment[end + 3:]

	def translate(self):
		self.swapem()
		self.log("\n======================\n", "prebot", self.translation[:200], "\n======================\n")
		self.bottomsup()
		self.log("\n======================\n", "preclean", self.translation[:200], "\n======================\n")
		self.cleanup()
		self.log("\n======================\n", "postclean", self.translation[:200], "\n======================\n")
		return self.translation

	def swapem(self):
		self.translation = self._swap(self.fragment, self.swappers)

	def bottomsup(self):
		h = self.translation
		flag = nextlast(h, self.flaggers)
		while flag:
			self.log("transing", flag, h[:100])
			h = trans(h, flag, flags=self.flaggers, styles=self.styles, cstyles=self.cstyles, loud=self.loud)
			flag = nextlast(h, self.flaggers)
		self.translation = h

	def _swap(self, txt, swapz, logline=False):
		for k, v in swapz.items():
			if k in txt:
				if logline:
					vbit = "%s on %s"%(v, txt)
				else:
					vbit = v
				self.log("swapping", k, "for", vbit)
				txt = txt.replace(k, v)
		return txt

	def cleanup(self):
		self.translation = self._swap(self.translation, self.postswaps)
		lines = []
		for line in self.translation.split("\n"):
			for flag in self.ifswaps:
				if flag in line:
					line = self._swap(line, self.ifswaps[flag], True)
			for flag in self.notswaps:
				if flag not in line:
					line = self._swap(line, self.notswaps[flag], True)
			lines.append(line)
		self.translation = "\n".join(lines)
		hasattr(self, "touchup") and self.touchup()