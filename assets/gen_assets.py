"""Generate the README cards in the portfolio's theme (paper and ink).

Run: python3 assets/gen_assets.py   (needs: pip install fonttools brotli)

Same palette and fonts as the portfolio (League Gothic, Cormorant Garamond,
Shadows Into Light), own content and layout. README images can't load web
fonts, so each SVG embeds a subset of them. Text widths are measured from the
font files so wrapping and alignment match.
"""
import base64
import io
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent

# --- content ---------------------------------------------------------------------
QUOTE = "Tutte le cose belle prima o poi finiscono."
NAME = "David W."
HANDLE = "@999david7"
TAGLINE = "building things \u00b7 breaking things \u00b7 learning things"
ROLES = "Developer \u00b7 Builder \u00b7 AI enthusiast"
PLACE = "Innsbruck, Austria"
SCHOOL = "HTL Anichstra\u00dfe"
PROJECTS = [
    ("AI & Automation", "AI-powered tools, agents and automation experiments.", ["Python", "FastAPI", "LLMs", "RAG"]),
    ("Web Projects", "Building applications and experimenting with new ideas.", ["TypeScript", "React", "Next.js"]),
    ("Random Stuff", "Side projects, experiments and things I build because I can.", ["Python", "Docker", "Git"]),
]
STACK = [
    ("Languages", "Python \u00b7 JavaScript \u00b7 TypeScript"),
    ("Back end", "FastAPI \u00b7 Node.js \u00b7 REST"),
    ("Front end", "React \u00b7 Next.js \u00b7 HTML \u00b7 CSS"),
    ("AI", "Claude \u00b7 OpenAI \u00b7 Gemini \u00b7 RAG"),
    ("Data", "PostgreSQL \u00b7 SQLite \u00b7 MongoDB"),
    ("Tools", "Git \u00b7 Docker \u00b7 Linux \u00b7 VS Code"),
]
CURRENTLY = ["building", "learning", "experimenting", "making questionable engineering decisions"]
MOTTO = "keep building."


# --- palette (portfolio :root) -----------------------------------------------------
BG, INK = "#FCFBF8", "#17140F"
MUTED, FAINT, LINE = 0.56, 0.34, 0.12          # ink opacities
W, PAD = 880, 64
EASE = "cubic-bezier(.33,1,.68,1)"


