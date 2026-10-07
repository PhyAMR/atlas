import math
import random
from atlas import Plate, bez_pt, leaf_path, lerp


def _wing(p, root_le, root_te, tip, le_bow, te_bulge, rng, mirror):
    """Dragonfly wing: leading/trailing edges + longitudinal and cross veins."""
    s = -1 if mirror else 1
    LE = (root_le, (root_le[0] + s * 300, root_le[1] - le_bow), (tip[0] - s * 260, tip[1] - le_bow * 0.4), tip)
    TE = (root_te, (root_te[0] + s * 200, root_te[1] + te_bulge), (tip[0] - s * 180, tip[1] + te_bulge * 0.8), tip)

    def at(u, v):
        a = bez_pt(*LE, u); b = bez_pt(*TE, u)
        return lerp(a, b, v)

    p.poly([bez_pt(*LE, i / 120) for i in range(121)] + [bez_pt(*TE, 1 - i / 120) for i in range(121)], "t1", closed=True)
    p.poly([bez_pt(*LE, i / 120) for i in range(121)], "mb")
    p.poly([bez_pt(*TE, i / 120) for i in range(121)], "m")
    vs = [0.06, 0.13, 0.22, 0.34, 0.48, 0.64, 0.8]
    for j, v in enumerate(vs):
        p.poly([at(i / 100 * 0.985, v * (1 - (i / 100) ** 6)) for i in range(101)], "s" if j < 4 else "f")
    # cross veins
    for j in range(len(vs) - 1):
        n = 26 + j * 4
        for k in range(1, n):
            u = k / n + rng.uniform(-0.008, 0.008)
            if u > 0.97:
                continue
            v0 = vs[j] * (1 - u ** 6); v1 = vs[j + 1] * (1 - u ** 6)
            p.line(*at(u, v0), *at(u + rng.uniform(-0.006, 0.006), v1), "f")
    # margin cells
    for k in range(1, 70):
        u = k / 70
        v0 = 0.8 * (1 - u ** 6)
        a = at(u, v0); b = at(u + 0.007, 1.0)
        p.line(*a, *b, "f")
    # nodus + pterostigma
    p.line(*at(0.42, 0), *at(0.42, 0.22), "s")
    a = at(0.86, 0.0); b = at(0.92, 0.0); c = at(0.92, 0.07); d = at(0.86, 0.07)
    p.poly([a, b, c, d], "a", closed=True)
    return at


