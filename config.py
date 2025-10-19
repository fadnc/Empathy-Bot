MODEL = "models/gemini-2.5-flash"
DB_FILE = "journal_entries.db"

# Enhanced crisis detection keywords
CRISIS_WORDS = [
    # Suicidal ideation
    "suicide", "kill myself", "end it", "no point", "no reason to live", 
    "better off dead", "want to die",
    
    # Self-harm
    "cutting", "self harm", "hurt myself", "starving", "overdose", 
    "harm myself", "slice", "bleed",
    
    # Hopelessness
    "everything's pointless", "give up", "can't take it", "never get better", 
    "hopeless", "worthless", "useless", "broken",
    
    # Acute distress
    "panicking", "can't breathe", "losing it", "falling apart", 
    "breaking down", "freaking out",
    
    # Substance abuse indicators
    "drinking to forget", "high all day", "need drugs", "substance abuse",
]

# Coping strategies suggestions based on emotion
COPING_STRATEGIES = {
    "anxious": [
        "Try the 5-4-3-2-1 grounding technique: name 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste",
        "Practice box breathing: breathe in for 4, hold for 4, out for 4, hold for 4",
        "Progressive muscle relaxation: tense and release each muscle group for 5 seconds",
    ],
    "overwhelmed": [
        "Break the task into 3 small steps and focus on just the first one",
        "Write down everything bothering you, then pick just one to address",
        "Take a 10-minute break and do something you enjoy",
    ],
    "lonely": [
        "Reach out to one person—even a text counts",
        "Join an online community around something you enjoy",
        "Do one activity in public (coffee shop, park) even if alone",
    ],
    "ashamed": [
        "Write a compassionate letter to yourself as if from a best friend",
        "Remember: you're human, mistakes are part of growth",
        "Consider sharing your feeling with one trusted person",
    ],
    "angry": [
        "Go for a 15-minute walk or run to release energy",
        "Journal without filter: write angry, don't hold back",
        "Do something physical: punch a pillow, shake it out",
    ],
    "grieving": [
        "Spend time with this feeling—it's valid and necessary",
        "Create a small ritual to honor what you've lost",
        "Reach out to someone who understands your loss",
    ],
    "default": [
        "Take a few deep breaths and notice your surroundings",
        "Move your body for 5 minutes—stretch, walk, dance",
        "Drink water and step outside if possible",
    ]
}

# Resource links for crisis support
CRISIS_RESOURCES = {
    "global": "https://findahelpline.com",
    "us_crisis_line": "https://988lifeline.org (call or text 988)",
    "crisis_text": "Text HOME to 741741",
    "international": "https://www.befrienders.org",
}
