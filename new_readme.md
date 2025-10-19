# 🧠 ReflectAI — AI-Powered Reflective Journaling Companion

## 💬 Overview

ReflectAI is an intelligent journaling application designed to provide emotional support and help users track their emotional well-being through AI-powered reflection. It combines sentiment analysis, emotion detection, and empathetic AI responses to help users understand their emotional patterns over time.

Built with Python and Streamlit, ReflectAI works both locally and deploys seamlessly to the cloud using Streamlit Cloud's infrastructure.

**This project was developed as part of a Capstone Project under the MSc Computer Science (Data Analytics) program.**

---

## 🚀 Key Features

- **Emotion & Sentiment Analysis:** Detects 15+ granular emotions and sentiment polarity from journal entries using transformer-based NLP models
- **Empathetic AI Reflections:** Generates personalized, contextual reflections on your entries using Google Gemini API (with local Ollama fallback)
- **Similar Entry Matching:** Finds and displays past journal entries with similar themes for pattern recognition
- **Persistent Storage:** Saves all entries to SQLite database for long-term tracking and analytics
- **Emotional Trend Dashboard:** Visualizes your emotional journey over time with sentiment graphs and emotion distribution charts
- **Advanced Search & Filtering:** Search by keywords, filter by emotion and sentiment range, sort by date or sentiment
- **Pattern Recognition:** Identifies emotion transitions, common themes in low-mood days, and emotional clusters
- **Crisis Detection:** Flags entries containing distress indicators and provides professional support resources
- **Actionable Insights:** Generates personalized coping suggestions and grounding techniques based on emotional state
- **Local-First or Cloud:** Works with local Ollama models or seamlessly falls back to cloud APIs when needed
- **Modular Architecture:** Clean separation of concerns with dedicated modules for AI logic, emotion analysis, and database handling

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **AI/LLM** | Google Gemini API 2.5 Flash + Ollama (local) |
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
├── emotion_analysis.py       # Sentiment & emotion detection (15+ emotions)
├── database.py               # SQLite database operations
├── config.py                 # Configuration, crisis keywords, coping strategies
├── utils.py                  # Advanced utilities (crisis detection, patterns, trends)
├── requirements.txt          # Python dependencies
├── .env.example              # Template for environment variables
├── .streamlit/
│   ├── config.toml          # Streamlit theme & settings
│   └── secrets.toml         # (Cloud only) API keys & secrets
└── README.md                # This file
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Google Gemini API key (free tier available at https://aistudio.google.com/app/apikeys)
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

**Getting your free Gemini API key:**
1. Go to https://aistudio.google.com/app/apikeys
2. Click "Get API Key"
3. Create a new API key
4. Copy it to your `.env` file

#### 5. Run Locally
```bash
streamlit run app.py
```

The app will open at: **http://localhost:8501**

---

## 🌐 Deployment on Streamlit Cloud

### Prerequisites
- GitHub account with your repo pushed
- Gemini API key

### Steps

1. **Prepare Repository**
   - Ensure `.env` and `.streamlit/secrets.toml` are in `.gitignore`
   - Push your code to GitHub

2. **Deploy via Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your repository, branch, and `app.py`
   - Click "Deploy"

3. **Add Secrets**
   - Once deployed, click Settings (gear icon) → Secrets
   - Paste your secrets:
     ```toml
     GEMINI_API_KEY = "your_key_here"
     ```
   - Save (app auto-redeploys)

### How It Works
- **Locally:** Tries to use local Ollama first, automatically falls back to Gemini if unavailable
- **Cloud:** Automatically uses Gemini API via encrypted secrets (Ollama not available on cloud)

---

## 📖 How to Use

### Writing a Journal Entry
1. Click the **Journal** tab
2. Write your thoughts freely in the text area
3. Click **Generate Reflection**
4. Receive AI-generated reflection, summary, actionable insights, and follow-up questions
5. Your entry is automatically saved with sentiment and emotion labels

### Viewing Your Dashboard
The sidebar shows:
- **Total Entries:** Number of journal entries
- **Average Sentiment:** Overall sentiment polarity (-1 to 1 scale)
- **Positive Days:** Count of entries with positive sentiment
- **Top Emotion:** Your most frequently recorded emotion
- **Last Entry:** Preview of your most recent entry
- **Quick Filter:** Filter all entries by emotion

### Search & Filter
- **Text Search:** Find entries by keywords or phrases
- **Emotion Filter:** Select multiple emotions to see only those entries
- **Sentiment Range:** Slider to filter by sentiment polarity
- **Sort Options:** By newest, oldest, most positive, or most negative

### Analytics Tab
- **Sentiment Over Time:** Color-coded line chart showing emotional trends
- **Emotion Distribution:** Bar chart of emotion frequencies
- **Key Statistics:** Average, highest, lowest sentiment, and volatility
- **Recent Entries:** Table of your last 10 entries with metadata

### Insights Tab
- **Emotion Frequency:** How often each emotion appears
- **Sentiment Statistics:** Range, average, and volatility metrics
- **Emotion Transitions:** Patterns of which emotions follow others
- **Low-Mood Context:** Common themes and words in difficult entries

---

## 🔐 Security & Privacy

- **Local-First Data:** All entries stored locally in SQLite (not sent to servers unless deployed)
- **API Keys:** Never committed to GitHub; stored in `.env` (local) or Streamlit Secrets (cloud)
- **No Data Training:** Your journal entries are never used to train the AI model
- **No Tracking:** This app doesn't collect analytics or user data
- **Open Source:** Full transparency—audit the code yourself

---

## ⚠️ Important Notes

**This is NOT a replacement for therapy or professional mental health support.**

- ReflectAI is a journaling tool to help you reflect on your emotions
- If you're in crisis or having suicidal thoughts, please contact a mental health professional immediately
- Crisis keywords are detected and flagged; resources are provided
- For serious mental health concerns, reach out to a therapist or counselor

### Crisis Support Resources
- **Global:** https://findahelpline.com
- **US (24/7):** Call or text 988
- **International:** https://www.befrienders.org

---

## 🧠 How the AI Works

### Reflection Generation
1. Your entry is sent to Google Gemini 2.5 Flash API (or local Ollama if available)
2. The AI generates context-aware responses including:
   - **Reflection:** Empathetic 2-3 sentence response tailored to your emotional state
   - **Summary:** One-line emotional theme
   - **Actionable Insight:** Practical suggestion for a small step forward
   - **Follow-up Questions:** 2 supportive prompts for deeper reflection
   - **Coping Suggestion:** Grounding technique if sentiment is low (e.g., 5-4-3-2-1 grounding)
   - **Tone:** Description of response style
   - **Safety Flag:** Indicates if distress was detected

### Emotion Detection
- **Sentiment:** TextBlob calculates polarity (-1 to +1)
- **Emotion Classification:** Zero-shot classification using `facebook/bart-large-mnli` transformer
- **Supported Emotions:** Anxious, overwhelmed, lonely, ashamed, grieving, joyful, content, frustrated, hopeful, peaceful, angry, stressed, unmotivated, confused, neutral
- **Severity Mapping:** Critical, High, Moderate, Good, Excellent

### Pattern Recognition
- **Similarity Matching:** TF-IDF vectorization to find thematically similar past entries
- **Emotion Transitions:** Identifies which emotions frequently follow others
- **Low-Mood Analysis:** Extracts common themes and words from difficult entries
- **Sentiment Trends:** Weekly and monthly sentiment patterns

---

## ❌ Troubleshooting

### Issue: "API key not valid" Error on Streamlit Cloud

This occurs when the Gemini API key is invalid, expired, or not properly set in Streamlit Cloud secrets.

**Solutions:**

1. **Verify your API key is active:**
   - Go to https://aistudio.google.com/app/apikeys
   - Confirm your key exists and hasn't been deleted
   - If deleted, create a new one

2. **Test the key locally first:**
   ```bash
   export GEMINI_API_KEY="your_key_here"
   python -c "import google.generativeai as genai; genai.configure(api_key='$GEMINI_API_KEY'); print(list(genai.list_models()))"
   ```
   - If this shows available models, your key is valid
   - If it shows an error, the key is invalid

3. **Re-add secrets to Streamlit Cloud:**
   - Go to your app → Settings → Secrets
   - Delete the existing key
   - Save
   - Add it again (copy-paste carefully, no extra spaces)
   - Save again (app auto-redeploys)

4. **Common causes:**
   - Free trial API key expired (Google gives 60-day free tier)
   - Copy-paste error (extra spaces or characters)
   - Using a key from a different Google account
   - Key was revoked or disabled

5. **If still failing:**
   - Create a completely new API key
   - Delete the old one
   - Update Streamlit Cloud secrets
   - Redeploy

### Issue: Ollama Not Found Locally

If you see warnings about Ollama, it's fine—the app will automatically use Gemini instead. Ollama is optional for local development.

To use Ollama locally:
```bash
ollama serve
# In another terminal:
streamlit run app.py
```

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
MODEL = "models/gemini-2.5-flash"  # Gemini model version
DB_FILE = "journal_entries.db"     # Database file path
CRISIS_WORDS = [...]               # Crisis detection keywords
COPING_STRATEGIES = {...}          # Emotion-specific coping techniques
```

---

## 📦 Dependencies

All dependencies are in `requirements.txt`:
- `streamlit` - Web framework
- `google-generativeai` - Gemini API client
- `transformers` - NLP models for emotion detection
- `textblob` - Sentiment analysis
- `pandas` - Data manipulation
- `matplotlib` - Charts & visualization
- `scikit-learn` - TF-IDF & similarity analysis
- `torch` - ML framework for transformers
- `python-dotenv` - Environment variables

---

## 🚧 Future Enhancements

- Voice journaling with transcription
- Export entries as PDF or CSV
- User-defined emotion tags
- Sentiment trend predictions
- Integration with wearable health data
- Multi-language support
- Dark/light theme toggle
- Scheduled journaling reminders
- Weekly email summaries
- Reflection feedback (rate if helpful)
- Mood streak tracking

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
- The open-source NLP community for transformers and sentiment analysis tools
