"""Generate the README cards in the style of the portfolio (paper and ink).

Run: python3 assets/gen_assets.py   (needs: pip install fonttools brotli)

README images can't load web fonts, so each SVG embeds a subset of the
portfolio's fonts (League Gothic, Cormorant Garamond, Shadows Into Light).
Text widths are measured from the font files so wrapping and alignment match.
"""
import base64
import io
import re
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent

# --- content ---------------------------------------------------------------------
QUOTE = "Tutte le cose belle prima o poi finiscono."
NAME = "David Winkler"
CAPTION = ["Software engineer & designer", "Innsbruck, Austria"]
LEAD = "From Innsbruck. I build programs that are fast, clean, and just work."
DIM = [
    "Most of what I do sits where engineering meets design — interfaces that load "
    "instantly, read clearly, and feel good to use. Your mentality is your limit.",
    "Currently studying at HTL Anichstraße, running bean4U, and taking on freelance "
    "work in web development and UI.",
]
EDUCATION = [("HTL Anichstraße", "Technical college in Innsbruck — engineering fundamentals", "Since 2025")]
STACK = [
    ("Languages", [("javascript", "#E8C800", "JavaScript"), ("typescript", "#3178C6", "TypeScript"),
                   ("openjdk", "#ED8B00", "Java"), ("python", "#3776AB", "Python"),
                   ("cplusplus", "#00599C", "C++"), ("html5", "#E34F26", "HTML"), ("css", "#663399", "CSS")]),
    ("Back end", [("nodedotjs", "#5FA04E", "Node.js"), ("express", None, "Express")]),
    ("Tools", [("git", "#F03C2E", "Git"), ("linux", None, "Linux"), ("gnubash", "#4EAA25", "Bash"),
               ("figma", "#F24E1E", "Figma"), ("ollama", None, "Ollama")]),
    ("AI", [("claude", "#D97757", "Claude Code"), ("openai", None, "ChatGPT"), ("googlegemini", "#8E75B2", "Gemini")]),
]
WORK = [
    ("Cortex", "A code editor that runs your own local models.", "2026"),
    ("bean4U", "Coffee recipes, brewing guides, and a brand built from scratch.", "2024 — Present"),
    ("Formula Arch", "Arch Linux, dressed in Formula 1 liveries.", "2026"),
    ("Portfolio", "This site — static pages and a small hardened API.", "2025"),
]
PATH = [
    ("Student", "HTL Anichstraße — technical college in Innsbruck", "2025 — now"),
    ("Founder", "bean4U — coffee recipe platform, brand and all", "2024 — now"),
    ("Freelance developer", "Web development and UI for clients", "Now"),
]
LINKS = ["Email", "GitHub", "Instagram", "CV"]
COPY = "© 2026 · David Winkler"

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


def rows(c, y, items, name_font, name_size, upper):
    """Portfolio .row list: name + note on the left, year on the right, hairlines between."""
    for name, note, year in items:
        c.hline(y)
        top = y + 30
        c.text(PAD, top + name_size * 0.72, name, name_font, name_size, ls=0.02 if upper else 0, upper=upper)
        c.text(W - PAD, top + name_size * 0.72, year, "serif", 17, FAINT, anchor="end")
        c.text(PAD, top + name_size * 0.72 + 30, note, "serif", 18, MUTED)
        y = top + name_size * 0.72 + 30 + 28
    c.hline(y)
    return y


# --- hero ----------------------------------------------------------------------------
c = Card()
c.text(W / 2, 74, QUOTE, "italic", 26, anchor="middle")
c.rise()
pw, ph, py = 140, 175, 120
portrait = base64.b64encode((HERE / "portrait.webp").read_bytes()).decode()
c.defs.append(f'<clipPath id="pc"><rect x="{(W - pw) / 2}" y="{py}" width="{pw}" height="{ph}" rx="14"/></clipPath>'
              f'<filter id="sh" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="14" stdDeviation="12" flood-color="{INK}" flood-opacity="0.28"/></filter>')
