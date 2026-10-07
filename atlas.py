"""Atlas plates: procedural technical drawings of the world, as wallpapers.

Every plate is drawn once as SVG with CSS classes for its line weights, then
rendered in each palette (ink on paper for light, solitude for dark).
"""

import math
import random

W, H = 2880, 1800
FONT = "Iosevka Nerd Font Mono, Iosevka, monospace"

PALETTES = {
    "dark": {  # Solitude
        "bg": "#101315",
        "grid": "#15191c",
        "grid2": "#1a1f22",
        "body": "#d0d4d6",   # main body: brightest, heaviest
        "main": "#98a1a7",
        "sec": "#5d6367",
        "hid": "#464c52",
        "faint": "#272d31",
        "text": "#798186",
        "accent": "#de6145",
        "tint": "#a5aeb4",
        "tint_a": 0.055,
        "tint2_a": 0.10,
    },
    "light": {  # Atlas Ink: graphite on warm beige paper
        "bg": "#e2dac8",
        "grid": "#dad2bf",
        "grid2": "#d2c9b5",
        "body": "#1e1b17",
        "main": "#4a453d",
        "sec": "#857e71",
        "hid": "#9d9585",
        "faint": "#c6bda9",
        "text": "#655e52",
        "accent": "#a8452c",
        "tint": "#3a342b",
        "tint_a": 0.06,
        "tint2_a": 0.11,
    },
}


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def pts(points):
    return " ".join(f"{f(x)},{f(y)}" for x, y in points)


