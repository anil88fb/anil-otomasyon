import numpy as np, cv2, wave, sys, math, subprocess, os
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
D = os.path.dirname(os.path.abspath(__file__))
INK = (17, 17, 17); FIRE = (232, 93, 38); CREAM = (240, 236, 229); MUTED = (136, 136, 128)
def bgr(c): return (c[2], c[1], c[0])

LINES = [
 "What if you fell into a black hole?",
 "From far away, it glows. A ring of super hot gas, spinning around... nothing.",
 "Get closer, and gravity pulls your feet way harder than your head.",
 "You'd stretch like a noodle. Scientists really call it spaghettification!",
 "But your friends watching from far away? They'd see you slow down, turn red, and fade at the edge.",
 "And what's inside? Nobody knows. Not even light gets out.",
]
durs = []
for i in range(6):
    with wave.open(f"{D}/vo/l{i+1}.wav") as w: durs.append(w.getnframes() / w.getframerate())
GAP, START = 0.45, 0.25
starts = []; t = START
for d in durs: starts.append(t); t += d + GAP
TOTAL = t + 1.2
# scene boundaries: each scene from its line start to next line start
SC = [(0 if i == 0 else starts[i] - 0.15, (starts[i+1] - 0.15) if i < 5 else TOTAL) for i in range(6)]

FONT = {k: f"{D}/fonts/{v}" for k, v in dict(b9="Barlow900.ttf", b6="Barlow600.ttf", mono="Plex500.ttf").items()}
_fc = {}
def font(k, s):
    if (k, s) not in _fc: _fc[(k, s)] = ImageFont.truetype(FONT[k], s)
    return _fc[(k, s)]
