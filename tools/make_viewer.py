"""Build a self-contained 3D assembly viewer page (three.js) for one robot.

    python3 tools/make_viewer.py <viz_dir> <out_html>

<viz_dir> holds robot.glb and robot.json from a robot's viz_export.py. The GLB is embedded in
the page as base64 (artifact hosting doesn't serve .glb files), so the page is self-contained.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

TEMPLATE = r"""<title>__TITLE__</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Layout: a workshop inspection bench - the model fills the bench, the job traveler sits beside it. */
:root {
  --bg: #e9edf0; --panel: #fbfcfc; --ink: #17212b; --muted: #556270; --line: #cbd3d9;
  --accent: #c2621a; --accent-soft: #f6e3d3; --pass: #2c7a4b; --pass-soft: #dcefe3; --warn: #9a6200; --warn-soft: #f6ead0;
  --stage: #dde3e8; --stage-floor: #cfd7dd; --grid-major: #aeb9c2; --grid-minor: #c3ccd3;
  --font-display: "Barlow Condensed", "Arial Narrow", "Roboto Condensed", sans-serif;
  --font-body: "Barlow", "Segoe UI", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #10151a; --panel: #172029; --ink: #e3e9ee; --muted: #93a1ad; --line: #283442;
    --accent: #e8893f; --accent-soft: #3a2616; --pass: #62c48b; --pass-soft: #173226; --warn: #e3ac45; --warn-soft: #362a12;
    --stage: #141b22; --stage-floor: #1a232c; --grid-major: #2f3c49; --grid-minor: #222d37; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #10151a; --panel: #172029; --ink: #e3e9ee; --muted: #93a1ad; --line: #283442;
  --accent: #e8893f; --accent-soft: #3a2616; --pass: #62c48b; --pass-soft: #173226; --warn: #e3ac45; --warn-soft: #362a12;
  --stage: #141b22; --stage-floor: #1a232c; --grid-major: #2f3c49; --grid-minor: #222d37; color-scheme: dark;
}
* { box-sizing: border-box; }
html, body { height: 100%; }
body { background: var(--bg); color: var(--ink); font-family: var(--font-body); font-size: 15px; line-height: 1.5;
  display: flex; flex-direction: column; overflow: hidden; }
header.top { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 18px; padding-block: 12px 10px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  border-bottom: 2px solid var(--ink); }
.eyebrow { font-family: var(--font-mono); font-size: 0.72rem; color: var(--accent); letter-spacing: 0.08em; text-transform: uppercase; }
h1 { font-family: var(--font-display); font-weight: 700; font-size: clamp(1.6rem, 3.6vw, 2.4rem); line-height: 1; margin: 0;
  text-transform: uppercase; letter-spacing: 0.01em; text-wrap: balance; }
.meta { font-family: var(--font-mono); font-size: 0.76rem; color: var(--muted); display: flex; flex-wrap: wrap; gap: 4px 16px; }
.meta b { color: var(--ink); font-weight: 500; }
.stamps { display: flex; flex-wrap: wrap; gap: 6px; margin-left: auto; }
.stamp { font-family: var(--font-mono); font-size: 0.68rem; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase;
  padding: 2px 7px; border: 1.5px solid currentColor; border-radius: 3px; white-space: nowrap; }
.stamp.pass { color: var(--pass); background: var(--pass-soft); }
.stamp.warn { color: var(--warn); background: var(--warn-soft); }
.stamp.note { color: var(--accent); background: var(--accent-soft); }
main { flex: 1; min-height: 0; display: grid; grid-template-columns: minmax(0, 1fr) 360px; }
#viewport { position: relative; min-width: 0; min-height: 0; background: var(--stage); }
#viewport canvas { display: block; width: 100%; height: 100%; touch-action: none; }
.hud { position: absolute; left: 12px; bottom: 10px; font-family: var(--font-mono); font-size: 0.7rem; color: var(--muted);
  pointer-events: none; }
