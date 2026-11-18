import sys; sys.path.insert(0, "/home/claude/shorts")
from lib import *
D = "/home/claude/shorts/v1"
LINES = ["How can one little lamp warn ships thirty kilometers away?",
         "A normal bulb spreads its light everywhere, so it fades fast.",
         "So lighthouses use a Fresnel lens: rings of glass that bend all that light into one strong beam.",
         "Then the lens turns, and the beam sweeps across the whole sea.",
         "Every lighthouse flashes its own pattern, so sailors know exactly which one they're seeing.",
         "One lamp. One lens. Thousands of ships home safe."]
tl = Timeline(D)
CO, COD, CR, CRD, BK, GR, WH = "#E85D5D", "#D44A4A", "#F5F0E8", "#E8E0D4", "#1A1A1A", "#6B6B6B", "#FFFFFF"
NIGHT = "#141821"
NO = Ink()
CAP = dict(font="bebas-neue-400", size=112, col=CR, hi=CO, upper=True, plate=BK, plate_alpha=0.92, y=1500, track=0.04)
CAP_L = dict(CAP, col=BK, plate=CR)

def hatch(f, x0, y0, x1, y1, col, gap=26, w=6):
    sub = f[y0:y1, x0:x1]
    for k in range(-(y1 - y0), x1 - x0, gap):
        cv2.line(sub, (k, y1 - y0), (k + (y1 - y0), 0), bgr(col), w, cv2.LINE_AA)

def chrome(f, num, label, dark=True):
    c = BK if dark is False else CR
    text(f, num, 70, 80, "bebas-neue-400", 64, CO if dark is not None else CR, track=0.06)
    text(f, label.upper(), 150, 98, "inter-600", 30, c, track=0.12)

def lighthouse(f, x, y, s, t, beam=True, beam_ang=None, face_on=True):
    """tower base at (x,y), s scale (1 = ~520px tall)"""
    k = s
    # rock
    NO.ellipse(f, x, y + 10 * k, 200 * k, 50 * k, "#2a2f3a")
    # tower: trapezoid with coral/cream stripes
    top_w, bot_w, hgt = 70 * k, 120 * k, 420 * k
    for i in range(6):
        y0 = y - hgt * i / 6; y1 = y - hgt * (i + 1) / 6
        w0 = lerp(bot_w, top_w, i / 6); w1 = lerp(bot_w, top_w, (i + 1) / 6)
        NO.poly(f, [(x - w0, y0), (x + w0, y0), (x + w1, y1), (x - w1, y1)], CO if i % 2 == 0 else CR)
    # gallery + lamp room
    gy = y - hgt
    NO.rect(f, x - 95 * k, gy - 18 * k, x + 95 * k, gy, BK)
    NO.rect(f, x - 60 * k, gy - 110 * k, x + 60 * k, gy - 18 * k, "#2b2b2b")
    glow = 0.75 + 0.25 * math.sin(t * 6)
    NO.rect(f, x - 48 * k, gy - 100 * k, x + 48 * k, gy - 26 * k, "#FFE9A8" if glow > 0.6 else "#FFD36B")
    NO.poly(f, [(x - 75 * k, gy - 110 * k), (x + 75 * k, gy - 110 * k), (x, gy - 175 * k)], CO)
    lamp = (int(x), int(gy - 63 * k))
    if face_on:
        face(f, x, y - hgt * 0.45, 1.3 * k, blink=blink_at(t), mouth="smile")
    return lamp

def beam(f, lamp, ang, length, width_deg=9, col=(255, 236, 170), a=0.55):
    ov = f.copy()
    for sgn in (0,):
        a0 = math.radians(ang - width_deg); a1 = math.radians(ang + width_deg)
        pts = [lamp, (lamp[0] + math.cos(a0) * length, lamp[1] + math.sin(a0) * length), (lamp[0] + math.cos(a1) * length, lamp[1] + math.sin(a1) * length)]
        cv2.fillPoly(ov, [np.array(pts, np.int32)], (col[2], col[1], col[0]), cv2.LINE_AA)
    cv2.addWeighted(ov, a, f, 1 - a, 0, f)

def sea(f, y, t, col="#1f3550", col2="#2c4a6e"):
    cv2.rectangle(f, (0, int(y)), (W, H), bgr(col), -1)
    for r in range(6):
        yy = int(y + 40 + r * 90)
        pts = [(x, int(yy + math.sin(x / 70 + t * 2 + r) * 10)) for x in range(0, W + 20, 20)]
        cv2.polylines(f, [np.array(pts)], False, bgr(col2), 6, cv2.LINE_AA)

