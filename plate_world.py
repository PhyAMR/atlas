import math
import random
from atlas import Plate, bez_pt, lerp


def turbofan():
    p = Plate(41)
    cy = 900
    x0, x1 = 420, 2300

    def mirror_path(fn, cls):
        for s in (1, -1):
            fn(s, cls)

    # nacelle
    def nacelle(s, cls):
        p.path(f"M{x0},{cy-s*420} C{x0-30},{cy-s*470} {x0+60},{cy-s*500} {x0+200},{cy-s*496} "
               f"C{x0+700},{cy-s*480} {x0+1100},{cy-s*440} {x0+1340},{cy-s*360} Z", "tb")
        p.path(f"M{x0+300},{cy-s*440} L{x0+1100},{cy-s*412}", "d")
        for k in range(30):
            xx = x0 + 320 + k * 26
            p.line(xx, cy - s * 412, xx + 8, cy - s * 432, "d")
        p.path(f"M{x0},{cy-s*420} C{x0+40},{cy-s*400} {x0+120},{cy-s*400} {x0+260},{cy-s*402} "
               f"C{x0+700},{cy-s*410} {x0+1100},{cy-s*380} {x0+1340},{cy-s*360}", "m")
    mirror_path(nacelle, "m")
    # core cowl
    for s in (1, -1):
        p.path(f"M{x0+520},{cy-s*230} C{x0+700},{cy-s*250} {x0+1100},{cy-s*250} {x0+1420},{cy-s*220} "
               f"C{x0+1600},{cy-s*200} {x0+1760},{cy-s*170} {x0+1820},{cy-s*150} L{x0+1820},{cy-s*120} L{x0+540},{cy-s*210} Z", "tb")
        p.path(f"M{x0+540},{cy-s*210} C{x0+700},{cy-s*200} {x0+900},{cy-s*150} {x0+1020},{cy-s*120} "
               f"L{x0+1500},{cy-s*120} C{x0+1640},{cy-s*130} {x0+1740},{cy-s*140} {x0+1820},{cy-s*150}", "m")
    # spinner
    p.path(f"M{x0+120},{cy} C{x0+130},{cy-60} {x0+220},{cy-120} {x0+300},{cy-130} L{x0+300},{cy+130} C{x0+220},{cy+120} {x0+130},{cy+60} {x0+120},{cy}", "tb")
    p.circle(x0 + 170, cy, 8, "m")
    # fan blade (section) + OGV
    for s in (1, -1):
        p.path(f"M{x0+300},{cy-s*130} L{x0+260},{cy-s*400} L{x0+420},{cy-s*402} L{x0+400},{cy-s*130} Z", "tm")
        for k in range(1, 6):
            yk = cy - s * (130 + k * 45)
            p.line(x0 + 300 - k * 7, yk, x0 + 400 + k * 3, yk, "f")
        p.path(f"M{x0+700},{cy-s*240} L{x0+680},{cy-s*404} L{x0+760},{cy-s*406} L{x0+780},{cy-s*242} Z", "s")
    # LP + HP compressor stages
    stages = [(x0 + 560, 210, 120, 4, 34), (x0 + 1040, 120, 60, 9, 34)]
    for (sx, rt, rh, n, w) in stages:
        for k in range(n):
            x = sx + k * (w + 14)
            t = k / max(1, n - 1)
            tip = rt - t * (rt - rh - 20) * 0.7
            for s in (1, -1):
                p.rect(x, cy - s * tip - (0 if s > 0 else -tip + tip), w * 0.55, 0, "f")
                p.path(f"M{x},{cy-s*rh*0.6} L{x-4},{cy-s*tip} L{x+w*0.5},{cy-s*tip} L{x+w*0.55},{cy-s*rh*0.6} Z", "ts")
                p.path(f"M{x+w*0.65},{cy-s*tip} L{x+w*0.68},{cy-s*rh*0.62} L{x+w},{cy-s*rh*0.62} L{x+w},{cy-s*tip} Z", "f")
    # combustor
    cx0 = x0 + 1500
    for s in (1, -1):
        p.path(f"M{cx0},{cy-s*80} C{cx0+40},{cy-s*150} {cx0+180},{cy-s*150} {cx0+260},{cy-s*110} L{cx0+260},{cy-s*70} C{cx0+180},{cy-s*60} {cx0+40},{cy-s*50} {cx0},{cy-s*80}", "tb")
        p.line(cx0 - 30, cy - s * 100, cx0 + 20, cy - s * 100, "m")
        p.circle(cx0 + 24, cy - s * 100, 9, "m")
        for k in range(5):
            p.path(f"M{cx0+60+k*36},{cy-s*102} q10,{-s*10} 20,0", "a")
    # turbines
    tx0 = cx0 + 300
    for k in range(6):
        x = tx0 + k * 44
        tip = 90 + k * 14
        for s in (1, -1):
            p.path(f"M{x},{cy-s*50} L{x+6},{cy-s*tip} L{x+30},{cy-s*tip} L{x+24},{cy-s*50} Z", "ts" if k > 1 else "tm")
    # exhaust plug
    p.path(f"M{tx0+270},{cy-60} C{tx0+400},{cy-50} {tx0+500},{cy-10} {tx0+560},{cy} C{tx0+500},{cy+10} {tx0+400},{cy+50} {tx0+270},{cy+60} Z", "tb")
    # pylon and accessory gearbox
    p.path(f"M{x0+700},{cy-496} L{x0+820},{cy-640} L{x0+1500},{cy-640} L{x0+1560},{cy-420}", "m")
    p.path(f"M{x0+700},{cy-496} L{x0+820},{cy-640} L{x0+1500},{cy-640} L{x0+1560},{cy-420} Z", "hatch")
    p.rect(x0 + 700, cy + 500, 360, 90, "tm", r=14)
    for k in range(5):
        p.circle(x0 + 750 + k * 65, cy + 545, 22, "s")
    for k in range(12):
        p.bolt(x0 + 560 + k * 110, cy - 224 - (k % 2) * 4, 6)
    # shafts
    p.line(x0 + 300, cy - 22, tx0 + 300, cy - 22, "h")
    p.line(x0 + 300, cy + 22, tx0 + 300, cy + 22, "h")
    p.line(x0 + 1000, cy - 40, tx0 + 90, cy - 40, "h")
    p.line(x0 + 1000, cy + 40, tx0 + 90, cy + 40, "h")
    p.centerline(x0 - 120, cy, x1 + 120, cy)
    # flow arrows in the bypass duct
    for s in (1, -1):
        for k in range(4):
            x = x0 + 820 + k * 140
            y = cy - s * 320
            p.poly([(x, y), (x + 70, y), (x + 56, y - 8), (x + 70, y), (x + 56, y + 8)], "a")

    # front view inset
    fx, fy = 2310, 470
    p.detail_circle(fx, fy, 280, "VIEW A")
    p.circle(fx, fy, 240, "m")
    p.circle(fx, fy, 70, "m")
    p.circle(fx, fy, 14, "s")
    for k in range(22):
        a = k * 2 * math.pi / 22
        p.path(f"M{fx+70*math.cos(a):.1f},{fy+70*math.sin(a):.1f} Q{fx+150*math.cos(a+0.28):.1f},{fy+150*math.sin(a+0.28):.1f} {fx+236*math.cos(a+0.42):.1f},{fy+236*math.sin(a+0.42):.1f}", "s")
    p.dim(x0, cy + 500, x0 + 1340, cy + 500, 100, "NACELLE 3 410")
    p.dim(x0 + 200, cy - 496, x0 + 200, cy + 496, 160, "Ø FAN 2 540")

    p.label(x0 + 340, cy - 300, 640, 230, "FAN", 1, "end")
    p.label(x0 + 640, cy - 180, 1060, 230, "LP COMPRESSOR", 2, "end")
    p.label(x0 + 1200, cy - 100, 1420, 230, "HP COMPRESSOR", 3)
    p.label(cx0 + 130, cy - 120, 2000, 1260, "COMBUSTOR", 4)
    p.label(tx0 + 100, cy + 120, 2140, 1360, "TURBINE", 5)
    p.label(x0 + 1100, cy + 320, 1180, 1580, "BYPASS DUCT", 6)
    p.label(tx0 + 460, cy + 20, 2380, 1180, "EXHAUST CONE", 7, "end")
    p.frame(5, "TURBOFAN", "high-bypass, two spool", "MERIDIONAL SECTION", "1:25",
            ("Bypass ratio 9:1", "Rotating parts shown sectioned"))
    return p


