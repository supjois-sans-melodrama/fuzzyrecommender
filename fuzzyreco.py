import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from rapidfuzz import process, fuzz

load_dotenv()

# ------------------------------------------------------------------------------
# 1. Page Configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Flow Music - Fuzzy Recommender",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# 2. State & Theme Management (Default set to Dark Mode)
# ------------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state["theme"] = "Dark Mode"

# Sidebar Branding at the very top
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🎵 Flow Music</div>', unsafe_allow_html=True)

is_dark = st.session_state["theme"] == "Dark Mode"

# Dynamic Theme Colors
bg_color = "#121316" if is_dark else "#f8fafc"
text_color = "#FFFFFF" if is_dark else "#0f172a"
subtext_color = "#94a3b8" if is_dark else "#475569"
card_bg = "#1a1c23" if is_dark else "#ffffff"
card_border = "#2d3139" if is_dark else "#cbd5e1"

# Sidebar Theme Colors
sidebar_bg = "#181a20" if is_dark else "#f1f5f9"
sidebar_text = "#FFFFFF" if is_dark else "#0f172a"

# Button Theme Colors
btn_bg = "#252836" if is_dark else "#f1f5f9"
btn_text = "#f8fafc" if is_dark else "#0f172a"
btn_border = "1px solid #3b4158" if is_dark else "1px solid #cbd5e1"

# Button Hover Theme Colors
btn_hover_bg = "#32374a" if is_dark else "#e2e8f0"
btn_hover_text = "#ffffff" if is_dark else "#0f172a"
btn_hover_border = "#06b6d4" if is_dark else "#0284c7"

# Minimalist Tab Accent Colors
tab_active_indicator = "#0ea5e9" if is_dark else "#0284c7"
tab_border_color = "#334155" if is_dark else "#cbd5e1"

