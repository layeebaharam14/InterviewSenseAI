import streamlit as st
import pyttsx3
import os
import base64
import uuid

from pathlib import Path


def _get_project_root() -> str:
    """
    Reliably resolves the absolute path to the project root directory.
    Walks up from this file's location (src/interviewsense/utils/) until
    it locates project markers such as 'app.py', '.streamlit', or 'assets'.
    Does not depend on the current working directory.
    """
    current = Path(__file__).resolve().parent
    for p in [current] + list(current.parents):
        if (p / "app.py").exists() or (p / ".streamlit").exists() or (p / "assets").exists():
            return str(p)
    # Fallback to current working directory if it contains project markers
    cwd = Path.cwd()
    if (cwd / "app.py").exists() or (cwd / "assets").exists():
        return str(cwd)
    # Default fallback: 3 levels up from src/interviewsense/utils
    if len(current.parents) >= 3:
        return str(current.parents[2])
    return str(current)


def _read_image_as_data_url(path: str) -> str | None:
    try:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(path)[1].lower().lstrip(".") or "png"
        mime = "png" if ext == "png" else ("jpeg" if ext in ("jpg", "jpeg") else ext)
        return f"data:image/{mime};base64,{encoded}"
    except Exception:
        return None

@st.cache_data
def _get_background_video_base64() -> str | None:
    """Reads and caches background video as base64 string to keep app fast and smooth."""
    root = _get_project_root()
    video_paths = [
        os.path.join(root, "assets", "background_video.mp4"),
        os.path.join(root, "static", "background_video.mp4"),
        os.path.join(root, "WhatsApp Video 2026-10-30 at 12.12.21 PM.mp4"),
    ]
    for p in video_paths:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                pass
    return None

