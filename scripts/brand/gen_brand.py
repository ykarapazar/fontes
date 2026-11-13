"""Generate the Fontes brand assets in docs/assets/brand/ (logo, lockup, favicons, touch icon,
social preview). From the repo root:

    uv run --with resvg-py --with uharfbuzz --with fonttools --with pillow python -I scripts/brand/gen_brand.py

Needs the Source Serif 4 variable font, which is not committed (SIL OFL 1.1, notice in
docs/assets/brand/FONT-LICENSE.txt). Download `SourceSerif4[opsz,wght].ttf` from
https://github.com/google/fonts/tree/main/ofl/sourceserif4 and save it as
scripts/brand/fonts/SourceSerif4.ttf (or point FONTES_BRAND_FONT at it). The static instances
the script derives from it are cached next to it. scripts/brand/fonts/ is gitignored.
"""
import io, math, os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb
import resvg_py
from PIL import Image, ImageDraw, ImageFont

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = str(ROOT / "docs" / "assets" / "brand")
VF = os.environ.get("FONTES_BRAND_FONT") or str(Path(__file__).resolve().parent / "fonts" / "SourceSerif4.ttf")
FONTS = os.path.dirname(VF)
if not os.path.exists(VF):
    raise SystemExit(f"font not found: {VF} (see the docstring for where to get it)")
os.makedirs(OUT, exist_ok=True)

NAVY = "#162644"   # sampled from concept 10 (dot + wordmark)
TEAL = "#1e88a0"   # sampled from concept 10 (median of arc pixels)
LIGHT = "#eef2f7"  # wordmark/dot on dark
TEAL_D = "#4cbdd3" # teal lifted for dark backgrounds
DARK_BG = "#0d1117"

# ---------------------------------------------------------------- fonts
def instance(wght, opsz, name):
    p = f"{FONTS}/{name}.ttf"
    if not os.path.exists(p):
        f = TTFont(VF)
        instancer.instantiateVariableFont(f, {"wght": wght, "opsz": opsz}, inplace=True)
        f.save(p)
    return p

WORD_TTF = instance(600, 60, "SourceSerif4-Semibold-Display")
HEAD_TTF = instance(500, 60, "SourceSerif4-Medium-Display")
SMALL_TTF = instance(400, 20, "SourceSerif4-Regular-Text")

def num(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s

def text_path(ttf, text, size, x, baseline, tracking=0):
    """Shape `text` and return (svg path d, ink bbox, advance width) in px."""
    blob = hb.Blob.from_file_path(ttf)
    face = hb.Face(blob)
    font = hb.Font(face)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    tt = TTFont(ttf); gs = tt.getGlyphSet(); order = tt.getGlyphOrder()
    upm = tt["head"].unitsPerEm; s = size / upm
    pen = SVGPathPen(gs, ntos=num)
    from fontTools.pens.boundsPen import BoundsPen
    pen_x = 0; bb = [1e9, 1e9, -1e9, -1e9]
    n = len(buf.glyph_infos)
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        g = order[info.codepoint]
        ox = x + (pen_x + pos.x_offset) * s
        oy = baseline - pos.y_offset * s
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, ox, oy)))
        bp = BoundsPen(gs); gs[g].draw(bp)
        if bp.bounds:
            x0, y0, x1, y1 = bp.bounds
            bb = [min(bb[0], ox + x0 * s), min(bb[1], oy - y1 * s), max(bb[2], ox + x1 * s), max(bb[3], oy - y0 * s)]
        pen_x += pos.x_advance + (tracking if i < n - 1 else 0)
    return pen.getCommands(), bb, pen_x * s

def font_metrics(ttf):
    tt = TTFont(ttf); return tt["head"].unitsPerEm, tt["OS/2"].sCapHeight, tt["OS/2"].sxHeight

# ---------------------------------------------------------------- mark geometry
# Unit u = dot radius. Rings concentric with the dot ("the source"). Variant A was chosen
# (2026-11-11); variant B (full circles, tapering strokes) was rejected and is kept here only
# as geometry for reference: build() makes A alone.
MASTER = {
    "A": dict(dot=1.0, radii=[2.1, 3.4, 4.7], sw=[0.38, 0.38, 0.38], cut=1.0),
    "B": dict(dot=1.0, radii=[2.05, 3.3, 4.75], sw=[0.5, 0.36, 0.24], cut=None),
}
# Small-size masters (units = pixels on the target grid; dot heavier, fewer/thicker rings)
SMALL = {
    ("A", 16): dict(dot=2.0, radii=[4.5, 7.0], sw=[1.5, 1.5], cut=2.0),
    ("B", 16): dict(dot=2.1, radii=[4.6, 7.1], sw=[1.55, 1.25], cut=None),
    ("A", 32): dict(dot=3.0, radii=[6.8, 10.5, 14.1], sw=[2.1, 2.1, 2.1], cut=3.0),
    ("B", 32): dict(dot=3.0, radii=[6.8, 10.5, 14.2], sw=[2.3, 1.9, 1.5], cut=None),
}

