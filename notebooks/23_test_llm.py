from pathlib import Path
import os

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError(
        "OPENROUTER_API_KEY was not found. "
        "Check that your .env file exists in the project root."
    )

print("[OK] OpenRouter API key loaded")


# ============================================================
# 2. CONNECT TO OPENROUTER
# ============================================================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


# ============================================================
# 3. SELECT A FREE MODEL
# ============================================================

MODEL = "openrouter/free"


# ============================================================
# 4. TEST PROMPT
# ============================================================

system_prompt = """
You are the AI guidance assistant for Āśraya AI,
a community disaster resilience platform.

Your role is to provide clear, practical and safe
flood-preparedness guidance.

Important rules:
- Do not claim to be an emergency authority.
- Do not issue official evacuation orders.
- Do not invent weather or flood information.
- Encourage users to follow official local authority instructions.
- Keep answers concise and easy to understand.
"""

user_prompt = """
A user asks:

"What should I do if flooding is expected tomorrow?"

Give a short, practical answer for a general user.
"""


# ============================================================
# 5. SEND REQUEST
# ============================================================

print("[INFO] Sending request to OpenRouter...")

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ],
)


# ============================================================
# 6. DISPLAY RESPONSE
# ============================================================

answer = response.choices[0].message.content

print("\n" + "=" * 60)
print("ĀŚRAYA AI - LLM TEST")
print("=" * 60)

print("\nModel:")
print(MODEL)

print("\nAI Response:")
print(answer)

print("\n" + "=" * 60)
print("[SUCCESS] LLM connection is working.")
print("=" * 60)