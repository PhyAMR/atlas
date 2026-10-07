import math
from atlas import Plate, gear_points, tangents


def engine():
    p = Plate(7)
    # ---- block -----------------------------------------------------------
    bx0, bx1 = 760, 1880
    p.path(f"M{bx0},640 L{bx1},640 L{bx1+30},700 L{bx1+30},1130 L{bx1},1170 L{bx0},1170 L{bx0-40},1120 L{bx0-40},700 Z", "tb")
    p.rect(bx0 - 10, 600, bx1 - bx0 + 20, 40, "m")              # head gasket line / deck
    p.rect(bx0 + 10, 480, bx1 - bx0 - 20, 120, "tb", r=10)       # cylinder head
    p.rect(bx0 + 10, 480, bx1 - bx0 - 20, 120, "t1", r=10)
    p.path(f"M{bx0+40},480 Q{bx0+60},400 {bx0+140},396 L{bx1-140},396 Q{bx1-60},400 {bx1-40},480 Z", "tb")  # valve cover
    for k in range(6):
        y = 404 + k * 12
        p.line(bx0 + 120 + k * 4, y, bx1 - 120 - k * 4, y, "d")
    for i in range(12):
        x = bx0 + 90 + i * (bx1 - bx0 - 180) / 11
        p.bolt(x, 452, 9)
        p.line(x - 30, 420, x + 30, 420, "f")
    # oil pan
    p.path(f"M{bx0+20},1170 L{bx0+60},1330 Q{bx0+70},1360 {bx0+110},1360 L{bx1-160},1360 Q{bx1-120},1360 {bx1-110},1330 L{bx1-60},1170 Z", "tb")
    p.path(f"M{bx0+60},1230 L{bx0+90},1330 L{bx1-140},1330 L{bx1-100},1230 Z", "hatch")
    p.line(bx0 + 40, 1200, bx1 - 80, 1200, "s")
    for i in range(10):
        p.bolt(bx0 + 70 + i * (bx1 - bx0 - 160) / 9, 1186, 7)
    p.circle(bx0 + 160, 1362, 14, "m")  # drain plug

    # ---- cylinders, pistons, rods, crank (hidden) ------------------------
    crank_y = 1080
    phases = [0, math.pi, math.pi, 0]
    stroke = 110
    for i in range(4):
        cx = bx0 + 170 + i * 260
        p.rect(cx - 105, 640, 210, 380, "h")
        p.rect(cx - 112, 630, 224, 395, "f")
        ang = phases[i] + 0.6
        pin_x = cx + stroke / 2 * math.sin(ang)
        pin_y = crank_y + stroke / 2 * math.cos(ang) * -1
        rod = 260
        piston_y = pin_y - math.sqrt(rod ** 2 - (pin_x - cx) ** 2)
        p.rect(cx - 98, piston_y - 90, 196, 150, "s", r=6)
        for k in range(3):
            p.line(cx - 98, piston_y - 72 + k * 14, cx + 98, piston_y - 72 + k * 14, "s")
        p.circle(cx, piston_y, 22, "s")
        p.line(cx - 14, piston_y + 16, pin_x - 26, pin_y, "s")
        p.line(cx + 14, piston_y + 16, pin_x + 26, pin_y, "s")
        p.circle(pin_x, pin_y, 34, "s")
        p.circle(pin_x, pin_y, 18, "f")
        # crank web
        p.path(f"M{cx-60},{crank_y-30} Q{pin_x},{pin_y-90} {cx+60},{crank_y-30} L{cx+60},{crank_y+30} Q{cx},{crank_y+110} {cx-60},{crank_y+30} Z", "h")
        # valves + springs
        for dx in (-50, 50):
            p.line(cx + dx, 520, cx + dx, 640, "s")
            p.path(f"M{cx+dx-24},646 L{cx+dx+24},646", "s")
            for k in range(6):
                y = 500 + k * 7
                p.line(cx + dx - 16, y, cx + dx + 16, y + 5, "f")
        # camshaft lobes
        for dx in (-50, 50):
            p.ellipse(cx + dx, 500, 26, 20, "h", rot=30 * i + dx)
        # injector
        p.rect(cx - 10, 340, 20, 200, "m", r=4)
        p.line(cx, 340, cx, 300, "m")
        p.circle(cx, 296, 7, "m")
    p.centerline(bx0 - 300, crank_y, bx1 + 380, crank_y)
    p.centerline(bx0 - 120, 500, bx1 + 260, 500)
    for i in range(5):
        p.circle(bx0 + 40 + i * 260, crank_y, 40, "h")
    # fuel rail
    p.path(f"M{bx0+170},296 C{bx0+300},260 {bx0+600},330 {bx0+950},296 S{bx1-60},270 {bx1+140},330", "m")
    p.path(f"M{bx0+170},306 C{bx0+300},270 {bx0+600},340 {bx0+950},306 S{bx1-60},280 {bx1+140},340", "s")

    # ---- flywheel + bell housing (rear) ---------------------------------
    fx, fy = 560, 1000
    p.circle(fx, fy, 330, "tb")
    p.add(f'<path class="xhatch" fill-rule="evenodd" d="M{fx-330},{fy} a330,330 0 1,0 660,0 a330,330 0 1,0 -660,0 M{fx-282},{fy} a282,282 0 1,0 564,0 a282,282 0 1,0 -564,0"/>')
    p.circle(fx, fy, 318, "s")
    p.poly(gear_points(fx, fy, 270, 96, 9), "s", closed=True)
    p.circle(fx, fy, 120, "h")
    p.circle(fx, fy, 60, "h")
    for k in range(8):
        a = k * math.pi / 4
        p.bolt(fx + 300 * math.cos(a), fy + 300 * math.sin(a), 10)
        p.circle(fx + 90 * math.cos(a + 0.2), fy + 90 * math.sin(a + 0.2), 10, "h")
    p.centermark(fx, fy, 40)

    # ---- front: timing + accessory drive --------------------------------
    crank_p = (2020, crank_y, 105)
    cam_p = (2010, 500, 92)
    alt = (2260, 760, 78)
    pump = (2080, 820, 58)
    idler = (2190, 1010, 40)
    for c in (crank_p, cam_p, alt, pump, idler):
        p.circle(*c, "m")
        p.circle(c[0], c[1], c[2] * 0.82, "s")
        p.circle(c[0], c[1], c[2] * 0.25, "s")
        p.centermark(c[0], c[1], c[2] * 0.4)
    p.poly(gear_points(cam_p[0], cam_p[1], 96, 40, 8), "s", closed=True)
    p.poly(gear_points(crank_p[0], crank_p[1], 110, 44, 8), "s", closed=True)
    belt = [((cam_p[0], cam_p[1], 104), (alt[0], alt[1], alt[2])),
            ((alt[0], alt[1], alt[2]), (idler[0], idler[1], idler[2])),
            ((idler[0], idler[1], idler[2]), (crank_p[0], crank_p[1], 118))]
    for c1, c2 in belt:
        a, b = tangents(c1, c2)
        p.line(*a[0], *a[1], "m")
    p.line(cam_p[0] - 104, cam_p[1], crank_p[0] - 118, crank_p[1], "m")
    # alternator fins
    for k in range(18):
        a = k * math.pi / 9
        p.line(alt[0] + 30 * math.cos(a), alt[1] + 30 * math.sin(a),
               alt[0] + 62 * math.cos(a + 0.25), alt[1] + 62 * math.sin(a + 0.25), "f")
    # fan, seen edge-on as overlapping blades
    fx2, fy2 = 2380, 900
    p.line(fx2, fy2 - 340, fx2, fy2 + 340, "cl")
    for k in range(7):
        a = k * 2 * math.pi / 7 + 0.3
        ex, ey = fx2 + 60 * math.cos(a), fy2 + 330 * math.sin(a)
        p.path(f"M{fx2},{fy2} Q{fx2+70*math.cos(a+0.5):.1f},{fy2+260*math.sin(a+0.5):.1f} {ex:.1f},{ey:.1f} Q{fx2-20*math.cos(a):.1f},{fy2+200*math.sin(a-0.3):.1f} {fx2},{fy2}", "s")
    p.ellipse(fx2, fy2, 26, 70, "m")

    # ---- turbocharger + manifold ----------------------------------------
    tx, ty = 980, 250
    b = 0.16
    pts_ = []
    for i in range(240):
        th = i / 240 * 2 * math.pi * 1.15
        r = 70 * math.exp(b * th)
        pts_.append((tx + r * math.cos(th), ty + r * math.sin(th) * 0.95))
    p.poly(pts_, "tb")
    p.circle(tx, ty, 60, "m")
    p.circle(tx, ty, 34, "s")
    for k in range(11):
        a = k * 2 * math.pi / 11
        p.path(f"M{tx+12*math.cos(a):.1f},{ty+12*math.sin(a):.1f} Q{tx+40*math.cos(a+0.5):.1f},{ty+40*math.sin(a+0.5):.1f} {tx+56*math.cos(a+0.2):.1f},{ty+56*math.sin(a+0.2):.1f}", "f")
    p.rect(tx + 120, ty - 40, 260, 80, "tb", r=30)  # center housing
    for k in range(9):
        p.line(tx + 150 + k * 25, ty - 36, tx + 150 + k * 25, ty + 36, "d")
    p.circle(tx + 470, ty, 95, "tb")                # compressor
    p.circle(tx + 470, ty, 70, "s")
    p.circle(tx + 470, ty, 20, "s")
    p.centerline(tx - 220, ty, tx + 620, ty)
    for i in range(4):
        x0 = 930 + i * 260
        p.path(f"M{x0},600 C{x0},420 {tx+40+i*8},{ty+260} {tx+20+i*10},{ty+120}", "m")
        p.path(f"M{x0+60},600 C{x0+60},440 {tx+90+i*8},{ty+250} {tx+60+i*10},{ty+125}", "s")
    # intercooler pipe from compressor to intake
    p.path(f"M{tx+560},{ty+40} C{tx+800},{ty+80} {tx+700},{ty+200} {tx+980},{ty+180} S{1880},{360} {1920},{560}", "m")
    p.path(f"M{tx+560},{ty+90} C{tx+780},{ty+130} {tx+690},{ty+250} {tx+980},{ty+230} S{1830},{380} {1866},{560}", "s")

    # ---- oil filter + starter -------------------------------------------
    ox, oy = 1660, 1290
    p.ellipse(ox, oy - 120, 70, 18, "m")
    p.line(ox - 70, oy - 120, ox - 70, oy + 40, "m")
    p.line(ox + 70, oy - 120, ox + 70, oy + 40, "m")
    p.ellipse(ox, oy + 40, 70, 18, "m")
    for k in range(9):
        p.line(ox - 70 + k * 17.5, oy - 100, ox - 70 + k * 17.5, oy + 26, "f")
    sx, sy = 930, 1260
    p.rect(sx - 150, sy - 55, 300, 110, "m", r=50)
    p.circle(sx - 150, sy, 55, "s")
    p.ellipse(sx + 150, sy, 22, 55, "s")
    for k in range(5):
        p.line(sx - 100 + k * 50, sy - 55, sx - 100 + k * 50, sy + 55, "f")

    # ---- extra detail: casting ribs, mounts, harness, hoses, downpipe -----
    for i in range(5):
        x = bx0 + 40 + i * 260
        p.line(x - 12, 660, x - 12, 1150, "d")
        p.line(x + 12, 660, x + 12, 1150, "d")
        p.path(f"M{x-12},1150 Q{x},1166 {x+12},1150", "d")
    p.path(f"M{bx0-40},1000 L{bx0-40},1120 L{bx0+20},1170 L{bx0+400},1170 L{bx0+400},1000 Z", "hatch")
    for (mx, my) in ((bx0 + 120, 1050), (bx1 - 80, 1050)):
        p.path(f"M{mx-70},{my} L{mx-70},{my+90} L{mx+70},{my+90} L{mx+70},{my} Q{mx},{my-40} {mx-70},{my} Z", "m")
        p.circle(mx, my + 30, 22, "s")
        p.ellipse(mx, my + 110, 60, 18, "s")
        for bxx in (mx - 46, mx + 46):
            p.bolt(bxx, my + 66, 8)
    harness = [(bx0 + 60, 380), (bx0 + 300, 370), (bx0 + 560, 384), (bx0 + 820, 366), (bx1 - 80, 382), (bx1 + 80, 430)]
    p.poly(harness, "s")
    p.poly([(x, y + 7) for x, y in harness], "s")
    for x, y in harness[1:-1]:
        p.rect(x - 9, y - 8, 18, 22, "m", r=3)
        p.line(x, y + 14, x, y + 44, "d")
    # coolant hose from pump to thermostat housing
    p.path("M2080,760 C2060,660 1960,640 1900,600", "m")
    p.path("M2104,764 C2090,640 1980,610 1910,574", "m")
    for k in range(7):
        t = k / 7
        p.line(2080 + 24 * t - 4, 760 - 160 * t, 2104 + 6 * t, 764 - 170 * t, "d")
    p.rect(1870, 548, 60, 70, "tb", r=8)
    # dipstick
    p.path(f"M{bx0+520},1170 C{bx0+500},900 {bx0+470},700 {bx0+470},540", "s")
    p.circle(bx0 + 470, 530, 14, "m")
    # exhaust downpipe with flex bellows
    p.path(f"M{tx-60},{ty+90} C{tx-180},{ty+160} {tx-260},{ty+300} {tx-280},{ty+520}", "m")
    p.path(f"M{tx-10},{ty+120} C{tx-130},{ty+190} {tx-200},{ty+320} {tx-220},{ty+520}", "m")
    for k in range(14):
        y = ty + 380 + k * 10
        p.line(tx - 276 + k * 0.4, y, tx - 222 + k * 0.4, y, "d")
    # heat shield over manifold
    p.path(f"M{bx0+120},330 Q{bx0+300},270 {bx0+560},300 L{bx0+560},360 Q{bx0+300},330 {bx0+120},390 Z", "hatch")
    p.path(f"M{bx0+120},330 Q{bx0+300},270 {bx0+560},300 L{bx0+560},360 Q{bx0+300},330 {bx0+120},390 Z", "s")
    # pulley groove detail
    for c in (crank_p, alt, pump):
        for k in range(1, 4):
            p.circle(c[0], c[1], c[2] * (0.82 - k * 0.12), "d")

    # ---- dimensions + labels --------------------------------------------
    p.dim(bx0 - 40, 1360, bx1 + 30, 1360, -110, "1 090")
    p.dim(bx1 + 30, 396, bx1 + 30, 1360, -560, "964")
    p.dim(bx0 + 170, 640, bx0 + 430, 640, 360, "BORE PITCH 130")
    p.label(tx - 60, ty - 70, 520, 160, "TURBOCHARGER", 1, "end")
    p.label(bx0 + 400, 520, 470, 520, "CYLINDER HEAD", 2, "end")
    p.label(bx0 + 690, 900, 1210, 1560, "PISTON + ROD", 3, "start")
    p.label(bx0 + 430, crank_y + 20, 940, 1600, "CRANKSHAFT", 4, "end")
    p.label(fx - 220, fy + 200, 330, 1450, "FLYWHEEL", 5, "end")
    p.label(alt[0] + 50, alt[1] - 50, 2500, 560, "ALTERNATOR", 6)
    p.label(cam_p[0] + 60, cam_p[1] - 70, 2300, 330, "TIMING DRIVE", 7)
    p.label(ox + 60, oy - 60, 1980, 1520, "OIL FILTER", 8)
    p.label(bx0 + 690, 296, 1500, 150, "COMMON RAIL", 9)
    p.frame(1, "DIESEL ENGINE", "inline four, turbocharged", "SIDE ELEVATION", "1:6",
            ("Hidden detail shown dashed", "Firing order 1-3-4-2", "All dimensions in mm"))
    return p
