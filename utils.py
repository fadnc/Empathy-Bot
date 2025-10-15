from config import CRISIS_WORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def crisis_detect(text):
    text_lower = text.lower()
    return any(word in text_lower for word in CRISIS_WORDS)

def compute_similarity(new_entry, old_entries):
    corpus = [new_entry] + old_entries
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    sim_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    return sim_scores

def get_similar_entries(current_text, df):
    if len(df) < 3:
        return []
    old_entries = df["entry"].tolist()
    scores = compute_similarity(current_text, old_entries)
    top_indices = scores.argsort()[-3:][::-1]
    similar = df.iloc[top_indices][["timestamp", "entry", "emotion"]]
    return similar
