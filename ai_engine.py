import subprocess
import json
import re
import os
import openai
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
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print("⚠️ Ollama not available, using OpenAI...")
        return None

def call_openai(prompt):
    """Call OpenAI API."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY environment variable not set."}

    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an empathetic reflection generator. Return only a valid JSON object."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        response_content = response.choices[0].message.content
        return json.loads(response_content)
    except Exception as e:
        print(f"⚠️ Error calling OpenAI: {e}")
        return {"error": f"Failed to get response from OpenAI: {e}"}

def generate_reflection(user_input):
    """Generate reflection with Ollama fallback to OpenAI."""
    prompt = f"""
You are an empathetic reflection generator.

User input:
\"\"\"{user_input}\"\"\"

Return only a valid JSON object — do not include any explanation, notes, or extra text.

Required keys:
- reflection: A deeply empathetic reflection (2–3 sentences).
- summary: One-line summary of user emotion/theme.
- followups: A list of exactly 2 follow-up objects, each containing:
  {{
    "question": "A supportive open-ended follow-up question",
    "follow_up": "A helpful suggestion or reasoning for asking that question"
  }}
- tone: Describe the tone used (e.g., warm, gentle, supportive, hopeful).
- safety_flag: true if input shows distress/risk, false otherwise.

Example (strict format):
{{
  "reflection": "It sounds like you're feeling overwhelmed but still trying your best.",
  "summary": "Feeling emotionally exhausted but resilient.",
  "followups": [
    {{
      "question": "What usually helps you recharge when you feel this way?",
      "follow_up": "Encourages self-awareness of coping methods."
    }},
    {{
      "question": "Would you like to talk about what's been the hardest part lately?",
      "follow_up": "Promotes openness and deeper reflection."
    }}
  ],
  "tone": "warm",
  "safety_flag": false
}}

Now generate the JSON response based on the user's input below:
User: {user_input}
"""

    print("\n🧠 Generating empathetic reflection...\n")
    
    # Try Ollama first (local development)
    response = call_ollama(prompt)
    
    if response:
        print("✓ Using local Ollama model\n")
        try:
            json_str = _extract_json(response)
            if not json_str:
                raise json.JSONDecodeError("No JSON found", response, 0)
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("⚠️ Ollama returned invalid JSON. Falling back to OpenAI...")
    
    # Fall back to OpenAI (cloud deployment)
    print("✓ Using OpenAI API\n")
    return call_openai(prompt)