#tip { position: absolute; pointer-events: none; background: var(--panel); color: var(--ink); border: 1px solid var(--line);
  border-left: 3px solid var(--accent); padding: 5px 8px; font-size: 0.8rem; border-radius: 3px; max-width: 260px; }
#tip small { display: block; color: var(--muted); font-family: var(--font-mono); font-size: 0.68rem; }
#loading { position: absolute; inset: 0; display: grid; place-items: center; font-family: var(--font-mono); font-size: 0.8rem; color: var(--muted); }
aside { min-width: 0; overflow-y: auto; border-left: 1px solid var(--line); background: var(--panel);
  padding-block: 4px 24px; padding-left: 16px; padding-right: max(16px, env(safe-area-inset-right, 0px)); }
section { padding-block: 12px; border-bottom: 1px solid var(--line); display: grid; gap: 10px; }
section:last-child { border-bottom: 0; }
h2 { font-family: var(--font-display); font-weight: 600; font-size: 1.05rem; text-transform: uppercase; letter-spacing: 0.05em; margin: 0;
  display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
h2 span { font-family: var(--font-mono); font-size: 0.68rem; color: var(--muted); letter-spacing: 0.02em; text-transform: none; font-weight: 400; }
p.lede { margin: 0; color: var(--muted); font-size: 0.9rem; }
.row { display: grid; grid-template-columns: 88px minmax(0, 1fr) 46px; align-items: center; gap: 8px; font-size: 0.86rem; }
.row label { color: var(--muted); }
.row output { font-family: var(--font-mono); font-size: 0.78rem; text-align: right; font-variant-numeric: tabular-nums; }
input[type=range] { width: 100%; accent-color: var(--accent); }
.btns { display: flex; flex-wrap: wrap; gap: 8px; }
button { font-family: var(--font-mono); font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--ink);
  background: transparent; border: 1.5px solid var(--line); border-radius: 3px; padding: 6px 10px; cursor: pointer; }
button:hover { border-color: var(--accent); color: var(--accent); }
button[aria-pressed="true"] { border-color: var(--accent); background: var(--accent-soft); color: var(--accent); }
button:focus-visible, input:focus-visible, li:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.toggles { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px 10px; font-size: 0.85rem; }
.toggles label { display: flex; align-items: center; gap: 6px; }
.toggles i { width: 10px; height: 10px; border-radius: 2px; display: inline-block; box-shadow: 0 0 0 1px var(--line); }
.swatch { display: flex; align-items: center; gap: 10px; font-size: 0.85rem; color: var(--muted); }
.swatch input { width: 36px; height: 24px; border: 1px solid var(--line); background: none; padding: 0; }
ul.parts { list-style: none; margin: 0; padding: 0; display: grid; }
ul.parts li { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 8px; padding: 5px 4px; border-bottom: 1px dashed var(--line);
  font-size: 0.85rem; cursor: pointer; border-radius: 2px; }
ul.parts li:hover, ul.parts li.on { background: var(--accent-soft); }
ul.parts li span:last-child { font-family: var(--font-mono); font-size: 0.75rem; color: var(--muted); }
h3 { font-family: var(--font-mono); font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; margin: 6px 0 0; font-weight: 500; }
.tbl { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 0.8rem; }
th, td { text-align: left; padding: 4px 6px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font-family: var(--font-mono); font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); font-weight: 500; }
td.n { text-align: right; font-family: var(--font-mono); font-variant-numeric: tabular-nums; white-space: nowrap; }
tfoot td { font-weight: 600; border-bottom: 0; }
dl { margin: 0; display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 4px 12px; font-size: 0.84rem; }
dt { color: var(--muted); font-family: var(--font-mono); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; padding-top: 2px; }
dd { margin: 0; }
@media (max-width: 860px) {
  body { overflow: auto; height: auto; }
  main { grid-template-columns: minmax(0, 1fr); }
  #viewport { height: 62vh; min-height: 340px; }
  aside { border-left: 0; border-top: 1px solid var(--line); overflow: visible; padding-left: max(16px, env(safe-area-inset-left, 0px)); }
  .stamps { margin-left: 0; }
}
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; } }
</style>

