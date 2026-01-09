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
        body { 
            margin: 0; 
            overflow: hidden; 
            background-color: #050505;
            font-family: 'Segoe UI', sans-serif;
            color: white;
            user-select: none;
        }
        #canvas-container { 
            width: 100%; 
            height: 100vh; 
            display: block; 
            background: radial-gradient(circle at center, #1a1a1a 0%, #000000 100%);
        }
        #overlay {
            position: absolute;
            bottom: 30px;
            left: 30px;
            pointer-events: none;
            text-align: left;
        }
        .title {
            font-size: 40px;
            font-weight: 800;
            color: white;
            text-shadow: 0 0 20px rgba(255,255,255,0.2);
            margin: 0;
            letter-spacing: -1px;
        }
        .subtitle {
            font-size: 14px;
            color: #00FFA3;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(0,255,163,0.5);
        }
        .instruction {
            color: #888;
            font-size: 12px;
            margin-top: 10px;
            font-family: monospace;
        }
        #loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #00FFA3;
            font-size: 18px;
            text-transform: uppercase;
            letter-spacing: 4px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 0.5; }
            50% { opacity: 1; }
            100% { opacity: 0.5; }
        }
    </style>
    
    <!-- ES Module Import Map for Modern Three.js -->
    <script type="importmap">
        {
            "imports": {
                "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
                "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/",
                "tone": "https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"
            }
        }
    </script>
    <!-- Tone.js is UMD, so load it normally -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tween.js/18.6.4/tween.umd.js"></script>
