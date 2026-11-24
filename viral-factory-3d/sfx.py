"""Music + sound effects for one video: python3 sfx.py <video-folder> [seed]

If <video-folder>/music.json exists it sets the music and the effect plan, so every
video can sound different. Keys (all optional):
  bpm, chords (list of MIDI triads, one per bar), pad (gain), arp (gain), kick (gain),
  pluck ("sine"|"bell"|"square"), arp_pattern (list of chord-tone indices, 8 per bar,
  values >=3 mean +octave), hat (gain), music_gain, duck,
  fx: [{"type": whoosh|ding|boom|riser|bubbles|ping|splash|rush|clunk|chime|file ("name": a file in assets/sfx),
        "seg": i, "at": seconds from segment start (negative = before), "gain": g,
        "freq": f (ding/ping), "dur": d (riser/rush)}]
  whoosh_all (gain, whoosh before every segment change; default 0.35)
Without music.json the original v01 plan is used.
"""
import sys, json, os, numpy as np, soundfile as sf
from scipy.signal import lfilter, butter, sosfilt, resample_poly
ROOT = os.path.dirname(os.path.abspath(__file__))
vid = sys.argv[1]
d = json.load(open(f"{ROOT}/{vid}/timing.json")); seg = d["segments"]; D = d["duration"]
cfgp = f"{ROOT}/{vid}/music.json"
cfg = json.load(open(cfgp)) if os.path.exists(cfgp) else None
sr = 44100; N = int(D*sr); rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 1)

def env(n, a, r):
    e = np.ones(n); a = max(1, int(a*sr)); r = max(1, int(r*sr)); a = min(a, n); r = min(r, n)
    e[:a] = np.linspace(0, 1, a); e[-r:] = np.minimum(e[-r:], np.linspace(1, 0, r)); return e
f = lambda m: 440*2**((m-69)/12)

C = cfg or {}
bpm = C.get("bpm", 96); beat = 60/bpm; bar = beat*4
chords = C.get("chords", [[57,60,64],[53,57,60],[48,52,55],[55,59,62]])
padg = C.get("pad", 0.05); arpg = C.get("arp", 0.06); kickg = C.get("kick", 0.22); hatg = C.get("hat", 0.0)
pluck = C.get("pluck", "sine"); pat = C.get("arp_pattern", [0,1,2,3,0,1,2,7])
music = np.zeros(N)
def tone(fr, ln, kind):
    tt = np.arange(ln)/sr; ph = 2*np.pi*fr*tt
    if kind == "bell": return np.exp(-tt*5)*(np.sin(ph)+0.5*np.sin(2.76*ph)*np.exp(-tt*8)+0.25*np.sin(5.4*ph)*np.exp(-tt*14))
    if kind == "square": return np.exp(-tt*10)*np.sign(np.sin(ph))*0.5
    return np.exp(-tt*9)*np.sin(ph)*(1+0.5*np.sin(2*ph))
