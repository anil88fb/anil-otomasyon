import sys, json, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
import os
M=os.environ.get("VF_MODELS","/home/claude/vf-models")
k = Kokoro(M+"/kokoro.onnx", M+"/voices.bin")
spec = json.load(open(sys.argv[1])); out = sys.argv[2]
voice = spec.get("voice","af_heart"); speed = spec.get("speed",1.05)
segs=[]; audio=[]; t=0.0; sr=24000
for i,line in enumerate(spec["lines"]):
    s, sr = k.create(line["say"], voice=voice, speed=speed, lang="en-us")
    pre = line.get("pause_before", 0.25)
    audio.append(np.zeros(int(pre*sr), dtype=np.float32)); t += pre
    segs.append({"i":i,"start":round(t,3),"end":round(t+len(s)/sr,3),"text":line["caption"]})
    audio.append(s.astype(np.float32)); t += len(s)/sr
audio.append(np.zeros(int(0.8*sr),dtype=np.float32)); t+=0.8
sf.write(out+"/voice.wav", np.concatenate(audio), sr)
json.dump({"segments":segs,"duration":round(t,3)}, open(out+"/timing.json","w"), indent=1)
print(json.dumps(segs, indent=0), t)
