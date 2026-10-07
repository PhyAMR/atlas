#!/usr/bin/env python3
"""Atlas screensaver: a murmuration of starlings in thin braille strokes.

Boids (separation, alignment, cohesion) follow a slowly wandering focus, a
few lone birds glide across on their own. Each bird is a small flapping "v"
drawn with Bresenham lines into a braille dot canvas (2x4 dots per cell), so
the strokes stay one dot thin. Colors come from the current Omarchy theme.

Exits on any key, or when the window loses focus (Omarchy's convention).
"""

import math
import os
import random
import select
import shutil
import signal
import subprocess
import sys
import termios
import time
import tty

FPS = 30
FLOCK = 260
LONERS = 5
STATE = os.path.expanduser("~/.local/state/omarchy/current/theme/colors.toml")


# -- theme ---------------------------------------------------------------------
def theme_colors():
    vals = {}
    try:
        for line in open(STATE):
            if "=" in line and '"#' in line:
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip().strip('"')
    except OSError:
        pass

    def rgb(key, fallback):
        h = vals.get(key, fallback).lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    bg = rgb("background", "#101315")
    fg = rgb("foreground", "#cacccc")
    mix = lambda a, b, t: tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
    # Depth tiers: far birds sink toward the background.
    return bg, [mix(bg, fg, t) for t in (0.32, 0.55, 0.8, 1.0)]


# -- terminal ------------------------------------------------------------------
def focused():
    try:
        out = subprocess.run(["hyprctl", "activewindow", "-j"], capture_output=True, text=True, timeout=1).stdout
        return '"org.omarchy.screensaver"' in out
    except Exception:
        return True


def set_cursor_invisible(on):
    val = "true" if on else "false"
    r = subprocess.run(["hyprctl", "eval", "hl.config({ cursor = { invisible = %s } })" % val], capture_output=True, text=True)
    if r.returncode != 0 or "error" in (r.stdout + r.stderr).lower():
        subprocess.run(["hyprctl", "keyword", "cursor:invisible", val], capture_output=True)


BRAILLE = [[0x01, 0x08], [0x02, 0x10], [0x04, 0x20], [0x40, 0x80]]


class Canvas:
    def __init__(self, cols, rows):
        self.cols, self.rows = cols, rows
        self.w, self.h = cols * 2, rows * 4
        self.clear()

    def clear(self):
        self.bits = bytearray(self.cols * self.rows)
        self.tier = bytearray(self.cols * self.rows)

    def dot(self, x, y, tier):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y >> 2) * self.cols + (x >> 1)
            self.bits[i] |= BRAILLE[y & 3][x & 1]
            if tier > self.tier[i]:
                self.tier[i] = tier

    def line(self, x0, y0, x1, y1, tier):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.dot(x0, y0, tier)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def render(self, palette):
        out = ["\033[H"]
        last = -1
        cols = self.cols
        for r in range(self.rows):
            row = []
            base = r * cols
            for c in range(cols):
                b = self.bits[base + c]
                if b:
                    t = self.tier[base + c]
                    if t != last:
                        row.append("\033[38;2;%d;%d;%dm" % palette[t - 1])
                        last = t
                    row.append(chr(0x2800 + b))
                else:
                    row.append(" ")
            out.append("".join(row))
            if r < self.rows - 1:
                out.append("\r\n")
        return "".join(out)


# -- birds -----------------------------------------------------------------------
class Bird:
    __slots__ = ("x", "y", "vx", "vy", "phase", "rate", "depth", "span")

    def __init__(self, x, y, depth):
        a = random.uniform(0, math.tau)
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(a) * 2, math.sin(a) * 2
        self.phase = random.uniform(0, math.tau)
        self.rate = random.uniform(0.35, 0.55)
        self.depth = depth  # 1 far .. 4 near
        self.span = 1.8 + depth * 0.7


def draw_bird(cv, b, glide=False):
    """Gull silhouette: two bent wings either side of the body, as birds read
    against the sky whatever their heading. Tilted slightly with the climb."""
    sp = math.hypot(b.vx, b.vy) or 1
    tilt = max(-0.5, min(0.5, math.atan2(b.vy, abs(b.vx) + 0.01) * 0.5)) * (1 if b.vx >= 0 else -1)
    ct, st = math.cos(tilt), math.sin(tilt)
    flap = 0.15 if glide else math.sin(b.phase)          # -1 down .. 1 up
    s = b.span
    pts = []
    for side in (-1, 1):
        # body -> elbow -> wingtip, in the bird's frame (y up = negative)
        ex, ey = side * s * 0.45, -s * (0.18 + 0.22 * flap)
        tx, ty = side * s, -s * (0.05 + 0.45 * flap) + s * 0.12
        pts.append(((ex, ey), (tx, ty)))
    bx, by = b.x, b.y
    rot = lambda x, y: (bx + x * ct - y * st, by + x * st + y * ct)
    for (ex, ey), (tx, ty) in pts:
        e = rot(ex, ey)
        t = rot(tx, ty)
        cv.line(bx, by, *e, b.depth)
        cv.line(*e, *t, b.depth)


