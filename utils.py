from config import CRISIS_WORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from collections import Counter

# Enhanced crisis detection keywords
CRISIS_KEYWORDS = {
    "self_harm": ["cutting", "self harm", "hurt myself", "starving", "overdose", "harm myself", "slice", "bleed"],
    "suicidal": ["suicide", "kill myself", "end it", "no point", "no reason to live", "better off dead"],
    "hopelessness": ["everything's pointless", "give up", "can't take it", "never get better", "hopeless", "worthless"],
    "acute_distress": ["panicking", "can't breathe", "losing it", "falling apart", "breaking down", "freaking out"],
    "substance_abuse": ["drinking to forget", "high all day", "need drugs", "substance", "intoxicated"],
}

def crisis_detect(text):
    """
    Enhanced crisis detection with severity levels.
    Returns: 'critical', 'high', 'moderate', or None
    """
    text_lower = text.lower()
    
    # Check critical keywords first
    critical_keywords = CRISIS_KEYWORDS["self_harm"] + CRISIS_KEYWORDS["suicidal"]
    for keyword in critical_keywords:
        if keyword in text_lower:
            return "critical"
    
    # Check high-risk keywords
    high_risk = CRISIS_KEYWORDS["hopelessness"] + CRISIS_KEYWORDS["acute_distress"]
    for keyword in high_risk:
        if keyword in text_lower:
            return "high"
    
    # Check moderate-risk keywords
    for keyword in CRISIS_KEYWORDS["substance_abuse"]:
        if keyword in text_lower:
            return "moderate"
    
    return None


def compute_similarity(new_entry, old_entries):
    """
    Computes TF-IDF based cosine similarity between new entry and old entries.
    """
    corpus = [new_entry] + old_entries
    vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    sim_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    return sim_scores


def get_similar_entries(current_text, df, top_n=3):
    """
    Finds similar entries based on TF-IDF cosine similarity.
    """
    if len(df) < 3:
        return []
    old_entries = df["entry"].tolist()
    scores = compute_similarity(current_text, old_entries)
    top_indices = scores.argsort()[-top_n:][::-1]
    similar = df.iloc[top_indices][["timestamp", "entry", "emotion", "sentiment"]]
    return similar


def get_emotion_patterns(df):
    """
    Analyzes emotion patterns in the journal.
    Returns dict with emotion frequency, combinations, and trends.
    """
    if df.empty:
        return {}
    
    emotion_counts = df["emotion"].value_counts().to_dict()
    sentiment_stats = {
        "average": df["sentiment"].mean(),
        "highest": df["sentiment"].max(),
        "lowest": df["sentiment"].min(),
        "std_dev": df["sentiment"].std()
    }
    
    # Find most common emotion combinations (emotion + sentiment category)
    df_copy = df.copy()
    df_copy["sentiment_level"] = df_copy["sentiment"].apply(
        lambda x: "positive" if x > 0.3 else "negative" if x < -0.3 else "neutral"
    )
    combo_counts = (df_copy["emotion"] + " + " + df_copy["sentiment_level"]).value_counts().head(5).to_dict()
    
    return {
        "emotion_frequency": emotion_counts,
        "sentiment_stats": sentiment_stats,
        "common_combinations": combo_counts,
        "total_entries": len(df)
    }


def get_sentiment_trends(df):
    """
    Returns weekly sentiment trends for visualization.
    """
    if df.empty:
        return None
    
    df_copy = df.copy()
    df_copy["timestamp"] = pd.to_datetime(df_copy["timestamp"])
    df_copy["week"] = df_copy["timestamp"].dt.isocalendar().week
    
    weekly_trends = df_copy.groupby("week").agg({
        "sentiment": ["mean", "min", "max", "count"]
    }).round(2)
    
    return weekly_trends


def get_emotion_triggers(df):
    """
    Identifies patterns: which emotions follow specific emotions?
    Returns most common emotion transitions.
    """
    if len(df) < 2:
        return {}
    
    df_sorted = df.sort_values("timestamp").reset_index(drop=True)
    emotions = df_sorted["emotion"].tolist()
    
    transitions = []
    for i in range(len(emotions) - 1):
        transitions.append(f"{emotions[i]} → {emotions[i+1]}")
    
    transition_counts = Counter(transitions).most_common(5)
    return {t[0]: t[1] for t in transition_counts}


def get_low_sentiment_context(df, threshold=-0.3):
    """
    For entries with low sentiment, analyze what might have contributed.
    Returns top words from low-sentiment entries.
    """
    if df.empty:
        return []
    
    low_sentiment_entries = df[df["sentiment"] < threshold]
    if low_sentiment_entries.empty:
        return []
    
    all_text = " ".join(low_sentiment_entries["entry"].tolist())
    
    # Simple word frequency (in production, use NLTK for better NLP)
    from collections import Counter
    words = all_text.lower().split()
    # Filter common stop words
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "is", "are", "was", "were"}
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
    
    top_words = Counter(filtered_words).most_common(10)
    return {word: count for word, count in top_words}
