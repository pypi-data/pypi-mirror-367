from cantools.web import strip_html, strip_html_carefully
from cantools.util.data import rgb2hex
from condox.util import symage, colormap
from .html2latex.rules import styles, cstyles

class Fragment(object):
	def __init__(self, fragment, starter, rules, styles=styles, cstyles=cstyles, loud=False):
		self.fragment = fragment
		self.starter = starter
		self.rules = rules
		self.styles = styles
		self.cstyles = cstyles
		self.loud = loud
		self.realign()

	def log(self, *msg):
		self.loud and print("Fragment", *msg)

	def repstart(self, a, b):
		self.log("repstart()", "swapping", a, "for", b)
		self.starter = self.starter.replace(a, b)

	def realign(self):
		aligner = ' align="'
		if not aligner in self.starter:
			return self.log("realign()", "aligner not present:", self.starter)
		alignment = self.starter.split(aligner).pop().split('"').pop(0)
		stysta = ' style="'
		sta = '%stext-align: %s;'%(stysta, alignment)
		if "style" in self.starter:
			self.repstart(stysta, '%s '%(sta,))
		else:
			self.repstart('%s%s"'%(aligner, alignment), '%s"'%(sta,))

	def attribute(self, aname, ender='"'):
		self.log("attribute()", aname, self.starter)
		starter = '%s="'%(aname,)
		if starter not in self.starter:
			return None
		start = self.starter.index(starter) + len(starter)
		end = self.starter.index(ender, start)
		return self.starter[start:end]

	def style(self, tx):
		if self.rules.get("nostyle"):
			return tx
		srules = self.attribute("style", ';"')
		if not srules:
			return tx
		colz = {}
		for rule in srules.split("; "):
			[key, val] = rule.split(": ")
			if key in self.styles:
				if val in self.styles[key]:
					self.log("style()", "restyling from:", tx)
					tx = self.styles[key][val]%(tx,)
					self.log("to:", tx)
			elif key in self.cstyles:
				colz[key] = val

		for key in ["background-color", "color", "border-color"]:
			if key in colz:
				val = colz[key]
				self.log("style()", key, "restyling from:", tx)
				if key == "background-color" or key == "border-color":
					hval = colormap(val)
				else: # color (\textcolor[HTML])
					if "rgb" in val:
						hval = rgb2hex(val)
					else:
						hval = val[-6:]
				tx = self.cstyles[key]%(hval, tx)
				self.log("to:", tx)
		return tx

	def sanitize(self, seg): # mainly strip for now
		strip = self.rules.get("strip")
		if strip == True:
			seg = strip_html(seg)
		elif strip:
			seg = strip_html_carefully(seg, strip)
		sanswap = self.rules.get("sanswap")
		if sanswap:
			for k, v in sanswap.items():
				seg = seg.replace(k, v)
		return seg

	def _translate(self):
		seg = self.style(self.sanitize(self.fragment))
		if "handler" in self.rules:
			return self.rules["handler"](seg)
		if "liner" in self.rules:
			lines = seg.strip().split("</li>")
			epart = lines.pop().replace("- ", "    - ")
			mdblock = "\n".join([self.rules["liner"]%(s.split(">", 1)[1].replace("- ",
				"    - "),) for s in lines])
			return "\n%s\n%s\n"%(mdblock, epart)
		if self.rules.get("sym"):
			seg = symage(seg)
		tex = self.rules.get("tex")
		if self.rules.get("href"):
			self.log("href", self.starter, seg)
			return tex%(self.attribute("href"), seg)
		return tex%(seg,)

	def translate(self):
		self.log("before:", self.fragment)
		trans = self._translate()
		self.log("after:", trans)
		return trans