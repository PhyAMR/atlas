import math
import random
from atlas import Plate, bez_pt, leaf_path, lerp


def fern():
    p = Plate(11)
    P = [(1250, 1560), (1180, 1150), (1420, 620), (1560, 230)]
    p.path(f"M{P[0][0]},{P[0][1]} C{P[1][0]},{P[1][1]} {P[2][0]},{P[2][1]} {P[3][0]},{P[3][1]}", "mb")
    p.path(f"M{P[0][0]+8},{P[0][1]} C{P[1][0]+8},{P[1][1]} {P[2][0]+6},{P[2][1]} {P[3][0]},{P[3][1]}", "s")
    n = 30
    for i in range(3, n):
        t = i / n
        x, y = bez_pt(*P, t)
        x2, y2 = bez_pt(*P, min(1, t + 0.01))
        ang = math.atan2(y2 - y, x2 - x)
        side = 1 if i % 2 else -1
        L = 520 * math.sin(math.pi * ((t - 0.1) / 0.92)) ** 0.9 * (1.0 - 0.25 * t)
        if L < 30:
            continue
        a = ang + side * 1.05
        tip = (x + L * math.cos(a) + 40 * math.cos(ang), y + L * math.sin(a) + 40 * math.sin(ang))
        ctrl = (x + L * 0.5 * math.cos(a - side * 0.12), y + L * 0.5 * math.sin(a - side * 0.12))
        p.path(f"M{x:.1f},{y:.1f} Q{ctrl[0]:.1f},{ctrl[1]:.1f} {tip[0]:.1f},{tip[1]:.1f}", "m")
        m = max(3, int(L / 34))
        for k in range(1, m):
            u = k / m
            q = (1 - u) ** 2 * x + 2 * (1 - u) * u * ctrl[0] + u * u * tip[0], (1 - u) ** 2 * y + 2 * (1 - u) * u * ctrl[1] + u * u * tip[1]
            pa = math.atan2(tip[1] - y, tip[0] - x)
            pl = (L / 5.2) * (1 - u * 0.75)
            for s in (1, -1):
                aa = pa + s * 0.95
                tp = (q[0] + pl * math.cos(aa) + pl * 0.35 * math.cos(pa), q[1] + pl * math.sin(aa) + pl * 0.35 * math.sin(pa))
                p.path(leaf_path(q, tp, pl * 0.32, bend=s * pl * 0.05), "ts" if i % 3 else "tm")
                p.line(q[0], q[1], q[0] + (tp[0] - q[0]) * 0.8, q[1] + (tp[1] - q[1]) * 0.8, "d")
            if i == 14 and k in (3, 4, 5):
                for s in (1, -1):
                    aa = pa + s * 0.95
                    for j in (0.35, 0.55):
                        p.circle(q[0] + pl * j * math.cos(aa), q[1] + pl * j * math.sin(aa), 3.5, "a")
    # stipe cross-section mark
    p.line(1150, 1430, 1320, 1430, "a")
    p.text(1330, 1436, "A", "tlb")
    p.text(1130, 1436, "A", "tlb", "end")
    # rhizome + roots
    p.path("M760,1560 C960,1530 1120,1590 1260,1562 S1600,1540 1760,1580", "mb")
    p.path("M760,1574 C960,1544 1120,1604 1260,1576 S1600,1554 1760,1594", "s")
    p.line(560, 1555, 1980, 1555, "h")
    rng = random.Random(5)
    for i in range(40):
        x = 800 + i * 24 + rng.uniform(-8, 8)
        y = 1570 + rng.uniform(-8, 8)
        pts_ = [(x, y)]
        for k in range(5):
            x += rng.uniform(-14, 14); y += rng.uniform(12, 24)
            pts_.append((x, y))
        p.poly(pts_, "s" if i % 2 else "f")

    # crozier (young frond unrolling), left
    cx, cy = 640, 760
    pts_ = []
    for i in range(260):
        th = i / 260 * 3.4 * math.pi
        r = 8 * math.exp(0.22 * th)
        pts_.append((cx + r * math.cos(th), cy + r * math.sin(th)))
    p.poly(pts_, "mb")
    for i in range(30, 260, 9):
        x, y = pts_[i]
        x2, y2 = pts_[i - 1]
        a = math.atan2(y - y2, x - x2) - 1.3
        r = 6 + i / 260 * 30
        p.path(leaf_path((x, y), (x + r * math.cos(a), y + r * math.sin(a)), r * 0.35), "s")
    ex, ey = pts_[-1]
    p.path(f"M{ex:.1f},{ey:.1f} C{ex+40:.1f},{ey+200:.1f} {cx-60},{cy+400} {cx+10},{cy+760}", "mb")
    p.text(cx, cy - 230, "FIG. 2  CROZIER", "tlb", "middle")

    # detail: sori on the underside of a pinnule
    dx, dy = 2280, 620
    p.detail_circle(dx, dy, 300, "DETAIL B")
    p.path(leaf_path((dx - 230, dy + 60), (dx + 240, dy - 40), 110), "tm")
    p.line(dx - 230, dy + 60, dx + 240, dy - 40, "s")
    for k in range(7):
        u = 0.15 + k * 0.11
        mx, my = lerp((dx - 230, dy + 60), (dx + 240, dy - 40), u)
        for s in (1, -1):
            p.line(mx, my, mx + 20 + 30 * s * 0.2, my + s * 70, "f")
            p.circle(mx + 14, my + s * 46, 16, "tb")
            for j in range(6):
                a = j * math.pi / 3
                p.line(mx + 14, my + s * 46, mx + 14 + 14 * math.cos(a), my + s * 46 + 14 * math.sin(a), "f")
    # stipe section A-A
    sx, sy = 2280, 1240
    p.circle(sx, sy, 130, "tm")
    p.circle(sx, sy, 118, "t1")
    p.circle(sx, sy, 118, "s")
    p.path(f"M{sx-60},{sy-30} Q{sx-80},{sy+60} {sx-20},{sy+50} Q{sx},{sy+10} {sx+20},{sy+50} Q{sx+80},{sy+60} {sx+60},{sy-30}", "m")
    p.path(f"M{sx-44},{sy-24} Q{sx-60},{sy+40} {sx-20},{sy+34} Q{sx},{sy-4} {sx+20},{sy+34} Q{sx+60},{sy+40} {sx+44},{sy-24}", "h")
    p.text(sx, sy + 190, "SECTION A-A", "tlb", "middle")

    p.label(*bez_pt(*P, 0.62), 1880, 300, "RACHIS", 1)
    p.label(*bez_pt(*P, 0.30), 880, 300, "PINNA", 2, "end")
    p.label(dx - 140, dy + 110, 1900, 1040, "SORUS", 3, "end")
    p.label(1270, 1555, 1560, 1690, "RHIZOME", 4)
    p.label(cx + 30, cy + 10, 470, 1100, "CIRCINATE VERNATION", 5, "end")
    p.label(sx - 20, sy + 40, 1900, 1500, "VASCULAR BUNDLE", 6, "end")
    p.frame(2, "FERN", "Dryopteris filix-mas", "FROND, ABAXIAL", "1:4",
            ("Pinnae alternate, bipinnate", "Sori reniform, indusiate"))
    return p


