import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import numpy as np
import os
from datetime import timedelta

from config import MODEL, COPING_STRATEGIES, CRISIS_RESOURCES
from database import init_db, insert_entry, load_entries
from ai_engine import generate_reflection
from emotion_analysis import analyze_emotion, get_emotion_category, get_emotion_severity
from utils import (
    crisis_detect, get_similar_entries, get_emotion_patterns, 
    get_sentiment_trends, get_emotion_triggers, get_low_sentiment_context
)

import google.generativeai as genai

# ============================
# PAGE CONFIG
# ============================
st.set_page_config(
    page_title="ReflectAI | Empathy Journal",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

EMOJI_MAP = {"happy": "😊", "sad": "😢", "angry": "😠", "neutral": "😐", "anxious": "😰", "excited": "🤩", "surprised": "😲", "joyful": "😄", "content": "😌", "lonely": "🥺", "ashamed": "😔", "grieving": "💔", "overwhelmed": "😫", "hopeful": "🌟", "frustrated": "😤", "confused": "😕", "unmotivated": "😒", "peaceful": "🧘", "stressed": "😟"}

# ============================
# CUSTOM CSS
# ============================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #121212;
    color: #E5E7EB;
}

.main-title {font-size: 2.8rem; font-weight: 800; color: #7C3AED; text-align: center; margin-bottom: 0.3rem;}
.sub-title {text-align: center; color: #B0B0C0; font-size: 1.1rem; margin-bottom: 2rem;}

.stContainer {
    border: 1px solid #2D2D40;
    border-radius: 0.75rem;
    background-color: #1E1E2F;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.25);
}

.stButton button {
    background: linear-gradient(90deg, #8B5CF6, #7C3AED);
    color: white;
    font-weight: 600;
    border-radius: 0.5rem;
    border: none;
}

.reflection-output {
    font-size: 1.15rem;
    color: #E5E7EB;
    line-height: 1.6;
    font-style: italic;
    background-color: #272732;
    border-left: 4px solid #7C3AED;
    padding: 1rem;
    border-radius: 0.5rem;
}

.actionable {
    background-color: #1F5F3A;
    padding: 1rem;
    border-left: 4px solid #10B981;
    border-radius: 0.5rem;
    margin: 1rem 0;
}

.crisis-warning {
    background-color: #7C2D12;
    padding: 1.5rem;
    border-left: 4px solid #DC2626;
    border-radius: 0.5rem;
    margin: 1rem 0;
}

.coping-box {
    background-color: #1E3A5F;
    padding: 1rem;
    border-left: 4px solid #3B82F6;
    margin: 0.5rem 0;
    border-radius: 0.5rem;
}

@keyframes fadeIn { from {opacity:0; transform:translateY(8px);} to {opacity:1; transform:translateY(0);} }
.fadeIn { animation: fadeIn 0.6s ease forwards; }

@media only screen and (max-width: 768px) {
    .main .block-container {padding-left: 1rem; padding-right: 1rem;}
}
</style>
""", unsafe_allow_html=True)

# ============================
# INIT
# ============================
st.markdown("""
<div class="main-title fadeIn">🧠 ReflectAI</div>
<div class="sub-title fadeIn">Your AI-Powered Reflective Journaling Companion</div>
""", unsafe_allow_html=True)

genai.api_key = os.getenv("GEMINI_API_KEY")
init_db()

# ============================
# SIDEBAR DASHBOARD
# ============================
with st.sidebar:
    st.markdown("### 📊 Dashboard")
    df_sidebar = load_entries()
    
    if df_sidebar.empty:
        st.info("No entries yet. Start journaling to see insights!")
    else:
        # Convert timestamp to datetime
        df_sidebar["timestamp"] = pd.to_datetime(df_sidebar["timestamp"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📝 Total Entries", len(df_sidebar))
            st.metric("🙂 Avg Sentiment", round(df_sidebar["sentiment"].mean(), 2))
        with col2:
            most_common_emotion = df_sidebar["emotion"].mode()[0] if not df_sidebar["emotion"].mode().empty else "N/A"
            st.metric("💖 Most Emotion", most_common_emotion)
            
            # Sentiment distribution
            positive = len(df_sidebar[df_sidebar["sentiment"] > 0.3])
            negative = len(df_sidebar[df_sidebar["sentiment"] < -0.3])
            st.metric("📈 Positive Days", positive)

        # Last entry preview
        st.markdown("---")
        last_entry = df_sidebar.iloc[0]
        last_emotion = last_entry["emotion"]
        emoji = EMOJI_MAP.get(last_emotion.lower(), '')
        st.markdown(f"**Last Entry** ({last_emotion}) {emoji}")
        st.write(f"> {last_entry['entry'][:150]}...")
        
        # Filter by emotion
        st.markdown("---")
        st.markdown("### 🔎 Filter Entries")
        selected_emotion = st.selectbox("By Emotion:", options=["All"] + df_sidebar["emotion"].unique().tolist())
        
        if selected_emotion != "All":
            filtered_df = df_sidebar[df_sidebar["emotion"] == selected_emotion]
        else:
            filtered_df = df_sidebar
        
        st.metric(f"Entries ({selected_emotion})", len(filtered_df))

# ============================
# MAIN TABS
# ============================
tabs = st.tabs(["📝 Journal", "🔍 Search & Filter", "📊 Analytics", "💡 Insights", "ℹ️ About"])

# ============================
# TAB 1: JOURNAL
# ============================
with tabs[0]:
    st.header("✍️ Write Your Journal Entry")
    entry = st.text_area(
        "What's on your mind today?",
        height=180,
        placeholder="Write freely — ReflectAI listens without judgment..."
    )

    if st.button("✨ Generate Reflection", use_container_width=True):
        if not entry.strip():
            st.warning("Please write something first.")
        else:
            sentiment, emotion = analyze_emotion(entry)
            crisis_level = crisis_detect(entry)
            df_prev = load_entries()
            
            if crisis_level:
                st.markdown(f"""
                <div class='crisis-warning'>
                <h3>🚨 We Detected Distress Indicators</h3>
                <p>Your safety matters. Please reach out to a mental health professional.</p>
                <ul>
                <li><strong>Global:</strong> <a href='{CRISIS_RESOURCES["global"]}' target='_blank'>findahelpline.com</a></li>
                <li><strong>US:</strong> Call or text <a href='{CRISIS_RESOURCES["us_crisis_line"]}' target='_blank'>988</a></li>
                <li><strong>International:</strong> <a href='{CRISIS_RESOURCES["international"]}' target='_blank'>befrienders.org</a></li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
                
                insert_entry({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "entry": entry,
                    "reflection": f"Crisis indicator detected: {crisis_level}",
                    "summary": "Safety resources provided",
                    "followups": [],
                    "tone": "alert",
                    "safety": crisis_level,
                    "sentiment": sentiment,
                    "emotion": emotion
                })
            else:
                with st.spinner("🧠 Thinking deeply about your feelings..."):
                    res = generate_reflection(entry, emotion, sentiment)
                    
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        # Main reflection
                        emoji = EMOJI_MAP.get(emotion.lower(), "")
                        st.markdown(f"### 💬 {emoji} AI Reflection")
                        st.markdown(f"<div class='reflection-output fadeIn'>\"{res['reflection']}\"</div>", unsafe_allow_html=True)
                        
                        # Sentiment & emotion info
                        severity = get_emotion_severity(sentiment)
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Sentiment", f
