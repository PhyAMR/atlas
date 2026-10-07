"""Render atlas plates: python3 render.py OUTDIR [plate ...]"""
import os
import subprocess
import sys

from plates import PLATES

out = sys.argv[1]
names = sys.argv[2:] or list(PLATES)
order = list(PLATES)
for name in names:
    plate = PLATES[name]()
    idx = order.index(name) + 1
    for pal in ("dark", "light"):
        d = os.path.join(out, pal)
        os.makedirs(d, exist_ok=True)
        svg = os.path.join(d, f"{idx:02d}-{name}.svg")
        png = svg[:-4] + ".png"
        with open(svg, "w") as fh:
            fh.write(plate.svg(pal))
        subprocess.run(["rsvg-convert", "-o", png, svg], check=True)
        os.remove(svg)
        print(png)