def apply_css():
    """Injects custom CSS for the dark blue gradient theme, background video, and UI styling."""
    root = _get_project_root()
    static_video_path = os.path.join(root, "static", "background_video.mp4")
    if os.path.exists(static_video_path):
        video_src = "app/static/background_video.mp4"
    else:
        video_b64 = _get_background_video_base64()
        video_src = f"data:video/mp4;base64,{video_b64}" if video_b64 else None

    if video_src:
        st.markdown(
            f"""
            <video id="bg-video" autoplay loop muted playsinline>
                <source src="{video_src}" type="video/mp4">
            </video>
            <div id="video-overlay"></div>
            """,
            unsafe_allow_html=True
        )
        background_css = """
            background-color: transparent !important;
            background: transparent !important;
        """
    else:
        bg_path = os.path.join(root, "assets", "home_bg.png")
        bg_data_url = _read_image_as_data_url(bg_path)
        background_css = (
            f"""
                background-color: #020617 !important;
                background-image:
                    linear-gradient(rgba(2, 6, 23, 0.55), rgba(2, 6, 23, 0.78)),
                    url('{bg_data_url}') !important;
                background-size: cover !important;
                background-position: center !important;
                background-repeat: no-repeat !important;
            """
            if bg_data_url
            else """
                background-color: #020617 !important;
                background-image:
                    radial-gradient(circle at 85% 22%, rgba(56, 189, 248, 0.18) 0%, rgba(56, 189, 248, 0.0) 55%),
                    radial-gradient(circle at 12% 45%, rgba(192, 132, 252, 0.14) 0%, rgba(192, 132, 252, 0.0) 60%),
                    radial-gradient(circle at 18% 25%, rgba(56, 189, 248, 0.10) 0%, rgba(56, 189, 248, 0.0) 35%),
                    radial-gradient(circle at 50% 35%, #061938 0%, #020617 70%),
                    radial-gradient(circle at 20% 30%, rgba(255,255,255,0.10) 0 1px, transparent 2px),
                    radial-gradient(circle at 75% 40%, rgba(255,255,255,0.08) 0 1px, transparent 2px),
                    radial-gradient(circle at 40% 60%, rgba(255,255,255,0.06) 0 1px, transparent 2px),
                    radial-gradient(circle at 60% 20%, rgba(255,255,255,0.06) 0 1px, transparent 2px);
                background-size:
                    cover,
                    cover,
                    cover,
                    cover,
                    420px 420px,
                    520px 520px,
                    680px 680px,
                    760px 760px;
                background-position:
                    center,
                    center,
                    center,
                    center,
                    0 0,
                    80px 120px,
                    120px 40px,
                    30px 200px;
                background-repeat: no-repeat !important;
            """
        )

    st.markdown("""
        <style>
        /* FIXED BACKGROUND VIDEO ON CONTINUOUS LOOP */
        #bg-video {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            min-width: 100% !important;
            min-height: 100% !important;
            object-fit: cover !important;
            z-index: -999999 !important;
            pointer-events: none !important;
        }

        /* OVERLAY TO PRESERVE DARK NAVY THEME AND TEXT READABILITY */
        #video-overlay {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            background: linear-gradient(rgba(2, 6, 23, 0.65), rgba(2, 6, 23, 0.82)) !important;
            z-index: -999998 !important;
            pointer-events: none !important;
        }

        /* 1 & 2. FULL BACKGROUND COLOR FIX & REMOVE TOP WHITE GAP */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    """ + background_css + """
            background-attachment: fixed !important;
            color: #ffffff !important;
            font-family: 'Inter', sans-serif !important;
            margin: 0 !important;
            padding: 0 !important;
            min-height: 100vh !important;
            width: 100vw !important;
        }

        /* Make Streamlit top header completely hidden to remove top white gap & reclaim space */
        header[data-testid="stHeader"],
        [data-testid="stHeader"],
        div[data-testid="stToolbar"] {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            visibility: hidden !important;
        }

        /* 4. CONTAINER LAYOUT & NATURAL TOP-DOWN SCROLLING - SLEEK PADDING */
        .main .block-container,
        [data-testid="block-container"],
        .block-container {
            max-width: 960px !important;
            min-height: 100vh !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
            align-items: stretch !important;
            padding: 0.4rem 1.5rem 1.5rem 1.5rem !important;
            margin: 0 auto !important;
            animation: fadeIn 0.35s ease-out;
        }

        /* Hide 0-size component iframes used for scroll-to-top */
        iframe[title="streamlit.components.v1.html"],
        iframe[title="st.iframe"],
        div[data-testid="stCustomComponentV1"] {
            position: absolute !important;
            width: 0px !important;
            height: 0px !important;
            border: none !important;
            opacity: 0 !important;
            pointer-events: none !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Clean separators */
        hr {
            margin-top: 0.45rem !important;
            margin-bottom: 0.55rem !important;
            border: 0 !important;
            border-top: 1px solid rgba(56, 189, 248, 0.2) !important;
        }

        /* SUBTLE ANIMATION */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* IMPROVE TEXT ALIGNMENT AND SPACING - COMPACT HEADINGS */
        h1, h2, h3 {
            color: #ffffff !important;
            text-align: center !important;
            margin-top: 0 !important;
            margin-bottom: 0.35rem !important; 
            text-shadow: 0 0 18px rgba(56, 189, 248, 0.22) !important;
        }

        h1 {
            font-size: 2.1rem !important;
        }
        h2 {
            font-size: 1.65rem !important;
        }
        h3 {
            font-size: 1.25rem !important;
        }
        
        p {
            color: #f8fafc !important;
            font-size: 1.02rem;
            line-height: 1.55;
            margin-bottom: 0.4rem !important;
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.12) !important;
        }

        .page-section p, .landing-hero-desc {
            text-align: center !important;
            max-width: 720px;
            margin-left: auto !important;
            margin-right: auto !important;
        }

        .question-text {
            font-size: 2.5rem;
            font-weight: 800;
            text-align: center;
            margin-top: 0;
            margin-bottom: 2rem;
            color: #38bdf8 !important;
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.3); 
        }

        /* 3. FIX BUTTON SPACING & DESIGN */
        .stButton {
            width: 100%;
            display: flex;
            justify-content: center;
            margin-top: 0.4rem !important;
            margin-bottom: 0.4rem !important;
        }

        button[kind="primary"] {
            background: linear-gradient(135deg, #2563eb, #0ea5e9) !important;
            color: #ffffff !important;
            font-weight: 800 !important;
            text-shadow: none !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            padding: 0.85rem 1.8rem !important;
            font-size: 1.15rem !important;
            letter-spacing: 0.5px !important;
            text-transform: uppercase !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 15px rgba(14, 165, 233, 0.45) !important;
            width: 100% !important;
            max-width: 340px !important;
            display: block !important;
            margin: 0 auto !important;
        }

        button[kind="primary"]:hover {
            transform: scale(1.05) translateY(-2px) !important;
            filter: brightness(1.15) !important;
            box-shadow: 0 10px 30px rgba(14, 165, 233, 0.7) !important;
            color: #ffffff !important;
        }

        button[kind="primary"]:active {
            transform: scale(0.98) translateY(0) !important;
            box-shadow: 0 2px 8px rgba(6, 182, 212, 0.4) !important;
        }

        button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.05) !important;
            color: #94a3b8 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
            padding: 0.4rem 0.9rem !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            margin-top: 0.1rem !important;
            margin-bottom: 0.3rem !important;
            width: auto !important;
        }
        
        button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 0.1) !important;
            color: #ffffff !important;
            border-color: #38bdf8 !important;
        }

        /* Verdict colors */
        .verdict-Ready { color: #22c55e !important; font-weight: 800; font-size: 1.75rem; text-shadow: 0 0 10px rgba(34, 197, 94, 0.3); }
        .verdict-Improve { color: #f59e0b !important; font-weight: 800; font-size: 1.75rem; text-shadow: 0 0 10px rgba(245, 158, 11, 0.3); }
        .verdict-NotReady { color: #ef4444 !important; font-weight: 800; font-size: 1.75rem; text-shadow: 0 0 10px rgba(239, 68, 68, 0.3); }
        
        /* Metric values */
        div[data-testid="stMetricValue"] {
            color: #38bdf8 !important;
            font-size: 2.5rem !important;
            font-weight: 800 !important;
            text-align: center !important;
            text-shadow: 0 0 15px rgba(56, 189, 248, 0.4) !important;
        }
        div[data-testid="stMetricLabel"] {
            text-align: center !important;
            font-size: 1.1rem !important;
            color: #cbd5e1 !important;
        }
        
        /* Center image/camera input */
        .stImage, div[data-testid="stImage"] {
            margin: 0 auto !important;
            max-width: 640px !important;
            border-radius: 14px !important;
            overflow: hidden !important;
            box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5) !important;
            border: 1px solid rgba(56, 189, 248, 0.25) !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
        .stImage > img, div[data-testid="stImage"] img {
            border-radius: 14px !important;
            max-width: 100% !important;
            margin: 0 auto !important;
            display: block !important;
        }

        /* Container card styling for st.container(border=True) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(145deg, #0b1120, #0f172a) !important;
            border: 1px solid rgba(56, 189, 248, 0.22) !important;
            border-radius: 14px !important;
            padding: 16px 20px !important;
            margin-bottom: 14px !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.35) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            gap: 0.6rem !important;
        }

        /* Standby camera preview box to prevent vertical layout shift */
        .camera-standby-box {
            background: linear-gradient(145deg, #070d19, #0b1329);
            border: 2px dashed rgba(56, 189, 248, 0.3);
            border-radius: 14px;
            height: 340px;
            max-width: 640px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 20px;
            box-shadow: inset 0 0 25px rgba(0, 0, 0, 0.5);
        }

        /* 6. MEDIA QUERY FOR MOBILE RESPONSIVENESS */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1.2rem 1rem !important; /* Proper padding on left and right */
                padding-top: 1.2rem !important;
            }
            h1 { font-size: 2rem !important; }
            h2 { font-size: 1.75rem !important; }
            h3 { font-size: 1.5rem !important; }
            
            p {
                font-size: 1rem !important;
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }
            
            .question-text {
                font-size: 2rem !important;
                margin-bottom: 1.5rem !important;
            }
            
            .stButton > button {
                width: 100% !important;
                max-width: 100% !important; /* Make button full-width */
                padding: 1.2rem 1rem !important; /* Slightly larger height for touch */
                font-size: 1.1rem !important;
            }
            
            div[data-testid="stMetricValue"] {
                font-size: 2rem !important;
            }
            
            .custom-navbar {
                flex-wrap: wrap;
                padding: 0.5rem !important;
            }
            .custom-navbar a {
                margin: 0.5rem;
                font-size: 0.9rem;
            }
            .about-section {
                flex-direction: column !important;
            }
        }

        /* 7. SINGLE PAGE NAVIGATION UI CSS */
        html {
            scroll-behavior: smooth !important;
        }
        
        /* Make precise room for fixed navbar on all tabs of the landing page */
        body:has(#landing-page-marker) .main .block-container,
        .main:has(#landing-page-marker) .block-container,
        body:has(#home-bg-injector) .main .block-container,
        .main:has(#home-bg-injector) .block-container {
            padding-top: 3.4rem !important;
        }
        
        /* Hide navbar class */
        .hide-navbar div[data-testid="stRadio"] {
            display: none !important;
        }

        /* Style st.radio as a navbar - sleek and compact */
        div[data-testid="stRadio"] {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            z-index: 999999 !important;
            background: rgba(15, 23, 42, 0.88) !important;
            backdrop-filter: blur(12px) !important;
            padding: 0.5rem 0 !important;
            display: flex !important;
            justify-content: center !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
            pointer-events: auto !important;
        }
        
        div[data-testid="stRadio"] > div[role="radiogroup"] {
            display: flex !important;
            flex-direction: row !important;
            justify-content: center !important;
            gap: 2rem !important;
            pointer-events: auto !important;
        }
        
        /* Make the radio option relatively positioned */
        div[data-testid="stRadio"] div[role="radio"] {
            position: relative !important;
            pointer-events: auto !important;
            display: flex;
            align-items: center;
        }

        /* Completely hide the radio circle SVG so only text remains */
        div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
            opacity: 0 !important;
            width: 0 !important;
        }
        
        .stRadio div[role="radiogroup"] label > div:first-child {
            display: none !important;
        }

        /* Remove "Navigation" label if it appears */
        div[data-testid="stRadio"] > label {
            display: none !important;
        }
        
        /* Style text */
        div[data-testid="stRadio"] label {
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            color: #cbd5e1 !important;
            cursor: pointer !important;
            padding: 0.5rem 1.5rem !important;
            transition: color 0.3s ease !important;
            margin: 0 !important;
            position: relative !important;
            pointer-events: auto !important;
            display: inline-block;
        }
        
        div[data-testid="stRadio"] label:hover {
            color: #38bdf8 !important;
        }

        /* Hover and active underline effect */
        div[data-testid="stRadio"] label::after {
            content: '';
            position: absolute;
            width: 0;
            height: 3px;
            display: block;
            margin-top: 5px;
            left: 50%;
            bottom: 0;
            transform: translateX(-50%);
            background: #38bdf8;
            border-radius: 2px;
            transition: width 0.25s ease;
        }

        div[data-testid="stRadio"] label:hover::after {
            width: 80%;
        }

        div[data-testid="stRadio"] label:has(input:checked)::after,
        div[data-testid="stRadio"] label[aria-checked="true"]::after,
        div[data-testid="stRadio"] div[role="radio"][aria-checked="true"] label::after,
        div[data-testid="stRadio"] div[role="radio"][aria-checked="true"]::after {
            width: 100% !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            background: #38bdf8 !important;
            box-shadow: 0 0 10px #38bdf8, 0 0 18px rgba(56, 189, 248, 0.5) !important;
        }
        
        /* Active state text color */
        div[data-testid="stRadio"] label:has(input:checked) p,
        div[data-testid="stRadio"] label[aria-checked="true"] p,
        div[data-testid="stRadio"] div[role="radio"][aria-checked="true"] label p,
        div[data-testid="stRadio"] div[role="radio"][aria-checked="true"] p,
        div[data-testid="stRadio"] label:has(input:checked),
        div[data-testid="stRadio"] div[role="radio"][aria-checked="true"] label {
            color: #38bdf8 !important;
            font-weight: 700 !important;
            text-shadow: 0 0 12px rgba(56, 189, 248, 0.4) !important;
        }

        /* SECTION STYLING */
        .page-section {
            padding-top: 0.2rem !important;
            padding-bottom: 0.8rem !important;
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            flex-grow: 1;
            animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .section-title {
            font-size: 2rem;
            font-weight: 800;
            color: #ffffff;
            text-align: center;
            margin-top: 0 !important;
            margin-bottom: 1.2rem;
            letter-spacing: 0.5px;
        }

        /* About Section Flex Layout */
        .about-section {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 2rem;
            background: rgba(255, 255, 255, 0.03);
            padding: 2rem;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .about-text {
            flex: 1;
            font-size: 1.1rem;
            line-height: 1.8;
            color: #e2e8f0;
            text-align: left !important;
        }

        .about-icon {
            flex: 1;
            text-align: center;
            font-size: 5rem;
            animation: float 4s ease-in-out infinite;
        }

        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-15px); }
            100% { transform: translateY(0px); }
        }

        /* Features Grid Layout */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            width: 100%;
            margin-top: 1rem;
        }

        .feature-card {
            background: rgba(255, 255, 255, 0.05);
            padding: 1.5rem;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
            transition: all 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.08);
            border-color: #38bdf8;
            box-shadow: 0 10px 25px rgba(56, 189, 248, 0.15);
        }

        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }

        .feature-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.5rem;
        }

        .feature-desc {
            font-size: 0.95rem;
            color: #94a3b8;
            line-height: 1.5;
        }

        /* Guidelines Styling */
        .guideline-list {
            list-style-type: none;
            padding-left: 0;
            text-align: left;
            margin: 0 auto;
            max-width: 800px;
        }
        
        .guideline-list li {
            margin-bottom: 0.8rem;
            padding-left: 1.5rem;
            position: relative;
            color: #e2e8f0;
            font-size: 1.05rem;
            line-height: 1.5;
        }
        
        .guideline-list li::before {
            content: "•";
            color: #38bdf8;
            font-weight: bold;
            font-size: 1.5rem;
            position: absolute;
            left: 0;
            top: -5px;
        }

        .guidelines-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
            width: 100%;
            margin-top: 1.5rem;
        }

        .guideline-card {
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid rgba(56, 189, 248, 0.16);
            border-radius: 16px;
            padding: 1.75rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            backdrop-filter: blur(12px);
        }

        .guideline-card:hover {
            transform: translateY(-4px);
            border-color: rgba(56, 189, 248, 0.45);
            box-shadow: 0 12px 30px rgba(56, 189, 248, 0.12);
            background: rgba(15, 23, 42, 0.82);
        }

        .guideline-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(180deg, #38bdf8 0%, #0284c7 100%);
            opacity: 0.7;
        }

        .guideline-badge {
            display: inline-block;
            align-self: flex-start;
            background: rgba(56, 189, 248, 0.12);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            margin-bottom: 0.85rem;
        }

        .guideline-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }

        .guideline-points {
            list-style-type: none;
            padding-left: 0;
            margin: 0;
            font-size: 0.95rem;
            color: #cbd5e1;
            line-height: 1.6;
        }

        .guideline-points li {
            margin-bottom: 0.6rem;
            padding-left: 1.2rem;
            position: relative;
        }

        .guideline-points li::before {
            content: '▹';
            color: #38bdf8;
            position: absolute;
            left: 0;
            font-weight: bold;
        }
        
        /* Interview Mode Badge */
        .mode-badge {
            display: inline-block;
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.4);
            color: #fca5a5;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin-bottom: 0.6rem;
            text-align: center;
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
        }

        </style>
    """, unsafe_allow_html=True)

