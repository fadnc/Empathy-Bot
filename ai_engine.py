import subprocess
import json
import re

def _extract_json(text):
    """
    Extracts a JSON object from a string, even if it's embedded in other text
    or markdown.
    """
    # Match the first JSON object in the string
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return None


def call_ollama(prompt, context=None):
    """
    Calls the local Ollama model 'gemma3:1b' for text generation.
    """
    combined_prompt = prompt if not context else f"Context:\n{context}\n\nUser:\n{prompt}"
    
    try:
        result = subprocess.run(
            ["ollama", "run", "gemma3:1b"],
            input=combined_prompt,
            text=True,
            capture_output=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("⚠️ Error calling Ollama:", e.stderr)
        return None

def generate_reflection(user_input):
    """
    Generates an empathetic reflection, summary, and follow-up questions
    using Gemma 3 model running locally via Ollama.
    """
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
  "reflection": "It sounds like you’re feeling overwhelmed but still trying your best.",
  "summary": "Feeling emotionally exhausted but resilient.",
  "followups": [
    {{
      "question": "What usually helps you recharge when you feel this way?",
      "follow_up": "Encourages self-awareness of coping methods."
    }},
    {{
      "question": "Would you like to talk about what’s been the hardest part lately?",
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
    response = call_ollama(prompt)
    if not response:
        return {"error": "Failed to get response from Ollama."}

    try:
        # First, try to extract JSON from potentially messy output
        json_str = _extract_json(response)
        if not json_str:
            raise json.JSONDecodeError("No JSON object found", response, 0)
        data = json.loads(json_str)
    except json.JSONDecodeError:
        print("⚠️ JSON formatting issue detected. Returning raw output.")
        data = {"raw_response": response}

    return data

# Example interaction
if __name__ == "__main__":
    user_input = "I’ve been feeling really alone lately. Even when I talk to people, it feels like they don’t really get me."
    
    reflection_data = generate_reflection(user_input)
    print("\n🪞 Reflection Output:")
    print(json.dumps(reflection_data, indent=2, ensure_ascii=False))

    print("\n✨ Summary")
    print("Generated locally via Ollama gemma3:1b\n")

    # Optional pretty print
    if isinstance(reflection_data, dict) and "followups" in reflection_data:
        print("Follow-up Questions")
        for item in reflection_data["followups"]:
            print(f"• {item['question']}")
            print(f"  ↳ {item['follow_up']}")
