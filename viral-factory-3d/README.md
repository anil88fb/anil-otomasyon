# Viral Factory 3D

"Why?" (@askdailywhy) kanalı için 3D kısa video üretim hattı. Low-poly 3D sahneler (three.js, başsız Chrome'da yazılımla render), Kokoro ile İngilizce seslendirme, kodla üretilen müzik ve efektler.

## How a video is built

```
./setup.sh                       # once per fresh session
cp -r examples/v01-tallest-mountains videos/<slug>
# edit videos/<slug>/script.json (narration lines: say = spoken, cap = on-screen caption)
# edit videos/<slug>/index.html  (scene, camera, overlays; renderAt(t) draws one frame)
python3 render.py videos/<slug> stills 2,10,20   # check frames before the full render
./make.sh videos/<slug>          # -> videos/<slug>/final.mp4 (1080x1920, 30 fps)
```

- `tts.py`: `script.json` → `voice.wav` + `timing.json` (segment start/end; scene timing follows the voice).
- `render.py`: serves this folder on localhost, calls `renderAt(t)` per frame, pipes JPEGs to ffmpeg. ~0.35 s/frame on 2 CPUs.
- `sfx.py`: music (chord pad, arpeggio, kick, hat) ducked under the voice, plus effects (whoosh, ding, ping, splash, rush, clunk, chime, riser, boom, bubbles). Put a `music.json` in the video folder to set bpm, chords, instrument and the effect plan per segment (see the docstring); without it the v01 plan is used. The second argument is a random seed.
- Fonts installed by setup: Montserrat, Bebas Neue, Space Grotesk, Fredoka (`/node_modules/@fontsource/<name>/files/...`).

## Videos made

| folder | title | look | voice |
|---|---|---|---|
| examples/v01-tallest-mountains | Earth's 5 Tallest Mountains | Himalaya flyover, Montserrat yellow cards | af_heart |
| videos/v02-ocean-depth | How Deep Is the Ocean? | probe dive + Everest cutaway, cyan sonar HUD, Bebas/Space Grotesk | am_michael |
| videos/v03-canal-locks | How Do Canal Locks Work? | sunny diorama cutaway, orange stickers, Fredoka | bf_emma |

## Channel rules (standing decisions)

- English, plain titles (no clickbait add-ons), no looping endings.
- Each video gets its own look, palette, voice and music: change `voice` in script.json (af_heart, am_michael, bf_emma, bm_george, am_adam, af_bella …), the scene and the chord set in `sfx.py`.
- 2 videos a day at 15:00 and 21:00 Istanbul, uploaded and scheduled through vidIQ.
- Facts must be checked with a web search before narration.

## Upload

`vidiq_video_upload` needs a public HTTPS URL; the cloud session cannot reach file hosts. Working routes: the vidIQ file picker (`vidiq_file_upload`, the user selects the file), or the user's Chrome with the Claude extension (YouTube Studio / vidIQ upload page).