def bbox(g):
    ro = g["radii"][-1] + g["sw"][-1] / 2
    if g["cut"] is None:
        return (-ro, -ro, ro, ro)
    bottom = max(g["dot"], g["cut"] + max(g["sw"]) / 2)
    return (-ro, -ro, ro, bottom)

def mark_svg(g, cx, cy, s, dot_c, ring_c):
    """SVG elements for mark with dot centre (cx,cy), scale s px per unit."""
    out = [f'<circle cx="{num(cx)}" cy="{num(cy)}" r="{num(g["dot"]*s)}" fill="{dot_c}"/>']
    for r, w in zip(g["radii"], g["sw"]):
        R, W = r * s, w * s
        if g["cut"] is None:
            out.append(f'<circle cx="{num(cx)}" cy="{num(cy)}" r="{num(R)}" fill="none" stroke="{ring_c}" stroke-width="{num(W)}"/>')
        else:
            k = g["cut"] * s
            dx = math.sqrt(R * R - k * k)
            out.append(f'<path d="M{num(cx-dx)} {num(cy+k)}A{num(R)} {num(R)} 0 1 1 {num(cx+dx)} {num(cy+k)}" '
                       f'fill="none" stroke="{ring_c}" stroke-width="{num(W)}" stroke-linecap="round"/>')
    return "\n  ".join(out)

def svg_doc(w, h, body, title, bg=None):
    rect = f'<rect width="{num(w)}" height="{num(h)}" fill="{bg}"/>\n  ' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{num(w)}" height="{num(h)}" viewBox="0 0 {num(w)} {num(h)}" '
            f'role="img" aria-label="{title}">\n  <title>{title}</title>\n  {rect}{body}\n</svg>\n')

def square_mark(g, size, pad_frac, dot_c, ring_c, bg=None, optical_dy=0.0):
    x0, y0, x1, y1 = bbox(g)
    s = size * (1 - 2 * pad_frac) / (x1 - x0)
    cx = size / 2 - (x0 + x1) / 2 * s
    cy = size / 2 - (y0 + y1) / 2 * s + optical_dy * size
    return svg_doc(size, size, mark_svg(g, cx, cy, s, dot_c, ring_c), "Fontes", bg)

def pixel_mark(g, n, dot_c, ring_c, optical_dy=0.0):
    """Small icon designed directly on an n-px grid (units = px)."""
    x0, y0, x1, y1 = bbox(g)
    cx = round(n / 2 - (x0 + x1) / 2)   # snap dot centre to the pixel grid
    cy = round(n / 2 - (y0 + y1) / 2 + optical_dy)
    body = mark_svg(g, cx, cy, 1.0, dot_c, ring_c)
    body = body.replace(f'fill="{dot_c}"', f'class="d" fill="{dot_c}"').replace(f'stroke="{ring_c}"', f'class="r" stroke="{ring_c}"')
    style = (f'<style>@media (prefers-color-scheme: dark){{.d{{fill:{LIGHT}}}.r{{stroke:{TEAL_D}}}}}</style>\n  ')
    return svg_doc(n, n, style + body, "Fontes")

# ---------------------------------------------------------------- lockup
UPM, CAP, XH = font_metrics(WORD_TTF)
TRACK = -12  # font units (-1.2% em): display setting, slightly tighter than default

def lockup(v, dark, F=200):
    dot_c, ring_c, word_c = (LIGHT, TEAL_D, LIGHT) if dark else (NAVY, TEAL, NAVY)
    g = MASTER[v]; cap = CAP / UPM * F
    base = 0.0  # baseline at y=0, shift later
    if v == "A":
        # top of outer arc -> baseline ~ 1.42 cap; dot bottom & arc cut line sit on the baseline
        x0, y0, x1, y1 = bbox(g)
        s = 1.42 * cap / (g["dot"] - y0)
        cy = base - g["dot"] * s
    else:
        x0, y0, x1, y1 = bbox(g)
        s = 1.62 * cap / (y1 - y0)
        cy = base - 0.47 * cap
    mx0, mx1 = x0 * s, x1 * s           # relative to cx
    my0, my1 = cy + y0 * s, cy + y1 * s
    cx = -mx0                           # mark left edge at x=0
    gap = 0.30 * cap
    d, bb, adv = text_path(WORD_TTF, "Fontes", F, 0, base, TRACK)
    tx = cx + mx1 + gap - bb[0]
    d, bb, adv = text_path(WORD_TTF, "Fontes", F, tx, base, TRACK)
    top = min(my0, bb[1]); bot = max(my1, bb[3]); right = bb[2]
    pad = 0.18 * cap
    W = right + 2 * pad; H = bot - top + 2 * pad
    ox, oy = pad, pad - top
    body = (f'<g transform="translate({num(ox)} {num(oy)})">\n  '
            + mark_svg(g, cx, cy, s, dot_c, ring_c)
            + f'\n  <path d="{d}" fill="{word_c}"/>\n</g>')
    return svg_doc(round(W, 1), round(H, 1), body, "Fontes"), (W, H)