class Plate:
    def __init__(self, seed=1):
        self.items = []
        self.rng = random.Random(seed)

    # -- primitives -------------------------------------------------------
    def add(self, s):
        self.items.append(s)

    def line(self, x1, y1, x2, y2, c="m"):
        self.add(f'<line class="{c}" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"/>')

    def poly(self, points, c="m", closed=False):
        tag = "polygon" if closed else "polyline"
        self.add(f'<{tag} class="{c}" points="{pts(points)}"/>')

    def path(self, d, c="m"):
        self.add(f'<path class="{c}" d="{d}"/>')

    def circle(self, x, y, r, c="m"):
        self.add(f'<circle class="{c}" cx="{f(x)}" cy="{f(y)}" r="{f(r)}"/>')

    def ellipse(self, x, y, rx, ry, c="m", rot=0):
        t = f' transform="rotate({f(rot)} {f(x)} {f(y)})"' if rot else ""
        self.add(f'<ellipse class="{c}" cx="{f(x)}" cy="{f(y)}" rx="{f(rx)}" ry="{f(ry)}"{t}/>')

    def rect(self, x, y, w, h, c="m", r=0, rot=0, cx=None, cy=None):
        t = ""
        if rot:
            t = f' transform="rotate({f(rot)} {f(cx if cx is not None else x + w / 2)} {f(cy if cy is not None else y + h / 2)})"'
        rr = f' rx="{f(r)}"' if r else ""
        self.add(f'<rect class="{c}" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"{rr}{t}/>')

    def text(self, x, y, s, c="t", anchor="start", size=None, rot=0):
        sz = f' font-size="{f(size)}"' if size else ""
        t = f' transform="rotate({f(rot)} {f(x)} {f(y)})"' if rot else ""
        s = s.replace("&", "&amp;").replace("<", "&lt;")
        self.add(f'<text class="{c}" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}"{sz}{t}>{s}</text>')

    def group(self, inner, transform):
        self.add(f'<g transform="{transform}">')
        inner()
        self.add("</g>")

    # -- drafting helpers -------------------------------------------------
    def arc(self, cx, cy, r, a0, a1, c="m", steps=None):
        steps = steps or max(8, int(abs(a1 - a0) * r / 6))
        self.poly([(cx + r * math.cos(a0 + (a1 - a0) * i / steps),
                    cy + r * math.sin(a0 + (a1 - a0) * i / steps)) for i in range(steps + 1)], c)

    def bolt(self, x, y, r, c="m"):
        self.circle(x, y, r, c)
        self.poly([(x + r * 0.62 * math.cos(math.pi / 6 + k * math.pi / 3),
                    y + r * 0.62 * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)], "s", closed=True)

    def centermark(self, x, y, r, c="a"):
        self.line(x - r, y, x + r, y, c)
        self.line(x, y - r, x, y + r, c)

    def centerline(self, x1, y1, x2, y2):
        self.line(x1, y1, x2, y2, "cl")

    def label(self, x, y, tx, ty, s, num=None, anchor=None):
        """Leader line from a point on the drawing to a callout."""
        self.circle(x, y, 3.2, "dot")
        self.poly([(x, y), (tx, ty)], "ld")
        anchor = anchor or ("start" if tx >= x else "end")
        run = 46 if anchor == "start" else -46
        self.line(tx, ty, tx + run, ty, "ld")
        if num is not None:
            nx = tx + run + (16 if anchor == "start" else -16)
            self.circle(nx, ty, 13, "ld")
            self.text(nx, ty + 5, str(num), "tn", "middle")
            tx2 = nx + (22 if anchor == "start" else -22)
        else:
            tx2 = tx + run + (8 if anchor == "start" else -8)
        self.text(tx2, ty + 6, s, "t", anchor)

    def dim(self, x1, y1, x2, y2, off, s, c="dm"):
        """Aligned dimension line offset perpendicular to the measured span."""
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L * off, dx / L * off
        a1 = (x1 + nx, y1 + ny)
        a2 = (x2 + nx, y2 + ny)
        ext = 10 if off > 0 else -10
        ex, ey = -dy / L * ext, dx / L * ext
        self.line(x1 + nx * 0.15, y1 + ny * 0.15, a1[0] + ex, a1[1] + ey, c)
        self.line(x2 + nx * 0.15, y2 + ny * 0.15, a2[0] + ex, a2[1] + ey, c)
        self.line(*a1, *a2, c)
        ux, uy = dx / L, dy / L
        for (px, py), sgn in ((a1, 1), (a2, -1)):
            self.poly([(px + sgn * (ux * 14 - uy * 4), py + sgn * (uy * 14 + ux * 4)), (px, py),
                       (px + sgn * (ux * 14 + uy * 4), py + sgn * (uy * 14 - ux * 4))], c)
        mx, my = (a1[0] + a2[0]) / 2, (a1[1] + a2[1]) / 2
        ang = math.degrees(math.atan2(dy, dx))
        if ang > 90 or ang < -90:
            ang += 180
        tx, ty = mx + nx / max(abs(off), 1) * 12, my + ny / max(abs(off), 1) * 12
        self.add(f'<text class="tdim" x="{f(tx)}" y="{f(ty)}" text-anchor="middle" '
                 f'transform="rotate({f(ang)} {f(tx)} {f(ty)})">{s}</text>')

    def detail_circle(self, x, y, r, tag):
        self.circle(x, y, r, "dc")
        self.text(x + r * 0.72, y - r * 0.72 - 8, tag, "tlb", "start")

    def bezier(self, p0, p1, p2, p3, n=40):
        out = []
        for i in range(n + 1):
            t = i / n
            a = (1 - t) ** 3
            b = 3 * (1 - t) ** 2 * t
            c = 3 * (1 - t) * t * t
            d = t ** 3
            out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                        a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
        return out

    # -- frame ------------------------------------------------------------
    def frame(self, plate_no, title, latin, view, scale, notes=()):
        # Drafting grid with major lines every 5 cells
        step = 40
        g = []
        for i, x in enumerate(range(0, W + 1, step)):
            g.append(f'<line class="{"g2" if i % 5 == 0 else "g"}" x1="{x}" y1="0" x2="{x}" y2="{H}"/>')
        for i, y in enumerate(range(0, H + 1, step)):
            g.append(f'<line class="{"g2" if i % 5 == 0 else "g"}" x1="0" y1="{y}" x2="{W}" y2="{y}"/>')
        self.items[:0] = g

        m = 60
        self.rect(m, m, W - 2 * m, H - 2 * m, "fr")
        self.rect(m + 10, m + 10, W - 2 * m - 20, H - 2 * m - 20, "f")
        # zone ticks along the border
        for i in range(1, 12):
            x = m + (W - 2 * m) * i / 12
            self.line(x, m, x, m + 10, "f")
            self.line(x, H - m - 10, x, H - m, "f")
            self.text(x - (W - 2 * m) / 24, m - 14, str(i), "tz", "middle")
        for i, ch in enumerate("ABCDEFGH"):
            y = m + (H - 2 * m) * (i + 0.5) / 8
            self.text(m - 22, y + 5, ch, "tz", "middle")
            if i:
                yy = m + (H - 2 * m) * i / 8
                self.line(m, yy, m + 10, yy, "f")
                self.line(W - m - 10, yy, W - m, yy, "f")
        # registration marks
        for (x, y) in ((m + 40, m + 40), (W - m - 40, m + 40), (m + 40, H - m - 40), (W - m - 40, H - m - 40)):
            self.circle(x, y, 9, "f")
            self.line(x - 16, y, x + 16, y, "f")
            self.line(x, y - 16, x, y + 16, "f")

        # title block, bottom right
        bw, bh = 700, 168
        bx, by = W - m - 10 - bw, H - m - 10 - bh
        self.rect(bx, by, bw, bh, "fr")
        self.line(bx, by + 56, bx + bw, by + 56, "f")
        self.line(bx, by + 118, bx + bw, by + 118, "f")
        self.line(bx + 150, by + 118, bx + 150, by + bh, "f")
        self.line(bx + 380, by + 118, bx + 380, by + bh, "f")
        self.text(bx + 20, by + 38, "ATLAS OF THE WORLD", "tt", "start")
        self.text(bx + bw - 20, by + 38, f"PL. {plate_no:02d}", "tt", "end")
        self.text(bx + 20, by + 92, title, "th", "start")
        self.text(bx + bw - 20, by + 92, latin, "ti", "end")
        self.text(bx + 20, by + 148, "SHEET 1/1", "ts", "start")
        self.text(bx + 170, by + 148, view, "ts", "start")
        self.text(bx + 400, by + 148, f"SCALE {scale}", "ts", "start")

        # notes, bottom left
        ny = H - m - 30 - 30 * len(notes)
        if notes:
            self.text(m + 40, ny, "NOTES", "tt", "start")
            for i, n in enumerate(notes):
                self.text(m + 40, ny + 30 * (i + 1), f"{i + 1}. {n}", "ts", "start")

    # -- output -----------------------------------------------------------
    def svg(self, palette):
        p = PALETTES[palette]
        css = f"""
        * {{ fill: none; stroke-linecap: round; stroke-linejoin: round; }}
        .g  {{ stroke: {p['grid']}; stroke-width: 1; }}
        .g2 {{ stroke: {p['grid2']}; stroke-width: 1.2; }}
        .m  {{ stroke: {p['main']}; stroke-width: 1.9; }}
        .mb {{ stroke: {p['body']}; stroke-width: 2.6; }}
        .t1 {{ fill: {p['tint']}; fill-opacity: {p['tint_a']}; stroke: none; }}
        .t2 {{ fill: {p['tint']}; fill-opacity: {p['tint2_a']}; stroke: none; }}
        .tb {{ fill: {p['tint']}; fill-opacity: {p['tint_a']}; stroke: {p['body']}; stroke-width: 2.6; }}
        .hatch {{ fill: url(#hatch); stroke: none; }}
        .xhatch {{ fill: url(#xhatch); stroke: none; }}
        .tm {{ fill: {p['tint']}; fill-opacity: {p['tint_a']}; stroke: {p['main']}; stroke-width: 1.9; }}
        .ts {{ fill: {p['tint']}; fill-opacity: {p['tint_a']}; stroke: {p['sec']}; stroke-width: 1.4; }}
        .lf {{ fill: {p['tint']}; fill-opacity: {p['tint_a']}; stroke: {p['sec']}; stroke-width: 0.9; stroke-opacity: 0.6; }}
        .d  {{ stroke: {p['sec']}; stroke-width: 1.0; stroke-opacity: 0.8; }}
        .s  {{ stroke: {p['sec']}; stroke-width: 1.4; }}
        .h  {{ stroke: {p['hid']}; stroke-width: 1.3; stroke-dasharray: 9 7; }}
        .f  {{ stroke: {p['faint']}; stroke-width: 1.2; }}
        .fr {{ stroke: {p['sec']}; stroke-width: 1.6; }}
        .cl {{ stroke: {p['hid']}; stroke-width: 1.1; stroke-dasharray: 34 8 4 8; }}
        .a  {{ stroke: {p['accent']}; stroke-width: 1.6; }}
        .ad {{ stroke: {p['accent']}; stroke-width: 1.4; stroke-dasharray: 6 6; }}
        .dc {{ stroke: {p['sec']}; stroke-width: 1.4; stroke-dasharray: 3 6; }}
        .dm {{ stroke: {p['text']}; stroke-width: 1.1; }}
        .ld {{ stroke: {p['text']}; stroke-width: 1.1; }}
        .dot {{ fill: {p['accent']}; stroke: none; }}
        .fill {{ fill: {p['bg']}; stroke: {p['main']}; stroke-width: 1.9; }}
        text {{ font-family: {FONT}; fill: {p['text']}; stroke: none; }}
        .t   {{ font-size: 22px; letter-spacing: 1px; }}
        .tn  {{ font-size: 16px; }}
        .tz  {{ font-size: 16px; fill: {p['sec']}; }}
        .tdim {{ font-size: 18px; }}
        .tlb {{ font-size: 22px; fill: {p['accent']}; letter-spacing: 2px; }}
        .tt  {{ font-size: 20px; letter-spacing: 4px; fill: {p['sec']}; }}
        .th  {{ font-size: 34px; letter-spacing: 6px; fill: {p['main']}; }}
        .ti  {{ font-size: 20px; font-style: italic; }}
        .ts  {{ font-size: 18px; letter-spacing: 2px; }}
        """
        body = "\n".join(self.items)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
                f'<defs><pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                f'<line x1="0" y1="0" x2="0" y2="9" style="stroke:{p["sec"]};stroke-width:1;stroke-opacity:0.55"/></pattern>'
                f'<pattern id="xhatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                f'<line x1="0" y1="0" x2="0" y2="8" style="stroke:{p["sec"]};stroke-width:0.9;stroke-opacity:0.5"/>'
                f'<line x1="0" y1="0" x2="8" y2="0" style="stroke:{p["sec"]};stroke-width:0.9;stroke-opacity:0.5"/></pattern></defs>'
                f'<style>{css}</style><rect x="0" y="0" width="{W}" height="{H}" style="fill:{p['bg']}"/>'
                f'{body}</svg>')