c.els.append(f'<rect x="{(W - pw) / 2 + 8}" y="{py + 8}" width="{pw - 16}" height="{ph - 16}" rx="14" fill="{BG}" filter="url(#sh)"/>'
             f'<image href="data:image/webp;base64,{portrait}" x="{(W - pw) / 2}" y="{py}" width="{pw}" height="{ph}" '
             f'preserveAspectRatio="xMidYMid slice" clip-path="url(#pc)"/>')
c.rise()
c.text(W / 2, py + ph + 132, NAME, "display", 128, ls=0.09, anchor="middle", upper=True)
c.rise()
for i, line in enumerate(CAPTION):
    c.text(W / 2, py + ph + 192 + i * 40, line, "script", 32, anchor="middle")
c.rise()
c.save("hero", py + ph + 192 + 40 + 56, f"{QUOTE} {NAME} — {CAPTION[0]}, {CAPTION[1]}")

# --- about + education -------------------------------------------------------------
c = Card()
c.label(PAD + 10, "About")
c.rise()
y = c.para(PAD, PAD + 62, LEAD, "serif", 27, 640, 38)
c.rise()
for p in DIM:
    y = c.para(PAD, y + 14, p, "serif", 23, 640, 33, MUTED)
c.rise()
y += 34
c.label(y, "Education")
y = rows(c, y + 30, EDUCATION, "serif", 30, False)
c.rise()
c.save("about", y + PAD - 10, "About David Winkler")

# --- stack -----------------------------------------------------------------------------
sprite = (HERE / "stack-icons.svg").read_text()
symbols = dict(re.findall(r'<symbol id="([^"]+)" viewBox="0 0 24 24">(.*?)</symbol>', sprite, re.S))
c = Card()
c.label(PAD + 10, "Stack")
c.hline(PAD + 38)
c.rise()
gap = 28
colw = (W - 2 * PAD - 3 * gap) / 4
bottom = 0
for gi, (group, items) in enumerate(STACK):
    x = PAD + gi * (colw + gap)
    y = PAD + 80
    c.text(x, y, group, "serif", 13, FAINT, ls=0.2, upper=True)
    y += 22
    for icon, brand, name in items:
        c.els.append(f'<rect x="{x + 0.5:.1f}" y="{y + 0.5:.1f}" width="35" height="35" rx="10" fill="#fff" stroke="{INK}" stroke-opacity="{LINE}"/>'
                     f'<g transform="translate({x + 8.5:.1f} {y + 8.5:.1f}) scale(0.8)" fill="{brand or INK}">{symbols[icon]}</g>')
        c.text(x + 48, y + 24, name, "serif", 20)
        y += 47
    bottom = max(bottom, y)
    c.rise()
c.save("stack", bottom + PAD - 20, "Stack: " + "; ".join(f"{g}: " + ", ".join(n for *_, n in it) for g, it in STACK))

# --- work ------------------------------------------------------------------------------
c = Card()
c.label(PAD + 10, "Work")
c.rise()
y = rows(c, PAD + 38, [(n, note, yr + "  ↗") for n, note, yr in WORK], "display", 50, True)
c.rise()
c.save("work", y + PAD - 10, "Work: " + "; ".join(f"{n} ({yr}) — {note}" for n, note, yr in WORK))

# --- path + footer ---------------------------------------------------------------------
c = Card()
c.label(PAD + 10, "Path")
c.rise()
y = rows(c, PAD + 38, PATH, "serif5", 26, False)
c.rise()
fy = y + 130
c.els.append('<g class="sign">')
c.text(PAD, fy, NAME, "script", 50)
c.els.append("</g>")
lx = W / 2 + 20
for i, link in enumerate(LINKS):
    c.text(lx, fy - 66 + i * 27, link, "serif", 19, MUTED)
c.text(W - PAD, fy + 14, COPY, "serif", 16, FAINT, anchor="end")
c.save("contact", fy + 14 + PAD - 10, f"Path: {', '.join(p[0] for p in PATH)}. Signed, {NAME}.")