def ship(f, x, y, s, t, col=CR, lit=0.0):
    bob = math.sin(t * 2.5) * 6 * s
    y = y + bob
    NO.poly(f, [(x - 90 * s, y), (x + 90 * s, y), (x + 65 * s, y + 40 * s), (x - 65 * s, y + 40 * s)], CO)
    NO.rect(f, x - 40 * s, y - 45 * s, x + 30 * s, y, col)
    NO.rect(f, x - 5 * s, y - 85 * s, x + 12 * s, y - 45 * s, BK)
    for wx in (-25, 0):
        NO.rect(f, x + (wx - 6) * s, y - 32 * s, x + (wx + 8) * s, y - 18 * s, "#FFE9A8" if lit > 0.5 else "#3a4660")

STARS = np.random.default_rng(4).uniform(0, 1, (120, 3))
def stars(f, t, ymax=900):
    for x, y, p in STARS:
        b = int(150 + 90 * math.sin(t * 2 + p * 9))
        cv2.circle(f, (int(x * W), int(y * ymax)), 2, (b, b, b), -1, cv2.LINE_AA)

def frame(t):
    i, lt, dur = tl.which(t)
    f = np.zeros((H, W, 3), np.uint8)
    if i == 0:
        f[:] = bgr(NIGHT); stars(f, t)
        text(f, "30", -20, 260, "bebas-neue-400", 760, "#232a38", lt=9)
        sea(f, 1200, t)
        lamp = lighthouse(f, 330, 1220, 1.15, t)
        ang = -20 + 25 * math.sin(lt * 1.3)
        beam(f, lamp, ang, 1400, 7)
        ship(f, 880, 1180, 0.55, t, lit=1 if abs(ang + 8) < 10 else 0)
        text(f, "HOW DOES ONE LAMP", 70, 1420, "bebas-neue-400", 120, CR, lt, 0.0, track=0.03)
        text(f, "REACH 30 KM?", 70, 1550, "bebas-neue-400", 190, CO, lt, 0.2, track=0.03)
        chrome(f, "01", "lighthouse")
    elif i == 1:
        f[:] = bgr(CR); hatch(f, 0, 1700, W, H, CRD)
        cx, cy = 540, 820
        fade = eio(lt / dur)
        for k in range(24):
            a = k / 24 * 2 * math.pi + lt * 0.2
            L = 160 + 520 * ease(lt / 1.2)
            for seg in range(6):
                r0 = 150 + L * seg / 6; r1 = 150 + L * (seg + 1) / 6
                al = (1 - seg / 6) * (1 - 0.7 * fade)
                c = tuple(int(lerp(hexc(CR)[j], hexc("#F2B544")[j], al)) for j in range(3))
                cv2.line(f, (int(cx + math.cos(a) * r0), int(cy + math.sin(a) * r0)), (int(cx + math.cos(a) * r1), int(cy + math.sin(a) * r1)), bgr(c), 10, cv2.LINE_AA)
        # bulb character
        NO.circle(f, cx, cy, 130, "#FFE08A")
        NO.rect(f, cx - 55, cy + 110, cx + 55, cy + 200, GR, 10)
        for yy in (135, 160, 185): cv2.line(f, (cx - 55, cy + yy), (cx + 55, cy + yy), bgr(BK), 4)
        face(f, cx, cy - 10, 2.2, blink=blink_at(t, 1), mouth="o" if lt > 2.0 else "smile")
        text(f, "EVERYWHERE", 70, 240, "bebas-neue-400", 190, BK, lt, track=0.02)
        text(f, "= WEAK", 70, 420, "bebas-neue-400", 150, CO, lt, 1.6)
        chrome(f, "02", "plain bulb", dark=False)
    elif i == 2:
        f[:] = bgr(CO); hatch(f, 0, 0, W, 60, COD); hatch(f, 0, H - 60, W, H, COD)
        cx, cy = 300, 860
        NO.circle(f, cx, cy, 55, "#FFE08A"); face(f, cx, cy - 6, 1.0, mouth="smile", blink=blink_at(t))
        lx = 560
        # fresnel lens: stacked prism teeth
        p = ease(lt / 0.8)
        for k in range(-5, 6):
            yy = cy + k * 70
            d = abs(k) * 9
            NO.poly(f, [(lx - 20, yy - 33), (lx + 18 + d * 0.0, yy - 33), (lx + 30 + d, yy + (33 if k > 0 else -33) * 0 ), (lx - 20, yy + 33)], "#BFE6F2")
            cv2.line(f, (lx - 20, yy - 33), (lx - 20, yy + 33), bgr(BK), 3)
        NO.rect(f, lx - 26, cy - 400, lx - 16, cy + 400, BK)
        # rays
        rp = ease((lt - 0.6) / 1.5)
        for k in range(-5, 6):
            yy = cy + k * 70
            cv2.line(f, (cx, cy), (int(lerp(cx, lx, rp)), int(lerp(cy, yy, rp))), bgr("#FFF2B0"), 5, cv2.LINE_AA)
            if rp >= 1:
                q = ease((lt - 2.1) / 1.2)
                cv2.line(f, (lx + 30, yy), (int(lx + 30 + 500 * q), yy), bgr("#FFF2B0"), 9, cv2.LINE_AA)
        text(f, "FRESNEL", 70, 200, "bebas-neue-400", 230, CR, lt, track=0.02)
        text(f, "LENS", 70, 410, "bebas-neue-400", 230, BK, lt, 0.15)
        if lt > 3.3: text(f, "ONE STRONG BEAM", 600, 1290, "bebas-neue-400", 80, CR, lt, 3.3, anchor="ct")
        chrome(f, "03", "rings of glass", dark=None)
    elif i == 3:
        f[:] = bgr("#1f3550")
        for r in range(14):
            yy = 120 + r * 130
            pts = [(x, int(yy + math.sin(x / 60 + t * 2 + r) * 8)) for x in range(0, W + 20, 20)]
            cv2.polylines(f, [np.array(pts)], False, bgr("#2c4a6e"), 5, cv2.LINE_AA)
        cx, cy = 540, 980
        ang = lt * 95 - 90
        beam(f, (cx, cy), ang, 1500, 8, a=0.6)
        # ships around, lit when beam passes
        for k, (sx, sy) in enumerate([(210, 520), (860, 640), (820, 1420), (230, 1350)]):
            sa = math.degrees(math.atan2(sy - cy, sx - cx))
            diff = (ang - sa + 540) % 360 - 180
            ship(f, sx, sy, 0.6, t + k, lit=1 if abs(diff) < 10 else 0)
        NO.circle(f, cx, cy, 120, "#2a2f3a"); NO.circle(f, cx, cy, 80, CO); NO.circle(f, cx, cy, 40, "#FFE08A")
        text(f, "SWEEP", 70, 150, "bebas-neue-400", 260, CR, lt)
        chrome(f, "04", "top view")
    elif i == 4:
        f[:] = bgr(CR)
        pats = [("FL 5S", lambda u: (u % 5) < 0.6), ("FL(2) 10S", lambda u: (u % 10) < 0.5 or 1.2 < (u % 10) < 1.7), ("OC 4S", lambda u: (u % 4) < 3.0)]
        for k, (lab, fn) in enumerate(pats):
            x = 200 + k * 340; y = 1150
            on = fn(lt * 2.2 + k)
            lamp = lighthouse(f, x, y, 0.55, t + k, face_on=False)
            if on:
                cv2.circle(f, lamp, 110, bgr("#FFE08A"), -1, cv2.LINE_AA)
                cv2.circle(f, lamp, 60, bgr("#FFF6D0"), -1, cv2.LINE_AA)
            p = ease((lt - 0.4 - k * 0.3) / 0.4)
            NO.rect(f, x - 130, y + 50, x + 130, y + 130, BK if True else CO)
            paste(f, text_img(lab, "bebas-neue-400", 66, CR, 0.04), x, y + 62, p, "ct")
        text(f, "EACH ONE HAS", 70, 230, "bebas-neue-400", 160, BK, lt)
        text(f, "ITS OWN CODE", 70, 390, "bebas-neue-400", 160, CO, lt, 0.2)
        chrome(f, "05", "light patterns", dark=False)
    else:
        f[:] = bgr(NIGHT); stars(f, t)
        sea(f, 1150, t)
        lamp = lighthouse(f, 240, 1170, 0.9, t)
        beam(f, lamp, -10 + 12 * math.sin(lt), 1300, 7)
        ship(f, 980 - 380 * eio(lt / dur), 1130, 0.7, t, lit=1)
        text(f, "ONE LAMP.", 70, 230, "bebas-neue-400", 200, CR, lt)
        text(f, "ONE LENS.", 70, 420, "bebas-neue-400", 200, CO, lt, 0.9)
        if lt > dur - 1.9:
            hatch(f, 0, 1700, W, 1780, CO, 30, 8)
            text(f, "FOLLOW FOR MORE", 540, 1795, "bebas-neue-400", 90, CR, lt, dur - 1.9, anchor="ct")
        chrome(f, "06", "safe home")
    st = CAP_L if i in (1, 4) else CAP
    captions(f, t, tl, LINES, st)
    if lt < 0.1 and i > 0: f[:] = np.clip(f.astype(np.int16) + int(80 * (1 - lt / 0.1)), 0, 255).astype(np.uint8)
    return f

run(D, tl, frame, "lighthouse_coral", "bright", 104, [(0.1, "boom"), (tl.starts[2] + 2.0, "ding"), (tl.starts[5], "ding")])
