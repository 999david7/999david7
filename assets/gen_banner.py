"""Generate assets/banner.txt and assets/banner.svg (ANSI-shadow 'DAVID 999')."""
from pathlib import Path

GLYPHS = {
    "D": ["██████╗ ", "██╔══██╗", "██║  ██║", "██║  ██║", "██████╔╝", "╚═════╝ "],
    "A": [" █████╗ ", "██╔══██╗", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"],
    "V": ["██╗   ██╗", "██║   ██║", "██║   ██║", "╚██╗ ██╔╝", " ╚████╔╝ ", "  ╚═══╝  "],
    "I": ["██╗", "██║", "██║", "██║", "██║", "╚═╝"],
    "9": [" █████╗ ", "██╔══██╗", "╚██████║", " ╚═══██║", " █████╔╝", " ╚════╝ "],
    " ": ["    "] * 6,
}
TEXT = "DAVID 999"

rows = ["".join(GLYPHS[c][r] for c in TEXT).rstrip() for r in range(6)]
width = max(len(r) for r in rows)
rows = [r.ljust(width) for r in rows]
here = Path(__file__).parent
(here / "banner.txt").write_text("\n".join(r.rstrip() for r in rows) + "\n")

# --- SVG: every cell drawn as geometry, so alignment never depends on fonts ---
CW, CH = 12, 22          # cell size
PADX, PADY = 40, 36
G = 2.6                  # half-gap of double lines
W, H = width * CW + 2 * PADX, 6 * CH + 2 * PADY + 34

# double-line box chars: which directions they connect (l, r, u, d)
BOX = {"═": "lr", "║": "ud", "╗": "ld", "╔": "rd", "╝": "lu", "╚": "ru"}

def box_path(ch, x, y):
    cx, cy = x + CW / 2, y + CH / 2
    l, r, u, d = x, x + CW, y, y + CH
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
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="DAVID 999">
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
  <clipPath id="artclip">{"".join(r for _, r in blocks)}</clipPath>
  <style>
    .b {{ opacity:0; animation: in .5s cubic-bezier(.2,.8,.2,1) forwards; }}
    @keyframes in {{ from {{ opacity:0; transform: translateY(-8px); }} to {{ opacity:1; transform:none; }} }}
    .lines {{ opacity:0; animation: fade .8s .9s forwards; }}
    @keyframes fade {{ to {{ opacity:1; }} }}
    .cursor {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity:0; }} }}
    .sub {{ font: 600 13px 'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace; letter-spacing: 3px; }}
    .flick {{ animation: flick 5s infinite; }}
    @keyframes flick {{ 0%,92%,100% {{ opacity:1; }} 93% {{ opacity:.6; }} 94% {{ opacity:1; }} 96% {{ opacity:.75; }} }}
  </style>
</defs>

<rect width="{W}" height="{H}" rx="14" fill="#0d1117"/>
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

<text class="sub" x="{PADX}" y="{H-24}" fill="#c084fc">~$ <tspan fill="#c9d1d9">developer · builder · AI enthusiast · Austria</tspan><tspan class="cursor" fill="#e879f9"> █</tspan></text>
</svg>
'''
(here / "banner.svg").write_text(svg)
print("\n".join(rows))
print(W, H)