def flower():
    p = Plate(13)
    cx, base = 1220, 1180
    p.centerline(cx, 180, cx, 1700)
    # stem + receptacle
    for s in (1, -1):
        p.path(f"M{cx+s*26},1700 C{cx+s*24},1450 {cx+s*30},1300 {cx+s*70},{base}", "m")
        p.path(f"M{cx+s*16},1700 C{cx+s*14},1450 {cx+s*18},1300 {cx+s*44},{base-10}", "h")
    # ovary (section) with ovules
    p.path(f"M{cx-70},{base} C{cx-120},{base-120} {cx-90},{base-260} {cx-34},{base-300} L{cx+34},{base-300} C{cx+90},{base-260} {cx+120},{base-120} {cx+70},{base} Z", "tb")
    p.line(cx, base - 10, cx, base - 290, "s")
    for k in range(7):
        y = base - 50 - k * 34
        for s in (1, -1):
            p.ellipse(cx + s * 32, y, 13, 10, "m")
            p.line(cx, y, cx + s * 20, y, "f")
    # style + stigma
    p.path(f"M{cx-12},{base-300} C{cx-14},{base-500} {cx-8},{base-640} {cx-14},{base-760}", "m")
    p.path(f"M{cx+12},{base-300} C{cx+14},{base-500} {cx+8},{base-640} {cx+14},{base-760}", "m")
    p.line(cx, base - 300, cx, base - 760, "h")
    for a in (-0.9, 0, 0.9):
        p.path(leaf_path((cx, base - 760), (cx + 60 * math.sin(a), base - 760 - 60 * math.cos(a)), 26), "m")
    # stamens
    for k, (dx, h, lean) in enumerate([(-50, 560, -220), (50, 560, 220), (-40, 470, -120), (40, 470, 120)]):
        x0, y0 = cx + dx, base - 40
        tx, ty = cx + dx + lean, base - h
        p.path(f"M{x0},{y0} C{x0},{y0-200} {tx-lean*0.2},{ty+200} {tx},{ty}", "m" if k < 2 else "s")
        p.ellipse(tx, ty - 6, 16, 52, "tb" if k < 2 else "ts", rot=math.degrees(math.atan2(lean, h)) * 0.6)
        if k < 2:
            for j in range(6):
                p.circle(tx + (j % 2) * 8 - 4, ty - 40 + j * 12, 2.5, "d")
        p.line(tx, ty - 50, tx, ty + 40, "f")
    # tepals: section through two, plus one seen whole behind (dashed)
    for s in (1, -1):
        d = (f"M{cx+s*70},{base} C{cx+s*200},{base-150} {cx+s*260},{base-420} {cx+s*330},{base-620} "
             f"C{cx+s*370},{base-730} {cx+s*470},{base-760} {cx+s*560},{base-700} "
             f"C{cx+s*470},{base-690} {cx+s*420},{base-610} {cx+s*370},{base-520} "
             f"C{cx+s*300},{base-380} {cx+s*230},{base-140} {cx+s*100},{base+10} Z")
        p.path(d, "tb")
        for k in (-0.5, 0.5, 1.0):
            p.path(f"M{cx+s*90},{base} C{cx+s*(220+k*30)},{base-150} {cx+s*(270+k*40)},{base-420} {cx+s*(340+k*20)},{base-600}", "d")
        p.path(f"M{cx+s*85},{base} C{cx+s*220},{base-150} {cx+s*290},{base-420} {cx+s*350},{base-580} S{cx+s*460},{base-720} {cx+s*540},{base-705}", "s")
        rng = random.Random(4 if s > 0 else 9)
        for k in range(14):
            t = rng.uniform(0.25, 0.7)
            x = cx + s * (100 + t * 280) + rng.uniform(-14, 14)
            y = base - t * 640 + rng.uniform(-10, 30)
            p.circle(x, y, rng.uniform(2.5, 5), "s")
        # sepal-like bract
        p.path(f"M{cx+s*40},{base+40} C{cx+s*160},{base+30} {cx+s*230},{base-20} {cx+s*300},{base-110} C{cx+s*220},{base-50} {cx+s*140},{base+30} {cx+s*60},{base+70}", "s")
    p.path(f"M{cx-60},{base-20} C{cx-120},{base-400} {cx-60},{base-760} {cx},{base-900} C{cx+60},{base-760} {cx+120},{base-400} {cx+60},{base-20}", "h")

    # leaf on stem
    p.path(leaf_path((cx + 20, 1500), (cx + 520, 1250), 70, bend=-40), "tm")
    for k in range(1, 8):
        bxk, byk = cx + 20 + 500 * k / 8, 1500 - 250 * k / 8 - 20
        p.line(bxk, byk, bxk + 50, byk - 50, "d")
        p.line(bxk, byk, bxk + 40, byk + 30, "d")
    p.path(f"M{cx+20},1500 Q{cx+270},1350 {cx+520},1250", "s")

    # floral diagram, top right
    fx, fy = 2240, 520
    p.detail_circle(fx, fy, 290, "FLORAL DIAGRAM")
    for k in range(3):
        for ring, rr, sz, cls in ((0, 220, 70, "m"), (1, 160, 58, "s")):
            a = k * 2 * math.pi / 3 + ring * math.pi / 3 - math.pi / 2
            x, y = fx + rr * math.cos(a), fy + rr * math.sin(a)
            p.path(f"M{x-sz*math.sin(a):.1f},{y+sz*math.cos(a):.1f} Q{x+40*math.cos(a):.1f},{y+40*math.sin(a):.1f} {x+sz*math.sin(a):.1f},{y-sz*math.cos(a):.1f} Q{x+10*math.cos(a):.1f},{y+10*math.sin(a):.1f} {x-sz*math.sin(a):.1f},{y+sz*math.cos(a):.1f}", cls)
    for k in range(6):
        a = k * math.pi / 3 - math.pi / 2
        x, y = fx + 100 * math.cos(a), fy + 100 * math.sin(a)
        p.ellipse(x, y, 20, 12, "m", rot=math.degrees(a) + 90)
        p.line(x - 8 * math.cos(a), y - 8 * math.sin(a), x + 8 * math.cos(a), y + 8 * math.sin(a), "f")
    p.circle(fx, fy, 50, "m")
    for k in range(3):
        a = k * 2 * math.pi / 3 - math.pi / 2
        p.line(fx, fy, fx + 50 * math.cos(a), fy + 50 * math.sin(a), "s")
        a2 = a + math.pi / 3
        p.circle(fx + 26 * math.cos(a2), fy + 26 * math.sin(a2), 6, "s")
    p.text(fx, fy + 340, "P3+3  A3+3  G(3)", "ts", "middle")

    # cross section of ovary, bottom right
    ox, oy = 2240, 1260
    p.circle(ox, oy, 150, "tb")
    p.circle(ox, oy, 138, "s")
    for k in range(3):
        a = k * 2 * math.pi / 3 - math.pi / 2
        p.line(ox, oy, ox + 138 * math.cos(a), oy + 138 * math.sin(a), "m")
        a2 = a + math.pi / 3
        for j in (-1, 1):
            p.ellipse(ox + 60 * math.cos(a2) + j * 18 * math.cos(a2 + math.pi / 2),
                      oy + 60 * math.sin(a2) + j * 18 * math.sin(a2 + math.pi / 2), 14, 10, "m")
    p.text(ox, oy + 200, "SECTION B-B", "tlb", "middle")
    p.line(cx - 160, base - 150, cx + 160, base - 150, "a")
    p.text(cx + 170, base - 144, "B", "tlb")

    p.label(cx + 380, base - 560, 1820, 380, "TEPAL", 1)
    p.label(cx - 270, base - 552, 760, 300, "ANTHER", 2, "end")
    p.label(cx - 150, base - 300, 760, 640, "FILAMENT", 3, "end")
    p.label(cx + 30, base - 790, 1640, 220, "STIGMA", 4)
    p.label(cx + 10, base - 600, 1700, 760, "STYLE", 5)
    p.label(cx - 30, base - 180, 760, 1000, "OVULE", 6, "end")
    p.label(cx + 80, base - 130, 1700, 1080, "OVARY", 7)
    p.label(cx + 260, base - 60, 1760, 1180, "BRACT", 8)
    p.label(cx - 30, 1500, 760, 1420, "PEDUNCLE", 9, "end")
    p.frame(6, "LILY", "Lilium candidum", "LONG. SECTION", "2:1",
            ("Hypogynous, actinomorphic", "Tepals six in two whorls", "Placentation axile"))
    return p