def main():
    cols, rows = shutil.get_terminal_size((160, 48))
    cv = Canvas(cols, rows)
    W, H = cv.w, cv.h
    bg, palette = theme_colors()

    flock = [Bird(W * 0.5 + random.gauss(0, W * 0.08), H * 0.45 + random.gauss(0, H * 0.08),
                  random.choice((1, 2, 2, 3, 3, 4))) for _ in range(FLOCK)]
    loners = []

    def spawn_loner():
        d = random.choice((2, 3, 4))
        left = random.random() < 0.5
        b = Bird(-20 if left else W + 20, random.uniform(H * 0.1, H * 0.7), d)
        b.vx, b.vy = (1 if left else -1) * random.uniform(1.0, 1.6), random.uniform(-0.15, 0.15)
        b.span = 5 + d * 1.8
        b.rate = random.uniform(0.18, 0.28)
        return b

    for _ in range(LONERS):
        lb = spawn_loner()
        lb.x = random.uniform(0, W)
        loners.append(lb)

    cell = 30.0
    t0 = time.monotonic()
    last_focus = time.monotonic()
    out = sys.stdout

    while True:
        frame_start = time.monotonic()
        t = frame_start - t0

        # Wandering focus the flock chases: slow Lissajous over the sky.
        fx = W * (0.5 + 0.32 * math.sin(t * 0.071) + 0.08 * math.sin(t * 0.23))
        fy = H * (0.42 + 0.22 * math.sin(t * 0.053 + 1.3) + 0.06 * math.cos(t * 0.19))

        grid = {}
        for b in flock:
            grid.setdefault((int(b.x // cell), int(b.y // cell)), []).append(b)

        for b in flock:
            gx, gy = int(b.x // cell), int(b.y // cell)
            ax = ay = cx = cy = sx = sy = 0.0
            n = 0
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    for o in grid.get((gx + i, gy + j), ()):
                        if o is b:
                            continue
                        dx, dy = o.x - b.x, o.y - b.y
                        d2 = dx * dx + dy * dy
                        if d2 < cell * cell:
                            n += 1
                            ax += o.vx; ay += o.vy
                            cx += o.x; cy += o.y
                            if d2 < 36:
                                inv = 1.0 / (d2 + 0.1)
                                sx -= dx * inv; sy -= dy * inv
            if n:
                b.vx += (ax / n - b.vx) * 0.06 + (cx / n - b.x) * 0.003 + sx * 0.7
                b.vy += (ay / n - b.vy) * 0.06 + (cy / n - b.y) * 0.003 + sy * 0.7
            b.vx += (fx - b.x) * 0.00035 - b.vx * 0.004
            b.vy += (fy - b.y) * 0.00045 - b.vy * 0.004
            # soft edges keep the murmuration on screen
            m = 0.08
            if b.x < W * m: b.vx += 0.08
            elif b.x > W * (1 - m): b.vx -= 0.08
            if b.y < H * m: b.vy += 0.08
            elif b.y > H * (1 - m): b.vy -= 0.08
            b.vx += random.uniform(-0.05, 0.05)
            b.vy += random.uniform(-0.05, 0.05)
            sp = math.hypot(b.vx, b.vy)
            lo, hi = 0.7, 1.5
            if sp > hi:
                b.vx, b.vy = b.vx / sp * hi, b.vy / sp * hi
            elif sp < lo and sp > 0:
                b.vx, b.vy = b.vx / sp * lo, b.vy / sp * lo
            b.x += b.vx
            b.y += b.vy
            b.phase += b.rate

        for k, b in enumerate(loners):
            b.x += b.vx * 0.6
            b.y += b.vy * 0.6 + math.sin(t * 0.4 + k) * 0.05
            b.phase += b.rate
            if b.x < -40 or b.x > W + 40:
                loners[k] = spawn_loner()

        cv.clear()
        for b in sorted(flock, key=lambda q: q.depth):
            draw_bird(cv, b)
        for b in loners:
            draw_bird(cv, b, glide=math.sin(b.phase * 0.25) > 0.6)
        if os.environ.get("ATLAS_BIRDS_DEBUG") and int(t * FPS) % 30 == 0:
            mx = sum(q.x for q in flock) / len(flock); my = sum(q.y for q in flock) / len(flock)
            with open("/tmp/atlas-birds.log", "a") as fh:
                fh.write(f"t={t:.1f} W={W} H={H} cols={cols} rows={rows} centroid=({mx:.0f},{my:.0f}) focus=({fx:.0f},{fy:.0f})\n")
        out.write(cv.render(palette))
        out.flush()

        # Input / focus checks.
        if select.select([sys.stdin], [], [], 0)[0]:
            return
        if frame_start - last_focus > 1.0:
            last_focus = frame_start
            if not focused():
                return
        size = shutil.get_terminal_size((cols, rows))
        if size != (cols, rows):
            cols, rows = size
            cv = Canvas(cols, rows)
            W, H = cv.w, cv.h

        delay = 1.0 / FPS - (time.monotonic() - frame_start)
        if delay > 0:
            time.sleep(delay)


def run():
    bg, _ = theme_colors()
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd) if os.isatty(fd) else None

    def restore(*_):
        if old:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        sys.stdout.write("\033[0m\033[?25h\033[?1049l")
        sys.stdout.flush()
        set_cursor_invisible(False)
        sys.exit(0)

    for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(s, restore)
    if old:
        tty.setcbreak(fd)
    # Alternate screen, hidden cursor, theme background.
    sys.stdout.write("\033[?1049h\033[?25l\033]11;#%02x%02x%02x\007\033[2J" % bg)
    sys.stdout.flush()
    set_cursor_invisible(True)
    try:
        main()
    finally:
        restore()


if __name__ == "__main__":
    run()
