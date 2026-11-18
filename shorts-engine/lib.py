"""Shared Shorts engine: timeline from voiceover, text, captions, shapes, music, mux."""
import numpy as np, cv2, wave, math, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FD = "/home/claude/shorts/fonts"

def hexc(h):
    h = h.lstrip('#'); return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
def bgr(c):
    if isinstance(c, str): c = hexc(c)
    return (c[2], c[1], c[0])

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def eio(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def back(x):
    x = min(max(x, 0), 1); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, k): return a + (b - a) * k

class Timeline:
    def __init__(self, d, gap=0.4, start=0.2, tail=1.4):
        self.durs = []
        for i in range(1, 7):
            with wave.open(f"{d}/vo/l{i}.wav") as w: self.durs.append(w.getnframes() / w.getframerate())
        self.starts = []; t = start
        for x in self.durs: self.starts.append(t); t += x + gap
        self.gap = gap; self.total = t + tail
        self.sc = [(0 if i == 0 else self.starts[i] - 0.12, (self.starts[i + 1] - 0.12) if i < 5 else self.total) for i in range(6)]
    def which(self, t):
        for i, (a, b) in enumerate(self.sc):
            if a <= t < b: return i, t - a, b - a
        return 5, t - self.sc[5][0], self.sc[5][1] - self.sc[5][0]