def dragonfly():
    p = Plate(23)
    rng = random.Random(3)
    cx = 1300
    # wings
    _wing(p, (cx + 30, 560), (cx + 30, 610), (cx + 1050, 470), 40, 90, rng, False)
    _wing(p, (cx - 30, 560), (cx - 30, 610), (cx - 1050, 470), 40, 90, rng, True)
    _wing(p, (cx + 30, 650), (cx + 30, 760), (cx + 980, 760), 20, 170, rng, False)
    _wing(p, (cx - 30, 650), (cx - 30, 760), (cx - 980, 760), 20, 170, rng, True)
    # head + eyes
    for s in (1, -1):
        p.circle(cx + s * 52, 410, 66, "tb")
        for k in range(26):
            a = rng.uniform(0, 2 * math.pi); r = rng.uniform(0, 56)
            x, y = cx + s * 52 + r * math.cos(a), 410 + r * math.sin(a)
            p.poly([(x + 6 * math.cos(j * math.pi / 3), y + 6 * math.sin(j * math.pi / 3)) for j in range(6)], "f", closed=True)
    p.path(f"M{cx-60},460 Q{cx},520 {cx+60},460", "m")
    p.path(f"M{cx-40},360 Q{cx},330 {cx+40},360", "s")
    # thorax
    p.path(f"M{cx-50},500 C{cx-80},560 {cx-80},680 {cx-40},760 L{cx+40},760 C{cx+80},680 {cx+80},560 {cx+50},500 Z", "tb")
    p.path(f"M{cx-40},520 C{cx-62},580 {cx-62},670 {cx-30},740 L{cx+30},740 C{cx+62},670 {cx+62},580 {cx+40},520 Z", "t1")
    for k in range(3):
        y = 560 + k * 60
        p.path(f"M{cx-64},{y} Q{cx},{y+24} {cx+64},{y}", "s")
    # abdomen, ten segments
    y = 760
    for k in range(10):
        w = 30 - k * 1.2 if k < 8 else 22
        h = 92 if k < 8 else 60
        p.path(f"M{cx-w},{y} L{cx-w+3},{y+h} L{cx+w-3},{y+h} L{cx+w},{y} Z", "tb")
        p.ellipse(cx, y + h * 0.62, w * 0.45, h * 0.18, "t2")
        for sgn in (1, -1):
            p.line(cx + sgn * (w - 8), y + 6, cx + sgn * (w - 9), y + h - 6, "d")
        p.line(cx - w + 6, y + h * 0.3, cx + w - 6, y + h * 0.3, "f")
        y += h
    for s in (1, -1):
        p.path(f"M{cx+s*16},{y} Q{cx+s*40},{y+50} {cx+s*28},{y+90}", "m")
    p.centerline(cx, 280, cx, y + 140)
    # legs (folded under thorax, hidden)
    for k, (dy, L) in enumerate(((560, 130), (620, 160), (690, 190))):
        for s in (1, -1):
            kx, ky = cx + s * (60 + L * 0.5), dy + 30 + k * 20
            p.poly([(cx + s * 30, dy), (kx, ky), (cx + s * (40 + L * 0.2), ky + L * 0.6)], "h")

    p.dim(cx - 1050, 470, cx + 1050, 470, -220, "WINGSPAN 104 mm")
    p.label(cx + 1000, 480, 2400, 330, "PTEROSTIGMA", 1)
    p.label(cx + 470, 590, 2000, 1060, "NODUS", 2)
    p.label(cx - 100, 420, 760, 260, "COMPOUND EYE", 3, "end")
    p.label(cx - 60, 620, 700, 1060, "SYNTHORAX", 4, "end")
    p.label(cx + 24, 1200, 1760, 1360, "ABDOMEN S1-S10", 5)
    p.label(cx - 30, y + 60, 900, 1560, "CERCI", 6, "end")
    p.frame(4, "DRAGONFLY", "Anax imperator", "DORSAL VIEW", "2:1",
            ("Wing venation schematic", "Hindwing base broader", "Legs shown hidden"))
    return p


