from textblob import TextBlob

def analyze_emotion(text):
    sentiment = TextBlob(text).sentiment.polarity
    if sentiment > 0.4:
        emotion = "Positive"
    elif sentiment < -0.4:
        emotion = "Negative"
    else:
        emotion = "Neutral"
    return sentiment, emotion
