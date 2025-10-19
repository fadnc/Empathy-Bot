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
    page_title="ReflectAI",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# Minimal emoji map - only professional use
EMOJI_MAP = {
    "anxious": "⚠️", "overwhelmed": "⚙️", "lonely": "👤", "ashamed": "◆",
    "grieving": "◆", "joyful": "●", "content": "●", "frustrated": "◆",
    "hopeful": "▲", "peaceful": "●", "angry": "◆", "stressed": "⚠️"
}

# ============================
# PROFESSIONAL CSS STYLING
# ============================
st.markdown("""
<style>
* {
    margin: 0;
    padding: 0;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background-color: #FAFBFC;
    color: #1F2937;
}

/* Typography */
h1 { font-size: 2rem; font-weight: 600; color: #111827; margin-bottom: 0.5rem; }
h2 { font-size: 1.5rem; font-weight: 600; color: #111827; margin-bottom: 1rem; }
h3 { font-size: 1.1rem; font-weight: 600; color: #1F2937; margin-bottom: 0.75rem; }

/* Header */
.header-container {
    padding: 2rem 0;
    border-bottom: 1px solid #E5E7EB;
    margin-bottom: 2rem;
}

.header-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 0.25rem;
}

.header-subtitle {
    font-size: 0.95rem;
    color: #6B7280;
    font-weight: 400;
}

/* Sidebar */
.css-1d58g30 {
    background-color: #F9FAFB;
    border-right: 1px solid #E5E7EB;
}

/* Cards & Containers */
.metric-card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.metric-card:hover {
    border-color: #D1D5DB;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    transition: all 0.2s ease;
}

.metric-label {
    font-size: 0.85rem;
    color: #6B7280;
    font-weight: 500;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #111827;
}

/* Buttons */
.stButton button {
    background-color: #3B82F6;
    color: white;
    font-weight: 600;
    border-radius: 6px;
    border: none;
    padding: 0.75rem 1.5rem;
    transition: all 0.2s ease;
    height: 44px;
}

.stButton button:hover {
    background-color: #2563EB;
    box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2);
}

.stButton button:active {
    background-color: #1D4ED8;
    transform: scale(0.98);
}

/* Input Fields */
.stTextArea textarea {
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    background-color: white;
    color: #1F2937;
    padding: 1rem;
    font-family: 'Inter', sans-serif;
}

.stTextArea textarea:focus {
    border-color: #3B82F6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 2rem;
    border-bottom: 1px solid #E5E7EB;
}

.stTabs [data-baseweb="tab"] {
    color: #6B7280;
    font-weight: 500;
    padding: 0.75rem 0;
    border-bottom: 2px solid transparent;
}

.stTabs [aria-selected="true"] {
    color: #3B82F6;
    border-bottom-color: #3B82F6;
}

/* Reflection Output */
.reflection-box {
    background: white;
    border-left: 3px solid #3B82F6;
    border-radius: 6px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    line-height: 1.6;
    color: #1F2937;
}

.reflection-box strong {
    color: #111827;
    font-weight: 600;
}

/* Actionable Insight */
.actionable-box {
    background: #ECFDF5;
    border-left: 3px solid #10B981;
    border-radius: 6px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.actionable-box strong {
    color: #059669;
}

/* Crisis Warning */
.crisis-box {
    background: #FEF2F2;
    border-left: 3px solid #DC2626;
    border-radius: 6px;
    padding: 1.5rem;
    margin: 1.5rem 0;
}

.crisis-box h3 {
    color: #DC2626;
    margin-bottom: 0.75rem;
}

.crisis-box ul {
    margin-left: 1.5rem;
    color: #1F2937;
}

.crisis-box li {
    margin-bottom: 0.5rem;
    line-height: 1.5;
}

.crisis-box a {
    color: #DC2626;
    text-decoration: underline;
}

/* Coping Suggestion */
.coping-box {
    background: #EFF6FF;
    border-left: 3px solid #0284C7;
    border-radius: 6px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.coping-box strong {
    color: #0284C7;
}

/* Info Box */
.info-box {
    background: #F3F4F6;
    border-radius: 6px;
    padding: 1.5rem;
    margin: 1rem 0;
    color: #4B5563;
}

/* Expander */
.streamlit-expanderHeader {
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 1rem;
    font-weight: 500;
    color: #1F2937;
}

.streamlit-expanderHeader:hover {
    background: #F3F4F6;
}

/* Charts */
.stPlotlyChart, .stPyplotChart {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid #E5E7EB;
}

/* Data Table */
.dataframe {
    border-collapse: collapse;
    width: 100%;
}

.dataframe th {
    background-color: #F9FAFB;
    border: 1px solid #E5E7EB;
    padding: 1rem;
    text-align: left;
    font-weight: 600;
    color: #111827;
}

.dataframe td {
    border: 1px solid #E5E7EB;
    padding: 1rem;
    color: #1F2937;
}

/* Metrics */
.stMetric {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 1rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

/* Selectbox & Multiselect */
.stSelectbox, .stMultiSelect {
    color: #1F2937;
}

.stSelectbox [data-baseweb="select"] {
    border-radius: 6px;
}

/* Spacing & Utilities */
.spacer { margin: 2rem 0; }

/* Responsive */
@media (max-width: 768px) {
    .header-title { font-size: 1.5rem; }
    h2 { font-size: 1.2rem; }
}
</style>
""", unsafe_allow_html=True)

