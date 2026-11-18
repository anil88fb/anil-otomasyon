import sys, json, numpy as np, soundfile as sf
import os
ROOT=os.path.dirname(os.path.abspath(__file__))
vid=sys.argv[1]; d=json.load(open(f"{ROOT}/{vid}/timing.json")); seg=d["segments"]; D=d["duration"]
sr=44100; N=int(D*sr); rng=np.random.default_rng(int(sys.argv[2]) if len(sys.argv)>2 else 1)
t=np.arange(N)/sr
def env(n,a,r): e=np.ones(n); a=int(a*sr); r=int(r*sr); e[:a]=np.linspace(0,1,a); e[-r:]=np.linspace(1,0,r); return e
def lp(x,k): # one-pole lowpass
    y=np.empty_like(x); acc=0.
    a=k
    from scipy.signal import lfilter
    return lfilter([a],[1,a-1],x)
# --- music: pad chords + soft pluck arpeggio + kick pulse
bpm=96; beat=60/bpm
chords=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]  # Am F C G
f=lambda m:440*2**((m-69)/12)
music=np.zeros(N)
bar=beat*4
for bi in range(int(D/bar)+1):
    ch=chords[bi%4]; s0=int(bi*bar*sr); n=min(int(bar*sr),N-s0)
    if n<=0: break
    tt=np.arange(n)/sr; e=env(n,0.3,0.4)
    for m in ch:
        for det in (-0.08,0.08):
            ph=2*np.pi*f(m-12+det/1)*tt
            music[s0:s0+n]+=0.05*e*(np.sin(ph)+0.3*np.sin(2*ph)+0.12*np.sin(3*ph))
    # arpeggio 8ths
    for k in range(8):
        m=ch[k%3]+12+(12 if k in (3,7) else 0); st=s0+int(k*beat/2*sr); ln=int(0.35*sr)
        if st+ln>N: break
        tt2=np.arange(ln)/sr; music[st:st+ln]+=0.06*np.exp(-tt2*9)*np.sin(2*np.pi*f(m)*tt2)*(1+0.5*np.sin(2*np.pi*f(m)*2*tt2))
    # kick on beats
    for k in range(4):
        st=s0+int(k*beat*sr); ln=int(0.25*sr)
        if st+ln>N: break
        tt2=np.arange(ln)/sr; music[st:st+ln]+=0.22*np.exp(-tt2*14)*np.sin(2*np.pi*(50+90*np.exp(-tt2*30))*tt2)
fx=np.zeros(N)
def add(x,at,g=1.0):
    s=int(at*sr); e=min(N,s+len(x)); 
    if s<N: fx[s:e]+=g*x[:e-s]
def whoosh(dur=0.9):
    n=int(dur*sr); w=rng.standard_normal(n); tt=np.arange(n)/n
    from scipy.signal import butter, sosfilt
    out=np.zeros(n)
    for i,(lo) in enumerate(np.linspace(300,3000,8)):
        sos=butter(2,[lo,lo*1.6],btype='band',fs=sr,output='sos'); seg_=sosfilt(sos,w)
        wgt=np.exp(-((tt-i/8)**2)/0.02); out+=seg_*wgt
    return out/np.max(np.abs(out))*np.sin(np.pi*tt)**1.5
def ding(freq=1320):
    n=int(0.9*sr); tt=np.arange(n)/sr
    return np.exp(-tt*6)*(np.sin(2*np.pi*freq*tt)+0.4*np.sin(2*np.pi*freq*2.01*tt)+0.2*np.sin(2*np.pi*freq*3.02*tt))
def boom():
    n=int(1.6*sr); tt=np.arange(n)/sr
    return np.exp(-tt*3)*np.sin(2*np.pi*(38+60*np.exp(-tt*8))*tt)+0.3*np.exp(-tt*12)*rng.standard_normal(n)*np.exp(-tt*20)
def riser(dur=1.5):
    n=int(dur*sr); tt=np.arange(n)/sr; fr=200+1200*(tt/dur)**2
    return 0.5*(tt/dur)**2*np.sin(2*np.pi*np.cumsum(fr)/sr)+0.3*(tt/dur)**3*rng.standard_normal(n)*0.4
def bubbles():
    out=np.zeros(int(2.5*sr))
    for k in range(25):
        st=int(rng.uniform(0,2.2)*sr); ln=int(0.08*sr); tt=np.arange(ln)/sr; fr=rng.uniform(400,1100)
        out[st:st+ln]+=np.exp(-tt*40)*np.sin(2*np.pi*fr*(1+tt*8)*tt)
    return out
for s in seg[1:]:
    add(whoosh(),s["start"]-0.75,0.35)
for s in seg[1:6]:
    add(ding(1320 if s["i"]<5 else 1760),s["start"]+0.15,0.22)
add(riser(1.6),seg[5]["start"]-1.6,0.35); add(boom(),seg[5]["start"]+0.05,0.7)
add(bubbles(),seg[6]["start"]+0.6,0.25); add(boom(),seg[6]["start"]+2.6,0.35)
add(ding(990),seg[7]["start"]+0.1,0.25)
# duck music under voice
v,vsr=sf.read(f"{ROOT}/{vid}/voice.wav"); 
from scipy.signal import resample_poly
v=resample_poly(v,147,80)[:N]; v=np.pad(v,(0,N-len(v)))
envv=np.convolve(np.abs(v),np.ones(int(0.15*sr))/(0.15*sr),'same'); duck=1-0.45*np.clip(envv/0.05,0,1)
music*=duck; music*=env(N,0.5,1.5)
mix=v*1.0+music*0.55+fx*0.8
mix/=max(1.0,np.max(np.abs(mix))/0.97)
sf.write(f"{ROOT}/{vid}/mix.wav",mix,sr)
print("ok",D)
