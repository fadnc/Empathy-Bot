import subprocess
import json
import re
import os
import google.generativeai as genai
from config import MODEL

def _extract_json(text):
    """Extract JSON from potentially messy text."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return None


def call_ollama(prompt, context=None):
    """Try local Ollama, return None if unavailable."""
    combined_prompt = prompt if not context else f"Context:\n{context}\n\nUser:\n{prompt}"
    
    try:
        result = subprocess.run(
            ["ollama", "run", "gemma3:1b"],
            input=combined_prompt,
            text=True,
            capture_output=True,
            check=True,
            encoding='utf-8',
            errors='replace',
            timeout=30
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def call_gemini(prompt):
    """Call Google Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY environment variable not set."}

    genai.configure(api_key=api_key)
    
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        json_str = _extract_json(response_text)
        if json_str:
            return json.loads(json_str)
        else:
            return json.loads(response_text)
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse response: {e}"}
    except Exception as e:
        return {"error": f"Failed to get response from Gemini: {e}"}


def build_contextual_prompt(user_input, emotion, sentiment, past_patterns=None):
    """
    Builds a smarter prompt based on detected emotion and sentiment.
    Includes context-specific follow-up questions.
    """
    
    # Determine prompt style based on emotion/sentiment
    if sentiment < -0.7:
        tone_instruction = "Use an extra compassionate, grounding tone. Focus on safety and immediate coping."
    elif sentiment < -0.3:
        tone_instruction = "Use a warm, validating tone. Help them see small positive steps they can take."
    elif sentiment < 0.3:
        tone_instruction = "Use a balanced, curious tone. Help them explore what they're experiencing."
    else:
        tone_instruction = "Use an encouraging, reinforcing tone. Help them build on this positive momentum."
    
    # Context-specific follow-ups
    followup_context = ""
    if emotion.lower() == "lonely":
        followup_context = "Focus follow-ups on connection: relationships, reaching out, community."
    elif emotion.lower() == "anxious" or emotion.lower() == "overwhelmed":
        followup_context = "Focus follow-ups on breaking things down into manageable steps and grounding techniques."
    elif emotion.lower() == "ashamed" or emotion.lower() == "grieving":
        followup_context = "Focus follow-ups on self-compassion and processing feelings."
    elif emotion.lower() == "joyful" or emotion.lower() == "hopeful":
        followup_context = "Focus follow-ups on sustaining this momentum and understanding what contributed."
    elif emotion.lower() == "frustrated" or emotion.lower() == "angry":
        followup_context = "Focus follow-ups on understanding the source and healthy expression."
    
    prompt = f"""
You are a compassionate, non-judgmental emotional support companion. Your role is to help users reflect deeply on their emotions and find actionable insights.

{tone_instruction}

User's emotional state: {emotion} (sentiment score: {sentiment:.2f})
{followup_context}

User's journal entry:
\"\"\"{user_input}\"\"\"

Generate a helpful response with this exact JSON format (no extra text):

{{
  "reflection": "A 3-4 sentence empathetic reflection that validates their feelings , shows you understand and also do join them in their emotions . If sentiment is very low, include a grounding element.",
  "summary": "One-line summary capturing the core emotion/theme.",
  "actionable_insight": "A brief, practical suggestion they could try (not therapy advice, just small actionable steps which could improve or refresh their mind and fresehn them up').",
  "followups": [
    {{
      "question": "A deeply thoughtful follow-up question tailored to their specific situation and emotion",
      "follow_up": "Why this question matters for their emotional growth"
    }},
    {{
      "question": "A second follow-up that explores either what led to this or what could help them move forward",
      "follow_up": "The psychological principle or insight behind this question"
    }}
  ],
  "tone": "Description of the tone used (e.g., warm and grounding, gently challenging, celebratory)",
  "safety_flag": true/false,
  "coping_suggestion": "If sentiment < -0.3: suggest a grounding or coping technique "
}}

Example for anxious entry:
{{
  "reflection": "It sounds like you're caught in a cycle of worry and uncertainty. That's a completely understandable response to feeling out of control.",
  "summary": "Overwhelmed by things beyond your control",
  "actionable_insight": "Try identifying just one thing you CAN control today and focus on that for 10 minutes",
  "followups": [
    {{
      "question": "What's one small thing that's actually within your control right now?",
      "follow_up": "Helps shift focus from overwhelming unknowns to what you can influence"
    }},
    {{
      "question": "When did this feeling start, and was there a specific trigger?",
      "follow_up": "Understanding the origin helps address the root cause vs. just the symptoms"
    }}
  ],
  "tone": "calm and grounding, gently refocusing",
  "safety_flag": false,
  "coping_suggestion": "Try the 5-4-3-2-1 grounding technique: name 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste"
}}
"""
    
    return prompt


def generate_reflection(user_input, emotion=None, sentiment=None, past_patterns=None):
    """
    Generates contextual reflection with smart follow-ups based on emotion.
    Falls back to Gemini if Ollama unavailable.
    """
    # If emotion/sentiment not provided, analyze them first
    if emotion is None or sentiment is None:
        from emotion_analysis import analyze_emotion
        sentiment, emotion = analyze_emotion(user_input)
    
    prompt = build_contextual_prompt(user_input, emotion, sentiment, past_patterns)
    
    print("\n🧠 Generating empathetic reflection...\n")
    
    # Try Ollama first
    response = call_ollama(prompt)
    
    if response:
        print("✓ Using local Ollama model\n")
        try:
            json_str = _extract_json(response)
            if not json_str:
                raise json.JSONDecodeError("No JSON found", response, 0)
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("⚠️ Ollama returned invalid JSON. Falling back to Gemini...")
    
    # Fall back to Gemini
    print("✓ Using Google Gemini API\n")
    return call_gemini(prompt)