# ============================
# INIT
# ============================
st.markdown("""
<div class="header-container">
    <div class="header-title">ReflectAI</div>
    <div class="header-subtitle">AI-Powered Reflective Journaling</div>
</div>
""", unsafe_allow_html=True)

genai.api_key = os.getenv("GEMINI_API_KEY")
init_db()

# ============================
# SIDEBAR
# ============================
with st.sidebar:
    st.markdown("### Dashboard")
    df_sidebar = load_entries()
    
    if df_sidebar.empty:
        st.info("Start journaling to see your insights")
    else:
        df_sidebar["timestamp"] = pd.to_datetime(df_sidebar["timestamp"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Entries", len(df_sidebar))
            st.metric("Avg Sentiment", f"{df_sidebar['sentiment'].mean():.2f}")
        with col2:
            positive = len(df_sidebar[df_sidebar["sentiment"] > 0.3])
            st.metric("Positive Days", positive)
            most_emotion = df_sidebar["emotion"].mode()[0] if not df_sidebar["emotion"].mode().empty else "—"
            st.metric("Top Emotion", most_emotion)

        st.divider()
        
        st.markdown("**Last Entry**")
        last_entry = df_sidebar.iloc[0]
        st.caption(last_entry['entry'][:120] + "...")
        
        st.divider()
        st.markdown("**Filter**")
        selected_emotion = st.selectbox("By emotion:", options=["All"] + sorted(df_sidebar["emotion"].unique().tolist()), key="sidebar_filter")
        
        if selected_emotion != "All":
            filtered = df_sidebar[df_sidebar["emotion"] == selected_emotion]
        else:
            filtered = df_sidebar
        
        st.caption(f"{len(filtered)} entries")

# ============================
# MAIN TABS
# ============================
tabs = st.tabs(["Journal", "Search", "Analytics", "Insights", "About"])

# ============================
# TAB 1: JOURNAL
# ============================
with tabs[0]:
    st.markdown("## Write an Entry")
    
    entry = st.text_area(
        "What's on your mind?",
        height=180,
        placeholder="Write freely, without judgment...",
        label_visibility="collapsed"
    )

    if st.button("Generate Reflection", width="stretch"):
        if not entry.strip():
            st.warning("Please write something first")
        else:
            sentiment, emotion = analyze_emotion(entry)
            crisis_level = crisis_detect(entry)
            df_prev = load_entries()
            
            if crisis_level:
                st.markdown(f"""
                <div class="crisis-box">
                <h3>Support Available</h3>
                <p>Your wellbeing matters. Please reach out for professional support:</p>
                <ul>
                <li><strong>Global:</strong> <a href='{CRISIS_RESOURCES["global"]}' target='_blank'>findahelpline.com</a></li>
                <li><strong>US (24/7):</strong> Call or text <strong>988</strong></li>
                <li><strong>International:</strong> <a href='{CRISIS_RESOURCES["international"]}' target='_blank'>befrienders.org</a></li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
                
                insert_entry({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "entry": entry,
                    "reflection": "Support resources provided",
                    "summary": "Safety flagged",
                    "followups": [],
                    "tone": "alert",
                    "safety": crisis_level,
                    "sentiment": sentiment,
                    "emotion": emotion
                })
            else:
                with st.spinner("Analyzing your entry..."):
                    res = generate_reflection(entry, emotion, sentiment)
                    
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        # Reflection
                        st.markdown(f"""
                        <div class="reflection-box">
                        <strong>Reflection</strong><br><br>
                        {res['reflection']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Emotion", emotion)
                        with col2:
                            st.metric("Sentiment", f"{sentiment:.2f}")
                        with col3:
                            severity = get_emotion_severity(sentiment)
                            st.metric("Intensity", severity.capitalize())
                        with col4:
                            st.metric("Summary", res.get("summary", "—")[:20])
                        
                        # Actionable insight
                        if res.get('actionable_insight'):
                            st.markdown(f"""
                            <div class="actionable-box">
                            <strong>Consider This</strong><br><br>
                            {res['actionable_insight']}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Coping suggestion
                        if res.get('coping_suggestion') and sentiment < -0.3:
                            st.markdown(f"""
                            <div class="coping-box">
                            <strong>Grounding Technique</strong><br><br>
                            {res['coping_suggestion']}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Follow-up questions
                        st.markdown("### Reflection Questions")
                        for i, fup in enumerate(res.get("followups", []), 1):
                            with st.expander(f"Q{i}: {fup['question']}", expanded=False):
                                st.write(fup.get('follow_up', ''))
                        
                        # Save
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
                            st.success("Entry saved")
                
                # Similar entries
                st.divider()
                st.markdown("### Similar Past Entries")
                df_prev = load_entries()
                similar = get_similar_entries(entry, df_prev, top_n=2)
                
                if isinstance(similar, list) and len(similar) == 0:
                    st.caption("No similar entries found")
                else:
                    for sim in (similar.to_dict("records") if hasattr(similar, 'to_dict') else similar):
                        st.markdown(f"""
                        <div class="metric-card">
                        <div style="color: #6B7280; font-size: 0.9rem; margin-bottom: 0.5rem;">
                        {sim['timestamp']} • {sim['emotion']} • Sentiment: {sim.get('sentiment', 0):.2f}
                        </div>
                        <div style="color: #1F2937; line-height: 1.5;">
                        {sim['entry'][:150]}...
                        </div>
                        </div>
                        """, unsafe_allow_html=True)

# ============================
# TAB 2: SEARCH & FILTER
# ============================
with tabs[1]:
    st.markdown("## Search Your Journal")
    
    df = load_entries()
    if df.empty:
        st.info("No entries yet")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search = st.text_input("Search entries", placeholder="keyword...")
        with col2:
            emotions = st.multiselect("Filter emotion", df["emotion"].unique())
        with col3:
            sent_range = st.slider("Sentiment", -1.0, 1.0, (-1.0, 1.0), label_visibility="collapsed")
        
        # Apply filters
        filtered = df.copy()
        if search:
            filtered = filtered[filtered["entry"].str.lower().str.contains(search.lower(), na=False)]
        if emotions:
            filtered = filtered[filtered["emotion"].isin(emotions)]
        filtered = filtered[(filtered["sentiment"] >= sent_range[0]) & (filtered["sentiment"] <= sent_range[1])]
        
        st.markdown(f"**{len(filtered)} entries**")
        
        if len(filtered) == 0:
            st.info("No matching entries")
        else:
            sort_by = st.radio("Sort:", ["Newest", "Oldest", "Most Positive", "Most Negative"], horizontal=True)
            
            if sort_by == "Newest":
                filtered = filtered.sort_values("timestamp", ascending=False)
            elif sort_by == "Oldest":
                filtered = filtered.sort_values("timestamp", ascending=True)
            elif sort_by == "Most Positive":
                filtered = filtered.sort_values("sentiment", ascending=False)
            else:
                filtered = filtered.sort_values("sentiment", ascending=True)
            
            for idx, row in filtered.iterrows():
                st.markdown(f"""
                <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <span style="font-weight: 600; color: #111827;">{row['timestamp'].strftime('%b %d, %Y')}</span>
                    <span style="color: #6B7280; font-size: 0.9rem;">{row['emotion']} • {row['sentiment']:.2f}</span>
                </div>
                <p style="color: #1F2937; line-height: 1.6; margin-bottom: 1rem;">{row['entry']}</p>
                <p style="color: #6B7280; font-style: italic; font-size: 0.95rem;">{row['reflection']}</p>
                </div>
                """, unsafe_allow_html=True)

# ============================
# TAB 3: ANALYTICS
# ============================
with tabs[2]:
    st.markdown("## Your Progress")
    
    df = load_entries()
    if df.empty:
        st.info("Start journaling to see analytics")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", len(df))
        with col2:
            st.metric("Avg Sentiment", f"{df['sentiment'].mean():.2f}")
        with col3:
            pct = int(len(df[df["sentiment"] > 0.3]) / len(df) * 100)
            st.metric("Positive %", f"{pct}%")
        with col4:
            days = (df["timestamp"].max() - df["timestamp"].min()).days
            st.metric("Days", days)
        
        st.divider()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Sentiment Trend")
            fig, ax = plt.subplots(figsize=(10, 4), facecolor='white')
            ax.set_facecolor('white')
            
            x = df["timestamp"]
            y = df["sentiment"].values
            
            colors = ["#10B981" if v >= 0.3 else "#F59E0B" if v > -0.3 else "#EF4444" for v in y]
            ax.plot(x, y, color="#3B82F6", linewidth=2, alpha=0.7)
            ax.scatter(x, y, c=colors, s=50, alpha=0.6)
            
            ax.set_ylabel("Sentiment", fontsize=10, color="#6B7280")
            ax.set_xlabel("Date", fontsize=10, color="#6B7280")
            ax.tick_params(colors="#6B7280")
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            ax.grid(alpha=0.1, color="#D1D5DB")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Emotions")
            emotion_counts = df["emotion"].value_counts()
            fig, ax = plt.subplots(figsize=(6, 4), facecolor='white')
            ax.set_facecolor('white')
            ax.barh(range(len(emotion_counts)), emotion_counts.values, color="#3B82F6", alpha=0.7)
            ax.set_yticks(range(len(emotion_counts)))
            ax.set_yticklabels(emotion_counts.index, fontsize=9)
            ax.set_xlabel("Count", fontsize=9, color="#6B7280")
            ax.tick_params(colors="#6B7280")
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
        
        st.markdown("### Recent Entries")
        display = df.tail(10).sort_values("timestamp", ascending=False)[["timestamp", "emotion", "sentiment", "summary"]].copy()
        display["timestamp"] = display["timestamp"].dt.strftime("%b %d")
        display["sentiment"] = display["sentiment"].round(2)
        display.columns = ["Date", "Emotion", "Sentiment", "Summary"]
        st.dataframe(display, use_container_width=True, hide_index=True)

# ============================
# TAB 4: INSIGHTS
# ============================
with tabs[3]:
    st.markdown("## Insights & Patterns")
    
    df = load_entries()
    if df.empty:
        st.info("Journal more to discover patterns")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        patterns = get_emotion_patterns(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Emotion Frequency")
            if patterns.get("emotion_frequency"):
                for emotion, count in list(patterns["emotion_frequency"].items())[:5]:
                    st.metric(emotion.capitalize(), count)
        
        with col2:
            st.markdown("### Sentiment Range")
            stats = patterns.get("sentiment_stats", {})
            st.metric("Average", f"{stats.get('average', 0):.2f}")
            st.metric("Range", f"{stats.get('lowest', 0):.2f} to {stats.get('highest', 0):.2f}")
        
        st.divider()
        
        st.markdown("### What Comes Before Low Days?")
        low_context = get_low_sentiment_context(df)
        if low_context:
            words_text = ", ".join([w for w, _ in list(low_context.items())[:8]])
            st.info(f"Common themes: {words_text}")
        else:
            st.caption("No pattern yet")
        
        st.divider()
        
        st.markdown("### Emotion Transitions")
        transitions = get_emotion_triggers(df)
        if transitions:
            for transition, count in list(transitions.items())[:5]:
                st.write(f"**{transition}** — {count} times")
        else:
            st.caption("Need more entries to detect patterns")

# ============================
# TAB 5: ABOUT
# ============================
with tabs[4]:
    st.markdown("""
    ## About ReflectAI
    
    ReflectAI is an AI-powered journaling tool designed to help you understand your emotional patterns and practice meaningful self-reflection.
    
    ### Features
    - Personalized emotional reflections powered by Google Gemini
    - Emotion and sentiment analysis
    - Journaling search and filtering
    - Emotional trend analytics
    - Pattern recognition across your entries
    - Crisis detection with support resources
    
    ### How It Works
    1. Write your thoughts and feelings
    2. ReflectAI analyzes your emotional state
    3. Receive personalized reflection and actionable insights
    4. Your entry is saved for future pattern analysis
    
    ### Important
    **This is not a substitute for professional mental health care.** If you're experiencing a crisis or suicidal thoughts, please contact a mental health professional immediately:
    - **Global:** findahelpline.com
    - **US:** Call or text 988
    - **International:** befrienders.org
    
    ### Technology
    - Google Gemini API for AI responses
    - Transformers for emotion detection
    - SQLite for local data storage
    - Streamlit for web interface
    
    ### Privacy
    Your data is stored locally on your device or securely on Streamlit Cloud servers. No personal data is sold or shared.
    
    ---
    
    **Author:** Fadhil Muhammed N C  
    **Capstone Project:** MSc Computer Science (Data Analytics) 2025
    """)
