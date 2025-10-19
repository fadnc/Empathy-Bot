from textblob import TextBlob
from transformers import pipeline

# Use a pipeline for zero-shot classification
emotion_classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

# More granular, mental-health-focused emotion labels
EMOTION_LABELS = [
    "anxious", "overwhelmed", "lonely", "ashamed", "grieving",
    "joyful", "content", "frustrated", "hopeful", "angry",
    "confused", "unmotivated", "stressed", "peaceful", "neutral"
]

def analyze_emotion(text):
    """
    Analyzes sentiment polarity and categorizes into granular emotion labels
    more relevant to emotional well-being tracking.
    """
    # Get sentiment polarity (-1 to 1)
    sentiment = TextBlob(text).sentiment.polarity
    
    # Get more specific emotion using zero-shot classification
    result = emotion_classifier(text, EMOTION_LABELS, multi_label=False)
    emotion = result['labels'][0].capitalize()
    
    return sentiment, emotion


def get_emotion_category(emotion):
    """
    Groups emotions into broader categories for pattern analysis.
    Returns: 'positive', 'negative', 'neutral'
    """
    positive_emotions = ["joyful", "content", "hopeful", "peaceful"]
    negative_emotions = ["anxious", "overwhelmed", "lonely", "ashamed", "grieving", "frustrated", "angry", "stressed", "unmotivated", "confused"]
    
    if emotion.lower() in positive_emotions:
        return "positive"
    elif emotion.lower() in negative_emotions:
        return "negative"
    else:
        return "neutral"


def get_emotion_severity(sentiment):
    """
    Maps sentiment to severity level for better crisis assessment.
    Returns: 'critical' (-1 to -0.7), 'high' (-0.7 to -0.3), 
             'moderate' (-0.3 to 0.3), 'good' (0.3 to 0.7), 'excellent' (0.7 to 1)
    """
    if sentiment <= -0.7:
        return "critical"
    elif sentiment <= -0.3:
        return "high"
    elif sentiment <= 0.3:
        return "moderate"
    elif sentiment <= 0.7:
        return "good"
    else:
        return "excellent"
