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

EMOJI_MAP = {
    "happy": "😊", "sad": "😢", "angry": "😠", "neutral": "😐", "anxious": "😰", 
    "excited": "🤩", "surprised": "😲", "joyful": "😄", "content": "😌", "lonely": "🥺", 
    "ashamed": "😔", "grieving": "💔", "overwhelmed": "😫", "hopeful": "🌟", 
    "frustrated": "😤", "confused": "😕", "unmotivated": "😒", "peaceful": "🧘", "stressed": "😟"
}

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

.positive-box {
    background-color: #1F5F3A;
    padding: 1rem;
    border-left: 4px solid #10B981;
    margin: 0.5rem 0;
    border-radius: 0.5rem;
}

@keyframes fadeIn { from {opacity:0; transform:translateY(8px);} to {opacity:1; transform:translateY(0);} }
.fadeIn { animation: fadeIn 0.6s ease forwards; }
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
        df_sidebar["timestamp"] = pd.to_datetime(df_sidebar["timestamp"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📝 Entries", len(df_sidebar))
            st.metric("🙂 Avg Sentiment", round(df_sidebar["sentiment"].mean(), 2))
        with col2:
            most_common_emotion = df_sidebar["emotion"].mode()[0] if not df_sidebar["emotion"].mode().empty else "N/A"
            st.metric("💖 Top Emotion", most_common_emotion)
            positive = len(df_sidebar[df_sidebar["sentiment"] > 0.3])
            st.metric("📈 Positive", positive)

        st.markdown("---")
        last_entry = df_sidebar.iloc[0]
        last_emotion = last_entry["emotion"]
        emoji = EMOJI_MAP.get(last_emotion.lower(), '')
        st.markdown(f"**Last Entry** {emoji}")
        st.caption(last_entry['entry'][:100] + "...")
        
        st.markdown("---")
        st.markdown("### 🔎 Quick Filter")
        selected_emotion = st.selectbox("By Emotion:", options=["All"] + sorted(df_sidebar["emotion"].unique().tolist()))
        
        if selected_emotion != "All":
            filtered_df = df_sidebar[df_sidebar["emotion"] == selected_emotion]
        else:
            filtered_df = df_sidebar
        
        st.metric(f"Entries", len(filtered_df))

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

    if st.button("✨ Generate Reflection", width="stretch"):
        if not entry.strip():
            st.warning("Please write something first.")
        else:
            sentiment, emotion = analyze_emotion(entry)
            crisis_level = crisis_detect(entry)
            df_prev = load_entries()
            
            if crisis_level:
                st.markdown(f"""
                <div class='crisis-warning'>
                <h3>🚨 Crisis Support Available</h3>
                <p>Your safety is important. Please reach out for professional support:</p>
                <ul>
                <li><strong>Global:</strong> <a href='{CRISIS_RESOURCES["global"]}' target='_blank'>findahelpline.com</a></li>
                <li><strong>US Crisis Line:</strong> Call/text <strong>988</strong></li>
                <li><strong>International:</strong> <a href='{CRISIS_RESOURCES["international"]}' target='_blank'>befrienders.org</a></li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
                
                insert_entry({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "entry": entry,
                    "reflection": f"Crisis support flagged",
                    "summary": "Safety resources provided",
                    "followups": [],
                    "tone": "alert",
                    "safety": crisis_level,
                    "sentiment": sentiment,
                    "emotion": emotion
                })
            else:
                with st.spinner("🧠 Generating personalized reflection..."):
                    res = generate_reflection(entry, emotion, sentiment)
                    
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        emoji = EMOJI_MAP.get(emotion.lower(), "")
                        st.markdown(f"### 💬 {emoji} Reflection")
                        st.markdown(f"<div class='reflection-output fadeIn'>\"{res['reflection']}\"</div>", unsafe_allow_html=True)
                        
                        # Metrics
                        severity = get_emotion_severity(sentiment)
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Emotion", emotion)
                        with col2:
                            st.metric("Sentiment", f"{sentiment:.2f}", delta=None)
                        with col3:
                            st.metric("Severity", severity)
                        
                        # Summary & Actionable Insight
                        st.info(f"**Summary:** {res['summary']}")
                        if res.get('actionable_insight'):
                            st.markdown(f"<div class='actionable'><strong>💡 Try This:</strong> {res['actionable_insight']}</div>", unsafe_allow_html=True)
                        
                        # Coping suggestions
                        if res.get('coping_suggestion') and sentiment < -0.3:
                            st.markdown(f"<div class='coping-box'><strong>🌿 Grounding Technique:</strong> {res['coping_suggestion']}</div>", unsafe_allow_html=True)
                        
                        # Follow-up questions
                        st.markdown("### 🪞 Reflection Questions")
                        for i, fup in enumerate(res.get("followups", []), 1):
                            with st.expander(f"Q{i}: {fup['question']}", expanded=False):
                                st.write(fup.get('follow_up', ''))
                        
                        # Save entry
                        if "reflection" in res:
                            insert_entry({
                                "timestamp": datetime.datetime.now().isoformat(),
                                "entry": entry,
                                "reflection": res["reflection"],
                                "summary": res.get("summary", ""),
                                "followups": res.get("followups", []),
                                "tone": res.get("tone", ""),
                                "safety": res.get("safety_flag", False),
                                "sentiment": sentiment,
                                "emotion": emotion
                            })
                            st.success("✅ Entry saved!")
                
                # Similar entries
                st.markdown("---")
                st.markdown("### 🧭 Similar Past Reflections")
                df_prev = load_entries()
                similar = get_similar_entries(entry, df_prev, top_n=3)
                
                if isinstance(similar, list) and len(similar) == 0:
                    st.caption("No similar entries yet.")
                else:
                    for idx, sim in enumerate(similar.to_dict("records") if hasattr(similar, 'to_dict') else similar):
                        st.markdown(f"""
                        <div class='stContainer'>
                            <strong>📅 {sim['timestamp']}</strong> — <em>({sim['emotion']}, sentiment: {sim.get('sentiment', 'N/A'):.2f})</em><br>
                            <small>{sim['entry'][:150]}...</small>
                        </div>
                        """, unsafe_allow_html=True)

# ============================
# TAB 2: SEARCH & FILTER
# ============================
with tabs[1]:
    st.header("🔍 Search & Filter Your Journal")
    
    df = load_entries()
    if df.empty:
        st.info("No entries yet. Start journaling!")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_query = st.text_input("🔎 Search entries", placeholder="keyword, phrase...")
        
        with col2:
            emotion_filter = st.multiselect("Filter by emotion", options=df["emotion"].unique())
        
        with col3:
            sentiment_range = st.slider("Sentiment range", -1.0, 1.0, (-1.0, 1.0))
        
        # Apply filters
        filtered = df.copy()
        
        if search_query:
            filtered = filtered[filtered["entry"].str.lower().str.contains(search_query.lower(), na=False)]
        
        if emotion_filter:
            filtered = filtered[filtered["emotion"].isin(emotion_filter)]
        
        filtered = filtered[(filtered["sentiment"] >= sentiment_range[0]) & (filtered["sentiment"] <= sentiment_range[1])]
        
        # Results
        st.markdown(f"### 📋 Results ({len(filtered)} entries)")
        
        if len(filtered) == 0:
            st.warning("No entries match your filters.")
        else:
            # Sort options
            sort_by = st.radio("Sort by:", ["Newest First", "Oldest First", "Most Positive", "Most Negative"], horizontal=True)
            
            if sort_by == "Newest First":
                filtered = filtered.sort_values("timestamp", ascending=False)
            elif sort_by == "Oldest First":
                filtered = filtered.sort_values("timestamp", ascending=True)
            elif sort_by == "Most Positive":
                filtered = filtered.sort_values("sentiment", ascending=False)
            else:
                filtered = filtered.sort_values("sentiment", ascending=True)
            
            # Display results
            for idx, row in filtered.iterrows():
                emotion_emoji = EMOJI_MAP.get(row["emotion"].lower(), "")
                st.markdown(f"""
                <div class='stContainer'>
                    <strong>📅 {row['timestamp'].strftime('%b %d, %Y - %I:%M %p')}</strong> {emotion_emoji}<br>
                    <strong>Emotion:</strong> {row['emotion']} | <strong>Sentiment:</strong> {row['sentiment']:.2f}<br>
                    <br>
                    <strong>Entry:</strong><br>
                    {row['entry']}<br>
                    <br>
                    <strong>Reflection:</strong><br>
                    <em>{row['reflection']}</em>
                </div>
                """, unsafe_allow_html=True)

# ============================
# TAB 3: ANALYTICS
# ============================
with tabs[2]:
    st.header("📊 Your Emotional Journey")
    
    df = load_entries()
    if df.empty:
        st.info("No entries yet — start journaling to see trends!")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Entries", len(df))
        with col2:
            st.metric("Avg Sentiment", f"{df['sentiment'].mean():.2f}")
        with col3:
            positive_pct = (len(df[df["sentiment"] > 0.3]) / len(df) * 100)
            st.metric("Positive Days", f"{positive_pct:.0f}%")
        with col4:
            days_span = (df["timestamp"].max() - df["timestamp"].min()).days
            st.metric("Span", f"{days_span} days")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Sentiment Over Time")
            fig, ax = plt.subplots(figsize=(10, 4), facecolor='#121212')
            ax.set_facecolor('#1E1E2F')
            
            x = df["timestamp"]
            y = df["sentiment"].values
            
            for i in range(len(x) - 1):
                color = "#22C55E" if y[i] >= 0.5 else "#F59E0B" if y[i] > 0 else "#EF4444"
                ax.plot(x.iloc[i:i+2], y[i:i+2], color=color, linewidth=3, marker='o')
            
            ax.set_ylabel("Sentiment Score", color="#E5E7EB")
            ax.set_xlabel("Date", color="#E5E7EB")
            ax.tick_params(colors="#E5E7EB")
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            ax.grid(alpha=0.2, color="#E5E7EB")
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            st.subheader("Emotion Distribution")
            emotion_counts = df["emotion"].value_counts()
            fig, ax = plt.subplots(figsize=(6, 4), facecolor='#121212')
            ax.set_facecolor('#1E1E2F')
            colors = ["#7C3AED" if i % 2 == 0 else "#8B5CF6" for i in range(len(emotion_counts))]
            ax.barh(emotion_counts.index, emotion_counts.values, color=colors)
            ax.set_xlabel("Count", color="#E5E7EB")
            ax.tick_params(colors="#E5E7EB")
            plt.tight_layout()
            st.pyplot(fig)
        
        # Detailed table
        st.subheader("📋 Recent Entries")
        display_df = df.tail(10).sort_values("timestamp", ascending=False)[["timestamp", "emotion", "sentiment", "summary"]].copy()
        display_df["timestamp"] = display_df["timestamp"].dt.strftime("%b %d, %Y")
        display_df["sentiment"] = display_df["sentiment"].round(2)
        st.dataframe(display_df, use_container_width=True)

# ============================
# TAB 4: INSIGHTS
# ============================
with tabs[3]:
    st.header("💡 Emotional Insights & Patterns")
    
    df = load_entries()
    if df.empty:
        st.info("Journal more entries to unlock pattern insights!")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Pattern analysis
        patterns = get_emotion_patterns(df)
        
        st.subheader("🎯 Emotion Frequency")
        if patterns.get("emotion_frequency"):
            col1, col2 = st.columns([2, 1])
            with col1:
                fig, ax = plt.subplots(figsize=(8, 4), facecolor='#121212')
                ax.set_facecolor('#1E1E2F')
                emotions = list(patterns["emotion_frequency"].keys())
                counts = list(patterns["emotion_frequency"].values())
                ax.bar(range(len(emotions)), counts, color="#7C3AED")
                ax.set_xticks(range(len(emotions)))
                ax.set_xticklabels(emotions, rotation=45, ha='right', color="#E5E7EB")
                ax.set_ylabel("Frequency", color="#E5E7EB")
                ax.tick_params(colors="#E5E7EB")
                plt.tight_layout()
                st.pyplot(fig)
            
            with col2:
                for emotion, count in patterns["emotion_frequency"].items():
                    emoji = EMOJI_MAP.get(emotion.lower(), "")
                    st.write(f"{emoji} {emotion}: **{count}**")
        
        st.markdown("---")
        
        st.subheader("📈 Sentiment Statistics")
        stats = patterns.get("sentiment_stats", {})
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Average", f"{stats.get('average', 0):.2f}")
        with col2:
            st.metric("Highest", f"{stats.get('highest', 0):.2f}")
        with col3:
            st.metric("Lowest", f"{stats.get('lowest', 0):.2f}")
        with col4:
            st.metric("Volatility", f"{stats.get('std_dev', 0):.2f}")
        
        st.markdown("---")
        
        st.subheader("🔄 Common Emotion Transitions")
        transitions = get_emotion_triggers(df)
        if transitions:
            for transition, count in transitions.items():
                st.write(f"**{transition}** — *happened {count} times*")
        else:
            st.info("Not enough entries to detect patterns yet.")
        
        st.markdown("---")
        
        st.subheader("🔍 What Comes Before Low Mood Days?")
        low_context = get_low_sentiment_context(df)
        if low_context:
            st.write("**Common themes in difficult days:**")
            for word, freq in list(low_context.items())[:10]:
                st.write(f"• {word} ({freq}x)")
        else:
            st.info("No low-sentiment entries yet.")

# ============================
# TAB 5: ABOUT
# ============================
with tabs[4]:
    st.markdown("""
    ### ℹ️ About ReflectAI
    
    ReflectAI is an AI-powered journaling companion designed to help you understand your emotional patterns and practice self-reflection.
    
    **Key Features:**
    - 🧠 Empathetic, personalized reflections based on your emotional state
    - 💬 Context-aware follow-up questions
    - 📊 Detailed emotional analytics and pattern recognition
    - 🔍 Full-text search across your journal
    - 🌿 Grounding techniques and coping suggestions
    - 🚨 Crisis detection with support resources
    
    **How It Works:**
    1. Write your thoughts freely
    2. ReflectAI analyzes your emotion and sentiment
    3. You receive an empathetic reflection with actionable insights
    4. Your entry is saved and analyzed for patterns over time
    
    **Important:**
    - This is **not a substitute for professional therapy**
    - If you're in crisis, please contact a mental health professional immediately
    - Your data is stored locally (or encrypted on Streamlit Cloud)
    
    **Technologies:**
    - Google Gemini API for AI responses
    - Transformers for emotion detection
    - SQLite for local data storage
    - Streamlit for the web interface
    
    **Author:** Fadhil Muhammed N C (Capstone Project, MSc Data Analytics 2025)
    
    ---
    
    💡 **Tips for Better Insights:**
    - Journal regularly (3-5 times per week is ideal)
    - Be honest and specific about your feelings
    - Track patterns by searching past entries
    - Review your analytics weekly to spot trends
    - Use the insights to inform your self-care
    """)
