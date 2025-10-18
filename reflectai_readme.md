# 🧠 ReflectAI — AI-Powered Reflective Journaling Companion

## 💬 Overview

ReflectAI is an intelligent journaling application designed to provide emotional support and help users track their emotional well-being through AI-powered reflection. It combines sentiment analysis, emotion detection, and empathetic AI responses to help users understand their emotional patterns over time.

Built with Python and Streamlit, ReflectAI works both locally and deploys seamlessly to the cloud using Streamlit Cloud's infrastructure.

**This project was developed as part of a Capstone Project under the MSc Computer Science (Data Analytics) program.**

---

## 🚀 Key Features

- **Emotion & Sentiment Analysis:** Detects emotions and sentiment polarity from journal entries using transformer-based NLP models
- **Empathetic AI Reflections:** Generates thoughtful, compassionate reflections on your entries using Google Gemini API (with local Ollama fallback)
- **Similar Entry Matching:** Finds and displays past journal entries with similar themes for pattern recognition
- **Persistent Storage:** Saves all entries to SQLite database for long-term tracking and analytics
- **Emotional Trend Dashboard:** Visualizes your emotional journey over time with sentiment graphs and emotion distribution charts
- **Crisis Detection:** Flags entries containing distress indicators and provides resources
- **Local-First or Cloud:** Works with local Ollama models or seamlessly falls back to cloud APIs when needed
- **Modular Architecture:** Clean separation of concerns with dedicated modules for AI logic, emotion analysis, and database handling

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **AI/LLM** | Google Gemini API + Ollama (local) |
| **NLP** | Transformers (facebook/bart-large-mnli), TextBlob |
| **Database** | SQLite |
| **Data Processing** | Pandas, Scikit-learn (TF-IDF) |
| **Visualization** | Matplotlib |
| **Language** | Python 3.10+ |

---

## 📋 Project Structure

```
empathy-bot/
├── app.py                    # Main Streamlit application
├── ai_engine.py              # Gemini API integration & Ollama fallback
├── emotion_analysis.py       # Sentiment & emotion detection
├── database.py               # SQLite database operations
├── config.py                 # Configuration & constants
├── utils.py                  # Utility functions (crisis detection, similarity)
├── requirements.txt          # Python dependencies
├── .env.example              # Template for environment variables
├── .streamlit/
│   ├── config.toml          # Streamlit theme & settings
│   └── secrets.toml         # (Cloud only) API keys & secrets
└── README.md                # This file
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Google Gemini API key (free tier available)
- Optional: Ollama installed locally for offline mode

### Quick Start

#### 1. Clone the Repository
```bash
git clone https://github.com/fadnc/Empathy-Bot.git
cd Empathy-Bot
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Setup Environment Variables

Copy the example file:
```bash
cp .env.example .env
```

Open `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
DB_PATH=journal_entries.db
```

Get your free Gemini API key from: https://aistudio.google.com/app/apikeys

#### 5. Run Locally
```bash
streamlit run app.py
```

The app will open at: **http://localhost:8501**

---

## 🌐 Deployment on Streamlit Cloud

### Steps

1. **Push to GitHub**
   - Ensure `.env` and `.streamlit/secrets.toml` are in `.gitignore`
   - Push your code to a GitHub repository

2. **Deploy via Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your repository, branch, and main file (`app.py`)
   - Click "Deploy"

3. **Add Secrets**
   - Once deployed, go to Settings (gear icon) → Secrets
   - Paste your secrets:
     ```toml
     GEMINI_API_KEY = "your_key_here"
     ```
   - Save (app auto-redeploys)

### How It Works
- **Locally:** Uses local Ollama (`gemma3:1b`) if available, falls back to Gemini
- **Cloud:** Automatically uses Gemini API via secrets

---

## 📖 How to Use

### Writing a Journal Entry
1. Click the **"📝 Journal"** tab
2. Write your thoughts freely in the text area
3. Click **"✨ Generate Empathetic Reflection"**
4. Receive AI-generated reflection, summary, and follow-up questions
5. Your entry is automatically saved with sentiment and emotion labels