def earth():
    p = Plate(43)
    cx, cy, R = 1240, 900, 560
    tilt = math.radians(23.44)
    view = math.radians(18)

    def proj(lat, lon):
        x = math.cos(lat) * math.sin(lon)
        y = math.sin(lat)
        z = math.cos(lat) * math.cos(lon)
        # tilt toward viewer, then axial tilt in screen plane
        y, z = y * math.cos(view) - z * math.sin(view), y * math.sin(view) + z * math.cos(view)
        x, y = x * math.cos(tilt) - y * math.sin(tilt), x * math.sin(tilt) + y * math.cos(tilt)
        return cx + R * x, cy - R * y, z

    def in_cut(lat, lon):
        return 0 <= lon <= math.pi / 2 and lat >= 0

    def draw_curve(samples, cls_front, cls_back):
        seg, last = [], None
        for lat, lon in samples:
            x, y, z = proj(lat, lon)
            vis = z >= 0 and not in_cut(lat, lon)
            if last is not None and vis != last:
                if len(seg) > 1:
                    p.poly(seg, cls_front if last else cls_back)
                seg = seg[-1:]
            seg.append((x, y))
            last = vis
        if len(seg) > 1:
            p.poly(seg, cls_front if last else cls_back)

    for lat_d in range(-75, 90, 15):
        lat = math.radians(lat_d)
        draw_curve([(lat, 2 * math.pi * i / 240) for i in range(241)], "s" if lat_d else "m", "f")
    for lon_d in range(0, 360, 15):
        lon = math.radians(lon_d)
        draw_curve([(math.radians(-90 + 180 * i / 120), lon) for i in range(121)], "s", "f")
    for lat_d, name in ((23.44, "TROPIC OF CANCER"), (-23.44, "TROPIC OF CAPRICORN"), (66.56, "ARCTIC CIRCLE")):
        draw_curve([(math.radians(lat_d), 2 * math.pi * i / 240) for i in range(241)], "ad", "f")
    p.circle(cx, cy, R, "mb")
    p.circle(cx, cy, R, "t1")

    # cutaway faces: equatorial quarter disc + two meridional quarter discs
    layers = [(1.0, "mb"), (0.985, "s"), (0.55, "m"), (0.19, "m")]
    for fr, cls in layers:
        r = fr
        p.poly([proj(0, math.pi / 2 * i / 40)[:2] for i in range(41)], cls)  # placeholder for outer edge
    def face_pt(fr, lat, lon):
        x, y, z = proj(lat, lon)
        return cx + (x - cx) * fr, cy + (y - cy) * fr
    for fr, cls in layers:
        p.poly([face_pt(fr, 0, math.pi / 2 * i / 40) for i in range(41)], cls)
        p.poly([face_pt(fr, math.pi / 2 * i / 40, 0) for i in range(41)], cls)
        p.poly([face_pt(fr, math.pi / 2 * i / 40, math.pi / 2) for i in range(41)], cls)
    for fr, cls in ((1.0, "t1"), (0.985, "t1"), (0.55, "t2"), (0.19, "t2")):
        for face in ((0, None), (None, 0), (None, math.pi / 2)):
            ptsf = [(cx, cy)]
            for i in range(41):
                u = math.pi / 2 * i / 40
                lat, lon = (0, u) if face[0] == 0 else (u, face[1])
                ptsf.append(face_pt(fr, lat, lon))
            p.poly(ptsf, cls, closed=True)
    for lat, lon in ((0, 0), (0, math.pi / 2), (math.pi / 2, 0)):
        p.line(cx, cy, *proj(lat, lon)[:2], "m")
    # mantle convection hint
    for k in range(5):
        fr = 0.62 + k * 0.07
        p.poly([face_pt(fr, 0, math.pi / 2 * (0.1 + 0.8 * i / 20)) for i in range(21)], "f")

    # axis
    n = proj(math.pi / 2, 0)
    s_ = proj(-math.pi / 2, 0)
    dx, dy = n[0] - s_[0], n[1] - s_[1]
    L = math.hypot(dx, dy)
    p.line(s_[0] - dx / L * 160, s_[1] - dy / L * 160, n[0] + dx / L * 160, n[1] + dy / L * 160, "cl")
    p.line(cx, cy - R - 200, cx, cy + R + 200, "f")
    p.arc(cx, cy, R + 120, -math.pi / 2 - tilt, -math.pi / 2, "a")
    p.text(cx - 40, cy - R - 140, "23.44°", "tdim", "end")

    # insolation
    for k in range(9):
        y = cy - 420 + k * 105
        p.line(140, y, 420, y, "s")
        p.poly([(400, y - 8), (420, y), (400, y + 8)], "s")
    p.text(280, cy - 460, "INSOLATION", "tlb", "middle")

    # moon + orbit
    p.ellipse(cx, cy, 980, 220, "f", rot=-5)
    mx, my = cx + 900, cy - 170
    p.circle(mx, my, 80, "m")
    p.arc(mx, my, 80, -math.pi / 2, math.pi / 2, "s")
    p.path(f"M{mx},{my-80} Q{mx-40},{my} {mx},{my+80}", "s")

    p.label(*face_pt(0.1, 0.4, 0.6), 1880, 1500, "INNER CORE  1 220 km", 1)
    p.label(*face_pt(0.4, 0.2, 0.9), 1880, 1420, "OUTER CORE  2 260 km", 2)
    p.label(*face_pt(0.8, 0.15, 1.1), 1880, 1340, "MANTLE  2 890 km", 3)
    p.label(*face_pt(0.995, 0.5, 0.9), 1880, 260, "CRUST", 4)
    tc = proj(math.radians(23.44), math.radians(-60))
    p.label(tc[0], tc[1], 520, 640, "TROPIC OF CANCER", 5, "end")
    eq = proj(0, math.radians(-40))
    p.label(eq[0], eq[1], 520, 1200, "EQUATOR", 6, "end")
    p.label(mx, my + 80, 2400, 1180, "MOON", 7)
    p.frame(8, "EARTH", "Terra, 3rd planet", "CUTAWAY, OBLIQUE", "1:2.5x10⁷",
            ("Graticule 15 deg", "Layers to mean radius 6 371 km"))
    return p