<header class="top">
  <div style="display:grid;gap:4px;min-width:0">
    <span class="eyebrow">__EYEBROW__</span>
    <h1>__TITLE__</h1>
    <div class="meta" id="meta"></div>
  </div>
  <div class="stamps" id="stamps"></div>
</header>
<main>
  <div id="viewport">
    <div id="loading">Loading the assembly…</div>
    <div id="tip" hidden></div>
    <div class="hud">drag to orbit · scroll or pinch to zoom · right-drag to pan · hover a part for its name</div>
  </div>
  <aside>
    <section>
      <p class="lede" id="lede"></p>
    </section>
    <section id="poseSec">
      <h2>__POSE_TITLE__ <span id="poseNote"></span></h2>
      <div id="joints" style="display:grid;gap:6px"></div>
      <div class="btns" id="poseBtns"></div>
    </section>
    <section>
      <h2>View</h2>
      <div class="row"><label for="explode">Exploded</label><input type="range" id="explode" min="0" max="100" value="0"><output id="explodeOut">0 %</output></div>
      <div class="toggles" id="cats"></div>
      <div class="swatch"><input type="color" id="petg" aria-label="Printed part colour"><span>Printed-part colour (PETG)</span></div>
      <div class="btns"><button type="button" id="resetView">Reset view</button></div>
    </section>
    <section>
      <h2>Parts list <span id="partCount"></span></h2>
      <div id="partsList"></div>
    </section>
    <section>
      <h2>Print plan <span>PETG · 0.20 mm · MK3S</span></h2>
      <div class="tbl"><table id="printTbl"><thead><tr><th>Part</th><th>Qty</th><th class="n">Time</th><th class="n">PETG</th></tr></thead><tbody></tbody><tfoot></tfoot></table></div>
    </section>
    <section>
      <h2>Build facts</h2>
      <dl id="facts"></dl>
    </section>
  </aside>
</main>

<script type="application/json" id="cfg">__CFG__</script>
<script type="application/octet-stream" id="glb">__GLB__</script>
<script type="importmap">
{ "imports": {
  "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
} }
</script>
<script type="module">
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const cfg = JSON.parse(document.getElementById('cfg').textContent);
const $ = (id) => document.getElementById(id);
const deg = THREE.MathUtils.degToRad;
const CAT = { printed: 'Printed parts', actuator: 'Servos & motors', electronics: 'Boards & chips', power: 'Power',
              hardware: 'Screws, nuts & pins', wiring: 'Leads' };
const CAT_DOT = { printed: cfg.petg, actuator: '#1e1f22', electronics: '#1e46a0', power: '#c82824', hardware: '#babec4', wiring: '#ec8020' };

// ---- page text -------------------------------------------------------------------------
$('lede').textContent = cfg.page.lede;
for (const [k, v] of cfg.page.meta) { const s = document.createElement('span'); s.innerHTML = `${k} <b></b>`; s.querySelector('b').textContent = v; $('meta').append(s); }
for (const st of cfg.page.stamps) { const s = document.createElement('span'); s.className = `stamp ${st.kind}`; s.textContent = st.text; $('stamps').append(s); }
for (const [k, v] of cfg.page.facts) { const dt = document.createElement('dt'); dt.textContent = k; const dd = document.createElement('dd'); dd.textContent = v; $('facts').append(dt, dd); }
{
  const tb = $('printTbl').tBodies[0]; let h = 0, g = 0, n = 0, todo = 0;
  for (const p of cfg.printed_parts) {
    const tr = tb.insertRow();
    tr.insertCell().textContent = p.label;
    tr.insertCell().textContent = p.plates > 1 ? `${p.qty} (${p.plates} plates)` : String(p.qty);
    const ph = p.hours != null ? p.hours * (p.plates || 1) : null, pg = p.grams != null ? p.grams * (p.plates || 1) : null;
    const c1 = tr.insertCell(); c1.className = 'n'; c1.textContent = ph != null ? `${ph.toFixed(1)} h` : '—';
    const c2 = tr.insertCell(); c2.className = 'n'; c2.textContent = pg != null ? `${pg.toFixed(0)} g` : '—';
    h += ph || 0; g += pg || 0; n += p.qty; if (ph == null) todo += 1;
  }
  const tf = $('printTbl').tFoot.insertRow();
  tf.insertCell().textContent = 'Total'; tf.insertCell().textContent = String(n);
  const more = todo ? ` + ${todo} not sliced` : '';   // never present a partial sum as the total
  const a = tf.insertCell(); a.className = 'n'; a.textContent = h ? `${h.toFixed(1)} h${more}` : '—';
  const b = tf.insertCell(); b.className = 'n'; b.textContent = g ? `${g.toFixed(0)} g${more}` : '—';
}

