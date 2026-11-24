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
- `sfx.py`: music (chord pad, arpeggio, kick, hat) ducked under the voice, plus effects (whoosh, ding, ping, splash, rush, clunk, chime, riser, boom, bubbles). Put a `music.json` in the video folder to set bpm, chords, instrument and the effect plan per segment (see the docstring); effects of type `file` play a sample from `assets/sfx/` (copied from the hyperframes-media SFX library, see its CREDITS.md); without it the v01 plan is used. The second argument is a random seed.
- Fonts installed by setup: Montserrat, Bebas Neue, Space Grotesk, Fredoka, Oswald, JetBrains Mono, Baloo 2, Rubik, Lilita One, Nunito, Archivo Black, Anton, DM Serif Display, Bungee (`/node_modules/@fontsource/<name>/files/...`).

## Videos made

| folder | title | look | voice |
|---|---|---|---|
| examples/v01-tallest-mountains | Earth's 5 Tallest Mountains | Himalaya flyover, Montserrat yellow cards | af_heart |
| videos/v02-ocean-depth | How Deep Is the Ocean? | probe dive + Everest cutaway, cyan sonar HUD, Bebas/Space Grotesk | am_michael |
| videos/v03-canal-locks | How Do Canal Locks Work? | sunny diorama cutaway, orange stickers, Fredoka | bf_emma |
| videos/v04-volcano-eruption | Why Do Volcanoes Explode? | dusk island, cutaway with glowing magma + eruption, hazard tags, Bebas | am_adam |
| videos/v05-tallest-buildings | The World's 5 Tallest Buildings | neon night city, towers rise one by one, meter HUD, Space Grotesk | bm_george |
| videos/v06-octopus-5-facts | 5 Facts About Octopuses | sunlit coral reef, see-through octopus, cream fact cards, Montserrat | af_bella |
| videos/v07-how-elevators-work | How Do Elevators Work? | dusk glass tower cutaway, sheave + counterweight, blueprint HUD, Oswald/JetBrains Mono, sepia Otis 1854 rig | am_liam |
| videos/v08-how-big-is-the-sun | How Big Is the Sun? | deep space, Earth → Jupiter → Sun to scale, 1.3M-Earth fill, gold pills, Baloo 2 | bf_isabella |
| videos/v09-honeybee-5-facts | 5 Facts About Honeybees | wildflower meadow + inside-the-hive comb, waggle dance, hexagon badges, Fredoka | af_sarah |
| videos/v10-deepest-hole | How Deep Have We Dug? | rock-layer cutaway slab, Burj flipped underground, Mponeng mine, Kola borehole, cutaway Earth; copper/slate cards + depth gauge, Montserrat/Space Grotesk | bm_lewis |
| videos/v11-hot-air-balloon | How Does a Hot Air Balloon Fly? | sunrise valley, see-through envelope with hot vs cool air particles, vent, two wind layers, 1783 Montgolfier with sheep/duck/rooster; white cards with coral edge, Baloo 2 | af_nova |
| videos/v12-shark-5-facts | 5 Facts About Sharks | dusk open ocean, x-ray cartilage skeleton, tooth conveyor, electric-sense rings, Greenland shark under sea ice; navy + lime, Bebas/Oswald | am_onyx |
| videos/v13-ears-pop-plane | Why Do Your Ears Pop on a Plane? | turquoise sky over a cloud sea, white/coral airliner climbing, then a see-through ear model (canal, bulging eardrum, air pocket, Eustachian tube) in a plum studio; boarding-pass cards + pressure gauges, Rubik | af_river |
| videos/v14-how-submarines-dive | How Do Submarines Dive? | tropical lagoon, yellow see-through sub with ballast tanks flooding/blowing, vent bubbles, hydroplanes, breach splash; navy stickers with orange dots + depth dial, Lilita One | am_fenrir |
| videos/v15-penguin-5-facts | 5 Facts About Penguins | Antarctic ice shelf under an aurora, emperor colony, deep dive, above/below camouflage swing, salt drip, dad with egg in a snowstorm, low-poly globe with the Arctic crossed out; frosted ice cards, Nunito | bf_lily |
| videos/v16-wrinkly-fingers | Why Do Fingers Wrinkle in Water? | mint-tiled bathroom, hand rising from the bath with fingertips buckling into ridges, x-ray finger with cut nerve, skin-slab cutaway (vessels squeezed), wet-marble test, tire tread in rain; soap-bubble labels + bubble-wipe cuts, Archivo Black, coral highlight | af_kore |
| videos/v17-hiccups | Why Do We Hiccup? | late-night retro diner (plum/teal/mustard, neon), guy with a fizzy soda; x-ray glass bust (lungs, diaphragm dome, stomach, phrenic nerves, vocal cords), womb with hiccuping baby, Iowa farm at night with 1922→1990 counter; neon-sign labels + iris cuts, DM Serif Display + Anton | am_puck |
| videos/v18-lightning-5-facts | 5 Facts About Lightning | violet prairie storm with seeded bolts, night globe flickering 44×/s, bolt vs Sun bar, shock rings bending grass, art-deco tower hit over a lit city, porch flash-to-thunder count; radar-panel cards with bolt badge, Bungee + Space Grotesk, orange accent | bm_daniel |

## Channel rules (standing decisions)

- English, plain titles (no clickbait add-ons), no looping endings.
- Each video gets its own look, palette, voice and music: change `voice` in script.json (af_heart, am_michael, bf_emma, bm_george, am_adam, af_bella …), the scene and the chord set in `sfx.py`.
- 2 videos a day at 15:00 and 21:00 Istanbul, uploaded and scheduled through vidIQ.
- Facts must be checked with a web search before narration.

## Schedule

`SCHEDULE.md` lists every posting slot and its status; take the first free 15:00/21:00 Istanbul slot.

Note: `npm i --no-save <pkg>` prunes other unsaved packages (three.js disappears); install every package in one command as `setup.sh` does.

## Upload

The cloud session cannot send local files to vidIQ (`localFile` is refused) and file-sharing sites are blocked. Working route (since 2026-11-20): the repo is public, so push each `final.mp4` as `<slug>.mp4` to the `shorts-media` branch, check `https://raw.githubusercontent.com/anil88fb/anil-otomasyon/shorts-media/<slug>.mp4` returns 200, then `vidiq_video_upload` with that `url` → draft → publish (scheduled). If the repo is private again the raw URL returns 404; then fall back to the vidIQ file picker (`vidiq_file_upload`).
