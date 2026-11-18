import sys, json, base64, subprocess, threading, http.server, functools, time
from playwright.sync_api import sync_playwright
vid = sys.argv[1]; mode = sys.argv[2]  # "stills t1,t2.." or "video"
import os
root=os.path.dirname(os.path.abspath(__file__))
H=functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
class Q(H.func):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(("127.0.0.1",0),functools.partial(Q,directory=root)); port=srv.server_address[1]
threading.Thread(target=srv.serve_forever,daemon=True).start()
dur=json.load(open(f"{root}/{vid}/timing.json"))["duration"]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--use-angle=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
    pg=b.new_page(viewport={"width":1080,"height":1920})
    pg.on("console", lambda m: print("console:", m.text))
    pg.on("pageerror", lambda e: print("PAGEERR:", e))
    pg.goto(f"http://127.0.0.1:{port}/{vid}/index.html"); pg.wait_for_function("window.READY===true", timeout=120000)
    if mode=="stills":
        for t in sys.argv[3].split(","):
            d=pg.evaluate(f"renderAt({t})"); open(f"{root}/{vid}/still_{t}.jpg","wb").write(base64.b64decode(d.split(",")[1]))
    else:
        n=int(dur*30); tmp=f"{root}/{vid}/video_tmp.mp4"
        ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","image2pipe","-framerate","30","-c:v","mjpeg","-i","-","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",tmp],stdin=subprocess.PIPE)
        t0=time.time()
        for f in range(n):
            d=pg.evaluate(f"renderAt({f/30})"); ff.stdin.write(base64.b64decode(d.split(",")[1]))
            if f%150==0: print(f, n, round(time.time()-t0,1), flush=True)
        ff.stdin.close(); ff.wait(); print("done", ff.returncode, round(time.time()-t0,1))
    b.close()