# -- mechanical helpers -------------------------------------------------------
def gear_points(cx, cy, r, n, h, phase=0.0):
    out = []
    for i in range(n):
        a = phase + i * 2 * math.pi / n
        da = 2 * math.pi / n
        for t, rr in ((0.0, r), (0.18, r), (0.3, r + h), (0.55, r + h), (0.67, r), (1.0, r)):
            out.append((cx + rr * math.cos(a + da * t), cy + rr * math.sin(a + da * t)))
    return out


def tangents(c1, c2):
    """External tangent segments between two circles (x, y, r)."""
    (x1, y1, r1), (x2, y2, r2) = c1, c2
    d = math.hypot(x2 - x1, y2 - y1)
    base = math.atan2(y2 - y1, x2 - x1)
    off = math.acos((r1 - r2) / d)
    segs = []
    for s in (1, -1):
        a = base + s * off
        segs.append(((x1 + r1 * math.cos(a), y1 + r1 * math.sin(a)),
                     (x2 + r2 * math.cos(a), y2 + r2 * math.sin(a))))
    return segs


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def bez_pt(p0, p1, p2, p3, t):
    a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; c = 3 * (1 - t) * t * t; d = t ** 3
    return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])


def leaf_path(base, tip, width, bend=0.0, fat=0.5):
    """Closed leaf outline from base to tip as an SVG path string."""
    bx, by = base; tx, ty = tip
    dx, dy = tx - bx, ty - by
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    mx, my = bx + dx * fat + nx * bend, by + dy * fat + ny * bend
    c1 = (mx + nx * width, my + ny * width)
    c2 = (mx - nx * width, my - ny * width)
    return (f"M{bx:.1f},{by:.1f} Q{c1[0]:.1f},{c1[1]:.1f} {tx:.1f},{ty:.1f} "
            f"Q{c2[0]:.1f},{c2[1]:.1f} {bx:.1f},{by:.1f} Z")
