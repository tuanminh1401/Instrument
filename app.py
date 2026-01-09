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
        background-color: #0E1117;
        color: #ffffff;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #00FFA3 !important; /* Neon Green */
        text-shadow: 0px 0px 10px rgba(0, 255, 163, 0.4);
    }
    /* Hide Streamlit Header/Footer for immersion */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom container styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎹 3D Virtual Instrument Simulator")
st.markdown("### Interactive Tone.js Audio Engine & Three.js Visualization")

# --- 2. Three.js + Tone.js HTML Injection ---
# This is where the magic happens. We inject a full 3D app into Streamlit.

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
            background-color: #0E1117;
            font-family: 'Segoe UI', sans-serif;
            color: white;
            user-select: none;
        }
        #canvas-container { 
            width: 100%; 
            height: 100vh; 
            display: block; 
        }
        #overlay {
            position: absolute;
            bottom: 20px;
            left: 20px;
            pointer-events: none;
        }
        .instruction {
            color: #00FFA3;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            background: rgba(0,0,0,0.5);
            padding: 8px 12px;
            border-radius: 4px;
            border: 1px solid #00FFA3;
        }
        #loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #00FFA3;
            font-size: 24px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
    </style>
    <!-- CDN Imports -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>
</head>
<body>
    <div id="loading">Initializing Audio & Graphics...</div>
    <div id="canvas-container"></div>
    <div id="overlay">
        <div class="instruction">Click / Tap to Play Note<br>Drag to Rotate<br>Double Click to Switch Focus</div>
    </div>

    <script>
    // --- APP STATE ---
    const instruments = [
        { type: 'piano', name: 'Grand Piano', color: 0x111111 },
        { type: 'guitar', name: 'Electric Guitar', color: 0xaa2222 },
        { type: 'sax', name: 'Tenor Saxophone', color: 0xD4AF37 }
    ];
    let activeIndex = 0;
    
    // --- THREE.JS SETUP ---
    const container = document.getElementById('canvas-container');
    const loading = document.getElementById('loading');
    
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0E1117);
    scene.fog = new THREE.Fog(0x0E1117, 10, 50);

    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0, 5, 12);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.toneMapping = THREE.ReinhardToneMapping;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 5;
    controls.maxDistance = 20;

    // --- LIGHTING ---
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const spotLight = new THREE.SpotLight(0x00FFA3, 1.5);
    spotLight.position.set(10, 20, 10);
    spotLight.angle = 0.3;
    spotLight.penumbra = 0.5;
    spotLight.castShadow = true;
    scene.add(spotLight);

    const pointLight = new THREE.PointLight(0xff00ff, 0.8); // Cyberpunk contrasting light
    pointLight.position.set(-10, 5, -5);
    scene.add(pointLight);

    // --- GEOMETRY GENERATORS ---
    // Materials
    const standardMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x333333, 
        metalness: 0.9, 
        roughness: 0.2 
    });
    
    const accentMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x00FFA3, 
        emissive: 0x004422,
        metalness: 0.5, 
        roughness: 0.2 
    });

    const whiteKeyMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.1 });
    const blackKeyMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

    function createPiano() {
        const group = new THREE.Group();
        
        // Body
        const bodyGeo = new THREE.BoxGeometry(4, 1.5, 4);
        const body = new THREE.Mesh(bodyGeo, new THREE.MeshStandardMaterial({ color: 0x050505, roughness: 0.1, metalness: 0.8 }));
        body.position.y = 0;
        group.add(body);
        
        // Keys
        const startX = -1.8;
        for(let i=0; i<8; i++) {
            const keyGeo = new THREE.BoxGeometry(0.4, 0.2, 1.5);
            const key = new THREE.Mesh(keyGeo, whiteKeyMat);
            key.position.set(startX + i*0.5, 0.8, 1.0);
            key.userData = { note: ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"][i] };
            group.add(key);
            
            // Black keys (simplified)
            if ([0,1,3,4,5].includes(i)) {
                 const bKeyGeo = new THREE.BoxGeometry(0.25, 0.25, 1);
                 const bKey = new THREE.Mesh(bKeyGeo, blackKeyMat);
                 bKey.position.set(startX + i*0.5 + 0.25, 0.95, 0.8);
                 bKey.userData = { note: ["C#4", "D#4", "", "F#4", "G#4", "A#4"][i] || "C#4" }; // Just fallback
                 group.add(bKey);
            }
        }
        return group;
    }

    function createGuitar() {
        const group = new THREE.Group();
        
        // Body
        const bodyGeo = new THREE.CylinderGeometry(1.2, 1.5, 0.5, 32);
        const body = new THREE.Mesh(bodyGeo, new THREE.MeshStandardMaterial({ color: 0xaa0000, metalness: 0.6 }));
        body.rotation.x = Math.PI / 2;
        group.add(body);
        
        // Neck
        const neckGeo = new THREE.BoxGeometry(0.4, 4, 0.2);
        const neck = new THREE.Mesh(neckGeo, new THREE.MeshStandardMaterial({ color: 0x5c4033 }));
        neck.position.y = 2.2;
        group.add(neck);

        // Strings (Abstract)
        const stringGeo = new THREE.CylinderGeometry(0.02, 0.02, 4);
        for(let i=0; i<4; i++) {
            const string = new THREE.Mesh(stringGeo, new THREE.MeshBasicMaterial({ color: 0xc0c0c0 }));
            string.position.set(-0.15 + i*0.1, 2.2, 0.15);
            string.userData = { note: ["E3", "A3", "D4", "G4"][i] };
            group.add(string);
        }

        return group;
    }

    function createSax() {
        const group = new THREE.Group();
        
        // Main Tube
        const tubePath = new THREE.CatmullRomCurve3([
            new THREE.Vector3(0, -1, 0),
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(0, 2, 0),
            new THREE.Vector3(0.5, 2.5, 0),
            new THREE.Vector3(1, 2, 0)
        ]);
        const tubeGeo = new THREE.TubeGeometry(tubePath, 20, 0.3, 8, false);
        const tube = new THREE.Mesh(tubeGeo, new THREE.MeshStandardMaterial({ color: 0xD4AF37, metalness: 1.0, roughness: 0.1 }));
        group.add(tube);
        
        // Bell
        const bellGeo = new THREE.ConeGeometry(0.8, 1, 32, 1, true);
        const bell = new THREE.Mesh(bellGeo, new THREE.MeshStandardMaterial({ color: 0xD4AF37, metalness: 1.0, roughness: 0.1, side: THREE.DoubleSide }));
        bell.position.set(0, -1, 0);
        bell.rotation.x = Math.PI;
        bell.userData = { note: "C4" }; // Clicking bell plays base note
        group.add(bell);

        // Buttons
        for(let i=0; i<5; i++) {
            const btnGeo = new THREE.CylinderGeometry(0.1, 0.1, 0.1);
            const btn = new THREE.Mesh(btnGeo, new THREE.MeshStandardMaterial({color: 0xffffff}));
            btn.position.set(0.2, i*0.4, 0.25);
            btn.rotation.z = Math.PI / 2;
            btn.userData = { note: ["D4", "E4", "F4", "G4", "A4"][i] };
            group.add(btn);
        }

        return group;
    }

    // --- CAROUSEL LOGIC ---
    const instrumentMeshes = [];
    const radius = 6;
    
    // Create instances
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

    // Initial positioning
    function updateCarousel() {
        // Active instrument at (0,0,0), scale 1
        // Next 1: (3, 0, -3), scale 0.5
        // Next 2: (4, -2, -4), scale 0.5 (Just a simple right stack layout as requested)
        
        // Let's implement the specific logic: Center Stage + Right Stack
        // Because strictly MAX 3 instruments.
        
        instrumentMeshes.forEach((mesh, index) => {
            // Calculate relative index based on activeIndex
            // 0 = Active, 1 = Next, 2 = Last
            // We want indices to wrap around: (index - active + len) % len
            const relIndex = (index - activeIndex + instrumentMeshes.length) % instrumentMeshes.length;
            
            if (relIndex === 0) {
                // Center Stage
                new TWEEN.Tween(mesh.position).to({ x:0, y:0, z:0 }, 500).easing(TWEEN.Easing.Quadratic.Out).start();
                new TWEEN.Tween(mesh.scale).to({ x:1, y:1, z:1 }, 500).easing(TWEEN.Easing.Quadratic.Out).start();
                new TWEEN.Tween(mesh.rotation).to({ x:0, y: (mesh.userData.type === 'guitar' ? 0 : 0), z:0 }, 500).start();
            } else if (relIndex === 1) {
                // Right Stack Top
                new TWEEN.Tween(mesh.position).to({ x:5, y:2, z:-2 }, 500).easing(TWEEN.Easing.Quadratic.Out).start();
                new TWEEN.Tween(mesh.scale).to({ x:0.4, y:0.4, z:0.4 }, 500).easing(TWEEN.Easing.Quadratic.Out).start();
                new TWEEN.Tween(mesh.rotation).to({ y: -0.5 }, 500).start();
            } else if (relIndex === 2) {
                // Right Stack Bottom
                new TWEEN.Tween(mesh.position).to({ x:5, y:-2, z:-2 }, 500).easing(TWEEN.Easing.Quadratic.Out).start();
                new TWEEN.Tween(mesh.scale).to({ x:0.4, y:0.4, z:0.4 }, 500).easing(TWEEN.Easing.Quadratic.Out).start();
                new TWEEN.Tween(mesh.rotation).to({ y: -0.5 }, 500).start();
            }
        });
    }

    // --- AUDIO ENGINE (Tone.js) ---
    const vol = new Tone.Volume(-10).toDestination();
    
    // Synths
    const pianoSynth = new Tone.PolySynth(Tone.Synth, {
        oscillator: { type: "triangle" },
        envelope: { attack: 0.02, decay: 0.1, sustain: 0.3, release: 1 }
    }).connect(vol);

    const guitarSynth = new Tone.PluckSynth({
        attackNoise: 1,
        dampening: 4000,
        resonance: 0.7
    }).connect(vol);

    const saxSynth = new Tone.MonoSynth({
        oscillator: { type: "sawtooth" },
        envelope: { attack: 0.1, decay: 0.2, sustain: 0.5, release: 0.8 },
        filterEnvelope: { attack: 0.06, decay: 0.2, sustain: 0.5, baseFrequency: 200, octaves: 2.6 }
    }).connect(vol);
    
    // Simple reverb
    const reverb = new Tone.Reverb(1.5).toDestination();
    pianoSynth.connect(reverb);
    guitarSynth.connect(reverb);
    saxSynth.connect(reverb);

    async function startAudio() {
        await Tone.start();
        loading.style.display = 'none';
        console.log("Audio Context Started");
    }

    function playNote(instrumentType, note) {
        if (!note) return;
        
        switch(instrumentType) {
            case 'piano':
                pianoSynth.triggerAttackRelease(note, "8n");
                break;
            case 'guitar':
                guitarSynth.triggerAttack(note);
                break;
            case 'sax':
                saxSynth.triggerAttackRelease(note, "4n");
                break;
        }
    }

    // --- INTERACTION ---
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    function onMouseClick(event) {
        // Calculate mouse position in normalized device coordinates
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);

        // Intersect with active instrument only to avoid confusion? 
        // Or all? Let's do all visible.
        const intersects = raycaster.intersectObjects(scene.children, true);

        if (intersects.length > 0) {
            startAudio(); // Ensure context is running

            // Check if we hit a carousel item that is NOT active (to switch)
            // Traverse up to find the group root
            let object = intersects[0].object;
            let group = object;
            while(group.parent && group.parent.type !== 'Scene') {
                group = group.parent;
            }
            
            // Identify which instrument group this is
            const hitIndex = instrumentMeshes.indexOf(group);
            
            if (hitIndex !== -1 && hitIndex !== activeIndex) {
                 // Switch Focus
                 activeIndex = hitIndex;
                 updateCarousel();
                 return;
            }

            // If we hit the active instrument parts, play note
            if (object.userData.note) {
                 playNote(instrumentMeshes[activeIndex].userData.type, object.userData.note);
                 
                 // Visual feedback
                 const originalColor = object.material.color.getHex();
                 object.material.color.setHex(0x00FFA3);
                 setTimeout(() => {
                     object.material.color.setHex(originalColor);
                 }, 150);
            }
        }
    }

    window.addEventListener('click', onMouseClick, false);
    
    // --- ANIMATION LOOP ---
    // Simple Tweening Polyfill since we didn't import TWEEN.js separately
    // Actually, let's just use CSS-like logic or a simple lerp for now to save imports?
    // Wait, the prompt implies "Smooth 3D/CSS transitions". 
    // I'll import TWEEN via CDN for robustness.
    
    const script = document.createElement('script');
    script.src = "https://cdnjs.cloudflare.com/ajax/libs/tween.js/18.6.4/tween.umd.js";
    script.onload = () => {
        updateCarousel(); // Initial Layout
        animate();
    };
    document.head.appendChild(script);

    function animate(time) {
        requestAnimationFrame(animate);
        TWEEN.update(time);
        
        // Idle animation for active instrument
        if (instrumentMeshes[activeIndex]) {
            instrumentMeshes[activeIndex].rotation.y = Math.sin(time * 0.001) * 0.1; 
        }

        controls.update();
        renderer.render(scene, camera);
    }

    // Handle Resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    loading.innerText = "Click anywhere to Start";
    
    </script>
</body>
</html>
"""

components.html(three_js_html, height=800, scrolling=False)