def speak_question(text):
    """
    Generates TTS audio for the given text using pyttsx3 and plays it loudly and automatically.
    Uses maximum volume (1.0) and plays via Windows audio subsystem (winsound) and browser audio.
    Returns the exact audio duration in seconds.
    """
    import wave
    import json
    import re
    import tempfile
    try:
        import streamlit.components.v1 as components
    except Exception:
        components = None

    clean_speech_text = re.sub(r'[`*_{}#]', '', str(text)).strip()
    if not clean_speech_text:
        clean_speech_text = str(text)

    filename = os.path.join(tempfile.gettempdir(), f"interviewsense_q_{uuid.uuid4().hex[:8]}.wav")
    audio_duration = 0.0
    played_via_winsound = False

    try:
        engine = pyttsx3.init()
        engine.setProperty('volume', 1.0)  # Maximum loudness
        engine.setProperty('rate', 145)    # Clear, intelligible speaking rate
        engine.save_to_file(clean_speech_text, filename)
        engine.runAndWait()

        # Read exact wave duration
        try:
            with wave.open(filename, 'r') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                audio_duration = frames / float(rate)
        except Exception:
            audio_duration = max(2.5, len(clean_speech_text.split()) / 2.5)

        # 1. Native Windows Audio Subsystem (winsound) - 100% reliable local playback
        try:
            import winsound
            # Stop any previously playing audio to prevent overlapping speech
            winsound.PlaySound(None, winsound.SND_PURGE)
            winsound.PlaySound(filename, winsound.SND_FILENAME | winsound.SND_ASYNC)
            played_via_winsound = True
        except Exception:
            played_via_winsound = False

        # 2. Browser Audio element & Web Speech API fallback (executed ONLY when not already played via winsound)
        if not played_via_winsound:
            try:
                with open(filename, "rb") as f:
                    audio_bytes = f.read()
                audio_base64 = base64.b64encode(audio_bytes).decode()

                # Standard audio tag for browser playback
                audio_html = f'''
                    <audio autoplay="true" style="display:none;">
                        <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
                    </audio>
                '''
                st.markdown(audio_html, unsafe_allow_html=True)

                if components is not None:
                    clean_text_json = json.dumps(clean_speech_text)
                    components.html(f"""
                    <script>
                    (function() {{
                        try {{
                            const a = new Audio("data:audio/wav;base64,{audio_base64}");
                            a.volume = 1.0;
                            const p = a.play();
                            if (p !== undefined) {{
                                p.catch(function() {{
                                    const synth = (window.parent && window.parent.speechSynthesis) ? window.parent.speechSynthesis : window.speechSynthesis;
                                    if (synth) {{
                                        synth.cancel();
                                        const u = new SpeechSynthesisUtterance({clean_text_json});
                                        u.volume = 1.0;
                                        u.rate = 0.95;
                                        synth.speak(u);
                                    }}
                                }});
                            }}
                        }} catch(e) {{}}
                    }})();
                    </script>
                    """, height=0, width=0)
            except Exception:
                pass

    except Exception as e:
        print(f"TTS Error: {e}")
        audio_duration = max(2.5, len(text.split()) / 2.5)
    finally:
        try:
            if 'engine' in locals() and engine is not None:
                engine.stop()
                del engine
        except Exception:
            pass

    return max(1.5, audio_duration)


