from textblob import TextBlob
from transformers import pipeline

# Use a pipeline for zero-shot classification. This is more flexible.
# The model is downloaded and cached automatically on first run.
emotion_classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

EMOTION_LABELS = ["joy", "sadness", "anger", "fear", "surprise", "love", "neutral"]

def analyze_emotion(text):
    """
    Analyzes the sentiment of a text and categorizes it into a more
    granular emotion label.
    granular emotion label using a zero-shot classification model.
    """
    sentiment = TextBlob(text).sentiment.polarity
    if sentiment > 0.6:
        emotion = "Very Positive"
    elif sentiment > 0.1:
        emotion = "Positive"
    elif sentiment < -0.6:
        emotion = "Very Negative"
    elif sentiment < -0.1:
        emotion = "Slightly Negative"
    else:
        emotion = "Neutral"

    # Get a more specific emotion
    result = emotion_classifier(text, EMOTION_LABELS, multi_label=False)
    # The top label is the most likely emotion
    emotion = result['labels'][0].capitalize()

    return sentiment, emotion