for bi in range(int(D/bar)+1):
    ch = chords[bi % len(chords)]; s0 = int(bi*bar*sr); n = min(int(bar*sr), N-s0)
    if n <= 0: break
    tt = np.arange(n)/sr; e = env(n, 0.3, 0.4)
    for m in ch:
        for det in (-0.08, 0.08):
            ph = 2*np.pi*f(m-12+det)*tt
            music[s0:s0+n] += padg*e*(np.sin(ph)+0.3*np.sin(2*ph)+0.12*np.sin(3*ph))
    for k in range(8):
        idx = pat[k % len(pat)]; m = ch[idx % 3]+12+12*(idx//3); st = s0+int(k*beat/2*sr); ln = int(0.45*sr)
        if st+ln > N: break
        music[st:st+ln] += arpg*tone(f(m), ln, pluck)
    for k in range(4):
        st = s0+int(k*beat*sr); ln = int(0.25*sr)
        if st+ln > N: break
        tt2 = np.arange(ln)/sr
        if kickg: music[st:st+ln] += kickg*np.exp(-tt2*14)*np.sin(2*np.pi*(50+90*np.exp(-tt2*30))*tt2)
        if hatg:
            h0 = st+int(beat/2*sr); hl = int(0.05*sr)
            if h0+hl < N:
                sos = butter(2, 7000, btype='high', fs=sr, output='sos')
                music[h0:h0+hl] += hatg*sosfilt(sos, rng.standard_normal(hl))*np.exp(-np.arange(hl)/sr*80)

fx = np.zeros(N)
def add(x, at, g=1.0):
    s = int(at*sr)
    if s < 0: x = x[-s:]; s = 0
    e = min(N, s+len(x))
    if s < N: fx[s:e] += g*x[:e-s]
def whoosh(dur=0.9):
    n = int(dur*sr); w = rng.standard_normal(n); tt = np.arange(n)/n; out = np.zeros(n)
    for i, lo in enumerate(np.linspace(300, 3000, 8)):
        sos = butter(2, [lo, lo*1.6], btype='band', fs=sr, output='sos'); out += sosfilt(sos, w)*np.exp(-((tt-i/8)**2)/0.02)
    return out/np.max(np.abs(out))*np.sin(np.pi*tt)**1.5
def ding(freq=1320):
    n = int(0.9*sr); tt = np.arange(n)/sr
    return np.exp(-tt*6)*(np.sin(2*np.pi*freq*tt)+0.4*np.sin(2*np.pi*freq*2.01*tt)+0.2*np.sin(2*np.pi*freq*3.02*tt))
def ping(freq=1480):  # sonar ping with echo
    n = int(2.2*sr); tt = np.arange(n)/sr; x = np.exp(-tt*4)*np.sin(2*np.pi*freq*tt)*np.minimum(1, tt*200)
    for k, dl in enumerate((0.45, 0.9, 1.35)):
        o = int(dl*sr); x[o:] += 0.35**(k+1)*x[:n-o]
    return x/np.max(np.abs(x))
def boom():
    n = int(1.6*sr); tt = np.arange(n)/sr
    return np.exp(-tt*3)*np.sin(2*np.pi*(38+60*np.exp(-tt*8))*tt)+0.3*np.exp(-tt*12)*rng.standard_normal(n)*np.exp(-tt*20)
def riser(dur=1.5):
    n = int(dur*sr); tt = np.arange(n)/sr; fr = 200+1200*(tt/dur)**2
    return 0.5*(tt/dur)**2*np.sin(2*np.pi*np.cumsum(fr)/sr)+0.3*(tt/dur)**3*rng.standard_normal(n)*0.4
def bubbles(dur=2.5):
    out = np.zeros(int(dur*sr))
    for k in range(int(10*dur)):
        st = int(rng.uniform(0, dur-0.3)*sr); ln = int(0.08*sr); tt = np.arange(ln)/sr; fr = rng.uniform(400, 1100)
        out[st:st+ln] += np.exp(-tt*40)*np.sin(2*np.pi*fr*(1+tt*8)*tt)
    return out
def splash():
    n = int(1.4*sr); tt = np.arange(n)/sr; sos = butter(2, [400, 6000], btype='band', fs=sr, output='sos')
    x = sosfilt(sos, rng.standard_normal(n))*np.exp(-tt*4)*np.minimum(1, tt*60)
    return x/np.max(np.abs(x))+0.6*bubbles(1.4)[:n]
def rush(dur=3.0):  # flowing water
    n = int(dur*sr); sos = butter(2, [150, 1800], btype='band', fs=sr, output='sos')
    x = sosfilt(sos, rng.standard_normal(n)); x /= np.max(np.abs(x))
    return x*env(n, 0.4, 0.8)*(0.8+0.2*np.sin(2*np.pi*3*np.arange(n)/sr))
def clunk():
    n = int(0.8*sr); tt = np.arange(n)/sr
    return np.exp(-tt*9)*(np.sin(2*np.pi*90*tt)+0.5*np.sin(2*np.pi*143*tt))+0.4*np.exp(-tt*40)*rng.standard_normal(n)
def chime():
    out = np.zeros(int(1.6*sr))
    for k, m in enumerate((84, 88, 91, 96)):
        x = tone(f(m), int(1.2*sr), "bell"); s = int(k*0.09*sr); out[s:s+len(x)] += 0.5*x
    return out
GEN = dict(whoosh=lambda o: whoosh(), ding=lambda o: ding(o.get("freq", 1320)), ping=lambda o: ping(o.get("freq", 1480)),
           boom=lambda o: boom(), riser=lambda o: riser(o.get("dur", 1.5)), bubbles=lambda o: bubbles(o.get("dur", 2.5)),
           splash=lambda o: splash(), rush=lambda o: rush(o.get("dur", 3.0)), clunk=lambda o: clunk(), chime=lambda o: chime(),
           file=lambda o: sample(o["name"]))
def sample(name):  # bundled SFX from assets/sfx/<name>.mp3 (hyperframes-media library)
    import subprocess
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f"{ROOT}/assets/sfx/{name}.mp3", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)

if cfg is None:  # original v01 plan
    plan = [dict(type="ding", seg=i, at=0.15, gain=0.22, freq=1320 if i < 5 else 1760) for i in range(1, 6)]
    plan += [dict(type="riser", seg=5, at=-1.6, gain=0.35, dur=1.6), dict(type="boom", seg=5, at=0.05, gain=0.7),
             dict(type="bubbles", seg=6, at=0.6, gain=0.25), dict(type="boom", seg=6, at=2.6, gain=0.35), dict(type="ding", seg=7, at=0.1, gain=0.25, freq=990)]
else:
    plan = cfg.get("fx", [])
wg = C.get("whoosh_all", 0.35)
if wg:
    for s in seg[1:]: add(whoosh(), s["start"]-0.75, wg)
for o in plan:
    if o["seg"] >= len(seg): continue
    add(GEN[o["type"]](o), seg[o["seg"]]["start"]+o.get("at", 0), o.get("gain", 0.3))

# duck music under voice
v, vsr = sf.read(f"{ROOT}/{vid}/voice.wav")
v = resample_poly(v, 147, 80)[:N]; v = np.pad(v, (0, N-len(v)))
envv = np.convolve(np.abs(v), np.ones(int(0.15*sr))/(0.15*sr), 'same'); duck = 1-C.get("duck", 0.45)*np.clip(envv/0.05, 0, 1)
music *= duck; music *= env(N, 0.5, 1.5)
mix = v*1.0+music*C.get("music_gain", 0.55)+fx*0.8
mix /= max(1.0, np.max(np.abs(mix))/0.97)
sf.write(f"{ROOT}/{vid}/mix.wav", mix, sr)
print("ok", D)
