import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import numpy as np
import os

from config import MODEL
from database import init_db, insert_entry, load_entries
from ai_engine import generate_reflection
from emotion_analysis import analyze_emotion
from utils import crisis_detect, get_similar_entries

import google.generativeai as genai

# ============================
# GLOBAL EMOJI MAP
# ============================
EMOJI_MAP = {"happy": "😊", "sad": "😢", "angry": "😠", "neutral": "😐", "anxious": "😰", "excited": "🤩", "surprised": "😲"}

# ============================
# STREAMLIT CONFIG
# ============================
st.set_page_config(
    page_title="ReflectAI | Empathy Journal",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# ============================
# CSS & THEME
# ============================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #121212;
    color: #E5E7EB;
}

/* Header titles */
.main-title {font-size: 2.8rem; font-weight: 800; color: #7C3AED; text-align: center; margin-bottom: 0.3rem;}
.sub-title {text-align: center; color: #B0B0C0; font-size: 1.1rem; margin-bottom: 2rem;}

/* Card containers */
.stContainer {
    border: 1px solid #2D2D40;
    border-radius: 0.75rem;
    background-color: #1E1E2F;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.25);
    transition: all 0.3s ease;
}
.stContainer:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
}

/* Buttons */
.stButton button {
    background: linear-gradient(90deg, #8B5CF6, #7C3AED);
    color: white;
    font-weight: 600;
    border-radius: 0.5rem;
    transition: all 0.3s ease;
    border: none;
}
.stButton button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 15px rgba(140, 92, 246, 0.4);
}

/* Reflection & follow-up */
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
.follow-up {
    background-color: #252536;
    padding: 1rem;
    border-left: 3px solid #5B21B6;
    margin-top: 0.5rem;
    border-radius: 0.5rem;
}

/* Fade-in animations */
@keyframes fadeIn { from {opacity:0; transform:translateY(8px);} to {opacity:1; transform:translateY(0);} }
.fadeIn { animation: fadeIn 0.6s ease forwards; }

/* Responsive design */
@media only screen and (max-width: 768px) {
    .main .block-container {padding-left: 1rem; padding-right: 1rem;}
}
</style>
""", unsafe_allow_html=True)

# ============================
# HEADER
# ============================
st.markdown("""
<div class="main-title fadeIn">🧠 ReflectAI</div>
<div class="sub-title fadeIn">Your AI-Powered Reflective Journaling Companion</div>
""", unsafe_allow_html=True)

init_db()

# ============================
# SIDEBAR DASHBOARD
# ============================
with st.sidebar:
    st.markdown("### 📊 Dashboard")
    df_sidebar = load_entries()
    if df_sidebar.empty:
        st.info("No entries yet. Start journaling to see stats!")
    else:
        total_entries = len(df_sidebar)
        avg_sentiment = round(df_sidebar["sentiment"].mean(), 2)
        most_common_emotion = df_sidebar["emotion"].mode()[0] if not df_sidebar["emotion"].mode().empty else "N/A"
        last_reflection = df_sidebar.tail(1).iloc[0]["reflection"] if not df_sidebar.empty else "—"
        last_emotion = df_sidebar.tail(1).iloc[0]["emotion"]

        st.metric("📝 Total Entries", total_entries)
        st.metric("🙂 Average Sentiment", avg_sentiment)
        st.metric("💖 Most Common Emotion", most_common_emotion)

        # Display last reflection with emoji
        emoji = EMOJI_MAP.get(last_emotion.lower(), '')
        st.markdown(f"**Last Reflection ({last_emotion})** {emoji}")
        st.write(f"> {last_reflection}")

        # Filter past entries by emotion
        st.markdown("---")
        st.markdown("### 🔎 Filter by Emotion")
        selected_emotion = st.selectbox("Choose emotion", options=["All"] + df_sidebar["emotion"].unique().tolist())
        if selected_emotion != "All":
            filtered_df = df_sidebar[df_sidebar["emotion"] == selected_emotion]
        else:
            filtered_df = df_sidebar
        st.dataframe(filtered_df.tail(5)[["timestamp", "emotion", "tone", "safety"]])

# ============================
# TABS
# ============================
tabs = st.tabs(["📝 Journal", "📊 Analytics", "ℹ️ About"])

# ============================
# JOURNAL TAB
# ============================
with tabs[0]:
    st.header("Write Your Journal Entry")
    entry = st.text_area(
        "What's on your mind today?",
        height=180,
        placeholder="Write freely — ReflectAI listens without judgment..."
    )

    if st.button("✨ Generate Empathetic Reflection"):
        if not entry.strip():
            st.warning("Please write something first.")
        else:
            sentiment, emotion = analyze_emotion(entry)
            is_crisis = crisis_detect(entry)
            df_prev = load_entries()
            context = "\n".join(df_prev.tail(3)["entry"].tolist()) if not df_prev.empty else ""

            if is_crisis:
                st.error("🚨 Crisis detected — please contact a professional immediately.")
                st.write("[Find support resources →](https://findahelpline.com)")
                insert_entry({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "entry": entry,
                    "reflection": "Crisis detected.",
                    "summary": "Safety notice issued.",
                    "followups": [],
                    "tone": "alert",
                    "safety": "crisis",
                    "sentiment": sentiment,
                    "emotion": emotion
                })
            else:
                with st.spinner("🧠 Thinking empathetically..."):
                    res = generate_reflection(entry)
                    if "error" in res:
                        st.error(res["error"])
                    elif "raw_response" in res and "reflection" not in res:
                        st.warning("Model returned unstructured response. Check raw output below.")
                        with st.expander("Raw Model Output"):
                            st.code(res["raw_response"])
                    else:
                        # Reflection
                        emoji = EMOJI_MAP.get(emotion.lower(), "")
                        st.markdown(f"### 💬 {emoji} AI Reflection")
                        st.markdown(f"<div class='reflection-output fadeIn'>\"{res['reflection']}\"</div>", unsafe_allow_html=True)
                        st.info(f"**Summary:** {res['summary']} | **Tone:** {res['tone']} | **Emotion:** {emotion}")

                        # Follow-ups
                        st.markdown("### 🪞 Follow-up Prompts")
                        for fup in res["followups"]:
                            st.markdown(f"<div class='follow-up fadeIn'><strong>{fup['question']}</strong></div>", unsafe_allow_html=True)

                        # Save to DB
                        if "reflection" in res:
                            insert_entry({
                                "timestamp": datetime.datetime.now().isoformat(),
                                "entry": entry,
                                "reflection": res["reflection"],
                                "summary": res["summary"],
                                "followups": res["followups"],
                                "tone": res["tone"],
                                "safety": res["safety_flag"],
                                "sentiment": sentiment,
                                "emotion": emotion
                            })

                st.markdown("---")
                st.markdown("### 🧭 Similar Past Reflections")
                similar = get_similar_entries(entry, df_prev)
                if isinstance(similar, list) and not similar:
                    st.caption("No similar reflections found.")
                else:
                    for sim in (similar if isinstance(similar, list) else similar.to_dict("records")):
                        st.markdown(f"""
                        <div class='stContainer fadeIn'>
                            <strong>🕓 {sim['timestamp']}</strong> — <em>({sim['emotion']})</em><br>
                            <small>{sim['entry'][:200]}...</small>
                        </div>
                        """, unsafe_allow_html=True)

# ============================
# ANALYTICS TAB
# ============================
with tabs[1]:
    st.header("📊 Your Emotional Journey")
    df = load_entries()
    if df.empty:
        st.info("No entries yet — start journaling to see your emotional trends!")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)

        # Create two columns for side-by-side charts
        col1, col2 = st.columns([2, 1])

        # --- Sentiment Over Time ---
        with col1:
            st.subheader("Sentiment Over Time")
            fig, ax = plt.subplots(figsize=(7,4))
            x = df.index
            y = df["sentiment"]

            # Color gradient based on sentiment
            for i in range(len(x)-1):
                color = "#22C55E" if y[i]>=0.5 else "#F59E0B" if y[i]>0 else "#EF4444"
                ax.plot(x[i:i+2], y[i:i+2], color=color, linewidth=2)
            ax.set_ylabel("Sentiment")
            ax.set_xlabel("Date")
            ax.set_title("")
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            ax.grid(alpha=0.3)
            st.pyplot(fig)

        # --- Emotion Distribution ---
        with col2:
            st.subheader("Emotion Distribution")
            st.bar_chart(df["emotion"].value_counts())

        # Recent Entries (full width below charts)
        st.subheader("🗂 Recent Entries")
        st.dataframe(df.tail(5).reset_index()[["timestamp", "emotion", "tone", "safety"]])


# ============================
# ABOUT TAB
# ============================
with tabs[2]:
    st.markdown("""
### ℹ️ About ReflectAI
ReflectAI is a **Generative AI-powered journaling assistant** designed for emotional awareness and self-reflection.

**Features**
- 🧠 Empathetic reflection generation  
- 💬 Emotion & sentiment analysis  
- 🔁 Memory-based similar reflections  
- 📊 Emotional trend analytics  

**Ethical Note**
- This is **not a replacement for therapy**.  
- Crisis phrases are detected and flagged for your safety.  
- Data is stored **locally** to protect privacy.  
""")

