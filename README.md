# 3D Virtual Instrument Simulator 🎹

A futuristic 3D interactive instrument simulator built with **Streamlit**, **Three.js**, and **Tone.js**.

## 🚀 How to Run

### Option 1: Run Locally
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the app:
    ```bash
    streamlit run app.py
    ```

### Option 2: Deploy to Streamlit Community Cloud (Free)
Since this is a Python application, it requires a server runtime and **cannot** be deployed via GitHub Pages (which only supports static HTML/JS).

**To get your "Web Access Link":**
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Sign in with GitHub.
3.  Click **"New app"**.
4.  Select this repository (`tuanminh1401/Instrument`).
5.  Set Main file path to `app.py`.
6.  Click **"Deploy!"**.

You will receive a URL (e.g., `https://instrument-simulator.streamlit.app`) to share.

## 🛠 Tech Stack
-   **Frontend**: Three.js (WebGL), HTML5, CSS3
-   **Audio**: Tone.js (Web Audio API)
-   **Backend/State**: Python (Streamlit)

## 🎨 Features
-   **Carousel Focus System**: Center stage + Right stack view.
-   **Procedural Instruments**: 3D Piano, Guitar, and Saxophone generated on the fly.
-   **Zero-Latency Audio**: Client-side audio synthesis for instant feedback.
