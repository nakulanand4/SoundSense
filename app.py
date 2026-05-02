"""
SoundSense - Music Recommendation System
Nakul Anand | VIPS-TC | 2025
"""

import streamlit as st
import pandas as pd
from recommender import get_recommendations, get_by_mood
from ollama_search import search_by_query
from music_player import get_youtube_embed_url, render_player


st.set_page_config(
    page_title="SoundSense",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# styles
st.markdown("""
<style>
    /* google font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* apply font to everything except icons */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp label, .stApp div[data-testid="stMarkdownContainer"], .stApp div[data-baseweb="select"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* dark bg with subtle gradients on corners */
    .stApp { 
        background-color: #050505; 
        background-image: 
            radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
            radial-gradient(at 50% 0%, hsla(225,39%,30%,0.1) 0, transparent 50%), 
            radial-gradient(at 100% 0%, hsla(339,49%,30%,0.1) 0, transparent 50%);
        color: #f8fafc;
        background-attachment: fixed;
    }

    /* purple-pink gradient title text */
    .gradient-text {
        background: linear-gradient(to right, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 1rem;
    }

    /* song card styling */
    .song-card {
        background: rgba(20, 20, 25, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-left: 4px solid transparent;
        border-radius: 16px;
        padding: 20px 24px;
        margin: 10px 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: fadeInUp 0.5s ease backwards;
    }
    .song-card:hover { 
        transform: translateY(-5px) scale(1.01);
        border-left: 4px solid #a855f7;
        border-color: rgba(168, 85, 247, 0.4); 
        box-shadow: 0 15px 30px -10px rgba(168, 85, 247, 0.25);
        background: rgba(30, 30, 35, 0.8);
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .song-title { font-size: 1.2rem; font-weight: 700; color: #ffffff; margin-bottom: 8px; letter-spacing: -0.01em; }
    .song-meta  { font-size: 0.85rem; color: #94a3b8; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-weight: 500; }

    /* badges for genre/mood/lang */
    .badge {
        display: inline-flex; align-items: center; justify-content: center;
        padding: 4px 10px; border-radius: 8px; font-size: 0.65rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.1em;
        transition: all 0.3s ease;
    }
    .badge:hover { filter: brightness(1.2); }
    .badge-genre { background: rgba(168, 85, 247, 0.15); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.3); }
    .badge-mood  { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-lang  { background: rgba(14, 165, 233, 0.15); color: #7dd3fc; border: 1px solid rgba(14, 165, 233, 0.3); }
    .badge-score { background: linear-gradient(135deg, #ec4899, #f43f5e); color: white; border: none; box-shadow: 0 4px 10px rgba(236, 72, 153, 0.4); }

    /* now playing bar at top */
    .now-playing-bar {
        background: linear-gradient(90deg, rgba(15,23,42,0.9) 0%, rgba(30,27,75,0.9) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(168, 85, 247, 0.25);
        border-radius: 20px;
        padding: 24px 30px;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
    }
    /* shine sweep animation */
    .now-playing-bar::after {
        content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        transform: skewX(-20deg); animation: shine 6s infinite; pointer-events: none;
    }
    @keyframes shine { 0% {left: -100%;} 20% {left: 200%;} 100% {left: 200%;} }

    /* audio wave bars */
    .soundwave { display: inline-flex; align-items: center; gap: 3px; height: 14px; margin-right: 8px; }
    .bar { width: 3px; height: 100%; background: #10b981; border-radius: 3px; animation: wave 1s ease-in-out infinite alternate; box-shadow: 0 0 8px #10b981; }
    .bar:nth-child(2) { animation-delay: 0.2s; height: 60%; }
    .bar:nth-child(3) { animation-delay: 0.4s; height: 80%; }
    @keyframes wave { 0% { transform: scaleY(0.4); } 100% { transform: scaleY(1); } }

    .np-label  { font-size: 0.75rem; color: #a78bfa; text-transform: uppercase; letter-spacing: 0.15em; font-weight: 800; display: flex; align-items: center; margin-bottom: 8px; }
    .np-title  { font-size: 1.6rem; font-weight: 800; color: white; margin: 4px 0 8px 0; letter-spacing: -0.02em; }
    .np-artist { font-size: 1rem; color: #cbd5e1; display: flex; align-items: center; gap: 12px; font-weight: 500; }

    /* spinning cd in sidebar */
    .sidebar-np-card {
        background: rgba(20, 20, 25, 0.5);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 16px;
        padding: 30px 16px;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
    }
    .cd-icon { 
        font-size: 4rem; margin-bottom: 16px; 
        filter: drop-shadow(0 8px 12px rgba(0,0,0,0.5));
        animation: spin 8s linear infinite;
        display: inline-block;
    }
    @keyframes spin { 100% { transform: rotate(360deg); } }

    .section-header {
        font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.2em; 
        font-weight: 800; margin: 32px 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 10px;
    }

    div[data-testid="stButton"] button { 
        background: rgba(255, 255, 255, 0.05); 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        border-radius: 12px; 
        color: #fff; 
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
    }
    div[data-testid="stButton"] button:hover { 
        background: rgba(168, 85, 247, 0.1); 
        border-color: #a855f7; 
        transform: translateY(-2px); 
        box-shadow: 0 6px 15px rgba(168, 85, 247, 0.25); 
        color: #d8b4fe; 
    }
    div[data-testid="stButton"] button:active { transform: translateY(0); }

    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] > div[data-baseweb="select"] {
        background: rgba(20, 20, 25, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px;
        color: white !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #a855f7 !important;
        box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.2) !important;
    }

    div[data-testid="stExpander"] {
        background: rgba(20, 20, 25, 0.6) !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    div[data-testid="stExpander"] summary {
        color: #c4b5fd !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)


# session state defaults
defaults = {
    "player_song": None,
    "player_artist": None,
    "player_genre": None,
    "player_mood": None,
    "embed_url": None,
    "play_history": [],
    "liked_songs": [],
    "disliked_songs": [],
    "ai_results": None,
    "ai_explanation": None,
    "active_tab": "Recommend",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# callbacks
def play_song_callback(song, artist, genre, mood):
    url = fetch_embed(song, artist)
    st.session_state.player_song = song
    st.session_state.player_artist = artist
    st.session_state.player_genre = genre
    st.session_state.player_mood = mood
    st.session_state.embed_url = url
    if song not in st.session_state.play_history:
        st.session_state.play_history.append(song)


def like_song_callback(song):
    if song not in st.session_state.liked_songs:
        st.session_state.liked_songs.append(song)
        if song not in st.session_state.play_history:
            st.session_state.play_history.append(song)


def dislike_song_callback(song):
    if song not in st.session_state.disliked_songs:
        st.session_state.disliked_songs.append(song)


def clear_session_callback():
    st.session_state.play_history = []
    st.session_state.liked_songs = []
    st.session_state.disliked_songs = []


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv("dataset.csv")


@st.cache_data
def fetch_embed(song: str, artist: str) -> str | None:
    return get_youtube_embed_url(song, artist)


def render_song_card(rank, rec, show_score=True, show_play=True):
    col1, col2 = st.columns([6, 1])
    with col1:
        score_badge = (
            f'<span class="badge badge-score">Match {rec["match_score"]:.0%}</span>'
            if show_score and "match_score" in rec else ""
        )
        lang = rec.get("language", "")

        html_content = f"""
        <div class="song-card">
            <div class="song-title">{rank}. {rec['song']}</div>
            <div class="song-meta">
                <span style="color:#e2e8f0; font-weight:500;">{rec['artist']}</span>
                <span class="badge badge-genre">{rec['genre']}</span>
                <span class="badge badge-mood">{rec['mood']}</span>
                <span class="badge badge-lang">{lang}</span>
                {score_badge}
            </div>
        </div>
        """.replace('\n', '')

        st.markdown(html_content, unsafe_allow_html=True)

    with col2:
        st.write("")
        if show_play:
            st.button("▶ Play", key=f"play_{rank}_{rec['song']}", help="Play", use_container_width=True,
                      on_click=play_song_callback, args=(rec["song"], rec["artist"], rec["genre"], rec["mood"]))
        c1, c2 = st.columns(2)
        with c1:
            st.button("👍", key=f"like_{rank}_{rec['song']}", help="Like", on_click=like_song_callback,
                      args=(rec["song"],))
        with c2:
            st.button("👎", key=f"dislike_{rank}_{rec['song']}", help="Dislike", on_click=dislike_song_callback,
                      args=(rec["song"],))


# sidebar
with st.sidebar:
    st.markdown("<h2 style='font-weight: 800; letter-spacing: -1px;'>🎵 SoundSense</h2>", unsafe_allow_html=True)
    st.caption("Hybrid Music Recommender · BCA Final Year Project")
    st.divider()

    if st.session_state.embed_url:
        st.markdown(f"""
        <div class="sidebar-np-card">
            <div class="cd-icon">💿</div>
            <div style="font-size: 0.75rem; color: #a78bfa; font-weight: 800; letter-spacing: 0.15em; margin-bottom: 8px;">NOW PLAYING</div>
            <div style="font-size: 1.25rem; font-weight: 800; color: white; margin: 4px 0;">{st.session_state.player_song}</div>
            <div style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 16px;">{st.session_state.player_artist}</div>
            <span class="badge badge-genre">{st.session_state.player_genre}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="text-align:center;color:#64748b;padding:30px 0;font-size:0.9rem;background:rgba(20,20,25,0.5);border-radius:16px;border:1px dashed #334155;">'
            '<div style="font-size:2rem;margin-bottom:8px;">🎧</div>Select a track to start</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    if st.session_state.play_history:
        st.markdown("<h3 style='font-size: 1rem; font-weight: 700;'> Your Session</h3>", unsafe_allow_html=True)
        st.caption(f"Played: {len(st.session_state.play_history)} songs")
        st.caption(f"Liked: {len(st.session_state.liked_songs)} · Disliked: {len(st.session_state.disliked_songs)}")
        st.button("Clear session", use_container_width=True, on_click=clear_session_callback)
        st.divider()

    st.caption("Nakul Anand · VIPS-TC · 2025")


# main page
st.markdown(
    "<h1 class='gradient-text'>🎵 SoundSense <span style='font-size: 1.4rem; font-weight: 500; color: #94a3b8;word-spacing: 4px;'>| Find Your Rhythm</span></h1>",
    unsafe_allow_html=True)

df = load_data()

# show now playing bar if something is playing
if st.session_state.embed_url:
    st.markdown(f"""
    <div class="now-playing-bar">
        <div class="np-label">
            <div class="soundwave">
                <div class="bar"></div><div class="bar"></div><div class="bar"></div>
            </div>
            Now Playing
        </div>
        <div class="np-title">{st.session_state.player_song}</div>
        <div class="np-artist">
            <span style="color:#f8fafc; font-weight:700;">{st.session_state.player_artist}</span>
            <span class="badge badge-genre">{st.session_state.player_genre}</span>
            <span class="badge badge-mood">{st.session_state.player_mood}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.components.v1.html(render_player(st.session_state.embed_url), height=220)
    st.markdown("")

tab1, tab2, tab3 = st.tabs(["Recommend", "Discover by Mood", "Ask AI"])

with tab1:
    st.markdown("### 🔍 Quick Search Library")

    search_options = ["— Type to search —"] + (df['song'] + " by " + df['artist']).tolist()

    selected_search = st.selectbox(
        "Search by Song or Artist Name",
        options=search_options,
        label_visibility="collapsed"
    )

    if selected_search and selected_search != "— Type to search —":
        song_name = selected_search.split(" by ")[0]
        search_results = df[df['song'] == song_name]

        if not search_results.empty:
            for i, (_, rec) in enumerate(search_results.iterrows(), 1):
                render_song_card(f"S{i}", rec.to_dict(), show_score=False)

    st.divider()
    st.markdown("###  Get Recommendations")

    col_filter, _ = st.columns([2, 1])
    with col_filter:
        lang_choice = st.radio(
            "Filter by Language",
            options=["Mix (All)", "Hindi", "English"],
            horizontal=True,
            label_visibility="collapsed"
        )

    if lang_choice == "Hindi":
        filtered_df = df[df["language"].str.casefold() == "hindi"]
    elif lang_choice == "English":
        filtered_df = df[df["language"].str.casefold() == "english"]
    else:
        filtered_df = df

    song_list = filtered_df["song"].tolist()

    selected_song = st.selectbox(
        "Choose a song",
        options=["— Pick a song —"] + song_list,
    )

    has_session = bool(st.session_state.play_history)
    if has_session:
        st.markdown(
            f'<div style="margin-top: 10px;"><span style="font-size:0.85rem;color:#94a3b8;font-weight:600;">Recommendations personalised using your session history</span>'
            f'<span style="display:inline-block; background: linear-gradient(90deg, #8b5cf6, #3b82f6); color: white; font-size: 0.65rem; font-weight: 800; padding: 4px 12px; border-radius: 20px; margin-left: 12px; box-shadow: 0 2px 10px rgba(139, 92, 246, 0.3);">HYBRID ACTIVE</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    if selected_song and selected_song != "— Pick a song —":
        row = df[df["song"] == selected_song].iloc[0]

        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(f"""
            <div class="song-card" style="border-left-color: #ec4899; background:rgba(236,72,153,0.05);">
                <div style="font-size:0.7rem;color:#f472b6;margin-bottom:8px;font-weight:800;letter-spacing:0.15em;">SELECTED TRACK</div>
                <div class="song-title" style="font-size:1.3rem;">{row['song']}</div>
                <div class="song-meta">
                    <span style="color:#e2e8f0; font-weight:600;">{row['artist']}</span>
                    <span class="badge badge-genre">{row['genre']}</span>
                    <span class="badge badge-mood">{row['mood']}</span>
                    <span class="badge badge-lang">{row['language']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.write("")
            st.button("▶ Play", key="play_selected", use_container_width=True, on_click=play_song_callback,
                      args=(row["song"], row["artist"], row["genre"], row["mood"]))

        st.markdown('<div class="section-header">Recommended for you</div>', unsafe_allow_html=True)

        recs = get_recommendations(
            selected_song,
            df,
            session_history=st.session_state.play_history if has_session else None,
        )

        if recs is not None and not recs.empty:
            for i, (_, rec) in enumerate(recs.iterrows(), 1):
                render_song_card(i, rec.to_dict(), show_score=True)
        else:
            st.info("Song not found in dataset.")

with tab2:
    st.markdown("")
    moods = ["Happy", "Sad", "Romantic", "Energetic", "Dark", "Calm", "Melancholic", "Motivational"]
    cols = st.columns(4)
    mood_icons = {"Happy": "😊", "Sad": "😢", "Romantic": "❤️", "Energetic": "⚡",
                  "Dark": "🌑", "Calm": "🌊", "Melancholic": "🌧️", "Motivational": "🔥"}

    if "selected_mood" not in st.session_state:
        st.session_state.selected_mood = None

    for i, mood in enumerate(moods):
        with cols[i % 4]:
            if st.button(
                    f"{mood_icons[mood]} {mood}",
                    key=f"mood_{mood}",
                    use_container_width=True,
            ):
                st.session_state.selected_mood = mood

    if st.session_state.selected_mood:
        mood = st.session_state.selected_mood
        st.markdown(f'<div class="section-header">{mood_icons[mood]} Top {mood} Songs</div>',
                    unsafe_allow_html=True)
        mood_songs = get_by_mood(mood, df, top_n=10)
        for i, (_, rec) in enumerate(mood_songs.iterrows(), 1):
            render_song_card(i, rec.to_dict(), show_score=False)

with tab3:
    st.markdown("")

    st.markdown("Describe what you want to listen to in plain English or Hindi. (Powered by Local Ollama AI)")
    examples = [
        "something sad and slow for a rainy evening",
        "energetic Bollywood songs for a workout",
        "romantic Hindi songs like Arijit Singh",
        "dark intense English rock songs",
    ]
    st.caption("Examples: " + " · ".join(f'*"{e}"*' for e in examples[:3]))
    st.markdown("")

    nl_query = st.text_input(
        "What do you want to hear?",
        placeholder="e.g. sad slow songs for a rainy night...",
        key="nl_query",
    )

    if st.button(" Ask AI", use_container_width=False) and nl_query.strip():
        with st.spinner("Asking Local AI Model (This might take a few seconds)..."):
            try:
                results, explanation = search_by_query(nl_query, df)
                st.session_state.ai_results = results
                st.session_state.ai_explanation = explanation
            except Exception as e:
                st.error(f"Local AI error: {e}")
                st.session_state.ai_results = None

    if st.session_state.ai_results is not None:
        if st.session_state.ai_explanation:
            with st.expander(" View AI Thinking Process"):
                st.markdown(
                    f'<div style="background: rgba(30, 41, 59, 0.5); border-left: 3px solid #a78bfa; border-radius: 0 8px 8px 0; padding: 16px 20px; font-size: 0.95rem; font-weight: 500; color: #c4b5fd;">🤖 {st.session_state.ai_explanation}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

        for i, (_, rec) in enumerate(st.session_state.ai_results.iterrows(), 1):
            render_song_card(f"AI_{i}", rec.to_dict(), show_score=False)