# -*- coding: UTF-8 -*-

from condox.util import symage, getstart
from condox import config

TSTART = '<table'
TSTARTEND = '<tbody>'
TEND = '\n</tr>\n</tbody>\n</table>'
TSEP = '</tr>'

swaps = {
	"_": "\\_",
	"<p>|": "|",
	"|</p>": "|",
	"&sect;": "§",
	"&ndash;": "-",
	"<br />": " \\hfill\\break ",
	"&amp;": "\\&",
	"&mu;": "$\\mu$",
	"&ldquo;": '"',
	"&rdquo;": '"',
	"&bull;": "\\textbullet",
	"text-align: left; ": "",
	"padding-left: 60px; text-align: center;": "text-align: center;",
	'<span style="text-align: center; ': '<span style="'
}
flags = {
	"center": {
		"start": '<p style="text-align: center;">',
		"end": "</p>",
		"tex": "\\begin{center}\n%s\n\\end{center}"
	},
	"right": {
		"start": '<p style="text-align: right;">',
		"end": "</p>",
		"tex": "\\begin{flushright}\n%s\n\\end{flushright}"
	},
	"underline": {
		"start": '<span style="text-decoration: underline;">',
		"end": "</span>",
		"tex": "\\underline{%s}"
	},
	"color": {
		"start": '<span style="color: #',
		"end": "</span>",
		"alt": {
			"split": "; background-color: #",
			"tex": "\\colorbox[HTML]{%s}{\\textcolor[HTML]{%s}{%s}}"
		},
		"mid": ';">',
		"tex": "\\textcolor[HTML]{%s}{%s}"
	},
	"background": {
		"start": '<span style="background-color: #',
		"end": "</span>",
		"alt": {
			"split": "; color: #",
			"tex": "\\textcolor[HTML]{%s}{\\colorbox[HTML]{%s}{%s}}"
		},
		"mid": ';">',
		"tex": "\\colorbox[HTML]{%s}{%s}"
	},
	"strong": {
		"tex": "\\textbf{%s}"
	},
	"em": {
		"tex": "\\emph{%s}"
	},
	"u": {
		"tex": "\\underline{%s}"
	},
	"p": {
		"tex": "\\hfill\\break %s \\hfill\\break"
	},
	"a": {
		"start": "<a",
		"startend": ">",
		"tex": "%s"
	},
	"img": {
		"start": '<img style="display: block; max-width: 100%;" src="../',
		"endstart": '" ',
		"end": ' />',
		"tex": "\\includegraphics[width=\\linewidth]{%s}"
	}
}
liners = {
	"ol": {
		"start": "<ol",
		"startend": ">",
		"liner": "1. %s"
	},
	"ul": {
		"start": "<ul",
		"startend": ">",
		"liner": "- %s"
	}
}
lahead = [ "\\large", "\\large", "\\Large", "\\LARGE", "\\huge", "\\Huge" ]
hflags = ["%s "%("#" * i,) for i in range(1, 7)]
hflags.reverse()
tflags = {
	"p": {
		"start": "<p",
		"startend": ">",
		"tex": " \\\\ %s"
	}
}

for i in range(1, 7):
	flags["h%s"%(i,)] = {
		"start": "<h%s"%(i,),
		"startend": ">",
		"tex": "#" * i + " %s"
	}
	tflags["h%s"%(i,)] = {
		"start": "<h%s"%(i,),
		"startend": ">",
		"tex": lahead[6 - i] + "{%s}\\normalsize "
	}

for i in range(1, 4):
	flags["t%s"%(i,)] = {
		"start": '<p style="padding-left: %spx;">'%(i * 30,),
		"end": "</p>",
		"tex": "\\begin{addmargin}[" + str(i) + "cm]{0cm}\n%s\n\\end{addmargin}"
	}

def clean(data):
	while "<div" in data:
		s = data.index("<div")
		se = data.index(">", s)
		e = data.index("</div>", s)
		data = data[:s] + data[se + 1 : e] + data[e + len("</div>"):]
	data = data.replace("\n", "")
	if "<p" in data or "<h" in data:
		data = trans(data, "p")
		for flag in tflags:
			data = trans(data, flag, tflags[flag])
		data = "\\Centerstack{%s}"%(data,)
	return data

def row(chunk):
	return [clean(part.split(">", 1)[1].split("</td>")[0]) for part in chunk.split('<td')[1:]]

TBL = """\\begin{center}
\\begin{tabular}{%s}
%s
\\end{tabular}
\\end{center}"""