</head>
<body>
    <div id="loading">System Initializing...</div>
    <div id="canvas-container"></div>
    <div id="overlay">
        <div class="subtitle">Virtual Studio</div>
        <div class="title" id="inst-name">Grand Piano</div>
        <div class="instruction">
            [CLICK] PLAY NOTE &nbsp;•&nbsp; [DRAG] ROTATE &nbsp;•&nbsp; [DOUBLE-CLICK] SWITCH FOCUS
        </div>
    </div>

    <script type="module">
        import * as THREE from 'three';
        import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
        import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
        import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
        import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

        // --- STATE ---
        const instruments = [
            { type: 'piano', name: 'Grand Piano' },
            { type: 'guitar', name: 'Cyber Guitar' },
            { type: 'sax', name: 'Neon Sax' }
        ];
        let activeIndex = 0;
        const instNameEl = document.getElementById('inst-name');

        // --- SETUP ---
        const container = document.getElementById('canvas-container');
        const loading = document.getElementById('loading');

        const scene = new THREE.Scene();
        // Background fog for infinite feel
        scene.fog = new THREE.FogExp2(0x050505, 0.02);

        const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 100);
        camera.position.set(0, 4, 14);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.0;
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(renderer.domElement);

        // --- POST PROCESSING (BLOOM) ---
        const renderScene = new RenderPass(scene, camera);
        
        const bloomPass = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85);
        bloomPass.threshold = 0;
        bloomPass.strength = 1.2; // High neon glow
        bloomPass.radius = 0.5;

        const composer = new EffectComposer(renderer);
        composer.addPass(renderScene);
        composer.addPass(bloomPass);

        // --- CONTROLS ---
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 5;
        controls.maxDistance = 20;
        controls.maxPolarAngle = Math.PI / 2 + 0.1; // Don't allow going too far below

        // --- LIGHTING ---
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.05); // Very dim ambient
        scene.add(ambientLight);

        // Main Spotlight (Key Light)
        const spotLight = new THREE.SpotLight(0xffffff, 100);
        spotLight.position.set(5, 10, 5);
        spotLight.angle = 0.5;
        spotLight.penumbra = 0.5;
        spotLight.castShadow = true;
        spotLight.shadow.bias = -0.0001;
        scene.add(spotLight);

        // Rim Light (Cyan/Blue)
        const rimLight = new THREE.SpotLight(0x00ffff, 50);
        rimLight.position.set(-5, 5, -5);
        rimLight.lookAt(0,0,0);
        scene.add(rimLight);

        // Fill Light (Neon Pink/Magenta)
        const fillLight = new THREE.PointLight(0xff0080, 2, 20);
        fillLight.position.set(-5, 2, 5);
        scene.add(fillLight);
        
        // Floor Reflection (Grid)
        const gridHelper = new THREE.GridHelper(50, 50, 0x333333, 0x111111);
        gridHelper.position.y = -2;
        scene.add(gridHelper);

        // Particles
        const particlesGeo = new THREE.BufferGeometry();
        const particlesCount = 200;
        const posArray = new Float32Array(particlesCount * 3);
        const particleColors = new Float32Array(particlesCount * 3);
        
        for(let i=0; i<particlesCount * 3; i+=3) {
            posArray[i] = (Math.random() - 0.5) * 30;
            posArray[i+1] = (Math.random() - 0.5) * 20 + 5;
            posArray[i+2] = (Math.random() - 0.5) * 30;
            
            // Random colors between Cyan and Green
            particleColors[i] = 0;
            particleColors[i+1] = 0.5 + Math.random() * 0.5; 
            particleColors[i+2] = 0.5 + Math.random() * 0.5;
        }
        particlesGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
        particlesGeo.setAttribute('color', new THREE.BufferAttribute(particleColors, 3));
        const particlesMat = new THREE.PointsMaterial({
            size: 0.1,
            vertexColors: true,
            transparent: true,
            opacity: 0.8,
            blending: THREE.AdditiveBlending
        });
        const particlesMesh = new THREE.Points(particlesGeo, particlesMat);
        scene.add(particlesMesh);

        // --- MATERIALS ---
        const plasticMat = new THREE.MeshPhysicalMaterial({ 
            color: 0x111111, roughness: 0.1, metalness: 0.1, clearcoat: 1.0, clearcoatRoughness: 0.1 
        });
        const metalMat = new THREE.MeshStandardMaterial({ 
            color: 0x888888, roughness: 0.2, metalness: 1.0 
        });
        const goldMat = new THREE.MeshStandardMaterial({ 
            color: 0xffcc00, roughness: 0.3, metalness: 1.0 
        });
        const neonMat = new THREE.MeshStandardMaterial({
            color: 0x000000, emissive: 0x00FFA3, emissiveIntensity: 2
        });
        const woodMat = new THREE.MeshStandardMaterial({
            color: 0x5c4033, roughness: 0.8, metalness: 0.0
        });

        // --- INSTRUMENT GENERATORS (Advanced) ---

        function createPiano() {
            const group = new THREE.Group();
            
            // Main Body (Grand Piano Curve)
            const shape = new THREE.Shape();
            shape.moveTo(0,0);
            shape.lineTo(4,0);
            shape.quadraticCurveTo(4, 4, 2, 6);
            shape.lineTo(0, 6);
            shape.lineTo(0, 0);
            
            const extrudeSettings = { depth: 1, bevelEnabled: true, bevelSegments: 2, steps: 2, bevelSize: 0.1, bevelThickness: 0.1 };
            const bodyGeo = new THREE.ExtrudeGeometry(shape, extrudeSettings);
            const body = new THREE.Mesh(bodyGeo, plasticMat);
            body.rotation.x = -Math.PI / 2;
            body.position.set(-2, 0, -3);
            group.add(body);
            
            // Legs
            const legGeo = new THREE.CylinderGeometry(0.1, 0.05, 2);
            [
                new THREE.Vector3(-1.5, -1, 2),
                new THREE.Vector3(1.5, -1, 2),
                new THREE.Vector3(0, -1, -2)
            ].forEach(pos => {
                const leg = new THREE.Mesh(legGeo, plasticMat);
                leg.position.copy(pos);
                group.add(leg);
            });

            // Keys Area
            const keyBedGeo = new THREE.BoxGeometry(4.2, 0.5, 1.5);
            const keyBed = new THREE.Mesh(keyBedGeo, plasticMat);
            keyBed.position.set(0, 0.5, 2.2);
            group.add(keyBed);
            
            // Keys
            const startX = -1.8;
            for(let i=0; i<8; i++) {
                // White Key
                const keyGeo = new THREE.BoxGeometry(0.4, 0.2, 1.2);
                const key = new THREE.Mesh(keyGeo, new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.1 }));
                key.position.set(startX + i*0.5, 0.8, 2.4);
                key.userData = { note: ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"][i] };
                key.castShadow = true;
                group.add(key);
                
                // Black Key
                if ([0,1,3,4,5].includes(i)) {
                    const bKeyGeo = new THREE.BoxGeometry(0.25, 0.25, 0.8);
                    const bKey = new THREE.Mesh(bKeyGeo, new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 }));
                    bKey.position.set(startX + i*0.5 + 0.25, 0.95, 2.2);
                    bKey.userData = { note: ["C#4", "D#4", "", "F#4", "G#4", "A#4"][i] || "C#4" }; 
                    group.add(bKey);
                }
            }
            return group;
        }

        function createGuitar() {
            const group = new THREE.Group();
            
            // Strat-like Body
            const shape = new THREE.Shape();
            // Simplified contour
            shape.moveTo(0, -1.5);
            shape.bezierCurveTo(1.5, -1.5, 1.5, 1.5, 0, 1.5);
            shape.bezierCurveTo(-0.5, 1.5, -0.5, 0.5, 0, 0); // Waist
            shape.bezierCurveTo(-1.2, 0.5, -1.5, -1.5, 0, -1.5);
            
            const bodyGeo = new THREE.ExtrudeGeometry(shape, { depth: 0.3, bevelEnabled: true, bevelThickness: 0.05, bevelSize: 0.05 });
            const body = new THREE.Mesh(bodyGeo, new THREE.MeshStandardMaterial({ color: 0xaa0000, metalness: 0.6, roughness: 0.1, clearcoat: 1.0 }));
            body.center(); // Center geometry
            group.add(body);
            
            // Pickguard
            const pgShape = new THREE.Shape();
            pgShape.moveTo(0.2, -1);
            pgShape.lineTo(0.8, -0.5);
            pgShape.lineTo(0.8, 0.5);
            pgShape.lineTo(0.2, 0.8);
            const pgGeo = new THREE.ExtrudeGeometry(pgShape, { depth: 0.32, bevelEnabled: false });
            const pg = new THREE.Mesh(pgGeo, new THREE.MeshStandardMaterial({ color: 0xffffff }));
            pg.position.z = -0.16; // Slight offset
            group.add(pg);

            // Neck
            const neckGeo = new THREE.BoxGeometry(0.4, 3.5, 0.15);
            const neck = new THREE.Mesh(neckGeo, new THREE.MeshStandardMaterial({ color: 0xd2b48c }));
            neck.position.set(0, 2, 0.1);
            group.add(neck);

            // Fretboard
            const fbGeo = new THREE.BoxGeometry(0.4, 3.5, 0.05);
            const fb = new THREE.Mesh(fbGeo, new THREE.MeshStandardMaterial({ color: 0x332211 }));
            fb.position.set(0, 2, 0.2);
            group.add(fb);

            // Strings (Emissive for Neon look)
            const stringGeo = new THREE.CylinderGeometry(0.01, 0.01, 3.5);
            for(let i=0; i<6; i++) {
                const string = new THREE.Mesh(stringGeo, neonMat);
                string.position.set(-0.15 + i*0.06, 2, 0.25);
                string.userData = { note: ["E2", "A2", "D3", "G3", "B3", "E4"][i] };
                group.add(string);
            }

            return group;
        }

        function createSax() {
            const group = new THREE.Group();
            
            // Complex Tube using TubeGeometry with more segments
            const path = new THREE.CatmullRomCurve3([
                new THREE.Vector3(0, -1.5, 0),
                new THREE.Vector3(0, 1.5, 0),
                new THREE.Vector3(0.5, 2.0, 0),
                new THREE.Vector3(1.0, 1.5, 0),
                new THREE.Vector3(0.8, 2.2, 0.2) // Neck
            ]);
            
            const tubeGeo = new THREE.TubeGeometry(path, 64, 0.25, 16, false);
            const tube = new THREE.Mesh(tubeGeo, goldMat);
            group.add(tube);
            
            // Bell
            const bellGeo = new THREE.LatheGeometry([
                new THREE.Vector2(0.25, 0),
                new THREE.Vector2(0.4, 0.2),
                new THREE.Vector2(0.8, 0.8),
                new THREE.Vector2(1.0, 1.0)
            ], 32);
            const bell = new THREE.Mesh(bellGeo, goldMat);
            bell.position.set(0, -1.5, 0);
            bell.rotation.x = Math.PI;
            bell.userData = { note: "C4" };
            group.add(bell);

            // Keys/Buttons along the body
            for(let i=0; i<8; i++) {
                const btnGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.1);
                const btn = new THREE.Mesh(btnGeo, new THREE.MeshStandardMaterial({ color: 0xeeeeee, metalness: 0.5 }));
                btn.position.set(0, -1 + i*0.4, 0.25);
                btn.rotation.x = Math.PI / 2;
                btn.userData = { note: ["D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5"][i] };
                group.add(btn);
            }
            
            return group;
        }

        // --- CAROUSEL ---
        const instrumentMeshes = [];
        
        const pMesh = createPiano(); 
        pMesh.userData = { type: 'piano' };
        scene.add(pMesh);
        instrumentMeshes.push(pMesh);

        const gMesh = createGuitar();
        gMesh.userData = { type: 'guitar' };
        scene.add(gMesh);
        instrumentMeshes.push(gMesh);

        const sMesh = createSax();
        sMesh.userData = { type: 'sax' };
        scene.add(sMesh);
        instrumentMeshes.push(sMesh);

        function updateCarousel() {
            instrumentMeshes.forEach((mesh, index) => {
                const relIndex = (index - activeIndex + instrumentMeshes.length) % instrumentMeshes.length;
                
                if (relIndex === 0) {
                    // Active
                    new TWEEN.Tween(mesh.position).to({ x:0, y:0, z:0 }, 800).easing(TWEEN.Easing.Back.Out).start();
                    new TWEEN.Tween(mesh.scale).to({ x:1, y:1, z:1 }, 800).easing(TWEEN.Easing.Elastic.Out).start();
                    new TWEEN.Tween(mesh.rotation).to({ x:0, y:0, z:0 }, 800).start();
                    
                    // Update Text
                    if(instNameEl) instNameEl.innerText = instruments[index].name;
                    
                } else if (relIndex === 1) {
                    // Right Top
                    new TWEEN.Tween(mesh.position).to({ x:6, y:3, z:-4 }, 800).easing(TWEEN.Easing.Cubic.Out).start();
                    new TWEEN.Tween(mesh.scale).to({ x:0.5, y:0.5, z:0.5 }, 800).easing(TWEEN.Easing.Cubic.Out).start();
                    new TWEEN.Tween(mesh.rotation).to({ x:0.2, y:-0.5, z:0.2 }, 800).start();
                } else if (relIndex === 2) {
                    // Right Bottom
                    new TWEEN.Tween(mesh.position).to({ x:6, y:-3, z:-4 }, 800).easing(TWEEN.Easing.Cubic.Out).start();
                    new TWEEN.Tween(mesh.scale).to({ x:0.5, y:0.5, z:0.5 }, 800).easing(TWEEN.Easing.Cubic.Out).start();
                    new TWEEN.Tween(mesh.rotation).to({ x: -0.2, y:-0.5, z: -0.2 }, 800).start();
                }
            });
        }
        updateCarousel(); // Init

        // --- AUDIO ENGINE ---
        const vol = new Tone.Volume(-8).toDestination();
        const reverb = new Tone.Reverb(2).toDestination();
        vol.connect(reverb);
        
        const pianoSynth = new Tone.Sampler({
            urls: { C4: "C4.mp3", D#4: "Ds4.mp3", F#4: "Fs4.mp3", A4: "A4.mp3" },
            baseUrl: "https://tonejs.github.io/audio/salamander/"
        }).connect(vol);
        // Fallback if sampler loads slow is hidden, but let's add a synth backup if needed.
        // Actually Sampler is best for realism. We will rely on online connection.
        
        const guitarSynth = new Tone.PluckSynth({
            attackNoise: 2, dampening: 4000, resonance: 0.98
        }).connect(vol);
        
        const saxSynth = new Tone.MonoSynth({
            oscillator: { type: "sawtooth" },
            envelope: { attack: 0.05, decay: 0.2, sustain: 0.8, release: 1.5 },
            filterEnvelope: { attack: 0.1, decay: 0.5, sustain: 0.3, baseFrequency: 300, octaves: 4 }
        }).connect(vol);

        async function startAudio() {
            if (Tone.context.state !== 'running') {
                await Tone.start();
                loading.style.display = 'none';
            }
        }

        function playNote(type, note) {
            switch(type) {
                case 'piano': pianoSynth.triggerAttackRelease(note, "2n"); break;
                case 'guitar': guitarSynth.triggerAttack(note); break;
                case 'sax': saxSynth.triggerAttackRelease(note, "4n"); break;
            }
        }

        // --- INTERACTION ---
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        window.addEventListener('click', (event) => {
            startAudio();
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;
            
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(scene.children, true);
            
            if(intersects.length > 0) {
                let obj = intersects[0].object;
                
                // Logic to find parent group
                let group = obj;
                while(group.parent && group.parent.type !== 'Scene') {
                    group = group.parent;
                }
                const hitIndex = instrumentMeshes.indexOf(group);
                
                // Note Play
                if(obj.userData.note && hitIndex === activeIndex) {
                    playNote(instruments[activeIndex].type, obj.userData.note);
                    
                    // Glow effect on hit
                    const oldEmissive = obj.material.emissive ? obj.material.emissive.getHex() : 0x000000;
                    if(obj.material.emissive) {
                        obj.material.emissive.setHex(0x00FFA3);
                        setTimeout(() => obj.material.emissive.setHex(oldEmissive), 200);
                    }
                }
            }
        });

        window.addEventListener('dblclick', (event) => {
             // Simple cycle on double click anywhere
             activeIndex = (activeIndex + 1) % instruments.length;
             updateCarousel();
        });

        // --- LOOP ---
        const clock = new THREE.Clock();
        
        function animate() {
            requestAnimationFrame(animate);
            const time = clock.getElapsedTime();
            TWEEN.update();
            controls.update();
            
            // Floating Animation for Carousel
            instrumentMeshes.forEach((mesh, idx) => {
                 if(idx === activeIndex) {
                     mesh.position.y = Math.sin(time) * 0.1; 
                 } else {
                     mesh.rotation.x += 0.005; // Gentle spin for background items
                 }
            });

            // Particles Animation
            particlesMesh.rotation.y = time * 0.05;

            composer.render();
        }

        animate();
        loading.innerText = "READY. CLICK TO START.";

        // Resize
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
            composer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""

components.html(three_js_html, height=850, scrolling=False)