# --- fonts -------------------------------------------------------------------------
class Font:
    def __init__(self, family, file):
        self.family, self.path = family, HERE / "fonts" / file
        tt = TTFont(self.path)
        self.cmap, self.hmtx = tt.getBestCmap(), tt["hmtx"].metrics
        self.upm = tt["head"].unitsPerEm
        self.used = set()

    def width(self, text, size, ls=0.0):
        adv = sum(self.hmtx[self.cmap.get(ord(c), ".notdef")][0] for c in text)
        return adv * size / self.upm + ls * size * max(len(text) - 1, 0)

    def face(self):
        opts = subset.Options()
        opts.flavor, opts.layout_features = "woff2", ["kern", "liga"]
        sub = subset.Subsetter(opts)
        tt = TTFont(self.path)
        sub.populate(text="".join(sorted(self.used)) + " ")
        sub.subset(tt)
        buf = io.BytesIO()
        tt.flavor = "woff2"
        tt.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        return f"@font-face {{ font-family: '{self.family}'; src: url(data:font/woff2;base64,{b64}) format('woff2'); }}"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Card:
    """One paper card. Collects elements and the glyphs each font needs."""

    def __init__(self):
        self.fonts = {
            "display": Font("PDisplay", "league-gothic.ttf"),
            "serif": Font("PSerif", "garamond-400.ttf"),
            "serif5": Font("PSerif5", "garamond-500.ttf"),
            "italic": Font("PItalic", "garamond-italic.ttf"),
            "script": Font("PScript", "shadows.ttf"),
        }
        self.els, self.defs, self.anim = [], [], 0

    def text(self, x, y, s, font="serif", size=18, op=1.0, ls=0.0, anchor="start", upper=False):
        f = self.fonts[font]
        s = s.upper() if upper else s
        f.used.update(s)
        if anchor == "middle":                      # center on glyphs, not trailing tracking
            x, anchor = x - f.width(s, size, ls) / 2, "start"
        attrs = f'x="{x:.1f}" y="{y:.1f}" font-family="{f.family}" font-size="{size}"'
        if op != 1:
            attrs += f' fill-opacity="{op}"'
        if ls:
            attrs += f' letter-spacing="{ls * size:.2f}"'
        if anchor != "start":
            attrs += f' text-anchor="{anchor}"'
        self.els.append(f"<text {attrs}>{esc(s)}</text>")

    def wrap(self, s, font, size, maxw):
        f, lines, cur = self.fonts[font], [], ""
        for word in s.split():
            test = f"{cur} {word}".strip()
            if f.width(test, size) > maxw and cur:
                lines.append(cur)
                cur = word
            else:
                cur = test
        return lines + [cur]

    def para(self, x, y, s, font, size, maxw, lh, op=1.0):
        for line in self.wrap(s, font, size, maxw):
            self.text(x, y, line, font, size, op)
            y += lh
        return y

    def hline(self, y, x0=PAD, x1=W - PAD):
        self.els.append(f'<rect x="{x0}" y="{y:.1f}" width="{x1 - x0}" height="1" fill="{INK}" fill-opacity="{LINE}"/>')

    def label(self, y, s):
        self.text(PAD, y, s, "serif", 15, FAINT, ls=0.26, upper=True)

    def rise(self):
        """Wrap everything added since the last call in a staggered fade-up."""
        body = self.els[self.anim:]
        del self.els[self.anim:]
        n = len([e for e in self.els if e.startswith('<g class="in"')])
        self.els.append(f'<g class="in" style="animation-delay:{0.1 + 0.14 * n:.2f}s">{"".join(body)}</g>')
        self.anim = len(self.els)

    def save(self, name, h, label):
        faces = "\n".join(f.face() for f in self.fonts.values() if f.used)
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{h:.0f}" viewBox="0 0 {W} {h:.0f}" role="img" aria-label="{esc(label)}">
<defs>
<style>
{faces}
text {{ fill: {INK}; }}
.in {{ animation: rise 1.1s {EASE} both; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} }}
/* the signature writes itself in from left to right, like the portfolio footer */
.sign {{ animation: write 1.6s cubic-bezier(.65,0,.35,1) .6s both; }}
@keyframes write {{ from {{ clip-path: inset(0 100% 0 0); }} to {{ clip-path: inset(0 0 0 0); }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
{"".join(self.defs)}
</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1:.0f}" rx="16" fill="{BG}" stroke="{INK}" stroke-opacity="0.08"/>
{chr(10).join(self.els)}
</svg>
"""
        (HERE / f"{name}.svg").write_text(svg)
        print(f"{name}.svg  {len(svg) // 1024} KB")



def rule(c, y, op=1.0, h=1.0, x0=PAD, x1=W - PAD):
    c.els.append(f'<rect x="{x0}" y="{y:.1f}" width="{x1 - x0}" height="{h}" fill="{INK}" fill-opacity="{op}"/>')


def caps(c, x, y, s, size=13, op=FAINT, anchor="start"):
    c.text(x, y, s, "serif", size, op, ls=0.22, anchor=anchor, upper=True)


# --- masthead ------------------------------------------------------------------------
c = Card()
caps(c, PAD, 58, f"Nº 999 — {PLACE}")
c.text(W - PAD, 58, HANDLE, "italic", 16, MUTED, anchor="end")
rule(c, 72, 0.9, 2)
rule(c, 77, 0.9, 0.75)
c.rise()
c.text(W / 2, 130, QUOTE, "italic", 26, anchor="middle")
c.rise()
c.text(W / 2, 318, NAME, "display", 190, ls=0.06, anchor="middle", upper=True)
c.rise()
rule(c, 352, 0.9, 0.75)
rule(c, 357, 0.9, 2)
c.text(W / 2, 410, TAGLINE, "script", 30, anchor="middle")
c.rise()
caps(c, PAD, 462, ROLES)
c.text(W - PAD, 462, SCHOOL, "italic", 16, MUTED, anchor="end")
c.rise()
c.save("hero", 500, f"{QUOTE} {NAME} ({HANDLE}) — {TAGLINE}. {ROLES}, {PLACE}.")

# --- projects --------------------------------------------------------------------------
c = Card()
caps(c, PAD, PAD + 8, "Projects", 15)
rule(c, PAD + 30, LINE)
c.rise()
gap = 40
colw = (W - 2 * PAD - 2 * gap) / 3
serif = c.fonts["serif"]
bottom = 0
for i, (title, desc, tags) in enumerate(PROJECTS):
    x = PAD + i * (colw + gap)
    c.text(x, PAD + 122, f"0{i + 1}", "display", 64, 0.16)
    c.text(x, PAD + 168, title, "serif5", 27)
    y = c.para(x, PAD + 200, desc, "serif", 19, colw, 26, MUTED)
    line = ""
    for t in tags:                                   # wrap the tag run at measured caps width
        test = f"{line} · {t}" if line else t
        if serif.width(test.upper(), 12, 0.22) > colw and line:
            caps(c, x, y + 16, line, 12)
            y, test = y + 20, t
        line = test
    caps(c, x, y + 16, line, 12)
    bottom = max(bottom, y + 20)
    c.rise()
for i in (1, 2):
    x = PAD + i * (colw + gap) - gap / 2
    c.els.append(f'<rect x="{x:.1f}" y="{PAD + 62}" width="1" height="{bottom - PAD - 52:.0f}" fill="{INK}" fill-opacity="{LINE}"/>')
c.save("projects", bottom + PAD, "Projects: " + "; ".join(f"{t} — {d} ({', '.join(g)})" for t, d, g in PROJECTS))

# --- stack, currently, sign-off --------------------------------------------------------
c = Card()
lw = 470
caps(c, PAD, PAD + 8, "Stack", 15)
rule(c, PAD + 30, LINE, x1=PAD + lw)
y = PAD + 72
serif = c.fonts["serif"]
for key, val in STACK:
    caps(c, PAD, y, key, 12)
    vw = serif.width(val, 19)
    kx = PAD + serif.width(key.upper(), 12, 0.22) + 10
    dots = "." * int((PAD + lw - vw - 18 - kx) / serif.width(".", 14))
    c.text(kx, y, dots, "serif", 14, LINE * 2.5)
    c.text(PAD + lw, y, val, "serif", 19, anchor="end")
    y += 38
c.rise()
rx = PAD + lw + 56
caps(c, rx, PAD + 8, "Currently", 15)
rule(c, PAD + 30, LINE, x0=rx)
cy = PAD + 76
for item in CURRENTLY:
    for j, line in enumerate(c.wrap(item, "script", 26, W - PAD - rx - 26)):
        if j == 0:
            c.text(rx, cy, "—", "serif", 20, FAINT)
        c.text(rx + 26, cy, line, "script", 26)
        cy += 34
    cy += 4
c.rise()
fy = max(y, cy) + 18
rule(c, fy, LINE)
c.text(PAD, fy + 62, MOTTO, "italic", 30)
c.text(W - PAD, fy + 64, f"— {NAME}", "script", 38, anchor="end")
c.rise()
c.save("index", fy + 64 + PAD - 18, "Stack: " + "; ".join(f"{k}: {v}" for k, v in STACK)
       + ". Currently: " + ", ".join(CURRENTLY) + f". {MOTTO}")
