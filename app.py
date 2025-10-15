import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os

from config import MODEL
from database import init_db, insert_entry, load_entries
from ai_engine import call_ollama, generate_reflection
from emotion_analysis import analyze_emotion
from utils import crisis_detect, get_similar_entries

import openai

# @st.cache_resource
# def get_generator():
#     return load_model()

# generator = get_generator()

# ============================
# STREAMLIT CONFIG
# ============================
st.set_page_config(page_title="Empathy Bot — Advanced", layout="wide")
st.title("🧠 Empathy Bot — AI Reflective Journaling ")
openai.api_key = os.getenv("OPENAI_API_KEY")

tabs = st.tabs(["📝 Journal", "📊 Analytics", "ℹ️ About"])
init_db()

# ============================
# JOURNAL TAB
# ============================
with tabs[0]:
    st.header("Write your journal entry")
    entry = st.text_area("Express your thoughts here:", height=200)

    if st.button("Reflect with AI"):
        if not entry.strip():
            st.warning("Please write something first.")
        else:
            sentiment, emotion = analyze_emotion(entry)
            is_crisis = crisis_detect(entry)
            df_prev = load_entries()
            context = "\n".join(df_prev.tail(3)["entry"].tolist()) if not df_prev.empty else ""

            if is_crisis:
                st.error("⚠️ Crisis detected. Please contact professional help immediately.")
                st.write("[Find support resources](https://findahelpline.com)")
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
                with st.spinner("Generating empathetic reflection..."):
                    #res = call_ollama(entry, context)
                    res = generate_reflection(entry)
                    if "error" in res:
                        st.error(res["error"])
                    elif "raw_response" in res and "reflection" not in res:
                        st.warning("The model returned an unstructured response. Please try again.")
                        with st.expander("View Raw Model Output"):
                            st.code(res["raw_response"], language=None)
                    else:
                        st.subheader("Reflection")
                        st.write(res["reflection"])
                        st.subheader("Summary")
                        st.write(res["summary"])
                        st.subheader("Follow-up Questions")
                        for item in res["followups"]:
                            st.markdown(f"**- {item['question']}**")
                            st.caption(f"*{item['follow_up']}*")
                        st.info(f"Tone: **{res['tone']}** | Sentiment: {emotion}")


                    if "reflection" in res:
                        data = {
                            "timestamp": datetime.datetime.now().isoformat(),
                            "entry": entry,
                            "reflection": res["reflection"],
                            "summary": res["summary"],
                            "followups": res["followups"],
                            "tone": res["tone"],
                            "safety": res["safety_flag"],
                            "sentiment": sentiment,
                            "emotion": emotion
                        }
                        insert_entry(data)
                    else:
                        st.warning("Skipping DB insert due to unstructured response.")

                    st.markdown("---")
                    st.subheader("🧭 Similar past reflections")
                    similar = get_similar_entries(entry, df_prev)
                    if isinstance(similar, list):
                        if not similar:
                            st.write("No similar past reflections found.")
                        else:
                            for sim in similar:
                                st.write(f"🕓 {sim['timestamp']} — ({sim['emotion']})")
                                st.caption(sim['entry'][:250] + "...")
                    else:
                        for _, row in similar.iterrows():
                            st.write(f"🕓 {row['timestamp']} — ({row['emotion']})")
                            st.caption(row["entry"][:250] + "...")


# ============================
# ANALYTICS TAB
# ============================
with tabs[1]:
    st.header("Your Emotional Journey")
    df = load_entries()
    if df.empty:
        st.write("No journal entries yet.")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        fig, ax = plt.subplots()
        ax.plot(df["timestamp"], df["sentiment"], marker='o')
        ax.set_xlabel("Date")
        ax.set_ylabel("Sentiment Score")
        ax.set_title("Sentiment Over Time")
        st.pyplot(fig)

        st.subheader("Emotion Breakdown")
        st.bar_chart(df["emotion"].value_counts())

        st.subheader("Recent Entries")
        st.dataframe(df.tail(5)[["timestamp", "emotion", "tone", "safety"]])

# ============================
# ABOUT TAB
# ============================
with tabs[2]:
    st.markdown("""
### ℹ️ About this Project
This project demonstrates a **Generative AI application** for mental well-being journaling.
It integrates:
- LLMs for empathetic reflection  
- Sentiment + emotion detection  
- Similarity retrieval (memory)  
- Streamlit for modern front-end  
- SQLite for persistent storage  

#### ⚖️ Ethics
- This bot is **not a therapist**.
- Detects crisis language & redirects users to professional help.
- Stores data **locally** for privacy.
""")