// ---- renderer, scene, theme ------------------------------------------------------------
const vp = $('viewport');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
vp.prepend(renderer.domElement);
const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
const camera = new THREE.PerspectiveCamera(32, 1, 2, 8000);
camera.up.set(0, 0, 1);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
const hemi = new THREE.HemisphereLight(0xffffff, 0x8899aa, 0.55);
hemi.position.set(0, 0, 1); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 1.6);
sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.6;
scene.add(sun, sun.target);
const groundMat = new THREE.MeshStandardMaterial({ roughness: 0.95, metalness: 0 });
const ground = new THREE.Mesh(new THREE.CircleGeometry(1, 96), groundMat);
ground.receiveShadow = true; scene.add(ground);
let grid = null;
const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
function applyTheme() {
  scene.background = new THREE.Color(css('--stage'));
  groundMat.color = new THREE.Color(css('--stage-floor'));
  if (grid) scene.remove(grid);
  const r = ground.scale.x || 400;
  grid = new THREE.GridHelper(r * 2, Math.round(r * 2 / 20), new THREE.Color(css('--grid-major')), new THREE.Color(css('--grid-minor')));
  grid.rotation.x = Math.PI / 2; grid.position.set(ground.position.x, ground.position.y, cfg.ground_z + 0.05);
  grid.material.transparent = true; grid.material.opacity = 0.7; scene.add(grid);
}
new MutationObserver(applyTheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'class'] });
window.matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change', applyTheme);

