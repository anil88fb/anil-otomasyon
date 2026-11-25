# Shorts engine — "Why?" channel (@askdailywhy)

Renders 1080×1920 animated explainer Shorts in pure Python (numpy + OpenCV + PIL + ffmpeg).

## Setup (fresh session)
```
mkdir -p /home/claude/shorts && cp shorts-engine/lib.py shorts-engine/grab.sh /home/claude/shorts/
bash shorts-engine/setup_fonts.sh
pip install --break-system-packages fonttools opencv-python-headless pillow numpy   # if missing
```

## Make a video
1. `mkdir -p /home/claude/shorts/vN/vo`
2. Voice 6 lines with Speko `audio_synthesize` (one call per line, sequentially, English, a different voice per video).
   Then `bash /home/claude/shorts/grab.sh /home/claude/shorts/vN/vo 6` copies the newest 6 Speko wavs as l1..l6.
3. Copy an example from `examples/` to `/home/claude/shorts/vN/make.py`, change `D`, `LINES`, palette and the 6 scenes.
4. Preview: `python3 make.py shot 2 6 11 16 21 27` → `sheet.png` (look at it, fix overlaps/clipping).
5. Render: `python3 make.py full` → `/home/claude/<name>.mp4` (video + voice + generated music + SFX).
6. Check before upload: `python3 shorts-tools/kontrol.py /home/claude/<name>.mp4 --duzelt --sikistir`
   (fixes loudness to -14 LUFS, shrinks the file so it stays well under GitHub's 100 MB limit).

Optional helpers from `shorts-tools/` (run `bash shorts-tools/kurulum.sh` once per session):
- Real SFX instead of synthetic beeps: `earshot make "a soft pop as a bubble appears" -o vN/sfx/pop.ogg`.
- Cut on the music: `python3 shorts-tools/ritim.py music.wav --cikti vN/beats.json`, move scene changes to the nearest beat.
- Captions/timing from the voice: `python3 shorts-tools/zamanla.py vN/vo/l1.wav --metin line1.txt --dil en`.
- Cut-out images (user photos, objects): `python3 shorts-tools/dekupe.py image.png`.

## Channel rules
- English only. Formats: body/everyday "Why…?", "What if…?", "How to build…" (problem → fix chain).
- 25–35 s, 6 narrated lines, hook in the first line, ending card "Follow for…".
- Every video: its own style preset from `anil-otomasyon/.claude/skills/hyperframes-creative/frame-presets/*/FRAME.md`
  (colors + fonts), its own character, voice and music mood. Never repeat a style twice in a row.
- Max 2 posts/day at 15:00 and 21:00 Europe/Istanbul. Never publish several at once.
- Check facts before narrating them.

## Style presets used so far
broadside (black hole), coral (lighthouse), cobalt-grid (moon), daisy-days (fingers), blue-professional (igloo),
bold-poster (earth), blockframe (submarine), creative-mode (skyscraper), capsule (sneeze), cartesian (underwater tunnel),
biennale-yellow (tickle), editorial-forest (sun disappears). All 13 presets used once; cycle again, least-recent first.