def radiolarian():
    p = Plate(47)
    cx, cy = 1180, 900
    rng = random.Random(9)

    def sphere(R, n, pore, cls_front, cls_back, rot=0.3):
        golden = math.pi * (3 - math.sqrt(5))
        for i in range(n):
            y = 1 - 2 * (i + 0.5) / n
            r = math.sqrt(1 - y * y)
            th = golden * i + rot
            x, z = r * math.cos(th), r * math.sin(th)
            px, py = cx + R * x, cy + R * y
            if z > 0:
                ang = math.degrees(math.atan2(y, x))
                p.ellipse(px, py, pore, pore * max(0.25, z), cls_front, rot=ang + 90)
            elif z > -0.6:
                p.circle(px, py, pore * 0.5, cls_back)

    p.circle(cx, cy, 470, "tb")
    p.circle(cx, cy, 458, "s")
    sphere(458, 420, 15, "m", "f")
    p.circle(cx, cy, 250, "tm")
    sphere(250, 140, 13, "s", "f", rot=1.1)
    p.circle(cx, cy, 90, "tb")
    sphere(90, 30, 9, "s", "f", rot=2.0)
    # radial beams linking shells + spines
    for k in range(20):
        a = k * 2 * math.pi / 20 + 0.08
        L = 760 if k % 2 == 0 else 640
        ca, sa = math.cos(a), math.sin(a)
        p.line(cx + 90 * ca, cy + 90 * sa, cx + 470 * ca, cy + 470 * sa, "h")
        nx, ny = -sa, ca
        w = 16
        p.poly([(cx + 470 * ca + nx * w, cy + 470 * sa + ny * w), (cx + L * ca, cy + L * sa),
                (cx + 470 * ca - nx * w, cy + 470 * sa - ny * w)], "tm", closed=True)
        p.line(cx + 470 * ca, cy + 470 * sa, cx + (L - 20) * ca, cy + (L - 20) * sa, "f")
        for j in range(3):
            d = 520 + j * 60
            if d < L - 40:
                for s in (1, -1):
                    bx, by = cx + d * ca, cy + d * sa
                    p.line(bx, by, bx + (ca * 0.5 + s * nx) * 26, by + (sa * 0.5 + s * ny) * 26, "s")
    p.centermark(cx, cy, 40)
    p.circle(cx, cy, 760, "f")

    # diatom (centric), right top
    dx, dy = 2280, 480
    p.detail_circle(dx, dy, 270, "FIG. 2")
    p.circle(dx, dy, 220, "tb")
    p.circle(dx, dy, 206, "s")
    for ring in range(1, 9):
        r = ring * 24
        n = 6 * ring
        for k in range(n):
            a = k * 2 * math.pi / n + ring * 0.1
            p.poly([(dx + r * math.cos(a) + 8 * math.cos(a + j * math.pi / 3),
                     dy + r * math.sin(a) + 8 * math.sin(a + j * math.pi / 3)) for j in range(6)], "f" if ring % 2 else "s", closed=True)
    p.circle(dx, dy, 10, "a")
    # diatom (pennate), right bottom
    px, py = 2280, 1230
    p.text(px, py - 210, "FIG. 3", "tlb", "middle")
    p.ellipse(px, py, 300, 70, "tb")
    p.ellipse(px, py, 286, 58, "s")
    p.line(px - 270, py, px - 20, py, "m")
    p.line(px + 20, py, px + 270, py, "m")
    p.circle(px, py, 12, "m")
    for k in range(-26, 27):
        x = px + k * 10.5
        h = 58 * math.sqrt(max(0, 1 - (k * 10.5 / 286) ** 2))
        if abs(k) > 1:
            p.line(x, py - 8, x + (2 if k > 0 else -2), py - h + 4, "f")
            p.line(x, py + 8, x + (2 if k > 0 else -2), py + h - 4, "f")
    p.dim(px - 300, py + 70, px + 300, py + 70, 80, "62 μm")
    p.dim(cx - 470, cy + 470, cx + 470, cy + 470, 260, "Ø 180 μm")

    p.label(cx + 300, cy - 330, 1900, 160, "CORTICAL SHELL", 1)
    p.label(cx + 120, cy + 200, 1900, 1500, "MEDULLARY SHELL", 2)
    p.label(cx - 30, cy + 50, 440, 1500, "CENTRAL CAPSULE", 3, "end")
    p.label(cx - 560, cy - 280, 360, 300, "RADIAL SPINE", 4, "end")
    p.label(cx + 150, cy - 400, 1500, 110, "PORE", 5)
    p.frame(11, "RADIOLARIAN", "Actinomma arcadophorum", "AFTER HAECKEL", "800:1",
            ("Silica skeleton, three shells", "20 primary spines, 2 orders"))
    return p