function resize() {
  const w = vp.clientWidth, h = vp.clientHeight;
  renderer.setSize(w, h, false); camera.aspect = w / Math.max(h, 1); camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(vp);

// ---- load the model --------------------------------------------------------------------
const parts = [];           // {obj, label, category, info, base: Vector3, center: Vector3 (local)}
const joints = [];          // {obj, sign, ...}
let model = null, modelCenter = new THREE.Vector3(), modelRadius = 300;
const state = { explode: 0, demo: false, demoT: 0, anim: false, s: 0, phase: 0 };

// the model ships inside the page (base64 GLB), so nothing is fetched
const glbText = document.getElementById('glb').textContent.trim();
const glbBytes = Uint8Array.from(atob(glbText), (c) => c.charCodeAt(0));
new GLTFLoader().parse(glbBytes.buffer, '', (gltf) => {
  model = gltf.scene; scene.add(model);
  model.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  for (const [name, meta] of Object.entries(cfg.nodes)) {
    const obj = model.getObjectByName(name);
    if (!obj) continue;
    obj.traverse((o) => { if (o.isMesh) { o.material = o.material.clone(); o.userData.part = obj; } });
    const box = new THREE.Box3().setFromObject(obj);
    obj.updateWorldMatrix(true, false);
    const center = obj.worldToLocal(box.getCenter(new THREE.Vector3()));
    parts.push({ obj, ...meta, base: obj.position.clone(), center });
  }
  for (const j of cfg.joints || []) {
    // a joint either turns its own node about local Z, or (with "drives") moves several nodes
    // together: {"node", "rot": deg per unit about local Z} or {"node", "move": [x, y, z] per unit}
    const obj = model.getObjectByName(j.node);
    const drives = (j.drives || []).map((d) => { const o = model.getObjectByName(d.node); return o ? { ...d, obj: o, base: o.position.clone() } : null; }).filter(Boolean);
    if (obj || drives.length) joints.push({ ...j, obj, drives });
  }
  setupPose(); applyPose();
  const box = new THREE.Box3().setFromObject(model);
  box.getCenter(modelCenter); modelRadius = box.getSize(new THREE.Vector3()).length() / 2;
  ground.scale.setScalar(modelRadius * 3.2); ground.position.set(modelCenter.x, modelCenter.y, cfg.ground_z);
  sun.position.set(modelCenter.x + modelRadius * 1.2, modelCenter.y - modelRadius * 1.6, modelCenter.z + modelRadius * 2.4);
  sun.target.position.copy(modelCenter);
  const sc = sun.shadow.camera; sc.left = sc.bottom = -modelRadius * 1.6; sc.right = sc.top = modelRadius * 1.6;
  sc.near = 1; sc.far = modelRadius * 8; sc.updateProjectionMatrix();
  applyTheme(); resetView(); buildLists(); $('loading').hidden = true;
}, (err) => { $('loading').textContent = 'The 3D model could not load. Reload the page to try again.'; console.error(err); });

function resetView() {
  // keep the configured viewing direction, but fit the whole model to this window's shape
  const c = cfg.camera, target = new THREE.Vector3(...c.target);
  const dir = new THREE.Vector3(...c.pos).sub(target).normalize();
  const fv = deg(camera.fov), fh = 2 * Math.atan(Math.tan(fv / 2) * camera.aspect);
  const dist = (modelRadius * 0.92) / Math.sin(Math.min(fv, fh) / 2);
  const want = new THREE.Vector3(...c.pos).distanceTo(target);
  camera.position.copy(target).addScaledVector(dir, Math.max(dist, want * 0.6));
  controls.target.copy(target); controls.update();
}
$('resetView').addEventListener('click', resetView);

// ---- pose: joints, demo, rover tracks, hexapod gait --------------------------------------
function setupPose() {
  const box = $('joints');
  if (cfg.robot === 'rover') {
    $('poseNote').textContent = 'tracks and sprockets';
    const r = document.createElement('div'); r.className = 'row';
    r.innerHTML = '<label for="speed">Speed</label><input type="range" id="speed" min="0" max="100" value="40"><output id="speedOut">40 %</output>';
    box.append(r);
    $('speed').addEventListener('input', (e) => { $('speedOut').textContent = `${e.target.value} %`; });
    addBtn('Drive', () => { state.anim = !state.anim; return state.anim; }, true);
    state.anim = true;
  } else {
    for (const j of joints) {
      const id = `j_${j.node}`;
      const r = document.createElement('div'); r.className = 'row';
      r.innerHTML = `<label for="${id}"></label><input type="range" id="${id}" min="${j.min}" max="${j.max}" value="${j.value}" step="1"><output></output>`;
      r.querySelector('label').textContent = j.label;
      const out = r.querySelector('output'); out.textContent = fmtJoint(j);
      r.querySelector('input').addEventListener('input', (e) => {
        j.value = +e.target.value; out.textContent = fmtJoint(j); state.demo = false; state.anim = false; syncBtns(); applyPose();
      });
      j.input = r.querySelector('input'); j.out = out;
      box.append(r);
    }
    if (cfg.robot === 'arm') { $('poseNote').textContent = 'servo angles'; addBtn('Play demo', () => { state.demo = !state.demo; state.demoT = 0; return state.demo; }); }
    if (cfg.robot === 'hexapod') { $('poseNote').textContent = 'left middle leg'; addBtn('Walk', () => { state.anim = !state.anim; return state.anim; }, true); state.anim = true; }
  }
}
const btns = [];
function addBtn(text, fn, pressed = false) {
  const b = document.createElement('button'); b.type = 'button'; b.textContent = text; b.setAttribute('aria-pressed', String(pressed));
  b.addEventListener('click', () => b.setAttribute('aria-pressed', String(fn()))); $('poseBtns').append(b); btns.push([b, text]);
}
function syncBtns() { for (const [b] of btns) b.setAttribute('aria-pressed', 'false'); }
const fmtJoint = (j) => (j.unit === 'mm' ? `${j.value} mm` : `${j.value}°`);
function applyPose() {
  for (const j of joints) {
    if (j.drives.length) {
      for (const d of j.drives) {
        if (d.rot !== undefined) d.obj.rotation.z = deg(d.rot * j.value);
        if (d.move) d.obj.position.set(d.base.x + d.move[0] * j.value, d.base.y + d.move[1] * j.value, d.base.z + d.move[2] * j.value);
      }
    } else if (j.obj) j.obj.rotation.z = deg(j.sign * j.value);
  }
}

const ease = (t) => t * t * (3 - 2 * t);
function stepDemo(dt) {
  const k = cfg.demo; const seg = 1.7; state.demoT = (state.demoT + dt) % (seg * (k.length - 1));
  const i = Math.floor(state.demoT / seg), t = ease((state.demoT % seg) / seg);
  joints.forEach((j, n) => { j.value = Math.round(k[i][n] + (k[i + 1][n] - k[i][n]) * t); j.input.value = j.value; j.out.textContent = fmtJoint(j); });
  applyPose();
}

// rover: links follow the pitch path; sprockets, idlers and road wheels spin
const tk = cfg.tracks;
let trackLinks = [], spinners = [];
function trackPos(u, out) {
  const { x1, za, r, P } = tk, L1 = x1, A = Math.PI * r, Ltot = 2 * x1 + 2 * A;
  u = ((u % Ltot) + Ltot) % Ltot;
  if (u < L1) return out.set(u, 0, za - r);
  u -= L1; if (u < A) { const a = -Math.PI / 2 + u / r; return out.set(x1 + r * Math.cos(a), 0, za + r * Math.sin(a)); }
  u -= A; if (u < L1) return out.set(x1 - u, 0, za + r);
  u -= L1; const a = Math.PI / 2 + u / r; return out.set(r * Math.cos(a), 0, za + r * Math.sin(a));
}
const _p0 = new THREE.Vector3(), _p1 = new THREE.Vector3(), _x = new THREE.Vector3(), _y = new THREE.Vector3(0, 1, 0), _z = new THREE.Vector3(), _m = new THREE.Matrix4();
function placeTracks() {
  if (!trackLinks.length && tk) {
    for (const side of tk.sides) side.links.forEach((n, i) => { const o = model.getObjectByName(n); if (o) trackLinks.push({ o, i, y: side.y }); });
    for (const sp of tk.spinners) { const o = model.getObjectByName(sp.node); if (o) spinners.push({ o, f: sp.per_mm }); }
  }
  for (const L of trackLinks) {
    const u = L.i * tk.P + state.s;
    trackPos(u, _p0); trackPos(u + tk.P, _p1);
    _x.subVectors(_p1, _p0).normalize(); _z.crossVectors(_x, _y);
    _m.makeBasis(_x, _y, _z); L.o.quaternion.setFromRotationMatrix(_m);
    L.o.position.set(_p0.x, L.y, _p0.z);
  }
  for (const s of spinners) s.o.rotation.z = s.f * state.s;
}

// hexapod: tripod walk in place
function stepGait(dt) {
  const g = cfg.gait; state.phase = (state.phase + dt / g.period) % 1;
  if (g.frames) {   // keyframes per leg: [coxa, femur, tibia] node angles (deg) over one cycle, e.g. from an IK gait
    const n = g.frames[0].length, u = state.phase * n, i = Math.floor(u) % n, k = (i + 1) % n, a = u - Math.floor(u);
    g.legs.forEach((leg, li) => {
      const A = g.frames[li][i], B = g.frames[li][k], v = A.map((x, m) => x + (B[m] - x) * a);
      if (!leg.objs) { leg.objs = {}; for (const key of ['coxa', 'femur', 'tibia']) leg.objs[key] = model.getObjectByName(leg[key]); }
      ['coxa', 'femur', 'tibia'].forEach((key, m) => { const o = leg.objs[key]; if (o) o.rotation.z = deg(v[m]); });
      if (leg.show) joints.forEach((j, m) => { j.value = Math.round(v[m] * j.sign); j.input.value = j.value; j.out.textContent = `${j.value}°`; });
    });
    return;
  }
  for (const leg of g.legs) {
    const ph = (state.phase + (leg.tripod ? 0.5 : 0)) % 1;
    let c, f, t;
    if (ph < 0.5) { const s = ph / 0.5; c = -g.swing + 2 * g.swing * ease(s); f = g.lift * Math.sin(Math.PI * s); t = g.tuck * Math.sin(Math.PI * s); }
    else { const s = (ph - 0.5) / 0.5; c = g.swing - 2 * g.swing * s; f = 0; t = 0; }
    const set = (n, v) => { const o = leg.objs?.[n]; if (o) o.rotation.z = deg(v); };
    if (!leg.objs) { leg.objs = {}; for (const k of ['coxa', 'femur', 'tibia']) leg.objs[k] = model.getObjectByName(leg[k]); }
    set('coxa', leg.dir * c); set('femur', f); set('tibia', t);
    if (leg.show) { const vals = [leg.dir * c, f, t]; joints.forEach((j, n) => { j.value = Math.round(vals[n] * j.sign); j.input.value = j.value; j.out.textContent = `${j.value}°`; }); }
  }
}

// ---- explode, visibility, parts list, hover -------------------------------------------
function explode() {
  for (const p of parts) p.obj.position.copy(p.base);
  if (!state.explode) return;
  model.updateMatrixWorld(true);
  const k = state.explode * 0.9;
  const w = new THREE.Vector3(), w2 = new THREE.Vector3(), a = new THREE.Vector3(), b = new THREE.Vector3();
  const origin = new THREE.Vector3(modelCenter.x, modelCenter.y, cfg.ground_z);   // explode outward and up, never through the floor
  for (const p of parts) {
    p.obj.localToWorld(w.copy(p.center));
    w2.subVectors(w, origin).multiplyScalar(k).add(w);
    const parent = p.obj.parent;
    a.copy(w); parent.worldToLocal(a); b.copy(w2); parent.worldToLocal(b);
    p.obj.position.add(b.sub(a));
  }
}
$('explode').addEventListener('input', (e) => { state.explode = e.target.value / 100; $('explodeOut').textContent = `${e.target.value} %`; });

const hidden = new Set();
function buildLists() {
  // category toggles
  const counts = {};
  for (const p of parts) counts[p.category] = (counts[p.category] || 0) + 1;
  for (const c of Object.keys(CAT)) {
    if (!counts[c]) continue;
    const l = document.createElement('label');
    l.innerHTML = `<input type="checkbox" checked id="cat_${c}"><i></i><span></span>`;
    l.querySelector('i').style.background = c === 'printed' ? cfg.petg : CAT_DOT[c];
    l.querySelector('span').textContent = CAT[c];
    l.querySelector('input').addEventListener('change', (e) => {
      e.target.checked ? hidden.delete(c) : hidden.add(c);
      for (const p of parts) p.obj.visible = !hidden.has(p.category);
    });
    $('cats').append(l);
  }
  // parts list grouped by label
  const groups = {};
  for (const p of parts) { const key = `${p.category}|${p.label}`; (groups[key] ||= []).push(p); }
  let total = 0;
  for (const c of Object.keys(CAT)) {
    const keys = Object.keys(groups).filter((k) => k.startsWith(c + '|'));
    if (!keys.length) continue;
    const h = document.createElement('h3'); h.textContent = CAT[c]; $('partsList').append(h);
    const ul = document.createElement('ul'); ul.className = 'parts';
    for (const k of keys.sort()) {
      const items = groups[k]; total += items.length;
      const li = document.createElement('li'); li.tabIndex = 0;
      li.innerHTML = '<span></span><span></span>';
      li.children[0].textContent = items[0].label; li.children[1].textContent = `× ${items.length}`;
      const pick = () => { const on = !li.classList.contains('on'); document.querySelectorAll('ul.parts li.on').forEach((x) => x.classList.remove('on')); highlight(on ? items : []); if (on) li.classList.add('on'); };
      li.addEventListener('click', pick); li.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(); } });
      ul.append(li);
    }
    $('partsList').append(ul);
  }
  $('partCount').textContent = `${total} items`;
  // printed colour
  const pc = $('petg'); pc.value = cfg.petg;
  pc.addEventListener('input', (e) => {
    for (const p of parts) if (p.category === 'printed') p.obj.traverse((o) => { if (o.isMesh) o.material.color.set(e.target.value); });
    document.querySelector('#cats i').style.background = e.target.value;
  });
}
let lit = [];
function highlight(items) {
  for (const p of lit) p.obj.traverse((o) => { if (o.isMesh) o.material.emissive?.setRGB(0, 0, 0); });
  lit = items;
  const col = new THREE.Color(css('--accent'));
  for (const p of lit) p.obj.traverse((o) => { if (o.isMesh) { o.material.emissive?.copy(col); o.material.emissiveIntensity = 0.45; } });
}
const ray = new THREE.Raycaster(), ptr = new THREE.Vector2(); let hoverAt = 0;
renderer.domElement.addEventListener('pointermove', (e) => {
  const now = performance.now(); if (now - hoverAt < 50 || !model) return; hoverAt = now;
  const r = renderer.domElement.getBoundingClientRect();
  ptr.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ptr, camera);
  const hit = ray.intersectObject(model, true).find((h) => h.object.visible && h.object.userData.part && h.object.userData.part.visible);
  const tip = $('tip');
  if (!hit) { tip.hidden = true; return; }
  const meta = cfg.nodes[hit.object.userData.part.name] || {};
  tip.innerHTML = '<span></span><small></small>';
  tip.children[0].textContent = meta.label || hit.object.userData.part.name;
  tip.children[1].textContent = `${CAT[meta.category] || ''}${meta.info ? ' · ' + meta.info : ''}`;
  tip.hidden = false;
  tip.style.left = `${Math.min(e.clientX - r.left + 14, r.width - 270)}px`; tip.style.top = `${e.clientY - r.top + 14}px`;
});
renderer.domElement.addEventListener('pointerleave', () => { $('tip').hidden = true; });