_fc, _tc = {}, {}
def font(name, s):
    k = (name, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(f"{FD}/{name}.ttf", s)
    return _fc[k]

def text_img(s, fname, size, col, track=0.0, stroke=0, stroke_col=None):
    key = (s, fname, size, str(col), track, stroke, str(stroke_col))
    if key in _tc: return _tc[key]
    if isinstance(col, str): col = hexc(col)
    if isinstance(stroke_col, str): stroke_col = hexc(stroke_col)
    f = font(fname, size); trk = track * size
    wid = int(sum(f.getlength(c) + trk for c in s) + size + stroke * 2)
    im = Image.new("RGBA", (max(wid, 4), int(size * 1.45) + stroke * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = stroke
    for c in s:
        d.text((x, stroke), c, font=f, fill=tuple(col) + (255,), stroke_width=stroke, stroke_fill=(tuple(stroke_col) + (255,)) if stroke else None)
        x += f.getlength(c) + trk
    a = np.array(im); ys, xs = np.nonzero(a[..., 3])
    if len(xs): a = a[:ys.max() + 3, :xs.max() + 3]
    _tc[key] = a; return a

def paste(f, rgba, x, y, alpha=1.0, anchor="lt", scale=1.0):
    if scale != 1.0:
        rgba = cv2.resize(rgba, (max(1, int(rgba.shape[1] * scale)), max(1, int(rgba.shape[0] * scale))), interpolation=cv2.INTER_LINEAR)
    h, w = rgba.shape[:2]
    if anchor in ("ct", "cc"): x -= w // 2
    if anchor == "cc": y -= h // 2
    if anchor == "rt": x -= w
    x, y = int(x), int(y)
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x0 >= x1 or y0 >= y1 or alpha <= 0.01: return
    src = rgba[y0 - y:y1 - y, x0 - x:x1 - x]
    a = (src[..., 3:4].astype(np.float32) / 255.0) * min(alpha, 1)
    reg = f[y0:y1, x0:x1].astype(np.float32)
    f[y0:y1, x0:x1] = (reg * (1 - a) + src[..., 2::-1].astype(np.float32) * a).astype(np.uint8)

def text(f, s, x, y, fname, size, col, lt=1.0, delay=0.0, anchor="lt", track=0.0, rise=50, stroke=0, stroke_col=None, pop=False):
    p = (lt - delay) / 0.4
    if p <= 0: return
    img = text_img(s, fname, size, col, track, stroke, stroke_col)
    if pop: paste(f, img, x, y, min(p * 2, 1), anchor, scale=max(0.05, back(p)))
    else: paste(f, img, x, y + (1 - ease(p)) * rise, ease(p), anchor)

# ---- shapes with optional outline + hard offset shadow (neo-brutal styles) ----
class Ink:
    def __init__(self, outline=None, ow=0, shadow=None, sh=(0, 0)):
        self.outline, self.ow, self.shadow, self.sh = outline, ow, shadow, sh
    def _do(self, f, fn, col):
        if self.shadow is not None and self.sh != (0, 0): fn(f, bgr(self.shadow), self.sh)
        if self.outline is not None and self.ow: fn(f, bgr(self.outline), (0, 0), self.ow)
        fn(f, bgr(col), (0, 0), 0)
    def rect(self, f, x0, y0, x1, y1, col, r=0):
        def fn(f, c, o, grow=0):
            a, b = (int(x0 + o[0] - grow), int(y0 + o[1] - grow)), (int(x1 + o[0] + grow), int(y1 + o[1] + grow))
            rr = int(r + grow) if r else 0
            if rr <= 0: cv2.rectangle(f, a, b, c, -1, cv2.LINE_AA); return
            rr = min(rr, (b[0] - a[0]) // 2, (b[1] - a[1]) // 2)
            cv2.rectangle(f, (a[0] + rr, a[1]), (b[0] - rr, b[1]), c, -1)
            cv2.rectangle(f, (a[0], a[1] + rr), (b[0], b[1] - rr), c, -1)
            for cx, cy in ((a[0] + rr, a[1] + rr), (b[0] - rr, a[1] + rr), (a[0] + rr, b[1] - rr), (b[0] - rr, b[1] - rr)):
                cv2.circle(f, (cx, cy), rr, c, -1, cv2.LINE_AA)
        self._do(f, fn, col)
    def circle(self, f, x, y, r, col):
        def fn(f, c, o, grow=0): cv2.circle(f, (int(x + o[0]), int(y + o[1])), int(r + grow), c, -1, cv2.LINE_AA)
        self._do(f, fn, col)
    def ellipse(self, f, x, y, rx, ry, col, ang=0, a0=0, a1=360):
        def fn(f, c, o, grow=0): cv2.ellipse(f, (int(x + o[0]), int(y + o[1])), (int(rx + grow), int(ry + grow)), ang, a0, a1, c, -1, cv2.LINE_AA)
        self._do(f, fn, col)
    def poly(self, f, pts, col):
        pts = np.array(pts, np.float32)
        def fn(f, c, o, grow=0):
            p = pts + np.array(o, np.float32)
            if grow:
                cv2.polylines(f, [p.astype(np.int32)], True, c, int(grow * 2), cv2.LINE_AA)
            cv2.fillPoly(f, [p.astype(np.int32)], c, cv2.LINE_AA)
        self._do(f, fn, col)
    def line(self, f, a, b, col, w):
        def fn(f, c, o, grow=0): cv2.line(f, (int(a[0] + o[0]), int(a[1] + o[1])), (int(b[0] + o[0]), int(b[1] + o[1])), c, int(w + grow * 2), cv2.LINE_AA)
        self._do(f, fn, col)

def face(f, x, y, s, look=0.0, blink=False, mouth="smile", eye="#111111", t=0.0):
    """cute face: two eyes + mouth, s = scale (~1 = 60px wide face)"""
    e = bgr(eye)
    for sx in (-1, 1):
        ex, ey = int(x + sx * 22 * s + look * 6 * s), int(y)
        if blink: cv2.line(f, (ex - int(9 * s), ey), (ex + int(9 * s), ey), e, max(2, int(4 * s)), cv2.LINE_AA)
        else:
            cv2.ellipse(f, (ex, ey), (int(9 * s), int(12 * s)), 0, 0, 360, e, -1, cv2.LINE_AA)
            cv2.circle(f, (ex + int(3 * s), ey - int(4 * s)), max(1, int(3 * s)), (255, 255, 255), -1, cv2.LINE_AA)
    my = int(y + 24 * s)
    if mouth == "smile": cv2.ellipse(f, (int(x + look * 6 * s), my), (int(13 * s), int(9 * s)), 0, 10, 170, e, max(2, int(4 * s)), cv2.LINE_AA)
    elif mouth == "o": cv2.ellipse(f, (int(x + look * 6 * s), my + int(4 * s)), (int(8 * s), int(11 * s)), 0, 0, 360, e, -1, cv2.LINE_AA)
    elif mouth == "flat": cv2.line(f, (int(x - 10 * s), my), (int(x + 10 * s), my), e, max(2, int(4 * s)), cv2.LINE_AA)
    elif mouth == "talk":
        o = abs(math.sin(t * 14)) * 10 * s + 2
        cv2.ellipse(f, (int(x + look * 6 * s), my + int(2 * s)), (int(11 * s), int(o)), 0, 0, 360, e, -1, cv2.LINE_AA)

def blink_at(t, seed=0):
    return ((t + seed * 0.37) % 3.1) < 0.12

# ---- captions ----
def words_for(tl, lines, i):
    ws = lines[i].split(); L = sum(len(w) + 2 for w in ws); out = []; t0 = tl.starts[i]
    for w in ws:
        d = tl.durs[i] * (len(w) + 2) / L; out.append((w, t0, t0 + d)); t0 += d
    return out

def captions(f, t, tl, lines, st, skip=(0,)):
    """st: dict(font,size,col,hi,plate,plate_alpha,y,upper,stroke,stroke_col,outline,radius)"""
    for i in range(6):
        if i in skip: continue
        end_i = tl.starts[i] + tl.durs[i] + tl.gap * 0.8
        if not (tl.starts[i] - 0.05 <= t <= end_i): continue
        ws = words_for(tl, lines, i); groups = [ws[j:j + 3] for j in range(0, len(ws), 3)]
        for gi, g in enumerate(groups):
            gend = g[-1][2] if gi < len(groups) - 1 else end_i
            if not (g[0][1] - 0.05 <= t < gend): continue
            imgs = []
            for w, a, b in g:
                ww = w.upper() if st.get("upper") else (w.lower() if st.get("lower") else w)
                col = st["hi"] if a <= t < b + 0.05 else st["col"]
                imgs.append(text_img(ww, st["font"], st["size"], col, st.get("track", 0), st.get("stroke", 0), st.get("stroke_col")))
            gapw = int(st["size"] * 0.28)
            tw = sum(im.shape[1] for im in imgs) + gapw * (len(imgs) - 1); x = (W - tw) // 2; y = st.get("y", 1480)
            hh = max(im.shape[0] for im in imgs)
            if st.get("plate") is not None:
                px, py = 34, 22
                ov = f.copy()
                Ink(st.get("outline"), st.get("ow", 0), st.get("shadow"), st.get("sh", (0, 0))).rect(ov, x - px, y - py, x + tw + px, y + hh + py * 0.6, st["plate"], st.get("radius", 0))
                a = st.get("plate_alpha", 1.0)
                if a >= 1: f[:] = ov
                else: cv2.addWeighted(ov, a, f, 1 - a, 0, f)
            pk = ease((t - g[0][1] + 0.05) / 0.12)
            for im in imgs:
                paste(f, im, x, y + (1 - pk) * 14, 1); x += im.shape[1] + gapw
            return

# ---- music ----
def music(T, out, mood="lofi", bpm=100, seed=1):
    SR = 44100; n = int(SR * T); o = np.zeros(n); rng = np.random.default_rng(seed)
    def note(m): return 440 * 2 ** ((m - 69) / 12)
    beat = 60 / bpm
    prog = {"lofi": [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 65]],
            "bright": [[60, 64, 67], [65, 69, 72], [57, 60, 64], [67, 71, 74]],
            "mystic": [[50, 53, 57], [46, 50, 53], [48, 52, 55], [45, 49, 52]],
            "march": [[48, 52, 55], [53, 57, 60], [55, 59, 62], [48, 52, 55]],
            "drama": [[45, 48, 52], [41, 45, 48], [43, 47, 50], [40, 44, 47]],
            "bubbly": [[62, 66, 69], [67, 71, 74], [64, 67, 71], [69, 73, 76]],
            "icy": [[64, 67, 71], [60, 64, 67], [62, 65, 69], [59, 62, 67]]}[mood]
    bar = beat * 4
    wav = {"lofi": "tri", "bright": "sq", "mystic": "sin", "march": "sq", "drama": "saw", "bubbly": "sq", "icy": "sin"}[mood]
    def osc(fr, tt, kind):
        ph = (fr * tt) % 1
        if kind == "sin": return np.sin(2 * np.pi * ph)
        if kind == "tri": return 2 * np.abs(2 * ph - 1) - 1
        if kind == "sq": return np.sign(np.sin(2 * np.pi * ph)) * 0.6
        return (2 * ph - 1) * 0.7
    for i in range(int(T / bar) + 1):
        s = int(i * bar * SR); e = min(n, int((i + 1) * bar * SR) + SR // 2)
        if s >= n: break
        tt = np.arange(e - s) / SR; env = np.minimum(1, tt / 0.4) * np.exp(-np.maximum(0, tt - bar) * 4)
        for m in prog[i % 4]: o[s:e] += 0.035 * env * np.sin(2 * np.pi * note(m) * tt)
        o[s:e] += 0.08 * env * np.sin(2 * np.pi * note(prog[i % 4][0] - 24) * tt)
    step = beat / 2 if mood not in ("mystic", "icy") else beat
    for k in range(int(T / step)):
        ch = prog[int(k * step / bar) % 4]; m = ch[k % len(ch)] + 12 + (12 if (mood == "bubbly" and k % 4 == 3) else 0)
        if mood == "lofi" and k % 3 == 2: continue
        s = int(k * step * SR); L = int(0.45 * SR); e = min(n, s + L); tt = np.arange(e - s) / SR
        dec = 9 if mood != "icy" else 3
        o[s:e] += 0.05 * np.exp(-tt * dec) * osc(note(m), tt, wav)
        if mood == "icy": o[s:e] += 0.03 * np.exp(-tt * 2) * np.sin(2 * np.pi * note(m + 12) * 2.01 * tt)
    if mood not in ("mystic",):
        for k in range(int(T / beat)):
            if k < 2: continue
            s = int(k * beat * SR); L = int(0.25 * SR); e = min(n, s + L); tt = np.arange(e - s) / SR
            if k % 2 == 0 or mood in ("march", "drama"):
                o[s:e] += 0.2 * np.exp(-tt * 16) * np.sin(2 * np.pi * (50 + 80 * np.exp(-tt * 35)) * tt)
            else:
                nz = rng.normal(0, 1, e - s); o[s:e] += 0.06 * np.exp(-tt * 25) * nz
            hs = s + int(beat / 2 * SR); he = min(n, hs + int(0.05 * SR))
            if hs < n: o[hs:he] += 0.025 * rng.normal(0, 1, he - hs) * np.exp(-np.arange(he - hs) / SR * 60)
    d = int(beat * 0.75 * SR); o[d:] += 0.25 * o[:-d]
    t = np.arange(n) / SR; o *= np.minimum(1, np.minimum(t / 0.8, (T - t) / 1.2)); o /= np.abs(o).max() * 1.1
    with wave.open(out, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((o * 32767).astype(np.int16).tobytes())

def sfx_track(tl, out, extra=()):
    """whoosh on every cut + extra list of (time, kind) kind in pop/boom/splash/ding"""
    SR = 24000; n = int(tl.total * SR); s = np.zeros(n); rng = np.random.default_rng(3)
    def add(t0, sig):
        k = int(max(t0, 0) * SR); e = min(n, k + len(sig)); s[k:e] += sig[:e - k]
    for i in range(1, 6):
        L = int(0.5 * SR); tt = np.arange(L) / SR; nz = np.convolve(rng.normal(0, 1, L), np.ones(10) / 10, 'same')
        add(tl.sc[i][0] - 0.25, 0.22 * np.sin(np.pi * tt / 0.5) ** 2 * nz)
    for t0, kind in extra:
        L = int(0.6 * SR); tt = np.arange(L) / SR
        if kind == "pop": sig = 0.35 * np.exp(-tt * 30) * np.sin(2 * np.pi * (300 + 900 * np.exp(-tt * 40)) * tt)
        elif kind == "boom": sig = 0.5 * np.exp(-tt * 5) * np.sin(2 * np.pi * (45 + 60 * np.exp(-tt * 8)) * tt)
        elif kind == "splash": sig = 0.3 * np.exp(-tt * 6) * np.convolve(rng.normal(0, 1, L), np.ones(4) / 4, 'same')
        elif kind == "ding": sig = 0.25 * np.exp(-tt * 4) * (np.sin(2 * np.pi * 1320 * tt) + 0.5 * np.sin(2 * np.pi * 2640 * tt))
        else: continue
        add(t0, sig)
    full = np.zeros(n)
    for i in range(6):
        with wave.open(f"{os.path.dirname(out)}/vo/l{i+1}.wav") as w: a = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
        k = int(tl.starts[i] * SR); full[k:k + len(a)] += a[:max(0, n - k)]
    for name, x in ((out, s), (os.path.dirname(out) + "/vo_full.wav", full)):
        with wave.open(name, 'w') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())

def run(d, tl, frame_fn, name, mood, bpm, extra_sfx=()):
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode == "shot":
        ts = [float(x) for x in sys.argv[2:]] or [ (a + b) / 2 for a, b in tl.sc ]
        ims = [cv2.resize(frame_fn(t), (270, 480)) for t in ts]
        cv2.imwrite(f"{d}/sheet.png", np.hstack(ims)); print("sheet", ts); return
    n = int(tl.total * FPS)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", f"{d}/video.mp4"], stdin=subprocess.PIPE)
    for k in range(n): p.stdin.write(frame_fn(k / FPS).tobytes())
    p.stdin.close(); p.wait()
    music(tl.total, f"{d}/music.wav", mood, bpm)
    sfx_track(tl, f"{d}/sfx.wav", extra_sfx)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{d}/video.mp4", "-i", f"{d}/vo_full.wav", "-i", f"{d}/music.wav", "-i", f"{d}/sfx.wav",
                    "-filter_complex", "[1:a]aresample=44100,asplit[k][v];[2:a]volume=0.36[m];[m][k]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[dk];[3:a]aresample=44100,volume=0.8[s];[v][dk][s]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", f"/home/claude/{name}.mp4"], check=True)
    print("DONE", name, tl.total)
