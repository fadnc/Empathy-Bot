#🧠 Empathy Bot — AI-Powered Emotional Support Chat Assistant
💬 Overview

Empathy Bot is an intelligent conversational assistant designed to provide emotional support and detect user sentiment through text interactions.
It combines Natural Language Processing (NLP), sentiment analysis, and context-aware AI responses to simulate empathetic communication.

This project was developed as part of a Capstone Project under the MSc Computer Science (Data Analytics) program.

🚀 Features

🗣️ Emotion Detection: Analyzes user input to detect emotions (e.g., sad, happy, stressed).

💖 Empathetic Responses: Generates emotionally aware responses using an AI engine.

🧩 Modular Design: Separate modules for AI logic, emotion analysis, and database handling.

💾 Journal Storage: Saves conversation entries to a SQLite database for tracking patterns.

🔐 Environment Variables: Secure configuration using .env files.

⚙️ Easy Deployment: Can be hosted on local server or deployed on Render / AWS / Hugging Face Spaces.

🗂️ Project Structure
Capstone/
│
├── ai_engine.py           # Core AI logic and response generation
├── app.py                 # Flask app entry point
├── config.py              # Configuration settings
├── database.py            # Handles SQLite database operations
├── emotion_analysis.py    # Emotion and sentiment detection module
├── utils.py               # Helper functions
├── requirements.txt       # Python dependencies
├── .env.example           # Template for environment variables
└── version_rollback/      # Backup or experimental versions

⚙️ Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/<your-username>/empathy-bot.git
cd empathy-bot

2️⃣ Create a virtual environment
python -m venv venv


Activate it:

Windows

venv\Scripts\activate


Mac/Linux

source venv/bin/activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Setup environment variables

Rename the file:

cp .env.example .env


Then open .env and add your keys:

API_KEY=your_openai_or_gemini_key
DB_PATH=journal_entries.db

5️⃣ Run the application
python app.py


The app will start on http://localhost:5000

🧩 Technologies Used

Python 3.10+

Flask – Web framework

SQLite – Lightweight local database

NLTK / TextBlob / Transformers – NLP and sentiment analysis

dotenv – Environment configuration

(Optional) OpenAI / Gemini / Hugging Face APIs

🧠 Future Enhancements

Real-time emotion tracking dashboard

Integration with voice-based emotion recognition

Enhanced memory for multi-session empathy

Deployable chatbot interface (Streamlit or React frontend)

🧑‍💻 Author

Fadhil
MSc Computer Science (Data Analytics)
Capstone Project 2025

🪪 License

This project is licensed under the MIT License — free to use, modify, and share with attribution.
