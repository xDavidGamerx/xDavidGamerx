import html
import os
import sys
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np

# Load cropped face or avatar
INP = r'C:\Users\DAVID\.gemini\antigravity\brain\626c7a3b-4330-4a14-aba0-d7e85571f471\scratch_zerotwo_face.png'
OUT_SVG = r'C:\Users\DAVID\.gemini\antigravity\scratch\xdavid-profile\zerotwo-ascii.svg'

# Target dimensions matching stats.svg (840 x 880)
W, H = 840, 880
PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
CANVAS_W = W
CANVAS_H = H

ART_W = CANVAS_W - PAD * 2
ART_H = CANVAS_H - TITLEBAR_H - STATUS_H - PAD

COLS = 130
CELL_W = ART_W / COLS
CELL_H = CELL_W * 15 / 8
ROWS = int(ART_H / CELL_H)

RAMP = " .`:-=+*cs#%@"

im = Image.open(INP).convert('L')
# Auto-contrast & sharpen for crisp anime line-art
im = ImageOps.autocontrast(im, cutoff=2)
im = ImageEnhance.Contrast(im).enhance(1.4)
im = ImageEnhance.Sharpness(im).enhance(2.0)
im = im.resize((COLS, ROWS), Image.LANCZOS)
px = im.load()

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
# Zero Two theme accent: soft pink / cyber-coral tint or clean silver
INK = "#ff79c6"      # iconic Zero Two pink / cyberpunk
INK_MUTED = "#bd93f9"
CURSOR = "#ff79c6"

ROW_DUR = 5.0 / ROWS
STAGGER = ROW_DUR

rows_txt = []
for y in range(ROWS):
    chars = []
    for x in range(COLS):
        lum = px[x, y] / 255.0
        # Invert so dark line art & hair details are drawn with luminous characters
        val = 1.0 - lum
        if val < 0.15:
            chars.append(" ")
            continue
        idx = int(val * (len(RAMP) - 1))
        idx = max(0, min(len(RAMP) - 1, idx))
        chars.append(RAMP[idx])
    rows_txt.append("".join(chars))

art_top = TITLEBAR_H + PAD * 0.5

parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
)
parts.append('<defs>'
             f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
             f'</linearGradient></defs>')

parts.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>')
parts.append(f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>')
parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')

for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')

parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" text-anchor="middle">xdavid@github: ~$ ./zero-two.sh</text>')

font_size = CELL_H * 0.90
for ry, line in enumerate(rows_txt):
    y = art_top + ry * CELL_H + CELL_H * 0.74
    row_y = art_top + ry * CELL_H
    delay = ry * STAGGER
    safe = html.escape(line)
    text = (f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
            f'font-size="{font_size:.1f}" textLength="{ART_W}" lengthAdjust="spacing">{safe}</text>')

    parts.append(
        f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H}" width="0">'
        f'<animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.2f}s" fill="freeze"/></rect></clipPath>'
    )
    parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
    parts.append(
        f'<rect y="{row_y+1:.1f}" width="{CELL_W}" height="{CELL_H-2}" fill="{CURSOR}" opacity="0">'
        f'<animate attributeName="x" from="{PAD}" to="{PAD+ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.2f}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
        f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/></rect>'
    )

status_line_y = CANVAS_H - STATUS_H
status_y = status_line_y + 19
parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
             f'xdavid@github:~$ whoami <tspan fill="{INK}">Zero Two (002) // xDavid</tspan></text>')

status_chars = len("xdavid@github:~$ whoami Zero Two (002) // xDavid ")
parts.append(f'<rect x="{PAD + status_chars * 13 * 0.6:.1f}" y="{status_y-12:.1f}" width="8" height="14" fill="{CURSOR}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></rect>')

parts.append("</svg>")
svg = "".join(parts)

with open(OUT_SVG, "w", encoding="utf-8") as f:
    f.write(svg)

print(f"Generated {OUT_SVG} successfully ({CANVAS_W}x{CANVAS_H})")
