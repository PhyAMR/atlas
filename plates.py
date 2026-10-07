import math
from atlas import Plate, W, H

TAU = math.pi * 2


def spiral_pt(cx, cy, a, b, th, rot=0.0):
    r = a * math.exp(b * th)
    return cx + r * math.cos(th + rot), cy + r * math.sin(th + rot)


# ---------------------------------------------------------------------------
def nautilus():
    p = Plate(3)
    cx, cy = 1180, 900
    b = 0.1745
    th_end = 4.6 * math.pi
    a = 640 / math.exp(b * th_end)
    rot = -0.35
    sp = lambda th: spiral_pt(cx, cy, a, b, th, rot)
    th0 = th_end - 6 * math.pi

    # outer wall (double line = shell thickness)
    ring = [sp(th_end - TAU + TAU * i / 360) for i in range(361)]
    p.poly(ring, "t1", closed=True)
    p.poly([sp(th_end - 2 * TAU + TAU * i / 360) for i in range(361)], "t1", closed=True)
    p.poly([sp(th_end - 3 * TAU + TAU * i / 360) for i in range(361)], "t1", closed=True)
    p.poly([sp(th0 + (th_end - th0) * i / 900) for i in range(901)], "mb")
    inner = []
    for i in range(901):
        th = th0 + (th_end - th0) * i / 900
        r = a * math.exp(b * th) * 0.965
        inner.append((cx + r * math.cos(th + rot), cy + r * math.sin(th + rot)))
    p.poly(inner, "s")
    outer_wall = [sp(th0 + (th_end - th0) * i / 900) for i in range(901)]
    p.poly(outer_wall + inner[::-1], "t2", closed=True)
    for i in range(0, 900, 4):
        th = th0 + (th_end - th0) * i / 900
        if th < th_end - TAU * 1.6:
            continue
        r = a * math.exp(b * th)
        p.line(cx + r * math.cos(th + rot), cy + r * math.sin(th + rot),
               cx + r * 0.975 * math.cos(th + rot), cy + r * 0.975 * math.sin(th + rot), "d")

    # aperture: closes outer whorl onto the previous whorl
    pe = sp(th_end)
    pi_ = sp(th_end - TAU)
    p.path(f"M{pe[0]:.1f},{pe[1]:.1f} Q{(pe[0]+pi_[0])/2+40:.1f},{(pe[1]+pi_[1])/2-60:.1f} {pi_[0]:.1f},{pi_[1]:.1f}", "m")

    # septa
    th = th_end - 2.4
    k = 0
    sipho = []
    while th > th0 + TAU + 0.3:
        po = sp(th)
        pin = sp(th - TAU)
        mx, my = (po[0] + pin[0]) / 2, (po[1] + pin[1]) / 2
        L = math.hypot(po[0] - pin[0], po[1] - pin[1])
        tx, ty = -math.sin(th + rot), math.cos(th + rot)  # direction of growth
        bx, by = mx - tx * L * 0.42, my - ty * L * 0.42
        p.path(f"M{pin[0]:.1f},{pin[1]:.1f} Q{bx:.1f},{by:.1f} {po[0]:.1f},{po[1]:.1f}", "m")
        p.path(f"M{pin[0]:.1f},{pin[1]:.1f} Q{bx - tx*10:.1f},{by - ty*10:.1f} {po[0]:.1f},{po[1]:.1f}", "f")
        # siphuncle passes through each septum close to the middle
        sx = 0.25 * pin[0] + 0.5 * bx + 0.25 * po[0]
        sy = 0.25 * pin[1] + 0.5 * by + 0.25 * po[1]
        sipho.append((sx, sy, L))
        k += 1
        th -= 0.36 + 0.0 * k
    # siphuncle tube
    pts_ = [(x, y) for x, y, _ in sipho]
    p.poly(pts_, "s")
    p.poly([(x + 5, y + 5) for x, y in pts_], "f")
    for x, y, L in sipho:
        p.circle(x, y, max(2.5, L * 0.03), "m")

    # protoconch
    p.circle(*sp(th0 + 0.2), 6, "m")

    # construction: radii every 90 degrees, showing the constant growth ratio
    for q in range(8):
        thq = th_end - q * math.pi / 2
        x, y = sp(thq)
        p.line(cx, cy, x, y, "cl")
        p.circle(x, y, 5, "s")
    p.centermark(cx, cy, 26)
    p.circle(cx, cy, 640, "f")

    # dimension: maximum diameter
    outer = [sp(th_end - TAU * i / 360) for i in range(360)]
    xs = [q[0] for q in outer]; ys = [q[1] for q in outer]
    p.dim(min(xs), max(ys), max(xs), max(ys), -70, "Ø 214 mm")
    p.dim(max(xs), min(ys), max(xs), max(ys), -70, "168 mm")

    # side elevation (whorl section) to the right
    sx, sy = 2240, 900
    hgt = 1180
    p.centerline(sx, sy - hgt / 2 - 60, sx, sy + hgt / 2 + 60)
    prof = []
    for i in range(121):
        t = i / 120
        y = sy - hgt / 2 + hgt * t
        w = 230 * math.sin(math.pi * t) ** 0.8 * (1 - 0.18 * (t - 0.5) ** 2)
        prof.append((w, y))
    p.poly([(sx + w, y) for w, y in prof] + [(sx - w, y) for w, y in reversed(prof)], "t1", closed=True)
    p.poly([(sx + w, y) for w, y in prof], "mb")
    # flame stripes radiating from the umbilicus
    for i in range(16):
        t = (i + 0.5) / 16
        y0 = sy - hgt / 2 + hgt * t
        if abs(y0 - sy - 120) < 330 * 0.9:
            continue
        w = 230 * math.sin(math.pi * t) ** 0.8
        for sgn in (1, -1):
            p.path(f"M{sx+sgn*w*0.95:.0f},{y0:.0f} q{-sgn*30},{30} {-sgn*w*0.4:.0f},{20 if y0<sy else -20} t{-sgn*w*0.3:.0f},{14 if y0<sy else -14}", "s")
    p.poly([(sx - w, y) for w, y in prof], "mb")
    p.poly([(sx + w * 0.9, y) for w, y in prof[6:-6]], "s")
    p.poly([(sx - w * 0.9, y) for w, y in prof[6:-6]], "s")
    # umbilicus + previous whorl hidden inside
    p.ellipse(sx, sy + 120, 150, 330, "h")
    p.ellipse(sx, sy + 120, 70, 150, "h")
    # growth stripes
    for i in range(1, 14):
        t = i / 14
        y0 = sy - hgt / 2 + hgt * t
        w = 230 * math.sin(math.pi * t) ** 0.8 * 0.9
        p.path(f"M{sx-w:.0f},{y0:.0f} Q{sx:.0f},{y0-60:.0f} {sx+w:.0f},{y0:.0f}", "f")
    p.dim(sx - 230, sy - hgt / 2 + 220, sx + 230, sy - hgt / 2 + 220, -330, "120 mm")
    p.text(sx, sy - hgt / 2 - 90, "VIEW B", "tlb", "middle")
    p.text(cx, 120 + 40, "SECTION A-A", "tlb", "middle")

    # ratio inset
    ix, iy = 330, 330
    p.detail_circle(ix, iy, 170, "DETAIL C")
    r0 = 30
    for q in range(5):
        rr = r0 * 1.315 ** q
        a0 = q * math.pi / 2
        p.arc(ix - 40, iy + 10, rr, a0, a0 + math.pi / 2, "m")
        p.line(ix - 40, iy + 10, ix - 40 + rr * math.cos(a0 + math.pi / 2), iy + 10 + rr * math.sin(a0 + math.pi / 2), "s")
    p.centermark(ix - 40, iy + 10, 12)
    p.text(ix, iy + 220, "r(n+1)/r(n) = e^(πb/2) = 1.315", "ts", "middle")

    p.label(*sipho[len(sipho) // 3 + 2][:2], 760, 300, "SIPHUNCLE", 1, anchor="end")
    mid = sipho[len(sipho) // 2]
    p.label(*sp(th_end - 2.4 - 0.18)[:2], 1880, 360, "SEPTUM", 2)
    bc = sp(th_end - 1.0)
    p.label((bc[0] + cx) / 2 + 60, (bc[1] + cy) / 2 + 60, 1760, 1560, "BODY CHAMBER", 3)
    cam = sipho[2]
    p.label(cam[0] - 20, cam[1] + 30, 640, 1300, "CAMERA / GAS CHAMBER", 4, anchor="end")
    p.label(*sp(th0 + 0.2), 640, 980, "PROTOCONCH", 5, anchor="end")
    p.label(pe[0] - 10, pe[1] - 30, 1880, 1230, "APERTURE", 6)

    p.frame(3, "NAUTILUS", "Nautilus pompilius", "MEDIAN SECTION", "1:1",
            ("Logarithmic spiral, b = 0.1745", "Septa spaced 20.6 deg", "Shell wall 1.2 mm, nacreous"))
    return p


from plate_engine import engine
from plate_botany import fern, flower, tree
from plate_fauna import dragonfly, beetle, fish
from plate_world import turbofan, earth, radiolarian

PLATES = {
    "engine": engine,
    "fern": fern,
    "nautilus": nautilus,
    "dragonfly": dragonfly,
    "turbofan": turbofan,
    "flower": flower,
    "fish": fish,
    "earth": earth,
    "tree": tree,
    "beetle": beetle,
    "radiolarian": radiolarian,
}
