from .util import Converter

DXPW = """\n\n```{=openxml}
<w:p>
  <w:r><w:t xml:space="preserve">%s</w:t></w:r>
</w:p>
```\n\n"""
DXPB = """```{=openxml}
<w:p>
  <w:r>
    <w:br w:type="page"/>
  </w:r>
</w:p>
```"""
DXPA = """```{=openxml}
<w:p>
  <w:pPr>
    <w:jc w:val="ALIGNMENT"/>
  </w:pPr>
  <w:r><w:t>%s</w:t></w:r>
</w:p>
```"""

def dxta(alignment):
	return DXPA.replace("ALIGNMENT", alignment)

def wt(txt, prp=False):
	if prp:
		txt = '<w:rPr>%s</w:rPr>'%(txt,)
	return '</w:t>%s<w:t xml:space="preserve">'%(txt,)

linestrips = ["NEWPAGE"]
swaps = {
	"NEWPAGE": DXPB,
	"&nbsp;": "&#160;",
	"&rsquo;": "'"
}
flags = {
	"p": {
		"strip": ["b", "br"],
		"tex": "\n\n%s\n\n",
		"sanswap": {
			"<b>": wt('<w:b w:val="true"/>', True),
			"</b>": wt('<w:b w:val="false"/>', True),
			"<br>": wt('<w:br/>')
		}
	}
}
styles = {
	"text-align": {
		"center": dxta("center"),
		"right": dxta("right"),
#		"left": dxta("left")
	}
}
nswaps = {
	"<w:r><w:t>": {
		"_": "\\_"
	}
}

class H2X(Converter):
	def __init__(self, fragment, depth=0, swappers=swaps, flaggers=flags, styles=styles, cstyles={}, linestrips=linestrips, postswaps={}, ifswaps={}, notswaps=nswaps, loud=True):
		Converter.__init__(self, fragment, depth, swappers, flaggers, styles, cstyles, linestrips, postswaps, ifswaps, notswaps, loud)

	def touchup(self):
		for line in self.translation.split("\n"):
			if "</w:t>" in line:
				marker = "\n\n%s\n\n"%(line,)
				if marker in self.translation:
					fixed = DXPW%(line,)
					self.log("touchup()", "swapping", line[:100], "for", fixed[:100])
					if "\\_" in fixed:
						self.log("touchup()", "unescaping underscores")
						fixed = fixed.replace("\\_", "_")
					self.translation = self.translation.replace(marker, fixed)