def scroll_to_top():
    """
    Forces the browser window and Streamlit scroll containers to scroll to the top immediately.
    Targets [data-testid="stAppViewContainer"], [data-testid="stMain"], .main, section.main,
    documentElement, body, window, and #top-anchor.
    Also ensures persistent click listener and MutationObserver so ANY button or tab clicked
    ensures the upcoming page opens directly from the top.
    """
    try:
        import streamlit.components.v1 as components
        import uuid
        call_id = uuid.uuid4().hex
        js_code = "<!-- scroll_reset_" + call_id + " -->\n" + """
        <script>
        (function() {
            function scrollAllToTop() {
                try {
                    const pDoc = (window.parent && window.parent.document) ? window.parent.document : document;
                    if (!pDoc) return;
                    const targets = [
                        pDoc.querySelector('[data-testid="stAppViewContainer"]'),
                        pDoc.querySelector('[data-testid="stMain"]'),
                        pDoc.querySelector('.main'),
                        pDoc.querySelector('section.main'),
                        pDoc.querySelector('.main .block-container'),
                        pDoc.querySelector('[data-testid="stApp"]'),
                        pDoc.documentElement,
                        pDoc.body
                    ];
                    targets.forEach(function(el) {
                        if (el) {
                            try { el.scrollTop = 0; } catch(e) {}
                            try { if (el.scrollTo) el.scrollTo({ top: 0, left: 0, behavior: 'instant' }); } catch(e) {}
                        }
                    });
                    const anchor = pDoc.getElementById('top-anchor');
                    if (anchor && anchor.scrollIntoView) {
                        try { anchor.scrollIntoView({ behavior: 'instant', block: 'start' }); } catch(e) {}
                    }
                    try { if (window.parent) window.parent.scrollTo(0, 0); } catch(e) {}
                    try { window.scrollTo(0, 0); } catch(e) {}
                } catch(e) {}
            }

            // Execute scroll immediately and across mounting ticks
            scrollAllToTop();
            if (typeof requestAnimationFrame === 'function') {
                requestAnimationFrame(scrollAllToTop);
            }
            [25, 75, 150, 300, 500, 800].forEach(function(t) {
                setTimeout(scrollAllToTop, t);
            });

            // Ensure parent document has the global navigation observer attached
            try {
                const pDoc = (window.parent && window.parent.document) ? window.parent.document : document;
                if (pDoc && !pDoc._stGlobalScrollObserverAttached) {
                    pDoc._stGlobalScrollObserverAttached = true;

                    // 1. Capture click on ANY button or tab
                    pDoc.addEventListener('click', function(e) {
                        const btn = e.target.closest('button') ||
                                    e.target.closest('[role="button"]') ||
                                    e.target.closest('input[type="submit"]') ||
                                    e.target.closest('div[data-testid="stRadio"] div[role="radio"]') ||
                                    e.target.closest('div[data-testid="stRadio"] label');
                        if (btn) {
                            window._stNeedsScrollTop = true;
                            window._stScrollDeadline = Date.now() + 2500;
                            scrollAllToTop();
                            [40, 100, 200, 350, 500, 750, 1000, 1400, 1900].forEach(function(delay) {
                                setTimeout(function() {
                                    if (window._stNeedsScrollTop && Date.now() < window._stScrollDeadline) {
                                        scrollAllToTop();
                                    }
                                }, delay);
                            });
                        }
                    }, true);

                    // 2. MutationObserver detects when Streamlit renders the next page
                    const container = pDoc.querySelector('[data-testid="stAppViewContainer"]') || pDoc.body;
                    if (container && window.MutationObserver) {
                        const observer = new MutationObserver(function() {
                            if (window._stNeedsScrollTop && Date.now() < window._stScrollDeadline) {
                                scrollAllToTop();
                                if (typeof requestAnimationFrame === 'function') {
                                    requestAnimationFrame(scrollAllToTop);
                                }
                            }
                        });
                        observer.observe(container, { childList: true, subtree: true });
                    }

                    // 3. User manual scroll disarms the auto-scroll
                    ['wheel', 'touchmove'].forEach(function(evt) {
                        pDoc.addEventListener(evt, function() {
                            window._stNeedsScrollTop = false;
                        }, { passive: true });
                    });
                }
            } catch(e) {}
        })();
        </script>
        """
        components.html(js_code, height=0, width=0, key=f"st_scroll_{call_id}")
    except Exception:
        pass


def clean_html(html_str: str) -> str:
    """
    Cleans multiline HTML strings so they never trigger CommonMark indented code blocks
    (<pre><code>) when passed to st.markdown(..., unsafe_allow_html=True).
    Strips leading and trailing whitespace from each line and removes empty lines.
    """
    if not html_str:
        return ""
    lines = [line.strip() for line in str(html_str).strip().splitlines() if line.strip()]
    return "\n".join(lines)


def render_html(html_str: str):
    """
    Safely renders HTML via st.markdown(..., unsafe_allow_html=True), ensuring that
    CommonMark treats it purely as HTML rather than an indented code block.
    """
    st.markdown(clean_html(html_str), unsafe_allow_html=True)