def table(seg):
	rowz = list(map(row, seg.split(TSEP)))
	numcols = len(rowz[0])
	if "img" in seg:
		iorig = flags["img"]
		seg = trans(seg, "img", {
			"start": iorig["start"],
			"endstart": iorig["endstart"],
			"end": iorig["end"],
			"tex": "\\includegraphics[width=" + str(1.0 / numcols)[:3] + "\\linewidth]{%s}"
		})
		rowz = list(map(row, seg.split(TSEP)))
		return TBL%(numcols * "c", "\\\\\n\n".join([" & ".join(r) for r in rowz]))
	else:
		return "\n".join(map(bartable, rowsets(rowz)))

def rowsets(rows):
	sets = []
	curnum = None
	while len(rows):
		item = rows.pop(0)
		if curnum != len(item):
			curnum = len(item)
			if curnum == 1:
				curset = []
			else:
				curset = [["   "] * curnum]
			sets.append(curset)
		curset.append(item)
	if len(sets) == 1:
		sets[0].pop(0)
	return sets

def bartable(rowz):
	if not rowz:
		return ""
	numcols = len(rowz[0])
	if numcols == 1 and len(rowz) == 1:
		return "\\begin{center}\n%s\n\\end{center}"%(rowz[0][0],)
	rowz = [rowz[0]] + [["-" * 30] * numcols] + rowz[1:]
	return "\n%s"%("\n".join(["| %s |"%(" | ".join(r),) for r in rowz]),)

TABLE_FLAGS = {
	"start": TSTART,
	"startend": TSTARTEND,
	"end": TEND,
	"handler": table
}

def nextlast(h, flagz):
	f = None
	i = 0
	for flag in flagz:
		sflag = flagz[flag].get("start", "<%s>"%(flag,))
		fi = getstart(h, sflag)
		if fi > i:
			i = fi
			f = flag
	return f

def trans(h, flag, rules=None):
	rules = rules or flags[flag]
	sflag = rules.get("start", "<%s>"%(flag,))
	seflag = rules.get("startend")
	esflag = rules.get("endstart")
	eflag = rules.get("end", "</%s>"%(flag,))
	tex = rules.get("tex")
	while sflag in h:
		start = getstart(h, sflag)
		startend = seflag and h.index(seflag, start)
		startender = (startend or start) + len(seflag or sflag)
		endstart = esflag and h.index(esflag, startender)
		end = h.index(eflag, startender or start)
		seg = h[startender : (endstart or end)]
		if "handler" in rules:
			tx = rules["handler"](seg)
		elif "liner" in rules:
			lines = seg.strip().split("</li>")
			epart = lines.pop().replace("-", "    -")
			mdblock = "\n".join([rules["liner"]%(s.split(">", 1)[1],) for s in lines])
			tx = "\n%s\n%s\n"%(mdblock, epart)
		elif "mid" in rules:
			[c, t] = seg.split(rules["mid"], 1)
			tx = tex%(c, t)
			if "alt" in rules:
				alt = rules["alt"]
				if alt["split"] in c:
					[fg, bg] = c.split(alt["split"])
					tx = alt["tex"]%(bg, fg, t)
		else:
			if flag == "img":
				seg = symage(seg)
			tx = tex%(seg,)
		h = h[:start] + tx + h[end + len(eflag):]
	return h

def pline(line, dpref):
	for flag in hflags:
		if line.startswith(flag):
			return "%s%s"%(dpref, line)
	return line

def dhead(h, depth):
	dpref = depth * "#"
	lines = h.split("\n")
	return "\n".join([pline(line, dpref) for line in lines])

def latline(line):
	for i in range(6):
		flag = hflags[i]
		if line.startswith(flag):
			return "\n%s{%s}\\normalsize\n"%(lahead[i], line[len(flag):])
	return line

def lhead(h):
	return "\n".join(map(latline, h.split("\n")))

def fixhead(h, depth):
	if not config.toc.secheaders:
		return lhead(h)
	return dhead(h, depth)

def b2t(h):
	flag = nextlast(h, flags)
	while flag:
		h = trans(h, flag)
		flag = nextlast(h, flags)
	flag = nextlast(h, liners)
	while flag:
		h = trans(h, flag, liners[flag])
		flag = nextlast(h, liners)
	return h

def cleanup(h):
	return h.replace("{#}", "{\\#}")

def h2l(h, depth=0):
	for swap in swaps:
		h = h.replace(swap, swaps[swap])
	h = trans(h, "table", TABLE_FLAGS)
	h = b2t(h)
	h = fixhead(h, depth)
	h = cleanup(h)
	return h