# ---------------------------------------------------------------- render helpers
def render(svg, w, h=None, bg=None):
    kw = dict(svg_string=svg, width=w, height=h or w)
    if bg: kw["background"] = bg
    data = resvg_py.svg_to_bytes(**kw)
    return Image.open(io.BytesIO(bytes(data))).convert("RGBA")

def write(name, text):
    with open(f"{OUT}/{name}", "w") as f: f.write(text)

# ---------------------------------------------------------------- social preview
def social(v):
    W, H = 1280, 640
    lsvg, (lw, lh) = lockup(v, False)
    inner = lsvg.split("<title>Fontes</title>", 1)[1].rsplit("</svg>", 1)[0]
    target_h = 150
    k = target_h / lh
    hs = 50
    l1, bb1, _ = text_path(HEAD_TTF, "The law of 120+ jurisdictions,", hs, 0, 0)
    l2, bb2, _ = text_path(HEAD_TTF, "one question away.", hs, 0, 0)
    gap1 = 64; lead = hs * 1.22
    cap_h = -bb1[1]; desc = bb2[3]
    block = target_h + gap1 + cap_h + lead + desc
    top = (H - 70 - block) / 2   # centre lockup+headline above the footer line
    lx = (W - lw * k) / 2; ly = top
    parts = [f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
             f'<g transform="translate({num(lx)} {num(ly)}) scale({k:.5f})">{inner}</g>']
    y1 = ly + target_h + gap1 + cap_h; y2 = y1 + lead
    w1 = bb1[2] - bb1[0]; w2 = bb2[2] - bb2[0]
    l1, _, _ = text_path(HEAD_TTF, "The law of 120+ jurisdictions,", hs, (W - w1) / 2 - bb1[0], y1)
    l2, _, _ = text_path(HEAD_TTF, "one question away.", hs, (W - w2) / 2 - bb2[0], y2)
    parts.append(f'<path d="{l1} {l2}" fill="{NAVY}"/>')
    ss = 24
    small = "Free and open source  ·  github.com/ykarapazar/fontes"
    _, bb3, _ = text_path(SMALL_TTF, small, ss, 0, 0)
    w3 = bb3[2] - bb3[0]
    l3, bb3, _ = text_path(SMALL_TTF, small, ss, (W - w3) / 2 - bb3[0], H - 88)
    parts.append(f'<path d="{l3}" fill="#4a5872"/>')
    svg = svg_doc(W, H, "\n  ".join(parts), "Fontes: the law of 120+ jurisdictions, one question away.")
    img = render(svg, W, H).convert("RGB")
    img.save(f"{OUT}/social-preview.png", optimize=True)
    print(v, "lockup", round(lx), round(ly), round(lx+lw*k), round(ly+target_h), "footer", [round(t) for t in bb3]); return img

# ---------------------------------------------------------------- build
def build(v="A"):
    g = MASTER[v]
    odx = 0.0
    write("mark.svg", square_mark(g, 512, 0.09, NAVY, TEAL, optical_dy=odx))
    write("mark-dark.svg", square_mark(g, 512, 0.09, LIGHT, TEAL_D, optical_dy=odx))
    for dark in (False, True):
        svg, _ = lockup(v, dark)
        write(f"lockup{'-dark' if dark else ''}.svg", svg)
    m = open(f"{OUT}/mark.svg").read()
    for n in (512, 1024):
        render(m, n).save(f"{OUT}/mark-{n}.png", optimize=True)
    md = open(f"{OUT}/mark-dark.svg").read()
    render(md, 512).save(f"{OUT}/mark-dark-512.png", optimize=True)
    # favicons: pixel-designed small masters
    ims = {}
    for n in (16, 32):
        fsvg = pixel_mark(SMALL[(v, n)], n, NAVY, TEAL)
        write(f"favicon-{n}.svg", fsvg)
        ims[n] = render(fsvg, n)
        ims[n].save(f"{OUT}/favicon-{n}.png", optimize=True)
    ims[32].save(f"{OUT}/favicon.ico", sizes=[(16, 16), (32, 32)], append_images=[ims[16]])
    # apple touch: opaque white, mark inside ~70% (iOS rounds corners)
    render(square_mark(g, 180, 0.15, NAVY, TEAL, bg="#ffffff"), 180).convert("RGB").save(
        f"{OUT}/apple-touch-icon.png", optimize=True)
    social(v)

if __name__ == "__main__":
    build()
    print("done")
