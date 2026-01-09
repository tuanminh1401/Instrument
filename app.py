import streamlit as st
import streamlit.components.v1 as components
import numpy as np

# --- 1. Streamlit Config & UI Setup ---
st.set_page_config(
    page_title="3D Virtual Instrument Simulator",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🎵"
)

# Custom CSS for that "Vibe Coding" aesthetic
st.markdown("""
<style>
    /* Dark Background & Neon Accents */
    .stApp {
        background-color: #050505; /* Deep Black */
        color: #ffffff;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #00FFA3 !important; /* Neon Green */
        text-shadow: 0px 0px 15px rgba(0, 255, 163, 0.6);
    }
    /* Hide Streamlit Header/Footer for immersion */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    
    /* Overlay UI for the "Pro" feel */
    .ui-overlay {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 100;
        pointer-events: none;
    }
    
    .status-badge {
        background: rgba(0, 255, 163, 0.1);
        border: 1px solid #00FFA3;
        color: #00FFA3;
        padding: 5px 10px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
        backdrop-filter: blur(5px);
    }
</style>
""", unsafe_allow_html=True)

# st.title("🎹 3D Virtual Instrument Simulator") 
# Commented out title to let the 3D scene take over full screen

# --- 2. Three.js + Tone.js HTML Injection ---
three_js_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Instrument Carousel</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #050505; font-family: 'Segoe UI', sans-serif; color: white; user-select: none; }
        #canvas-container { width: 100%; height: 100vh; display: block; background: radial-gradient(circle at center, #1a1a1a 0%, #000000 100%); }
        #overlay { position: absolute; bottom: 30px; left: 30px; pointer-events: none; text-align: left; }
        .title { font-size: 40px; font-weight: 800; color: white; text-shadow: 0 0 20px rgba(255,255,255,0.2); margin: 0; letter-spacing: -1px; }
        .subtitle { font-size: 14px; color: #00FFA3; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; text-shadow: 0 0 10px rgba(0,255,163,0.5); }
        .instruction { color: #888; font-size: 12px; margin-top: 10px; font-family: monospace; }
        #loading { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #00FFA3; font-size: 18px; text-transform: uppercase; letter-spacing: 4px; text-align: center; width: 80%; }
        #error-log { color: #ff3333; font-size: 12px; margin-top: 20px; text-transform: none; letter-spacing: normal; background: rgba(0,0,0,0.8); padding: 10px; border: 1px solid #ff3333; display: none;}
    </style>
    <!-- Dependencies -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tween.js/18.6.4/tween.umd.js"></script>
</head>
<body>
    <div id="loading">
        System Initializing...
        <div id="error-log"></div>
    </div>
    <div id="canvas-container"></div>
    <div id="overlay">
        <div class="subtitle">Virtual Studio</div>
        <div class="title" id="inst-name">Grand Piano</div>
        <div class="instruction">[CLICK] PLAY NOTE &nbsp;•&nbsp; [DRAG] ROTATE &nbsp;•&nbsp; [DOUBLE-CLICK] SWITCH FOCUS</div>
    </div>

    <script type="module">
        // Error Handling
        window.onerror = function(msg, url, line, col, error) {
            const log = document.getElementById('error-log');
            log.style.display = 'block';
            log.innerHTML = `ERROR: ${msg}<br>Line: ${line}`;
            document.getElementById('loading').innerHTML = "SYSTEM ERROR";
            document.getElementById('loading').appendChild(log);
            return false;
        };

        // Use esm.sh for reliable module resolution without import maps
        import * as THREE from 'https://esm.sh/three@0.160.0';
        import { OrbitControls } from 'https://esm.sh/three@0.160.0/examples/jsm/controls/OrbitControls.js';
        import { EffectComposer } from 'https://esm.sh/three@0.160.0/examples/jsm/postprocessing/EffectComposer.js';
        import { RenderPass } from 'https://esm.sh/three@0.160.0/examples/jsm/postprocessing/RenderPass.js';
        import { UnrealBloomPass } from 'https://esm.sh/three@0.160.0/examples/jsm/postprocessing/UnrealBloomPass.js';

        // --- STATE & SETUP ---
        const instruments = [
            { type: 'piano', name: 'Grand Piano' },
            { type: 'guitar', name: 'Cyber Guitar' },
            { type: 'sax', name: 'Neon Sax' }
        ];
        let activeIndex = 0;
        const instNameEl = document.getElementById('inst-name');
        const container = document.getElementById('canvas-container');
        const loading = document.getElementById('loading');

        try {
            const scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x050505, 0.02);

            const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 100);
            camera.position.set(0, 4, 14);

            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // Limit pixel ratio for perf
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.0;
            renderer.shadowMap.enabled = true;
            container.appendChild(renderer.domElement);

            // --- COMPOSER ---
            const renderScene = new RenderPass(scene, camera);
            const bloomPass = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85);
            bloomPass.threshold = 0;
            bloomPass.strength = 1.2;
            bloomPass.radius = 0.5;

            const composer = new EffectComposer(renderer);
            composer.addPass(renderScene);
            composer.addPass(bloomPass);

            // --- CONTROLS + LIGHTS ---
            const controls = new OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.minDistance = 5;
            controls.maxDistance = 20;

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.05);
            scene.add(ambientLight);
            const spotLight = new THREE.SpotLight(0xffffff, 100);
            spotLight.position.set(5, 10, 5);
            spotLight.castShadow = true;
            scene.add(spotLight);
            const rimLight = new THREE.SpotLight(0x00ffff, 50);
            rimLight.position.set(-5, 5, -5);
            scene.add(rimLight);
            const fillLight = new THREE.PointLight(0xff0080, 2, 20);
            fillLight.position.set(-5, 2, 5);
            scene.add(fillLight);
            const gridHelper = new THREE.GridHelper(50, 50, 0x333333, 0x111111);
            gridHelper.position.y = -2;
            scene.add(gridHelper);

            // --- PARTICLES ---
            const particlesGeo = new THREE.BufferGeometry();
            const particlesCount = 200;
            const posArray = new Float32Array(particlesCount * 3);
            const particleColors = new Float32Array(particlesCount * 3);
            for(let i=0; i<particlesCount * 3; i+=3) {
                posArray[i] = (Math.random() - 0.5) * 30;
                posArray[i+1] = (Math.random() - 0.5) * 20 + 5;
                posArray[i+2] = (Math.random() - 0.5) * 30;
                particleColors[i] = 0;
                particleColors[i+1] = 0.5 + Math.random() * 0.5; 
                particleColors[i+2] = 0.5 + Math.random() * 0.5;
            }
            particlesGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
            particlesGeo.setAttribute('color', new THREE.BufferAttribute(particleColors, 3));
            const particlesMesh = new THREE.Points(particlesGeo, new THREE.PointsMaterial({ size: 0.1, vertexColors: true, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending }));
            scene.add(particlesMesh);

            // --- MATERIALS ---
            const plasticMat = new THREE.MeshPhysicalMaterial({ color: 0x111111, roughness: 0.1, metalness: 0.1, clearcoat: 1.0 });
            const neonMat = new THREE.MeshStandardMaterial({ color: 0x000000, emissive: 0x00FFA3, emissiveIntensity: 2 });
            const goldMat = new THREE.MeshStandardMaterial({ color: 0xffcc00, roughness: 0.3, metalness: 1.0 });

            // --- MODELS ---
            function createPiano() {
                const group = new THREE.Group();
                const shape = new THREE.Shape(); shape.moveTo(0,0); shape.lineTo(4,0); shape.quadraticCurveTo(4, 4, 2, 6); shape.lineTo(0, 6); shape.lineTo(0, 0);
                const body = new THREE.Mesh(new THREE.ExtrudeGeometry(shape, {depth:1, bevelEnabled:true, bevelThickness:0.1, bevelSize:0.1}), plasticMat);
                body.rotation.x = -Math.PI/2; body.position.set(-2,0,-3); group.add(body);
                const keys = new THREE.Group();
                for(let i=0; i<8; i++) {
                    let k = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.2, 1.2), new THREE.MeshStandardMaterial({color:0xffffff}));
                    k.position.set(-1.8 + i*0.5, 0.8, 2.4); k.userData = {note: ["C4","D4","E4","F4","G4","A4","B4","C5"][i]}; keys.add(k);
                    if([0,1,3,4,5].includes(i)){
                        let bk = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.25, 0.8), new THREE.MeshStandardMaterial({color:0x111111}));
                        bk.position.set(-1.8 + i*0.5 + 0.25, 0.95, 2.2); bk.userData = {note:"C#4"}; keys.add(bk);
                    }
                }
                group.add(keys);
                return group;
            }

            function createGuitar() {
                const group = new THREE.Group();
                const shape = new THREE.Shape(); shape.moveTo(0,-1.5); shape.bezierCurveTo(1.5,-1.5,1.5,1.5,0,1.5); shape.bezierCurveTo(-0.5,1.5,-0.5,0.5,0,0); shape.bezierCurveTo(-1.2,0.5,-1.5,-1.5,0,-1.5);
                const body = new THREE.Mesh(new THREE.ExtrudeGeometry(shape, {depth:0.3, bevelEnabled:true, bevelThickness:0.05}), new THREE.MeshStandardMaterial({color:0xaa0000, metalness:0.6}));
                body.center(); group.add(body);
                const neck = new THREE.Mesh(new THREE.BoxGeometry(0.4, 3.5, 0.15), new THREE.MeshStandardMaterial({color:0xd2b48c}));
                neck.position.set(0, 2, 0.1); group.add(neck);
                for(let i=0; i<4; i++){ let s = new THREE.Mesh(new THREE.CylinderGeometry(0.01,0.01,3.5), neonMat); s.position.set(-0.15+i*0.1, 2, 0.25); s.userData={note:"E3"}; group.add(s); }
                return group;
            }

            function createSax() {
                const group = new THREE.Group();
                const path = new THREE.CatmullRomCurve3([new THREE.Vector3(0,-1.5,0), new THREE.Vector3(0,1.5,0), new THREE.Vector3(0.5,2.0,0), new THREE.Vector3(1.0,1.5,0)]);
                const tube = new THREE.Mesh(new THREE.TubeGeometry(path, 64, 0.25, 16, false), goldMat);
                group.add(tube);
                const bell = new THREE.Mesh(new THREE.ConeGeometry(0.5, 1, 32, 1, true), goldMat);
                bell.position.set(0,-1.5,0); bell.rotation.x=Math.PI; bell.userData={note:"C4"}; group.add(bell);
                return group;
            }

            const instrumentMeshes = [createPiano(), createGuitar(), createSax()];
            instrumentMeshes.forEach((m,i) => { m.userData.type=instruments[i].type; scene.add(m); });
            
            function updateCarousel() {
                 instrumentMeshes.forEach((mesh, index) => {
                    const relIndex = (index - activeIndex + instrumentMeshes.length) % instrumentMeshes.length;
                    if(relIndex === 0) {
                        new TWEEN.Tween(mesh.position).to({x:0,y:0,z:0},800).easing(TWEEN.Easing.Back.Out).start();
                        new TWEEN.Tween(mesh.scale).to({x:1,y:1,z:1},800).easing(TWEEN.Easing.Elastic.Out).start();
                        new TWEEN.Tween(mesh.rotation).to({x:0,y:0,z:0},800).start();
                        if(instNameEl) instNameEl.innerText = instruments[index].name;
                    } else {
                         const side = relIndex === 1 ? 1 : -1;
                         new TWEEN.Tween(mesh.position).to({x:6, y: side*3, z:-4},800).easing(TWEEN.Easing.Cubic.Out).start();
                         new TWEEN.Tween(mesh.scale).to({x:0.5,y:0.5,z:0.5},800).start();
                         new TWEEN.Tween(mesh.rotation).to({x: side*0.2, y:-0.5, z: side*0.2},800).start();
                    }
                 });
            }
            updateCarousel();

            // --- AUDIO ---
            const vol = new Tone.Volume(-8).toDestination();
            const reverb = new Tone.Reverb(2).toDestination();
            vol.connect(reverb);
            const synths = {
                piano: new Tone.PolySynth(Tone.Synth).connect(vol),
                guitar: new Tone.PluckSynth().connect(vol),
                sax: new Tone.MonoSynth({oscillator:{type:"sawtooth"}}).connect(vol)
            };

            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();

            window.addEventListener('click', async (e) => {
                if(Tone.context.state !== 'running') await Tone.start();
                mouse.x = (e.clientX/window.innerWidth)*2-1; mouse.y = -(e.clientY/window.innerHeight)*2+1;
                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(scene.children, true);
                if(intersects.length > 0) {
                    let obj = intersects[0].object;
                    let group = obj; while(group.parent && group.parent.type !== 'Scene') group = group.parent;
                    if(instrumentMeshes.indexOf(group) === activeIndex && obj.userData.note) {
                        let type = instruments[activeIndex].type;
                        if(type==='piano') synths.piano.triggerAttackRelease(obj.userData.note, "8n");
                        else if(type==='guitar') synths.guitar.triggerAttack(obj.userData.note);
                        else synths.sax.triggerAttackRelease(obj.userData.note, "4n");
                        
                        if(obj.material && obj.material.emissive) {
                             const old = obj.material.emissive.getHex();
                             obj.material.emissive.setHex(0x00FFA3);
                             setTimeout(()=>obj.material.emissive.setHex(old), 200);
                        }
                    }
                }
            });

            window.addEventListener('dblclick', () => { activeIndex = (activeIndex+1)%3; updateCarousel(); });
            window.addEventListener('resize', () => { 
                camera.aspect = window.innerWidth/window.innerHeight; camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth,window.innerHeight); composer.setSize(window.innerWidth,window.innerHeight);
            });

            // --- LOOP ---
            const clock = new THREE.Clock();
            function animate() {
                requestAnimationFrame(animate);
                const t = clock.getElapsedTime();
                TWEEN.update();
                controls.update();
                instrumentMeshes[activeIndex].position.y = Math.sin(t)*0.1;
                particlesMesh.rotation.y = t*0.05;
                composer.render();
            }
            animate();
            loading.innerText = "READY. CLICK TO START.";
            
        } catch (err) {
            console.error(err);
            loading.innerHTML = "CRITICAL ERROR: " + err.message;
            document.getElementById('error-log').innerText = err.stack;
            document.getElementById('error-log').style.display = 'block';
        }
    </script>
</body>
</html>
"""

components.html(three_js_html, height=850, scrolling=False)