def beetle():
    p = Plate(29)
    cx = 1300

    def both(fn):
        fn(1); fn(-1)

    # elytra
    def elytron(s):
        p.path(f"M{cx},760 C{cx+s*170},760 {cx+s*330},800 {cx+s*340},1000 C{cx+s*350},1240 {cx+s*260},1480 {cx},1580", "tb")
        for k in range(1, 7):
            off = k * 44
            for j in range(16):
                t = j / 15
                yy = 820 + t * (660 - k * 10)
                xx = off * (1 - 0.5 * t ** 2) + 10
                p.circle(cx + s * xx, yy, 2.2, "d")
        p.path(f"M{cx},780 C{cx+s*160},780 {cx+s*312},820 {cx+s*322},1000 C{cx+s*330},1230 {cx+s*248},1460 {cx+s*6},1560", "s")
        for k in range(1, 7):
            off = k * 44
            p.path(f"M{cx+s*off},800 C{cx+s*(off+8)},1000 {cx+s*(off*0.95)},1250 {cx+s*off*0.5},{1500 - k * 6}", "h")
    both(elytron)
    p.line(cx, 760, cx, 1580, "m")
    p.path(f"M{cx-40},760 L{cx},840 L{cx+40},760", "s")  # scutellum
    # pronotum
    p.path(f"M{cx-250},750 C{cx-290},640 {cx-250},520 {cx-140},480 L{cx+140},480 C{cx+250},520 {cx+290},640 {cx+250},750 Z", "tb")
    p.path(f"M{cx-250},750 C{cx-290},640 {cx-250},520 {cx-140},480 L{cx+140},480 C{cx+250},520 {cx+290},640 {cx+250},750 Z", "t1")
    p.path(f"M{cx-220},730 C{cx-256},640 {cx-226},540 {cx-130},504 L{cx+130},504 C{cx+226},540 {cx+256},640 {cx+220},730", "f")
    # head + mandibles
    p.path(f"M{cx-130},480 C{cx-150},400 {cx-110},330 {cx},320 C{cx+110},330 {cx+150},400 {cx+130},480 Z", "tb")
    p.path(f"M{cx-130},480 C{cx-150},400 {cx-110},330 {cx},320 C{cx+110},330 {cx+150},400 {cx+130},480 Z", "t1")
    def mandible(s):
        p.path(f"M{cx+s*70},336 C{cx+s*140},270 {cx+s*120},200 {cx+s*40},190 C{cx+s*80},220 {cx+s*80},270 {cx+s*30},326", "m")
        p.circle(cx + s * 100, 390, 26, "m")
        p.circle(cx + s * 100, 390, 16, "f")
    both(mandible)
    # antennae, 11 segments
    def antenna(s):
        x, y, a = cx + s * 110, 370, -math.pi / 2 + s * 0.95
        for k in range(11):
            L = 25 if k > 0 else 40
            nx, ny = x + L * math.cos(a), y + L * math.sin(a)
            w = 9 + (k > 7) * 7
            p.ellipse((x + nx) / 2, (y + ny) / 2, L / 2, w, "m", rot=math.degrees(a))
            x, y = nx, ny
            a += s * 0.13 if k < 3 else -s * 0.05
    both(antenna)
    # legs
    def leg(s, y0, ang, lens, cls):
        x, y = cx + s * 150, y0
        a = ang
        pts_ = [(x, y)]
        for i, L in enumerate(lens):
            nx, ny = x + s * L * math.cos(a), y + L * math.sin(a)
            p.path(leaf_path((x, y), (nx, ny), 14 - i * 3), "tm")
            for j in range(3):
                hx, hy = x + (nx - x) * (0.3 + j * 0.25), y + (ny - y) * (0.3 + j * 0.25)
                p.line(hx, hy, hx + s * 10, hy + 9, "d")
            p.circle(nx, ny, 6, "s")
            x, y = nx, ny
            a += 0.75 if i == 0 else 0.35
            pts_.append((x, y))
        for k in range(4):  # tarsi
            nx, ny = x + s * 22 * math.cos(a), y + 22 * math.sin(a)
            p.circle((x + nx) / 2, (y + ny) / 2, 9, "s")
            x, y = nx, ny
        p.path(f"M{x:.1f},{y:.1f} l{s*14},{-8} M{x:.1f},{y:.1f} l{s*14},{8}", "s")
    for s in (1, -1):
        leg(s, 640, -0.9, (110, 190, 170), "m")
        leg(s, 860, -0.1, (130, 230, 190), "m")
        leg(s, 960, 0.5, (150, 260, 220), "m")
    # wing (hidden under elytron, one side)
    p.path(f"M{cx+40},820 C{cx+300},860 {cx+520},1100 {cx+460},1460 C{cx+300},1500 {cx+120},1420 {cx+40},1300", "h")
    p.centerline(cx, 100, cx, 1660)
    # side view, right
    sx, sy = 2250, 960
    p.text(sx, 520, "LATERAL VIEW", "tlb", "middle")
    p.path(f"M{sx-260},{sy} C{sx-260},{sy-210} {sx+80},{sy-230} {sx+280},{sy-60} C{sx+300},{sy+20} {sx+240},{sy+70} {sx+120},{sy+70} L{sx-200},{sy+60} Z", "tb")
    p.path(f"M{sx-260},{sy} C{sx-300},{sy-60} {sx-340},{sy-40} {sx-360},{sy+10} C{sx-330},{sy+40} {sx-290},{sy+50} {sx-240},{sy+40}", "m")
    for k in range(3):
        x0 = sx - 150 + k * 150
        p.poly([(x0, sy + 60), (x0 - 70, sy + 150), (x0 - 20, sy + 260), (x0 + 30, sy + 268)], "m")
        for (jx, jy) in ((x0 - 70, sy + 150), (x0 - 20, sy + 260)):
            p.circle(jx, jy, 6, "s")
    p.path(f"M{sx-360},{sy+10} C{sx-420},{sy-10} {sx-450},{sy-40} {sx-440},{sy-80}", "m")
    p.circle(sx - 300, sy - 10, 18, "s")
    for k in range(5):
        p.path(f"M{sx-200+k*90},{sy-150+abs(k-2)*14} Q{sx-150+k*90},{sy-30} {sx-210+k*90},{sy+50}", "f")
    p.dim(sx - 360, sy + 300, sx + 290, sy + 300, 40, "34 mm")
    p.dim(cx - 340, 150, cx - 340, 1580, 160, "52 mm")

    p.label(cx + 220, 1100, 1900, 1400, "ELYTRON", 1)
    p.label(cx + 200, 600, 1800, 360, "PRONOTUM", 2)
    p.label(cx - 100, 240, 760, 160, "MANDIBLE", 3, "end")
    p.label(cx - 250, 250, 760, 420, "ANTENNA (11)", 4, "end")
    p.label(cx - 390, 900, 760, 1200, "MESOTHORACIC LEG", 5, "end")
    p.label(cx + 300, 1180, 1900, 1440, "HINDWING (FOLDED)", 6)
    p.frame(10, "STAG BEETLE", "Lucanus cervus (f.)", "DORSAL VIEW", "3:1",
            ("Striae shown hidden", "Tarsal formula 5-5-5"))
    return p