// ---- loop --------------------------------------------------------------------------------
const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
let last = performance.now();
function tick(now) {
  const dt = Math.min(0.05, (now - last) / 1000); last = now;
  if (model) {
    if (cfg.robot === 'arm' && state.demo) stepDemo(dt);
    if (cfg.robot === 'rover') { if (state.anim && !reduce) state.s += dt * ($('speed')?.value || 0) * 1.2 * (tk.dir || 1); placeTracks(); }
    if (cfg.robot === 'hexapod' && state.anim && !reduce) stepGait(dt);
    explode();
  }
  controls.update(); renderer.render(scene, camera);
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);
</script>
"""


def main(viz_dir: Path, out_html: Path):
    import base64
    cfg = json.loads((viz_dir / "robot.json").read_text())
    glb64 = base64.b64encode((viz_dir / "robot.glb").read_bytes()).decode("ascii")
    page = cfg["page"]
    html = (TEMPLATE.replace("__TITLE__", page["title"]).replace("__EYEBROW__", page["eyebrow"])
            .replace("__POSE_TITLE__", page.get("pose_title", "Pose"))
            .replace("__CFG__", json.dumps(cfg, separators=(",", ":")).replace("</", "<\\/"))
            .replace("__GLB__", glb64))
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html, encoding="utf-8")
    print(f"{out_html} {len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
