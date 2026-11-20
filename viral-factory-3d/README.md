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
| videos/v04-volcano-eruption | Why Do Volcanoes Explode? | dusk island, cutaway with glowing magma + eruption, hazard tags, Bebas | am_adam |
| videos/v05-tallest-buildings | The World's 5 Tallest Buildings | neon night city, towers rise one by one, meter HUD, Space Grotesk | bm_george |
| videos/v06-octopus-5-facts | 5 Facts About Octopuses | sunlit coral reef, see-through octopus, cream fact cards, Montserrat | af_bella |

## Channel rules (standing decisions)

- English, plain titles (no clickbait add-ons), no looping endings.
- Each video gets its own look, palette, voice and music: change `voice` in script.json (af_heart, am_michael, bf_emma, bm_george, am_adam, af_bella …), the scene and the chord set in `sfx.py`.
- 2 videos a day at 15:00 and 21:00 Istanbul, uploaded and scheduled through vidIQ.
- Facts must be checked with a web search before narration.

## Upload

The cloud session cannot send local files to vidIQ (`localFile` is refused) and file-sharing sites are blocked. Working route (since 2026-11-20): the repo is public, so push each `final.mp4` as `<slug>.mp4` to the `shorts-media` branch, check `https://raw.githubusercontent.com/anil88fb/anil-otomasyon/shorts-media/<slug>.mp4` returns 200, then `vidiq_video_upload` with that `url` → draft → publish (scheduled). If the repo is private again the raw URL returns 404; then fall back to the vidIQ file picker (`vidiq_file_upload`).