def tree():
    p = Plate(17)
    rng = random.Random(21)
    gx, gy = 1280, 1180
    # ground
    p.line(300, gy, 2560, gy, "m")
    for i in range(80):
        x = 320 + i * 28
        p.line(x, gy + 4, x - 18, gy + 22, "f")

    def branch(x, y, ang, length, width, depth, down=False):
        if depth == 0 or length < 8:
            if not down and rng.random() < 0.7:
                for k in range(3):
                    a = ang + rng.uniform(-1.2, 1.2)
                    L = rng.uniform(16, 26)
                    p.path(leaf_path((x, y), (x + L * math.cos(a), y + L * math.sin(a)), L * 0.35), "lf")
            return
        bend = rng.uniform(-0.25, 0.25)
        ex = x + length * math.cos(ang)
        ey = y + length * math.sin(ang)
        mx = x + length * 0.5 * math.cos(ang + bend)
        my = y + length * 0.5 * math.sin(ang + bend)
        w2 = width * 0.68
        if width > 7:
            nx, ny = -math.sin(ang), math.cos(ang)
            cls = "h" if down else "m"
            p.path(f"M{x+nx*width:.1f},{y+ny*width:.1f} Q{mx+nx*(width+w2)/2:.1f},{my+ny*(width+w2)/2:.1f} {ex+nx*w2:.1f},{ey+ny*w2:.1f}", cls)
            p.path(f"M{x-nx*width:.1f},{y-ny*width:.1f} Q{mx-nx*(width+w2)/2:.1f},{my-ny*(width+w2)/2:.1f} {ex-nx*w2:.1f},{ey-ny*w2:.1f}", cls)
        else:
            p.path(f"M{x:.1f},{y:.1f} Q{mx:.1f},{my:.1f} {ex:.1f},{ey:.1f}", "h" if down else ("s" if depth > 2 else "f"))
        n = 2 if rng.random() < 0.75 else 3
        for i in range(n):
            spread = (0.9 if down else 0.62)
            a = ang + (i - (n - 1) / 2) * spread + rng.uniform(-0.18, 0.18)
            if down:
                a = max(min(a, math.pi - 0.1), 0.1)
            branch(ex, ey, a, length * rng.uniform(0.68, 0.8), w2, depth - 1, down)

    branch(gx, gy, -math.pi / 2, 250, 40, 9)
    rng.seed(4)
    for a in (0.55, 1.25, 1.9, 2.6):
        branch(gx + 30 * math.cos(a), gy, a, 120, 18, 6, down=True)
    p.centerline(gx, 140, gx, 1700)
    # bark: trunk tint and furrows
    p.path(f"M{gx-40},{gy} Q{gx-34},{gy-130} {gx-28},{gy-250} L{gx+28},{gy-250} Q{gx+34},{gy-130} {gx+40},{gy} Z", "t2")
    for k in range(9):
        x = gx - 32 + k * 8
        pts_ = [(x + 3 * math.sin(j * 0.7 + k), gy - j * 12) for j in range(21)]
        p.poly(pts_, "d")

    # rings detail
    rx, ry = 2300, 520
    p.detail_circle(rx, ry, 280, "SECTION A-A")
    rng2 = random.Random(8)
    phase = [rng2.uniform(0, 6.28) for _ in range(4)]
    for k in range(1, 23):
        r = k * 10.5
        pts_ = []
        for i in range(121):
            a = i / 120 * 2 * math.pi
            rr = r * (1 + 0.04 * math.sin(3 * a + phase[0]) + 0.025 * math.sin(5 * a + phase[1])) + (k * 0.5) * math.cos(a)
            pts_.append((rx + 4 * k * 0.3 + rr * math.cos(a), ry + rr * math.sin(a)))
        if k in (22, 19, 8):
            p.poly(pts_, "t1", closed=True)
        p.poly(pts_, "mb" if k == 22 else ("m" if k == 1 else ("s" if k % 5 == 0 else "f")))
    for k in range(10):
        a = k * 2 * math.pi / 10 + 0.2
        p.line(rx + 20 * math.cos(a), ry + 20 * math.sin(a), rx + 230 * math.cos(a), ry + 230 * math.sin(a), "f")
    p.line(gx - 120, gy - 160, gx + 120, gy - 160, "a")
    p.text(gx + 130, gy - 154, "A", "tlb")

    # oak leaf
    lx, ly = 420, 520
    lobes = 6
    pts_ = []
    for i in range(0, 201):
        t = i / 200
        y = ly + 300 - 600 * t
        w = 150 * math.sin(math.pi * t) ** 0.7 * (0.7 + 0.3 * abs(math.sin(lobes * math.pi * t)))
        pts_.append((lx + w, y))
    p.poly(pts_ + [(lx - x + lx, y) for x, y in reversed(pts_)], "tb")
    p.line(lx, ly + 380, lx, ly - 300, "m")
    for k in range(1, lobes):
        t = (k - 0.5) / lobes
        y = ly + 300 - 600 * t
        for s in (1, -1):
            p.path(f"M{lx},{y+30:.1f} Q{lx+s*60},{y:.1f} {lx+s*120*math.sin(math.pi*t)**0.7:.1f},{y-20:.1f}", "s")
    p.text(lx, ly - 360, "FIG. 2  LEAF", "tlb", "middle")

    p.label(gx + 30, gy - 300, 1700, 1040, "TRUNK", 1)
    p.label(gx - 380, 560, 640, 1040, "CROWN", 2, "end")
    p.label(gx + 150, gy + 120, 1860, 1460, "ROOT PLATE", 3)
    p.label(rx - 60, ry + 40, 2500, 960, "LATEWOOD RING", 4)
    p.label(lx + 100, ly - 40, 760, 760, "SINUATE LOBE", 5)
    p.dim(gx + 600, gy, gx + 600, 220, 120, "H 24 m")
    p.frame(9, "OAK", "Quercus robur", "ELEVATION + ROOTS", "1:150",
            ("Root spread ~ crown spread", "Rings: 1 per year"))
    return p