def fish():
    p = Plate(31)
    # body outline (hidden), fusiform
    top = ((420, 900), (600, 560), (1500, 520), (2040, 820))
    bot = ((420, 900), (620, 1220), (1500, 1260), (2040, 960))
    p.poly([bez_pt(*top, i / 120) for i in range(121)] + [bez_pt(*bot, 1 - i / 120) for i in range(121)], "t1", closed=True)
    # scale rows, faint
    for r in range(1, 9):
        v = r / 9
        for k in range(40):
            t = 0.22 + k * 0.019
            if t > 0.98:
                break
            a_ = bez_pt(*top, t); b_ = bez_pt(*bot, t)
            x = a_[0] + (b_[0] - a_[0]) * v + (r % 2) * 9
            y = a_[1] + (b_[1] - a_[1]) * v
            p.path(f"M{x:.1f},{y-9:.1f} a10,10 0 0 1 0,18", "f")
    p.poly([bez_pt(*top, i / 120) for i in range(121)], "h")
    p.poly([bez_pt(*bot, i / 120) for i in range(121)], "h")
    # caudal fin
    p.path("M2040,820 C2160,760 2300,620 2420,520 C2380,700 2360,820 2330,890 C2360,960 2380,1080 2420,1260 C2300,1160 2160,1020 2040,960 Z", "tm")
    for k in range(18):
        t = k / 17
        ex = 2420 - 90 * math.sin(math.pi * t)
        ey = 520 + 740 * t
        p.path(f"M2050,{820 + 140 * t:.1f} Q2200,{870 + (t - 0.5) * 300:.1f} {ex:.1f},{ey:.1f}", "s")
    # spine
    spine = ((760, 860), (1100, 830), (1600, 840), (2050, 890))
    n = 38
    for k in range(n):
        t = k / (n - 1)
        x, y = bez_pt(*spine, t)
        x2, y2 = bez_pt(*spine, min(1, t + 0.01))
        a = math.atan2(y2 - y, x2 - x)
        w, h = 16, 22 - 6 * t
        p.rect(x - w, y - h, 2 * w, 2 * h, "tb", r=6, rot=math.degrees(a), cx=x, cy=y)
        p.line(x, y - h, x, y + h, "f")
        # neural spine (up, swept back)
        top_y = bez_pt(*top, 0.25 + 0.75 * t)[1]
        p.path(f"M{x:.1f},{y-h:.1f} Q{x+20:.1f},{(y+top_y)/2:.1f} {x+70+40*t:.1f},{top_y+40:.1f}", "m")
        if t < 0.45:
            # ribs
            bot_y = bez_pt(*bot, 0.25 + 0.75 * t)[1]
            p.path(f"M{x:.1f},{y+h:.1f} C{x+40:.1f},{y+120:.1f} {x+30:.1f},{bot_y-80:.1f} {x+60+20*t:.1f},{bot_y-30:.1f}", "m")
        else:
            bot_y = bez_pt(*bot, 0.25 + 0.75 * t)[1]
            p.path(f"M{x:.1f},{y+h:.1f} Q{x+20:.1f},{(y+bot_y)/2:.1f} {x+70+40*t:.1f},{bot_y-40:.1f}", "m")
    # skull
    p.path("M420,900 C430,780 520,660 680,640 C760,630 820,700 820,780 L820,1040 C760,1120 620,1140 520,1060 Z", "tb")
    p.path("M470,860 C500,760 580,700 680,690 C740,690 780,730 790,780 L790,900 C700,880 600,880 470,860 Z", "t1")
    for k in range(8):
        p.path(f"M{600+k*24},660 q20,60 0,140", "d")
    p.circle(560, 790, 62, "m")
    p.circle(560, 790, 30, "s")
    p.path("M420,900 L560,930 L700,1000", "m")       # jaw line
    p.path("M430,920 C480,990 560,1040 660,1060", "m")  # dentary
    for k in range(9):
        p.line(450 + k * 22, 925 + k * 4, 452 + k * 22, 912 + k * 4, "s")
    for k in range(4):  # operculum + gill arches
        p.path(f"M{760+k*22},700 C{830+k*22},800 {830+k*22},960 {740+k*22},1080", "s" if k else "m")
    # dorsal fin
    tips = []
    for k in range(20):
        t = k / 19
        bx, by = bez_pt(*top, 0.38 + 0.25 * t)
        tip = (bx + 60 + 40 * t, by - 60 - 200 * math.sin(math.pi * (0.15 + 0.85 * t)) ** 0.6 * (1 - 0.5 * t))
        p.line(bx, by, *tip, "s")
        tips.append(tip)
    p.poly([bez_pt(*top, 0.38)] + tips + [bez_pt(*top, 0.63)], "tm", closed=True)
    # anal fin
    tips = []
    for k in range(12):
        t = k / 11
        bx, by = bez_pt(*bot, 0.62 + 0.18 * t)
        tip = (bx + 80 + 30 * t, by + 160 - 100 * t)
        p.line(bx, by, *tip, "s")
        tips.append(tip)
    p.poly([bez_pt(*bot, 0.62)] + tips + [bez_pt(*bot, 0.80)], "tm", closed=True)
    # pectoral + pelvic
    for k in range(12):
        a = 0.3 + k * 0.08
        p.line(860, 980, 860 + 300 * math.cos(a), 980 + 300 * math.sin(a) * 0.6, "s")
    p.path(f"M860,980 Q1050,1000 {860+300*math.cos(0.3):.1f},{980+300*math.sin(0.3)*0.6:.1f}", "f")
    for k in range(8):
        a = 0.7 + k * 0.08
        p.line(1220, 1180, 1220 + 200 * math.cos(a), 1180 + 200 * math.sin(a) * 0.8, "s")
    p.centerline(300, 880, 2500, 880)
    p.dim(420, 1260, 2040, 1260, 150, "SL 610 mm")

    p.label(560, 790, 500, 360, "ORBIT", 1, "end")
    p.label(780, 740, 820, 260, "OPERCULUM", 2, "end")
    p.label(1300, 830, 1640, 200, "VERTEBRAL COLUMN", 3)
    p.label(1100, 1050, 1260, 1620, "PLEURAL RIBS", 4)
    p.label(1180, 500, 2000, 260, "DORSAL FIN RAYS", 5)
    p.label(2300, 1000, 2380, 1440, "CAUDAL FIN", 6, "end")
    p.label(1000, 1060, 640, 1500, "PECTORAL FIN", 7, "end")
    p.frame(7, "FISH SKELETON", "Perca fluviatilis", "LATERAL VIEW", "1:2",
            ("38 vertebrae, 14 rib pairs", "Outline of body shown hidden"))
    return p