_tc = {}
def text_img(s, k, size, col, track=-0.04):
    key = (s, k, size, col, track)
    if key in _tc: return _tc[key]
    f = font(k, size); trk = track * size
    wid = int(sum(f.getlength(c) + trk for c in s) + size)
    im = Image.new("RGBA", (max(wid, 4), int(size * 1.35)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 0
    for c in s:
        d.text((x, 0), c, font=f, fill=col + (255,)); x += f.getlength(c) + trk
    a = np.array(im); ys, xs = np.nonzero(a[..., 3])
    a = a[:, :max(xs.max() + 2, 1)] if len(xs) else a
    _tc[key] = a; return a

def paste(f, rgba, x, y, alpha=1.0, anchor="lt"):
    h, w = rgba.shape[:2]
    if anchor == "ct": x -= w // 2
    if anchor == "cc": x -= w // 2; y -= h // 2
    x, y = int(x), int(y)
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x0 >= x1 or y0 >= y1 or alpha <= 0: return
    src = rgba[y0 - y:y1 - y, x0 - x:x1 - x]
    a = (src[..., 3:4].astype(np.float32) / 255.0) * alpha
    reg = f[y0:y1, x0:x1].astype(np.float32)
    f[y0:y1, x0:x1] = (reg * (1 - a) + src[..., 2::-1].astype(np.float32) * a).astype(np.uint8)

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def eio(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)

# ---------- astronaut sprite (drawn at 2x, RGBA) ----------
def astronaut(wave_t=0.0, col_body=CREAM, tint=0.0):
    S = 520; im = np.zeros((S, S, 4), np.uint8)
    def C(c):
        c = np.array(c, float); r = np.array(FIRE, float) * 0.0 + np.array((200, 40, 30), float)
        c = c * (1 - tint) + r * tint; return (int(c[2]), int(c[1]), int(c[0]), 255)
    body = C(col_body); shade = C(tuple(int(v * 0.78) for v in col_body)); ink = (17, 17, 17, 255)
    cx = S // 2
    cv2.rectangle(im, (cx - 95, 215), (cx + 95, 350), shade, -1, cv2.LINE_AA)  # backpack
    # legs
    for s in (-1, 1):
        cv2.ellipse(im, (cx + s * 45, 400), (38, 70), 0, 0, 360, body, -1, cv2.LINE_AA)
        cv2.ellipse(im, (cx + s * 48, 462), (44, 26), 0, 0, 360, shade, -1, cv2.LINE_AA)
    # torso
    cv2.ellipse(im, (cx, 300), (100, 115), 0, 0, 360, body, -1, cv2.LINE_AA)
    cv2.rectangle(im, (cx - 42, 280), (cx + 42, 330), (38, 93, 232, 255), -1, cv2.LINE_AA)  # fire panel (BGR)
    cv2.circle(im, (cx - 20, 305), 8, (229, 236, 240, 255), -1, cv2.LINE_AA)
    cv2.circle(im, (cx + 14, 305), 8, ink, -1, cv2.LINE_AA)
    # arms
    ang = math.sin(wave_t * 6) * 25
    for s in (-1, 1):
        a = math.radians((-60 - ang) if s > 0 else 200)
        ex, ey = cx + s * 95, 260
        hx, hy = int(ex + math.cos(a) * 90 * (1 if s > 0 else 1)), int(ey + math.sin(a) * 90)
        if s < 0: hx, hy = cx - 150, 350
        cv2.line(im, (ex, ey), (hx, hy), body, 52, cv2.LINE_AA)
        cv2.circle(im, (hx, hy), 30, shade, -1, cv2.LINE_AA)
    # helmet
    cv2.circle(im, (cx, 150), 118, body, -1, cv2.LINE_AA)
    cv2.ellipse(im, (cx + 8, 155), (82, 66), 0, 0, 360, ink, -1, cv2.LINE_AA)
    cv2.ellipse(im, (cx + 40, 128), (22, 12), -30, 0, 360, (38, 93, 232, 255), -1, cv2.LINE_AA)
    cv2.ellipse(im, (cx - 20, 190), (14, 6), -10, 0, 360, (90, 90, 90, 255), -1, cv2.LINE_AA)
    # eyes inside visor (cute)
    for s in (-1, 1):
        cv2.ellipse(im, (cx + 8 + s * 30, 158), (13, 17), 0, 0, 360, (229, 236, 240, 255), -1, cv2.LINE_AA)
    rgba = im.copy(); rgba[..., :3] = im[..., 2::-1]  # to RGBA order for paste()
    return rgba

def place_sprite(f, spr, cx, cy, scale=1.0, sx=1.0, sy=1.0, rot=0.0, alpha=1.0):
    h, w = spr.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, 1.0)
    M[0, :2] *= scale * sx; M[1, :2] *= scale * sy
    # rebuild proper affine: scale then rotate about center
    a = math.radians(rot); ca, sa = math.cos(a), math.sin(a)
    A = np.array([[ca * scale * sx, sa * scale * sy], [-sa * scale * sx, ca * scale * sy]])
    t = np.array([cx, cy]) - A @ np.array([w / 2, h / 2])
    M = np.hstack([A, t[:, None]])
    out = cv2.warpAffine(spr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    paste(f, out, 0, 0, alpha)

# ---------- backgrounds ----------
rng = np.random.default_rng(7)
STARS = np.c_[rng.uniform(0, W, 420), rng.uniform(0, H, 420), rng.uniform(0.5, 2.6, 420), rng.uniform(0, 6.28, 420)]
def stars(f, t, drift=0.0, pull=None, k=0.0):
    for x, y, r, ph in STARS:
        x2 = (x + drift * t * r * 10) % W; y2 = y
        if pull is not None and k > 0:  # stars bend toward hole
            dx, dy = x2 - pull[0], y2 - pull[1]; d = math.hypot(dx, dy) + 1
            fac = 1 + k * 9000 / (d * d + 3000); x2 = pull[0] + dx * fac; y2 = pull[1] + dy * fac
        b = 0.55 + 0.45 * math.sin(t * 2.2 + ph)
        c = int(140 + 100 * b)
        cv2.circle(f, (int(x2), int(y2)), max(1, int(r)), (c - 8, c - 4, c), -1, cv2.LINE_AA)

PART = np.c_[rng.uniform(0, 6.283, 900), rng.uniform(0.78, 1.55, 900), rng.uniform(0.4, 1.0, 900)]
def black_hole(f, cx, cy, R, t, tilt=0.30, glow=1.0, spin=1.0):
    # glow layer
    g = np.zeros((H // 2, W // 2, 3), np.float32)
    cv2.ellipse(g, (int(cx / 2), int(cy / 2)), (int(R * 1.6), int(R * 1.6 * tilt + R * 0.35)), 0, 0, 360, (38 * 1.0, 93, 232), -1)
    cv2.circle(g, (int(cx / 2), int(cy / 2)), int(R * 0.62), (60, 140, 255), -1)
    g = cv2.GaussianBlur(g, (0, 0), R * 0.55 + 2) * 0.55 * glow
    g = cv2.resize(g, (W, H))
    ff = f.astype(np.float32) + g
    # back half of disk
    def ring(front):
        for a0, rr, br in PART:
            a = a0 + t * spin * (1.6 / rr ** 1.5)
            x = cx + math.cos(a) * R * rr * 1.9; y = cy + math.sin(a) * R * rr * 1.9 * tilt
            isfront = math.sin(a) > 0
            if isfront != front: continue
            dop = 0.55 + 0.45 * math.cos(a)  # doppler brightening on one side
            c = np.array([38, 93, 232]) * (0.5 + br * dop) + np.array([60, 120, 160]) * (br * dop * (1.6 - rr))
            c = np.clip(c, 0, 255)
            cv2.ellipse(ff, (int(x), int(y)), (int(5 + 6 * br), 2 + int(2 * br)), math.degrees(a + 1.57) * tilt, 0, 360, c.tolist(), -1, cv2.LINE_AA)
    ring(False)
    # lensed top arc (light bent over the hole)
    cv2.ellipse(ff, (int(cx), int(cy)), (int(R * 1.25), int(R * 1.18)), 0, 180, 360, (70, 150, 255), int(R * 0.12) + 2, cv2.LINE_AA)
    cv2.circle(ff, (int(cx), int(cy)), int(R * 1.03), (120, 200, 255), max(2, int(R * 0.03)), cv2.LINE_AA)  # photon ring
    cv2.circle(ff, (int(cx), int(cy)), int(R), (0, 0, 0), -1, cv2.LINE_AA)
    ring(True)
    f[:] = np.clip(ff, 0, 255).astype(np.uint8)

def chrome(f, t, num, label):
    paste(f, text_img(f"/ {num}", "mono", 34, FIRE, 0.14), 70, 90)
    paste(f, text_img(label.upper(), "mono", 30, MUTED, 0.14), 70, 140)
    paste(f, text_img("WHAT IF?", "mono", 30, CREAM, 0.14), W - 70 - text_img("WHAT IF?", "mono", 30, CREAM, 0.14).shape[1], 90)
    cv2.line(f, (70, 190), (70 + int(300 * ease(t * 2)), 190), bgr(FIRE), 4, cv2.LINE_AA)

def display(f, s, x, y, lt, size=150, col=CREAM, delay=0.0):
    """massive lowercase Barlow 900, rises in"""
    p = ease((lt - delay) / 0.45)
    if p <= 0: return
    img = text_img(s, "b9", size, col)
    paste(f, img, x, y + (1 - p) * 60, p)

# ---------- captions: word timings approximated by length ----------
def words_for(i):
    ws = LINES[i].split(); L = sum(len(w) + 1 for w in ws); out = []; t0 = starts[i]
    for w in ws:
        d = durs[i] * (len(w) + 1) / L; out.append((w, t0, t0 + d)); t0 += d
    return out
WORDS = [words_for(i) for i in range(6)]
def captions(f, t):
    for i in range(1, 6):
        if starts[i] - 0.05 <= t <= starts[i] + durs[i] + GAP * 0.8:
            ws = WORDS[i]
            # chunk into groups of 3 words
            groups = [ws[j:j + 3] for j in range(0, len(ws), 3)]
            for g in groups:
                if g[0][1] - 0.05 <= t < (g[-1][2] if g is not groups[-1] else starts[i] + durs[i] + GAP * 0.8):
                    imgs = []
                    for w, a, b in g:
                        col = FIRE if a <= t < b + 0.05 else CREAM
                        imgs.append(text_img(w.lower(), "b9", 84, col, -0.02))
                    tw = sum(im.shape[1] for im in imgs) + 22 * (len(imgs) - 1); x = (W - tw) // 2
                    ov = f.copy(); cv2.rectangle(ov, (x - 36, 1450), (x + tw + 36, 1590), bgr(INK), -1)
                    cv2.addWeighted(ov, 0.82, f, 0.18, 0, f)
                    cv2.line(f, (x - 36, 1450), (x + tw + 36, 1450), bgr(FIRE), 3)
                    pop = 1.0
                    for im in imgs:
                        # dark plate for legibility
                        paste(f, im, x, 1470, pop); x += im.shape[1] + 22
                    return

# ---------- scenes ----------
SPR = {}
def spr(key, **kw):
    if key not in SPR: SPR[key] = astronaut(**kw)
    return SPR[key]

def scene(i, t):
    f = np.full((H, W, 3), bgr(INK), np.uint8)
    a, b = SC[i]; lt = t - a; dur = b - a
    if i == 0:
        stars(f, t, 0.4)
        z = 0.6 + 0.4 * eio(lt / dur)
        black_hole(f, 540, 1150, 120 * z, t)
        place_sprite(f, astronaut(wave_t=t), 540 + math.sin(t * 1.3) * 40, 560 + math.sin(t * 2) * 18, 0.95, rot=math.sin(t) * 10)
        display(f, "what if you", 70, 1380, lt, 110, CREAM)
        display(f, "fell into a", 70, 1490, lt, 110, CREAM, 0.12)
        display(f, "black hole?", 70, 1610, lt, 150, FIRE, 0.3)
        chrome(f, lt, "01", "space / gravity")
    elif i == 1:
        stars(f, t, 0.15)
        R = 150 + 40 * eio(lt / dur)
        black_hole(f, 540, 1000, R, t, glow=1.2)
        display(f, "it glows.", 70, 300, lt, 170, CREAM)
        # stat cards
        if lt > 2.2:
            p = ease((lt - 2.2) / 0.5)
            cv2.line(f, (70, 1250), (70 + int(440 * p), 1250), bgr(FIRE), 3)
            paste(f, text_img("millions °C", "b9", 92, FIRE), 70, 1270, p)
            paste(f, text_img("SUPER HOT GAS", "mono", 28, MUTED, 0.14), 70, 1385, p)
        if lt > 4.6:
            p = ease((lt - 4.6) / 0.5)
            paste(f, text_img("…around nothing", "b6", 64, CREAM, -0.02), 1010 - text_img("…around nothing", "b6", 64, CREAM, -0.02).shape[1], 760, p)
            cv2.arrowedLine(f, (900, 860), (int(900 - 200 * p), int(860 + 110 * p)), bgr(CREAM), 4, cv2.LINE_AA, tipLength=0.15)
        chrome(f, lt, "02", "accretion disk")
    elif i == 2:
        stars(f, t, 0, pull=(540, 1580), k=0.6)
        black_hole(f, 540, 1700, 260, t, tilt=0.25)
        y = 700 + 120 * eio(lt / dur)
        place_sprite(f, spr("plain"), 560, y, 0.9, rot=180 + math.sin(t * 3) * 4)  # feet first (upside down)
        # force arrows: head (top) small, feet (bottom) big
        p = ease((lt - 0.8) / 0.6)
        if p > 0:
            cv2.arrowedLine(f, (850, int(y - 200)), (850, int(y - 200 + 70 * p)), bgr(CREAM), 10, cv2.LINE_AA, tipLength=0.35)
            paste(f, text_img("HEAD", "mono", 30, CREAM, 0.14), 885, int(y - 200))
            cv2.arrowedLine(f, (850, int(y + 130)), (850, int(y + 130 + 300 * p)), bgr(FIRE), 18, cv2.LINE_AA, tipLength=0.2)
            paste(f, text_img("FEET", "mono", 30, FIRE, 0.14), 885, int(y + 150))
        display(f, "feet > head", 70, 300, lt, 150, CREAM)
        chrome(f, lt, "03", "tidal force")
    elif i == 3:
        stars(f, t, 0, pull=(540, 1580), k=1.0)
        black_hole(f, 540, 1750, 300, t, tilt=0.22, glow=1.3, spin=1.6)
        s = eio(lt / (dur * 0.8))
        place_sprite(f, spr("plain"), 540 + math.sin(t * 8) * 8 * s, 900 + 250 * s, 0.85, sx=1 - 0.68 * s, sy=1 + 2.1 * s, rot=180)
        # noodle squiggle lines
        if s > 0.4:
            for k in range(3):
                pts = [(int(380 + k * 160 + math.sin(yy / 40 + t * 6 + k) * 18), yy) for yy in range(560, 1400, 20)]
                cv2.polylines(f, [np.array(pts)], False, bgr(FIRE), 3, cv2.LINE_AA)
        display(f, "spaghetti-", 70, 230, lt - 1.4, 150, FIRE)
        display(f, "fication", 70, 390, lt - 1.4, 150, CREAM, 0.15)
        if lt < 1.3: display(f, "stretch.", 70, 300, lt, 170, CREAM)
        chrome(f, lt, "04", "real science word")
    elif i == 4:
        stars(f, t, 0.05)
        black_hole(f, 760, 1080, 210, t, glow=0.9)
        # friend on the left, far away, looking through a spyglass
        place_sprite(f, spr("plain"), 200, 1230, 0.55, rot=-5)
        cv2.line(f, (250, 1185), (340, 1150), bgr(MUTED), 16, cv2.LINE_AA)
        # falling astronaut slowing at the edge: position approaches horizon asymptotically
        prog = 1 - math.exp(-lt * 0.9)
        tint = min(1, max(0, (lt - 2.2) / 2.0)); fade = 1 - min(1, max(0, (lt - 4.2) / 2.0)) * 0.9
        place_sprite(f, astronaut(tint=tint), 610 - 250 * (1 - prog), 930 - 330 * (1 - prog), 0.42 * (1 - 0.4 * prog), rot=40 * prog, alpha=fade)
        # slowing clock
        cx, cy = 880, 560; cv2.circle(f, (cx, cy), 90, bgr(CREAM), 6, cv2.LINE_AA)
        ang = (1 - math.exp(-lt * 0.6)) * 6.0
        cv2.line(f, (cx, cy), (int(cx + 70 * math.sin(ang)), int(cy - 70 * math.cos(ang))), bgr(FIRE), 8, cv2.LINE_AA)
        paste(f, text_img("TIME", "mono", 26, MUTED, 0.14), cx, cy + 115, 1, "ct")
        display(f, "slow.", 70, 300, lt - 1.8, 140, CREAM)
        display(f, "red.", 70, 450, lt - 3.0, 140, FIRE)
        display(f, "gone.", 70, 600, lt - 4.3, 140, MUTED)
        chrome(f, lt, "05", "what friends see")
    else:
        z = 1 + 3.5 * eio(lt / dur)
        stars(f, t, 0, pull=(540, 980), k=1.2)
        black_hole(f, 540, 980, 170 * z, t, glow=1.0 * (1 - 0.5 * eio(lt / dur)))
        # light rays curving into hole
        for k in range(5):
            ph = (lt * 0.8 + k * 0.2) % 1
            pts = []
            for u in np.linspace(0, ph, 30):
                ang = 3.6 + k * 0.5 + u * 2.5; r = 900 * (1 - u) + 170 * z * 0.9 * u
                pts.append((int(540 + math.cos(ang) * r), int(980 + math.sin(ang) * r)))
            if len(pts) > 1: cv2.polylines(f, [np.array(pts)], False, bgr(CREAM), 3, cv2.LINE_AA)
        display(f, "nobody knows.", 70, 300, lt - 1.0, 128, CREAM)
        if lt > dur - 1.8:
            p = ease((lt - (dur - 1.8)) / 0.5)
            paste(f, text_img("follow for the next", "b6", 60, CREAM, -0.02), 540, 1700, p, "ct")
            paste(f, text_img("what if?", "b9", 110, FIRE), 540, 1770, p, "ct")
        chrome(f, lt, "06", "event horizon")
    captions(f, t)
    # vignette-free flash on cut
    if lt < 0.12 and i > 0:
        f[:] = np.clip(f.astype(np.int16) + int(90 * (1 - lt / 0.12)), 0, 255).astype(np.uint8)
    return f

def frame(t):
    for i in range(6):
        if SC[i][0] <= t < SC[i][1]: return scene(i, t)
    return scene(5, t)

if __name__ == "__main__":
    if sys.argv[1] == "shot":
        for tt in sys.argv[2:]:
            cv2.imwrite(f"{D}/shot_{tt}.png", frame(float(tt)))
    else:
        n = int(TOTAL * FPS)
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", f"{D}/video.mp4"], stdin=subprocess.PIPE)
        for k in range(n):
            p.stdin.write(frame(k / FPS).tobytes())
        p.stdin.close(); p.wait()
        print("TIMES", starts, durs, TOTAL)