### Viewing Your Dashboard
The sidebar shows:
- **Total Entries:** Number of journal entries
- **Average Sentiment:** Overall sentiment polarity
- **Most Common Emotion:** Your predominant emotional state
- **Last Reflection:** Your most recent entry
- **Filter by Emotion:** Browse past entries by emotion type

### Analytics
Click the **"📊 Analytics"** tab to see:
- **Sentiment Over Time:** Line chart showing emotional trends (color-coded)
- **Emotion Distribution:** Bar chart of emotion frequencies
- **Recent Entries:** Table of your last 5 entries with metadata

### Similar Reflections
After generating a reflection, the app shows past entries with similar themes using TF-IDF cosine similarity matching.

---

## 🔐 Security & Privacy

- **Local-First Data:** All entries stored locally in SQLite (not sent to servers unless you deploy)
- **API Keys:** Never committed to GitHub; stored in `.env` (local) or Streamlit Secrets (cloud)
- **No Tracking:** This app doesn't collect analytics or user data
- **Open Source:** Full transparency—audit the code yourself

---

## ⚠️ Important Notes

**This is NOT a replacement for therapy or professional mental health support.**

- ReflectAI is a journaling tool to help you reflect on your emotions
- If you're in crisis, please contact a mental health professional immediately
- Crisis keywords are flagged and link to resources (findahelpline.com)
- For serious mental health concerns, reach out to a therapist or counselor

---

## 🧠 How the AI Works

### Reflection Generation
1. Your entry is sent to Google Gemini API (or local Ollama)
2. The AI generates a JSON response containing:
   - **Reflection:** Empathetic 2-3 sentence response
   - **Summary:** One-line emotional theme
   - **Follow-up Questions:** 2 supportive prompts for deeper reflection
   - **Tone:** Description of response tone
   - **Safety Flag:** Whether distress indicators were detected

### Emotion Detection
- **Sentiment:** TextBlob calculates polarity (-1 to +1)
- **Emotion:** Zero-shot classification using `facebook/bart-large-mnli` transformer
- **Labels:** Joy, Sadness, Anger, Fear, Surprise, Love, Neutral

### Similar Entry Matching
- Uses TF-IDF vectorization to find thematically similar past entries
- Computes cosine similarity scores
- Returns top 3 most similar reflections

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
MODEL = "models/gemini-2.5-flash"  # Gemini model version
DB_FILE = "journal_entries.db"     # Database path
CRISIS_WORDS = [...]               # Crisis detection keywords
```

---

## 📦 Dependencies

All dependencies are listed in `requirements.txt`:
- `streamlit` - Web framework
- `google-generativeai` - Gemini API client
- `transformers` - NLP models
- `textblob` - Sentiment analysis
- `pandas` - Data manipulation
- `matplotlib` - Charts & visualization
- `scikit-learn` - TF-IDF & similarity
- `torch` - ML framework for transformers
- `python-dotenv` - Environment variables

---

## 🚧 Future Enhancements

- **Voice Journaling:** Support audio input with transcription
- **Export Features:** Download journal as PDF or CSV
- **Custom Emotion Tags:** User-defined emotion categories
- **Mood Predictions:** Predict emotional trends based on historical data
- **Integration with Wearables:** Connect with health data (heart rate, sleep)
- **Multi-language Support:** Support for journaling in different languages
- **Dark/Light Theme Toggle:** User preference settings
- **Scheduled Prompts:** Daily reflection reminders

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the **MIT License** — free to use, modify, and distribute with attribution. See the LICENSE file for details.

---

## 👨‍💻 Author

**Fadhil Muhammed N C**  
*MSc Computer Science (Data Analytics)*  
*Capstone Project 2025*

---

## 📞 Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check existing issues and discussions first
- Include details about your setup and the problem

---

## ❤️ Acknowledgments

- Google Gemini API for empathetic response generation
- Ollama for local LLM support
- Streamlit for the elegant web framework
- The open-source NLP community

