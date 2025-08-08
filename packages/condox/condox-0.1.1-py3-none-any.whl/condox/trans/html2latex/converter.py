from .util import TABLE_FLAGS, flags, swaps, styles, cstyles, trans, Converter
from .header import Header

linestrips = ["NEWPAGE"]
pswaps = {
	"{#}": "{\\#}",
	"NEWPAGE": "\\newpage"
}
iswaps = {
	"\\begin{center}": {
		" \\hfill\\break ": " \\\\ "
	}
}

class H2L(Converter):
	def __init__(self, fragment, depth=0, swappers=swaps, flaggers=flags, styles=styles, cstyles=cstyles, linestrips=linestrips, postswaps=pswaps, ifswaps=iswaps, notswaps={}, loud=False):
		Converter.__init__(self, fragment, depth, swappers, flaggers, styles, cstyles, linestrips, postswaps, ifswaps, notswaps, loud)
		self.header = Header()

	def translate(self):
		self.swapem()
		self.translation = trans(self.translation, "table", TABLE_FLAGS)
		self.bottomsup()
		self.translation = self.header(self.translation, self.depth)
		self.cleanup()
		return self.translation