# Realistic look (from v19 on)

The owner asked (25 Nov 2026) for more realistic videos. Toy low-poly (flatShading, primitive blobs, flat colours) is out.
Tested in this sandbox: the setup below renders ~0.6 s per 1080x1920 frame with SwiftShader, so a 25 s Short takes ~8-10 min.

## Scene setup (copy into every new index.html)

```html
<script type="importmap">{"imports":{"three":"/node_modules/three/build/three.module.js","three/addons/":"/node_modules/three/examples/jsm/"}}</script>
```
```js
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap;
const pm=new THREE.PMREMGenerator(renderer); scene.environment=pm.fromScene(new RoomEnvironment(),0.04).texture; // reflections everywhere
sun.castShadow=true; sun.shadow.mapSize.set(2048,2048); sun.shadow.radius=4;   // mesh.castShadow / receiveShadow on the hero objects + ground
const composer=new EffectComposer(renderer); composer.addPass(new RenderPass(scene,camera));
composer.addPass(new UnrealBloomPass(new THREE.Vector2(W/2,H/2),0.25,0.5,0.9)); composer.addPass(new OutputPass());
// in renderAt: composer.render() instead of renderer.render()
```

## Rules
- Materials: MeshStandardMaterial / MeshPhysicalMaterial with `flatShading:false`, real roughness/metalness values (metal 1/0.2-0.4, glass `transmission`, plastic/paint `clearcoat`). Never default grey.
- Geometry: enough segments for smooth silhouettes (spheres 48+, cylinders 32+), bevelled boxes (ExtrudeGeometry with bevel or RoundedBoxGeometry from `three/addons/geometries/RoundedBoxGeometry.js`), LatheGeometry for bottles/bowls.
- Surface detail from canvas textures: subtle noise in `map` and `roughnessMap` (wood grain, concrete, skin, fabric), never a flat fill on big surfaces.
- Light like a film set: one key light with soft shadows, a cooler fill (HemisphereLight low), a rim light behind the subject; contact shadows under every object.
- Atmosphere: `scene.fog` for depth, real sky gradients, particles (dust, droplets, steam) where they belong.
- Camera: 28-50 mm lens (fov 30-45), slow dolly/orbit, rack-focus feel by framing, tiny deterministic hand-held drift (`sin` of t). No snapping cuts without a transition.
- People/animals: proportioned figures (not ball-head toys). If a believable figure isn't possible, show the subject itself (organ, machine, object) close up instead of a mascot.
- Overlays stay crisp and minimal so the 3D image carries the video; captions bottom third, one headline at a time.
- Keep `renderAt(t)` deterministic (no Math.random, no clock); bloom low (strength ≤ 0.3) so it doesn't look like a glow filter.
