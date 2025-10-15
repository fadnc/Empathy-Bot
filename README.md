# 🧠 Empathy Bot — AI-Powered Emotional Support Chat Assistant

## 💬 Overview

Empathy Bot is an intelligent conversational assistant designed to provide emotional support and detect user sentiment through text interactions.  
It combines Natural Language Processing (NLP), sentiment analysis, and context-aware AI responses to simulate empathetic communication.

This project was developed as part of a Capstone Project under the MSc Computer Science (Data Analytics) program.

---

## 🚀 Features

- 🗣️ **Emotion Detection:** Analyzes user input to detect emotions (e.g., sad, happy, stressed).  
- 💖 **Empathetic Responses:** Generates emotionally aware responses using an AI engine.  
- 🧩 **Modular Design:** Separate modules for AI logic, emotion analysis, and database handling.  
- 💾 **Journal Storage:** Saves conversation entries to a SQLite database for tracking patterns.  
- 🔐 **Environment Variables:** Secure configuration using `.env` files.  
- ⚙️ **Easy Deployment:** Can be hosted locally or deployed on Render / AWS / Hugging Face Spaces.  

---

## 🗂️ Project Structure

```
Capstone/
│
├── ai_engine.py           # Core AI response logic
├── app.py                 # Flask app entry point
├── config.py              # Configuration settings
├── database.py            # SQLite handling
├── emotion_analysis.py    # Emotion and sentiment detection
├── utils.py               # Utility functions
├── requirements.txt       # Dependencies
├── .env.example           # Template for API keys
├── version_rollback/      # Backup or experimental versions
└── README.md              # Project documentation
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/empathy-bot.git
cd empathy-bot
```

### 2️⃣ Create a virtual environment
```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Setup environment variables
Rename the example file:
```bash
cp .env.example .env
```

Then open `.env` and add your keys:
```
API_KEY=your_openai_or_gemini_key
DB_PATH=journal_entries.db
```

### 5️⃣ Run the application
```bash
python app.py
```

The app will start on:  
👉 **http://localhost:5000**

---

## 🧩 Technologies Used

- **Python 3.10+**  
- **Flask** – Web framework  
- **SQLite** – Lightweight local database  
- **NLTK / TextBlob / Transformers** – NLP and sentiment analysis  
- **dotenv** – Environment configuration  
- *(Optional)* **OpenAI / Gemini / Hugging Face APIs**

---

## 🧠 Future Enhancements

- Real-time emotion tracking dashboard  
- Integration with voice-based emotion recognition  
- Enhanced memory for multi-session empathy  
- Deployable chatbot interface (Streamlit or React frontend)

---

## 🧑‍💻 Author

**Fadhil Muhammed N C**  
*MSc Computer Science (Data Analytics)*  
*Capstone Project 2025*

---

## 🪪 License

This project is licensed under the **MIT License** — free to use, modify, and share with attribution.