st.markdown(f"""
    <style>
    /* Global Typography Reset & Matching Fonts */
    html, body, [class*="css"], button, input {{
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    }}

    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}

    /* Sidebar Styling & Contrast Fix */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {sidebar_text} !important;
    }}
    
    .sidebar-brand {{
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: {sidebar_text} !important;
        margin-bottom: 0.75rem;
        padding-top: 0.2rem;
    }}

    /* Top Radio Theme Toggle Labels */
    div[data-testid="stRadio"] label, div[data-testid="stRadio"] p, div[data-testid="stRadio"] span {{
        color: {text_color} !important;
    }}

    .hero-title {{
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
        letter-spacing: -0.03em;
        color: {text_color};
    }}
    .hero-creator {{ color: #0284c7; }}
    .hero-listener {{ color: #0369a1; }}
    .hero-sub {{
        color: {subtext_color};
        text-align: center;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }}
    .section-title {{
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 1.8rem;
        margin-bottom: 1rem;
        color: {text_color};
    }}

    /* -------------------------------------------------------------------------
       MINIMALIST BORDERLESS & FILL-LESS TABS
       ------------------------------------------------------------------------- */
    .stTabs [data-baseweb="tab-list"],
    div[data-baseweb="tab-list"] {{
        gap: 24px !important;
        border-bottom: 1px solid {tab_border_color} !important;
        margin-bottom: 1.5rem !important;
        padding: 0px !important;
    }}

    /* Active Tab Bottom Indicator Bar */
    .stTabs [data-baseweb="tab-highlight"],
    div[data-baseweb="tab-highlight"] {{
        background-color: {tab_active_indicator} !important;
        height: 3px !important;
        border-radius: 3px 3px 0 0 !important;
    }}

    /* Tab Base Styles (Transparent, No Border) */
    .stTabs [data-baseweb="tab"],
    div[data-baseweb="tab-list"] button[data-baseweb="tab"] {{
        background-color: transparent !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 10px 4px !important;
        transition: color 0.2s ease-in-out !important;
    }}

    /* UNSELECTED INACTIVE TAB TEXT */
    .stTabs [data-baseweb="tab"][aria-selected="false"] *,
    .stTabs [data-baseweb="tab"][aria-selected="false"] div,
    .stTabs [data-baseweb="tab"][aria-selected="false"] span,
    .stTabs [data-baseweb="tab"][aria-selected="false"] p,
    div[data-baseweb="tab-list"] button[aria-selected="false"] *,
    div[data-baseweb="tab-list"] button[aria-selected="false"] div,
    div[data-baseweb="tab-list"] button[aria-selected="false"] span,
    div[data-baseweb="tab-list"] button[aria-selected="false"] p {{
        color: {subtext_color} !important;
        -webkit-text-fill-color: {subtext_color} !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
    }}

    /* SELECTED ACTIVE TAB TEXT */
    .stTabs [data-baseweb="tab"][aria-selected="true"] *,
    .stTabs [data-baseweb="tab"][aria-selected="true"] div,
    .stTabs [data-baseweb="tab"][aria-selected="true"] span,
    .stTabs [data-baseweb="tab"][aria-selected="true"] p,
    div[data-baseweb="tab-list"] button[aria-selected="true"] *,
    div[data-baseweb="tab-list"] button[aria-selected="true"] div,
    div[data-baseweb="tab-list"] button[aria-selected="true"] span,
    div[data-baseweb="tab-list"] button[aria-selected="true"] p {{
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }}

    /* Tab Hover Effect */
    .stTabs [data-baseweb="tab"][aria-selected="false"]:hover *,
    div[data-baseweb="tab-list"] button[aria-selected="false"]:hover * {{
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
    }}
    
    /* -------------------------------------------------------------------------
       CARDS WITH FIXED MAXIMUM WIDTH TO PREVENT OVER-STRETCHING
       ------------------------------------------------------------------------- */
    .flow-card-container {{
        max-width: 310px;
        width: 100%;
    }}

    .flow-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 14px;
        padding: 16px;
        height: 195px;
        margin-bottom: 12px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: {'0 4px 6px -1px rgba(0, 0, 0, 0.4)' if is_dark else '0 4px 6px -1px rgba(0, 0, 0, 0.05)'};
        transition: border-color 0.2s ease, transform 0.2s ease;
    }}
    .flow-card:hover {{
        border-color: #0284c7;
        transform: translateY(-2px);
    }}
    
    .video-card {{
        background: linear-gradient(180deg, #1e1b4b 0%, #0f172a 100%);
        border: 1px solid #3b82f6;
        border-radius: 14px;
        padding: 16px;
        height: 195px;
        margin-bottom: 12px;
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        color: #ffffff !important;
        transition: transform 0.2s ease;
    }}
    .video-card:hover {{
        transform: translateY(-2px);
    }}
    .video-play-icon {{
        position: absolute;
        top: 38%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 2.2rem;
        color: #ffffff;
        opacity: 0.9;
        text-shadow: 0px 4px 8px rgba(0,0,0,0.8);
    }}

    .space-card {{
        border-radius: 14px;
        padding: 16px;
        height: 195px;
        margin-bottom: 12px;
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.2s ease;
    }}
    .space-card:hover {{
        transform: translateY(-2px);
    }}
    
    .card-badge {{
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #0284c7;
        margin-bottom: 4px;
    }}
    .card-title {{
        font-size: 0.98rem;
        font-weight: 700;
        color: inherit;
        line-height: 1.25;
    }}
    .card-sub {{
        font-size: 0.8rem;
        color: {subtext_color};
        margin-top: 4px;
    }}

    /* -------------------------------------------------------------------------
       ACTION BUTTONS
       ------------------------------------------------------------------------- */
    .stButton > button {{
        background-color: {btn_bg} !important;
        color: {btn_text} !important;
        border: {btn_border} !important;
        border-radius: 10px !important;
        font-family: system-ui, -apple-system, sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.02em !important;
        padding: 6px 12px !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }}
    
    .stButton > button:hover {{
        background-color: {btn_hover_bg} !important;
        color: {btn_hover_text} !important;
        border-color: {btn_hover_border} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 3. Dataset Loader & Master Pools
# ------------------------------------------------------------------------------
@st.cache_data
def load_dataset():
    excel_path = "flowmusic.xlsx"
    if not os.path.exists(excel_path):
        return pd.DataFrame([
            {"Song": "I Remain", "Genre": "Epic Cinematic Folk-Bass", "Main Creature": "dragon and rider", "Summary": "A reflection on survival", "Prompt": "Create a song about dragon riders"},
            {"Song": "Hold On", "Genre": "Soulful Narrative Folk-Rock", "Main Creature": "Gardener elf", "Summary": "Resilience in a blooming garden", "Prompt": "Folk song about an elf farmer"},
            {"Song": "Rapid-er", "Genre": "Gypsy Jazz EDM", "Main Creature": "Frustrated flyer", "Summary": "High energy beat seeking a blade", "Prompt": "Gypsy jazz EDM remix track"},
            {"Song": "Over Third Man", "Genre": "Indie-Folk", "Main Creature": "Wizard batsman", "Summary": "Defiant shot at Centurion", "Prompt": "Indie song about a wizard batsman"},
            {"Song": "Total Saturation", "Genre": "Folktronica", "Main Creature": "Observer elf", "Summary": "Watching the world freeze", "Prompt": "Folktronica track about ice"},
            {"Song": "The Prize is Ours", "Genre": "Dark Orchestral Metal", "Main Creature": "Keeper and Hunter", "Summary": "Folk horror battle", "Prompt": "Dark orchestral folk horror"},
            {"Song": "Watering Plastic Flowers", "Genre": "Americana Folk", "Main Creature": "Weary laborer", "Summary": "Heavy pail and longing", "Prompt": "Americana troubadour song"},
            {"Song": "This Song Does Not Matter", "Genre": "Dreamy Trip-Hop", "Main Creature": "Mermaid with lead tail", "Summary": "Drying scales at sunset", "Prompt": "Dreamy trip-hop mermaid track"}
        ])
    df = pd.read_excel(excel_path)
    df["Song"] = df["Song"].fillna("Untitled Track")
    df["Genre"] = df["Genre"].fillna("Fusion")
    df["Main Creature"] = df["Main Creature"].fillna("Entity")
    df["Summary"] = df["Summary"].fillna("")
    df["Prompt"] = df["Prompt"].fillna("")
    return df

df = load_dataset()

# Master Spaces Catalog
MASTER_SPACES = [
    {"id": "space_101", "badge": "AI Lab", "icon": "🤖", "bg_gradient": "linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)", "title": "Robot Music Lab", "sub": "12 Active Creators Jamming", "action": "Join Robot Music Lab"},
    {"id": "space_102", "badge": "Fantasy Stage", "icon": "🐉", "bg_gradient": "linear-gradient(135deg, #b91c1c 0%, #7c2d12 100%)", "title": "Dragon Maze Musical", "sub": "Live Fantasy Score Co-op", "action": "Join Dragon Maze Musical"},
    {"id": "space_103", "badge": "Game Room", "icon": "🎯", "bg_gradient": "linear-gradient(135deg, #15803d 0%, #047857 100%)", "title": "Music Trivia", "sub": "AI Audio Guessing Challenge", "action": "Enter Music Trivia space"},
    {"id": "space_104", "badge": "Classical Fusion", "icon": "🪕", "bg_gradient": "linear-gradient(135deg, #a21caf 0%, #6b21a8 100%)", "title": "Resonance Darbar", "sub": "Classical Fusion Studio", "action": "Enter Resonance Darbar"},
    {"id": "space_105", "badge": "Audio Visuals", "icon": "🌊", "bg_gradient": "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)", "title": "Waveform Visualizer", "sub": "Real-time Frequency Canvas", "action": "Launch Waveform Visualizer"},
    {"id": "space_106", "badge": "Instrument", "icon": "🎹", "bg_gradient": "linear-gradient(135deg, #d97706 0%, #b45309 100%)", "title": "Mini Keyboard", "sub": "Interactive Melody Composer", "action": "Open Mini Keyboard"},
    {"id": "space_107", "badge": "Rhythm Lab", "icon": "🥁", "bg_gradient": "linear-gradient(135deg, #4338ca 0%, #3730a3 100%)", "title": "Simple Drums", "sub": "Groove & Beat Sequencer", "action": "Open Simple Drums"},
    {"id": "space_108", "badge": "Party Zone", "icon": "🪩", "bg_gradient": "linear-gradient(135deg, #db2777 0%, #9d174d 100%)", "title": "Disco Oasis", "sub": "Non-stop Retro Synth Jam", "action": "Enter Disco Oasis"},
    {"id": "space_109", "badge": "Ear Training", "icon": "👂", "bg_gradient": "linear-gradient(135deg, #0d9488 0%, #0f766e 100%)", "title": "Relative Pitch Trainer", "sub": "Ear Training & Interval Quiz", "action": "Start Pitch Trainer"},
    {"id": "space_110", "badge": "Creative Canvas", "icon": "🎨", "bg_gradient": "linear-gradient(135deg, #ca8a04 0%, #a16207 100%)", "title": "Doodle Lab", "sub": "Sketch-to-Sound Studio", "action": "Open Doodle Lab"},
    {"id": "space_111", "badge": "Rhythm Quiz", "icon": "⏱️", "bg_gradient": "linear-gradient(135deg, #059669 0%, #047857 100%)", "title": "Guess The BPM", "sub": "Tempo Estimation Challenge", "action": "Play Guess The BPM"}
]

if "disliked_ids" not in st.session_state:
    st.session_state["disliked_ids"] = set()

if "liked_ids" not in st.session_state:
    st.session_state["liked_ids"] = set()

def get_filtered_pools(query="", count=4):
    available = df[~df.index.isin(st.session_state["disliked_ids"])].copy()

    if query and query.strip():
        q = query.strip().lower()

        corpus = (
            available["Song"].astype(str) + " " +
            available["Genre"].astype(str) + " " +
            available["Main Creature"].astype(str) + " " +
            available["Summary"].astype(str) + " " +
            available["Prompt"].astype(str)
        ).str.lower()

        matches = process.extract(
            q,
            corpus,
            scorer=fuzz.WRatio,
            limit=len(available),
            score_cutoff=45
        )

        if matches:
            matched_indices = [idx for _, score, idx in matches]
            available = available.loc[matched_indices]

    pool_indices = available.index.tolist()

    starter_idx = pool_indices[:count]
    song_idx = pool_indices[count:count*2] if len(pool_indices) >= count*2 else pool_indices[:count]
    video_idx = pool_indices[count*2:count*3] if len(pool_indices) >= count*3 else pool_indices[::-1][:count]

    return df.loc[starter_idx], df.loc[song_idx], df.loc[video_idx]

def get_filtered_spaces(query="", count=4):
    available = [s for s in MASTER_SPACES if s["id"] not in st.session_state["disliked_ids"]]
    
    if query and query.strip():
        q = query.strip().lower()

        space_corpus = {
            s["id"]: f"{s['title']} {s['sub']} {s['badge']}".lower()
            for s in available
        }

        matches = process.extract(
            q,
            space_corpus,
            scorer=fuzz.WRatio,
            limit=len(available),
            score_cutoff=45
        )

        if matches:
            matched_ids = [space_id for _, score, space_id in matches]
            available = [s for sid in matched_ids for s in available if s["id"] == sid]

    return available[:count]

# ------------------------------------------------------------------------------
# 4. Sidebar Navigation
# ------------------------------------------------------------------------------
st.sidebar.button("+ New session", use_container_width=True)
st.sidebar.markdown("---")
st.sidebar.caption("QUICK SPACES")
st.sidebar.text("• Robot Music Lab")
st.sidebar.text("• Dragon Maze Musical")
st.sidebar.text("• Waveform Visualizer")
st.sidebar.text("• Disco Oasis")

# Shared Search Value State
if "search_query_val" not in st.session_state:
    st.session_state["search_query_val"] = ""

# ------------------------------------------------------------------------------
# Top App Area: Theme Toggle & Controls Header
# ------------------------------------------------------------------------------
top_col1, top_col2 = st.columns([6, 2])
with top_col2:
    theme_options = ["Dark Mode", "Light Mode"]
    current_index = 0 if st.session_state["theme"] == "Dark Mode" else 1
    theme_choice = st.radio(
        "Appearance", 
        theme_options, 
        index=current_index,
        horizontal=True,
        label_visibility="collapsed"
    )
    if theme_choice != st.session_state["theme"]:
        st.session_state["theme"] = theme_choice
        st.rerun()

# ------------------------------------------------------------------------------
# 5. Dynamic Card Renderer (Fixed width for single-item rows)
# ------------------------------------------------------------------------------
def render_cards(title, cat_key, card_list, mode_name, card_type="standard"):
    if not card_list:
        return
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    
    # Always create a 4-column grid layout structure to prevent single items from stretching full-width
    cols = st.columns(4)

    for idx, c in enumerate(card_list):
        cid = c["id"]
        col_idx = idx % 4
        with cols[col_idx]:
            st.markdown('<div class="flow-card-container">', unsafe_allow_html=True)
            if card_type == "video":
                st.markdown(f"""
                    <div class="video-card">
                        <div class="card-badge">🎬 {c['badge']}</div>
                        <div class="video-play-icon">▶</div>
                        <div>
                            <div class="card-title">{c['title']}</div>
                            <div style="font-size:0.78rem; color:#cbd5e1; margin-top:4px;">{c['sub']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            elif card_type == "space":
                st.markdown(f"""
                    <div class="space-card" style="background: {c['bg_gradient']};">
                        <div class="card-badge" style="color: #67e8f9;">📡 {c['badge']}</div>
                        <div style="font-size:1.8rem; text-align:center;">{c['icon']}</div>
                        <div>
                            <div class="card-title">{c['title']}</div>
                            <div style="font-size:0.78rem; color:#f1f5f9; margin-top:4px;">{c['sub']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="flow-card">
                        <div>
                            <div class="card-badge">{c['badge']}</div>
                            <div class="card-title">{c['title']}</div>
                            <div class="card-sub">{c['sub']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            bcol1, bcol2, bcol3 = st.columns([2.5, 1, 1])
            
            with bcol1:
                action_text = "Use" if mode_name == "create" else "Play"
                if st.button(action_text, key=f"act_{cat_key}_{cid}_{idx}", use_container_width=True):
                    st.session_state["search_query_val"] = c["action"]
                    st.rerun()

            with bcol2:
                liked = cid in st.session_state["liked_ids"]
                icon = "❤️" if liked else "👍"
                if st.button(icon, key=f"lk_{cat_key}_{cid}_{idx}"):
                    if liked:
                        st.session_state["liked_ids"].remove(cid)
                    else:
                        st.session_state["liked_ids"].add(cid)
                        st.toast(f"Liked '{c['title']}'!")
                    st.rerun()

            with bcol3:
                if st.button("👎", key=f"dk_{cat_key}_{cid}_{idx}"):
                    st.session_state["disliked_ids"].add(cid)
                    st.toast(f"Removed '{c['title']}'!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 6. Main Surface Tabs
# ------------------------------------------------------------------------------
tab_create, tab_explore = st.tabs(["💡 I want to create", "🎧 I want to explore"])

# ==============================================================================
# TAB 1: CREATOR SURFACE
# ==============================================================================
with tab_create:
    st.markdown('<div class="hero-title">Bring your taste. Create any <span class="hero-creator">vibe</span>.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Chat with your co-producer about ideas, edit songs and stay in flow with free unlimited downloads.</div>', unsafe_allow_html=True)

    create_query = st.text_input(
        "", 
        value=st.session_state["search_query_val"],
        placeholder="Search genres, creatures, spaces or prompt ideas...", 
        key="create_search_input"
    )

    starters_df, songs_df, videos_df = get_filtered_pools(create_query, count=4)
    c_spaces = get_filtered_spaces(create_query, count=4)

    # 1. Get Started Starters
    starters = [
        {
            "id": idx, "badge": "Creative Prompt",
            "title": f"Make a {r['Genre'].split()[0]} Track",
            "sub": r["Prompt"][:70] + "...", "action": r["Prompt"]
        } for idx, r in starters_df.iterrows()
    ]
    render_cards("Get started", "c_starter", starters, "create")

    # 2. Recommended Reference Songs
    c_songs = [
        {
            "id": idx, "badge": r["Genre"],
            "title": r["Song"],
            "sub": f"Reference Concept: {r['Main Creature']}",
            "action": f"Create a track inspired by '{r['Song']}' ({r['Genre']})"
        } for idx, r in songs_df.iterrows()
    ]
    render_cards("Recommended Songs (For Reference)", "c_songs", c_songs, "create")

    # 3. Recommended Visual Prompts
    c_videos = [
        {
            "id": idx, "badge": "AI Video Prompt",
            "title": f"Visual: {r['Song']}",
            "sub": f"4K Scene: {r['Main Creature']} in {r['Genre']} visual theme.",
            "action": f"Generate music video prompt for {r['Main Creature']}."
        } for idx, r in videos_df.iterrows()
    ]
    render_cards("Recommended Visual Prompts", "c_videos", c_videos, "create", card_type="video")

    # 4. Recommended Spaces
    if c_spaces:
        render_cards("Recommended Spaces", "c_spaces", c_spaces, "create", card_type="space")

# ==============================================================================
# TAB 2: EXPLORE / LISTENER SURFACE
# ==============================================================================
with tab_explore:
    st.markdown('<div class="hero-title">Bring your taste. Discover any <span class="hero-listener">song</span>.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Listen to live spaces, curated community playlists, and watch music videos.</div>', unsafe_allow_html=True)

    explore_query = st.text_input(
        "", 
        value=st.session_state["search_query_val"],
        placeholder="Search songs, artists, creatures, spaces, or playlists...", 
        key="explore_search_input"
    )

    starters_df, songs_df, videos_df = get_filtered_pools(explore_query, count=4)
    l_spaces = get_filtered_spaces(explore_query, count=4)

    # 1. Recommended Songs
    l_songs = [
        {
            "id": idx, "badge": r["Genre"],
            "title": r["Song"],
            "sub": r["Summary"][:70] + "...", "action": r["Song"]
        } for idx, r in songs_df.iterrows()
    ]
    render_cards("Recommended Songs", "l_songs", l_songs, "explore")

    # 2. Recommended Music Videos
    l_videos = [
        {
            "id": idx, "badge": "Official AI Video",
            "title": f"{r['Song']} (Music Video)",
            "sub": f"Visuals: {r['Main Creature']}", "action": f"Play video for {r['Song']}"
        } for idx, r in videos_df.iterrows()
    ]
    render_cards("Recommended Videos", "l_videos", l_videos, "explore", card_type="video")

    # 3. Trending Spaces
    if l_spaces:
        render_cards("Trending Spaces", "l_spaces", l_spaces, "explore", card_type="space")

    # 4. Curated Playlists
    playlists = [
        {"id": "p_301", "badge": "Curated Playlist", "title": "Elven Folk & Bass", "sub": "24 Tracks · Epic Fantasy EDM", "action": "Elven Folk & Bass playlist"},
        {"id": "p_302", "badge": "Top Charts", "title": "Dragon Rider Anthems", "sub": "18 Tracks · High Energy Orchestral", "action": "Dragon Rider Anthems playlist"},
        {"id": "p_303", "badge": "Chillout", "title": "Late Night Trip-Hop", "sub": "30 Tracks · Lo-Fi & Downtempo", "action": "Late Night Trip-Hop playlist"},
        {"id": "p_304", "badge": "Discover Weekly", "title": "Himalayan Folk-Trap", "sub": "15 Tracks · Deep Sub Bass & Flutes", "action": "Himalayan Folk-Trap playlist"}
    ]
    render_cards("Curated Playlists", "l_playlists", playlists, "explore")