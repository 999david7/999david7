"""Generate the README artwork: banner, whoami, projects and footer SVGs.

Run: python3 assets/gen_assets.py

The art is drawn as SVG geometry instead of text: GitHub renders the block and
box-drawing characters from mismatched fallback fonts, so a text copy drifts.
"""
import random
from pathlib import Path

GLYPHS = {
    "D": ["██████╗ ", "██╔══██╗", "██║  ██║", "██║  ██║", "██████╔╝", "╚═════╝ "],
    "A": [" █████╗ ", "██╔══██╗", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"],
    "V": ["██╗   ██╗", "██║   ██║", "██║   ██║", "╚██╗ ██╔╝", " ╚████╔╝ ", "  ╚═══╝  "],
    "I": ["██╗", "██║", "██║", "██║", "██║", "╚═╝"],
    "9": [" █████╗ ", "██╔══██╗", "╚██████║", " ╚═══██║", " █████╔╝", " ╚════╝ "],
    "W": ["██╗    ██╗", "██║    ██║", "██║ █╗ ██║", "██║███╗██║", "╚███╔███╔╝", " ╚══╝╚══╝ "],
    ".": ["   ", "   ", "   ", "   ", "██╗", "╚═╝"],
    " ": ["    "] * 6,
}
TEXT = "DAVID W."

rows = ["".join(GLYPHS[c][r] for c in TEXT).rstrip() for r in range(6)]
width = max(len(r) for r in rows)
rows = [r.ljust(width) for r in rows]
here = Path(__file__).parent

# --- SVG: every cell drawn as geometry, so alignment never depends on fonts ---
CW, CH = 12, 22          # cell size
PADX, PADY = 40, 36
G = 2.6                  # half-gap of double lines
W, H = width * CW + 2 * PADX, 6 * CH + 2 * PADY + 74

# double-line box chars: which directions they connect (l, r, u, d)
BOX = {"═": "lr", "║": "ud", "╗": "ld", "╔": "rd", "╝": "lu", "╚": "ru"}

def box_path(ch, x, y, cw=None, chh=None, g=None):
    cw, chh, G = cw or CW, chh or CH, g or globals()["G"]
    cx, cy = x + cw / 2, y + chh / 2
    l, r, u, d = x, x + cw, y, y + chh
    segs = []
    dirs = BOX[ch]
    if dirs == "lr":
        segs += [f"M{l},{cy-G}H{r}", f"M{l},{cy+G}H{r}"]
    elif dirs == "ud":
        segs += [f"M{cx-G},{u}V{d}", f"M{cx+G},{u}V{d}"]
    else:
        h = l if "l" in dirs else r          # horizontal side
        v = u if "u" in dirs else d          # vertical side
        sx = 1 if h == r else -1             # toward horizontal side
        sy = 1 if v == d else -1             # toward vertical side
        # outer stroke (far from the corner) and inner stroke (near the corner)
        ox, oy = cx - sx * G, cy - sy * G
        ix, iy = cx + sx * G, cy + sy * G
        segs += [f"M{h},{oy}H{ox}V{v}", f"M{h},{iy}H{ix}V{v}"]
    return " ".join(segs)

blocks, lines = [], []
for ri, row in enumerate(rows):
    for ci, ch in enumerate(row):
        x, y = PADX + ci * CW, PADY + ri * CH
        if ch == "█":
            blocks.append((ci, f'<rect x="{x}" y="{y}" width="{CW+0.4}" height="{CH+0.4}"/>'))
        elif ch in BOX:
            lines.append(box_path(ch, x, y))

# group blocks by column bands so they can reveal left -> right
bands = {}
for ci, rect in blocks:
    bands.setdefault(ci // 4, []).append(rect)
band_svg = "\n".join(
    f'<g class="b" style="animation-delay:{0.04*k:.2f}s">{"".join(v)}</g>'
    for k, v in sorted(bands.items())
)

ART_W = width * CW

rng = random.Random(7)
cells = {(PADX + ci * CW, PADY + ri * CH) for ri, row in enumerate(rows) for ci, ch in enumerate(row) if ch != " "}
def free(x, y):
    return (PADX + int((x - PADX) // CW) * CW, PADY + int((y - PADY) // CH) * CH) not in cells
pts = [(rng.uniform(8, W - 8), rng.uniform(30, H - 90)) for _ in range(140)]
pts = [p for p in pts if free(*p)][:70]
stars = "".join(
    f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.choice([0.6, 0.8, 1, 1.3])}" '
    f'fill="#e9d5ff" class="tw" style="animation-delay:{rng.uniform(0, 4):.2f}s;animation-duration:{rng.uniform(2, 5):.2f}s"/>'
    for x, y in pts
)

GT = PADY + 6 * CH + 18                  # top of the grid floor (horizon)
GH = H - GT
VPX = W / 2
N = 9
def gy(k):                               # perspective spacing toward the viewer
    return GT + GH * (k / N) ** 2
hlines = "".join(
    f'<rect x="0" y="{gy(k):.1f}" width="{W}" height="1" fill="#a855f7" opacity="{0.15 + 0.6 * k / N:.2f}">'
    f'<animate attributeName="y" values="{gy(k):.1f};{gy(k+1):.1f}" dur="1.6s" repeatCount="indefinite"/></rect>'
    for k in range(N)
)
vlines = "".join(
    f'<line x1="{VPX + (i * 26):.1f}" y1="{GT}" x2="{VPX + i * 26 * 9:.1f}" y2="{H}" />'
    for i in range(-16, 17)
)
grid = f'''<g clip-path="url(#frame)">
  <rect x="0" y="{GT}" width="{W}" height="{GH}" fill="url(#floor)"/>
  <g stroke="#a855f7" stroke-opacity="0.45" stroke-width="1">{vlines}</g>
  {hlines}
  <rect x="0" y="{GT-1}" width="{W}" height="2" fill="#f0abfc" filter="url(#glow)" opacity="0.9"/>
</g>'''

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{TEXT}">
<defs>
  <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="{PADX}" y1="0" x2="{PADX+ART_W}" y2="0">
    <stop offset="0" stop-color="#7c3aed"/>
    <stop offset="0.35" stop-color="#c084fc"/>
    <stop offset="0.55" stop-color="#f0abfc"/>
    <stop offset="0.75" stop-color="#a855f7"/>
    <stop offset="1" stop-color="#6d28d9"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-{ART_W} 0; {ART_W} 0" dur="6s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="grad2" gradientUnits="userSpaceOnUse" x1="{PADX}" y1="0" x2="{PADX+ART_W}" y2="0" spreadMethod="repeat">
    <stop offset="0" stop-color="#7c3aed"/><stop offset="0.5" stop-color="#e879f9"/><stop offset="1" stop-color="#7c3aed"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{ART_W} 0" dur="4s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#fff" stop-opacity="0.55"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <filter id="glow" x="-20%" y="-40%" width="140%" height="180%">
    <feGaussianBlur stdDeviation="6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect width="4" height="2" fill="#000" opacity="0.12"/>
  </pattern>
  <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3b0764" stop-opacity="0.55"/><stop offset="1" stop-color="#0d1117" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="haze" cx="0.5" cy="0.62" r="0.6">
    <stop offset="0" stop-color="#7c3aed" stop-opacity="0.28"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="14"/></clipPath>
  <clipPath id="artclip">{"".join(r for _, r in blocks)}</clipPath>
  <style>
    .b {{ opacity:0; animation: in .5s cubic-bezier(.2,.8,.2,1) forwards; }}
    @keyframes in {{ from {{ opacity:0; transform: translateY(-8px); }} to {{ opacity:1; transform:none; }} }}
    .lines {{ opacity:0; animation: fade .8s .9s forwards; }}
    @keyframes fade {{ to {{ opacity:1; }} }}
    .cursor {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity:0; }} }}
    .sub {{ font: 600 13px 'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace; letter-spacing: 3px; }}
    .tw {{ animation: tw 3s ease-in-out infinite; }}
    @keyframes tw {{ 0%,100% {{ opacity:.15; }} 50% {{ opacity:1; }} }}
    .flick {{ animation: flick 5s infinite; }}
    @keyframes flick {{ 0%,92%,100% {{ opacity:1; }} 93% {{ opacity:.6; }} 94% {{ opacity:1; }} 96% {{ opacity:.75; }} }}
  </style>
</defs>

<rect width="{W}" height="{H}" rx="14" fill="#0d1117"/>
<rect width="{W}" height="{H}" rx="14" fill="url(#haze)"/>
{stars}
{grid}
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="url(#grad2)" stroke-opacity="0.7"/>
<circle cx="20" cy="18" r="5" fill="#ff5f56"/><circle cx="37" cy="18" r="5" fill="#ffbd2e"/><circle cx="54" cy="18" r="5" fill="#27c93f"/>

<g class="flick">
  <g class="lines" fill="none" stroke="#6b21a8" stroke-width="1.6" stroke-linecap="square">
    <path d="{" ".join(lines)}"/>
  </g>
  <g fill="url(#grad)" filter="url(#glow)">
{band_svg}
  </g>
  <g clip-path="url(#artclip)">
    <rect x="-200" y="{PADY}" width="140" height="{6*CH}" fill="url(#sheen)" transform="skewX(-20)">
      <animate attributeName="x" values="-200;{W+200}" dur="3.5s" begin="1.2s" repeatCount="indefinite"/>
    </rect>
  </g>
</g>
<rect width="{W}" height="{H}" rx="14" fill="url(#scan)" pointer-events="none"/>

<rect x="{PADX-12}" y="{H-50}" width="{W-2*PADX+24}" height="32" rx="8" fill="#0d1117" fill-opacity="0.82" stroke="#7c3aed" stroke-opacity="0.5"/>
<text class="sub" x="{PADX}" y="{H-29}" fill="#c084fc">~$ <tspan fill="#c9d1d9">developer · builder · AI enthusiast · Austria</tspan><tspan class="cursor" fill="#e879f9"> █</tspan></text>
</svg>
'''
(here / "banner.svg").write_text(svg)
print("\n".join(rows))
print(W, H)

# --- footer: static terminal showing `cat ~/banner.txt` -----------------------
FY = 74                                  # top of the art
fblocks, flines = [], []
for ri, row in enumerate(rows):
    for ci, ch in enumerate(row):
        x, y = PADX + ci * CW, FY + ri * CH
        if ch == "█":
            fblocks.append(f'<rect x="{x}" y="{y}" width="{CW+0.4}" height="{CH+0.4}"/>')
        elif ch in BOX:
            flines.append(box_path(ch, x, y))
FH = FY + 6 * CH + 96
MONO = "'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace"
footer = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{FH}" viewBox="0 0 {W} {FH}" role="img" aria-label="$ cat ~/banner.txt: {TEXT}">
<defs>
  <linearGradient id="fg" gradientUnits="userSpaceOnUse" x1="{PADX}" y1="0" x2="{PADX+ART_W}" y2="0">
    <stop offset="0" stop-color="#7c3aed"/><stop offset="0.5" stop-color="#c084fc"/><stop offset="1" stop-color="#7c3aed"/>
  </linearGradient>
  <style>
    text {{ font: 600 15px {MONO}; }}
    .cursor {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity:0; }} }}
  </style>
</defs>
<rect width="{W}" height="{FH}" rx="14" fill="#0d1117"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{FH-1}" rx="14" fill="none" stroke="#7c3aed" stroke-opacity="0.7"/>
<circle cx="20" cy="18" r="5" fill="#ff5f56"/><circle cx="37" cy="18" r="5" fill="#ffbd2e"/><circle cx="54" cy="18" r="5" fill="#27c93f"/>
<text x="{PADX}" y="54" fill="#c084fc">$ <tspan fill="#c9d1d9">cat ~/banner.txt</tspan></text>
<path d="{" ".join(flines)}" fill="none" stroke="#6b21a8" stroke-width="1.6" stroke-linecap="square"/>
<g fill="url(#fg)">{"".join(fblocks)}</g>
<text x="{PADX}" y="{FY + 6*CH + 44}" fill="#c084fc">$ <tspan fill="#c9d1d9">echo "keep building"</tspan></text>
<text x="{PADX}" y="{FY + 6*CH + 70}" fill="#c9d1d9">keep building.<tspan class="cursor" fill="#e879f9"> █</tspan></text>
</svg>
'''
(here / "footer.svg").write_text(footer)


# --- shared card chrome --------------------------------------------------------
def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def chrome(w, h, title):
    return f"""<rect width="{w}" height="{h}" rx="14" fill="#0d1117"/>
<rect width="{w}" height="{h}" rx="14" fill="url(#haze)"/>
<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="14" fill="none" stroke="url(#edge)" stroke-opacity="0.8"/>
<circle cx="20" cy="18" r="5" fill="#ff5f56"/><circle cx="37" cy="18" r="5" fill="#ffbd2e"/><circle cx="54" cy="18" r="5" fill="#27c93f"/>
<text x="{w/2}" y="22" text-anchor="middle" class="t">{esc(title)}</text>"""


def defs(w, extra=""):
    return f"""<defs>
  <linearGradient id="edge" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="0" spreadMethod="repeat">
    <stop offset="0" stop-color="#7c3aed"/><stop offset="0.5" stop-color="#e879f9"/><stop offset="1" stop-color="#7c3aed"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{w} 0" dur="4s" repeatCount="indefinite"/>
  </linearGradient>
  <radialGradient id="haze" cx="0.15" cy="0.4" r="0.7">
    <stop offset="0" stop-color="#7c3aed" stop-opacity="0.18"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="logo" gradientUnits="userSpaceOnUse" x1="40" y1="96" x2="240" y2="216">
    <stop offset="0" stop-color="#7c3aed"/><stop offset="0.5" stop-color="#c084fc"/><stop offset="1" stop-color="#f0abfc"/>
  </linearGradient>
  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <style>
    text {{ font-family: {MONO}; }}
    .t {{ font-size: 12px; fill: #6b7280; }}
    .p {{ font-size: 15px; font-weight: 600; }}
    .k {{ font-size: 14px; font-weight: 700; fill: #c084fc; }}
    .v {{ font-size: 14px; fill: #c9d1d9; }}
    .r {{ opacity:0; animation: rin .45s ease-out forwards; }}
    @keyframes rin {{ from {{ opacity:0; transform: translateX(-10px); }} to {{ opacity:1; transform:none; }} }}
    .cursor {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity:0; }} }}
    {extra}
  </style>
</defs>"""


# --- whoami: neofetch-style card -------------------------------------------------
LCW, LCH, LG = 11, 20, 2.2
logo_rows = ["".join(GLYPHS[c][r] for c in "DW") for r in range(6)]
LX, LY = 40, 96
lrects, llines = [], []
for ri, row in enumerate(logo_rows):
    for ci, ch in enumerate(row):
        x, y = LX + ci * LCW, LY + ri * LCH
        if ch == "█":
            lrects.append(f'<rect x="{x}" y="{y}" width="{LCW+0.6}" height="{LCH+0.6}"/>')
        elif ch in BOX:
            llines.append(box_path(ch, x, y, LCW, LCH, LG))
logo_w = len(logo_rows[0]) * LCW

INFO = [
    ("name", "David Winkler"),
    ("handle", "@999david7"),
    ("location", "Austria · AT"),
    ("school", "HTL Anichstraße"),
    ("focus", "software · AI · automation"),
    ("stack", "Python · TS · FastAPI · React · LLMs"),
    ("status", "building ▸ learning ▸ experimenting"),
    ("bugs", "questionable engineering decisions"),
    ("motto", "“keep building.”"),
]
IX, IY, LH = LX + logo_w + 48, 92, 23
WW = W
info = [f'<text x="{IX}" y="{IY}" class="r p" style="animation-delay:.3s"><tspan fill="#e879f9">david</tspan><tspan fill="#6b7280">@</tspan><tspan fill="#a855f7">999david7</tspan></text>',
        f'<rect x="{IX}" y="{IY+9}" width="{20*8.4:.0f}" height="1.5" fill="#7c3aed" class="r" style="animation-delay:.4s"/>']
for i, (k, v) in enumerate(INFO):
    y = IY + 30 + i * LH
    info.append(f'<text x="{IX}" y="{y}" class="r" style="animation-delay:{0.5 + i*0.12:.2f}s"><tspan class="k">{k}</tspan><tspan x="{IX+92}" class="v">{esc(v)}</tspan></text>')
py = IY + 30 + len(INFO) * LH
PAL = ["#0d1117", "#3b0764", "#6b21a8", "#7c3aed", "#9333ea", "#a855f7", "#c084fc", "#e879f9", "#f0abfc", "#c9d1d9"]
info.append("".join(f'<rect x="{IX + i*26}" y="{py - 8}" width="24" height="14" rx="2" fill="{c}" class="r" style="animation-delay:{0.5 + len(INFO)*0.12 + i*0.04:.2f}s"/>' for i, c in enumerate(PAL)))
WH = py + 32
whoami = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WW}" height="{WH}" viewBox="0 0 {WW} {WH}" role="img" aria-label="whoami: David Winkler, @999david7, Austria, HTL Anichstra&#223;e">
{defs(WW, ".float {{ animation: float 4s ease-in-out infinite; }} @keyframes float {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-4px); }} }}".replace("{{", "{").replace("}}", "}"))}
{chrome(WW, WH, "david@999david7: ~")}
<text x="{LX}" y="58" class="p" fill="#c084fc">$ <tspan fill="#c9d1d9">neofetch</tspan></text>
<g class="float">
  <path d="{" ".join(llines)}" fill="none" stroke="#6b21a8" stroke-width="1.3" stroke-linecap="square"/>
  <g fill="url(#logo)" filter="url(#glow)">{"".join(lrects)}</g>
</g>
{chr(10).join(info)}
</svg>
"""
(here / "whoami.svg").write_text(whoami)


# --- projects: three neon cards ------------------------------------------------
PROJECTS = [
    ("01", "~/ai-automation", ["AI tools, agents and", "automation experiments."], ["Python", "FastAPI", "LLMs", "RAG"]),
    ("02", "~/web", ["Apps, sites and", "experiments with ideas."], ["TypeScript", "React", "Next.js"]),
    ("03", "~/random-stuff", ["Side projects and things", "I build because I can."], ["Python", "Docker", "Git"]),
]
GAP, CWD = 16, (W - 2 * 24 - 2 * 16) / 3
PH = 214
cards = []
for n, (num, name, desc, tags) in enumerate(PROJECTS):
    x0, y0 = 24 + n * (CWD + GAP), 52
    ch_ = PH - y0 - 20
    d = n * 0.25
    tag_svg, tx, ty = [], x0 + 16, y0 + 88
    for t in tags:
        tw = len(t) * 6.8 + 16
        if tx + tw > x0 + CWD - 12:
            tx, ty = x0 + 16, ty + 22
        tag_svg.append(f'<rect x="{tx:.1f}" y="{ty}" width="{tw:.1f}" height="18" rx="9" fill="#2e1065" stroke="#7c3aed" stroke-opacity="0.7"/>'
                       f'<text x="{tx + tw/2:.1f}" y="{ty + 13}" text-anchor="middle" font-size="11" fill="#e9d5ff">{esc(t)}</text>')
        tx += tw + 6
    cards.append(f"""<g class="r" style="animation-delay:{0.2 + d:.2f}s">
  <rect x="{x0:.1f}" y="{y0}" width="{CWD:.1f}" height="{ch_}" rx="12" fill="#161b22"/>
  <rect x="{x0:.1f}" y="{y0}" width="{CWD:.1f}" height="{ch_}" rx="12" fill="none" stroke="url(#edge)" stroke-width="1.5" filter="url(#glow)" class="pulse" style="animation-delay:{d:.2f}s"/>
  <text x="{x0 + CWD - 12:.1f}" y="{y0 + ch_ - 12}" text-anchor="end" font-size="44" font-weight="800" fill="#7c3aed" fill-opacity="0.16">{num}</text>
  <text x="{x0 + 16:.1f}" y="{y0 + 28}" font-size="14" font-weight="700" fill="#e879f9">{esc(name)}</text>
  <text x="{x0 + 16:.1f}" y="{y0 + 52}" font-size="12.5" fill="#9ca3af">{esc(desc[0])}</text>
  <text x="{x0 + 16:.1f}" y="{y0 + 68}" font-size="12.5" fill="#9ca3af">{esc(desc[1])}</text>
  {"".join(tag_svg)}
</g>""")
projects = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{PH}" viewBox="0 0 {W} {PH}" role="img" aria-label="Projects: AI and automation, web projects, random stuff">
{defs(W, ".pulse { animation: pulse 3s ease-in-out infinite; } @keyframes pulse { 0%,100% { stroke-opacity:.35; } 50% { stroke-opacity:1; } }")}
{chrome(W, PH, "~/projects")}
{chr(10).join(cards)}
</svg>
"""
(here / "projects.svg").write_text(projects)
