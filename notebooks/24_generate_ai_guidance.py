from pathlib import Path
import os
import pandas as pd
import numpy as np

from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CONTEXT_PATH = PROJECT_ROOT / "models" / "ai_guidance_context.csv"
ML_DATASET_PATH = PROJECT_ROOT / "data" / "kerala_ml_dataset.csv"

EMBEDDINGS_PATH = PROJECT_ROOT / "models" / "rag" / "embeddings.npy"
CHUNKS_PATH = PROJECT_ROOT / "models" / "rag" / "chunks.npy"


# ============================================================
# 2. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env")

print("[OK] OpenRouter API key loaded")


# ============================================================
# 3. OPENROUTER CLIENT
# ============================================================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

MODEL = "openrouter/free"


# ============================================================
# 4. LOAD ĀŚRAYA RISK CONTEXT
# ============================================================

risk_df = pd.read_csv(CONTEXT_PATH)

print(f"[OK] Risk context loaded: {len(risk_df)} records")


# ============================================================
# 5. LOAD RAINFALL / ML DATASET
# ============================================================

ml_df = pd.read_csv(ML_DATASET_PATH)

print(f"[OK] ML rainfall dataset loaded: {len(ml_df)} records")


# ============================================================
# 6. CHECK REQUIRED COLUMNS
# ============================================================

required_risk_columns = [
    "Date",
    "District",
    "Risk_Probability",
    "Risk_Category",
]

required_rainfall_columns = [
    "Date",
    "District",
    "Rainfall_1d",
    "Rainfall_3d",
    "Rainfall_7d",
    "Rainfall_30d",
]


missing_risk = [
    col for col in required_risk_columns
    if col not in risk_df.columns
]

missing_rainfall = [
    col for col in required_rainfall_columns
    if col not in ml_df.columns
]

if missing_risk:
    raise ValueError(
        f"Missing risk columns: {missing_risk}"
    )

if missing_rainfall:
    raise ValueError(
        f"Missing rainfall columns: {missing_rainfall}"
    )

print("[OK] Required columns verified")


# ============================================================
# 7. LOAD RAG MODEL + DATA
# ============================================================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

embeddings = np.load(
    EMBEDDINGS_PATH,
    allow_pickle=True
)

chunks = np.load(
    CHUNKS_PATH,
    allow_pickle=True
)

print(f"[OK] RAG embeddings loaded: {embeddings.shape}")
print(f"[OK] RAG chunks loaded: {len(chunks)}")


# ============================================================
# 8. RAG RETRIEVAL
# ============================================================

def retrieve_guidance(question, top_k=3):

    question_embedding = embedding_model.encode(
        question,
        normalize_embeddings=True
    )

    scores = embeddings @ question_embedding

    top_indices = np.argsort(scores)[::-1][:top_k]

    retrieved = []

    for index in top_indices:

        chunk = chunks[index]

        if isinstance(chunk, dict):
            source = chunk.get(
                "source",
                "Unknown"
            )
            text = chunk.get(
                "text",
                ""
            )
        else:
            source = "flood_preparedness.txt"
            text = str(chunk)

        retrieved.append({
            "source": source,
            "text": text,
            "score": float(scores[index])
        })

    return retrieved


# ============================================================
# 9. GET RISK + RAINFALL INFORMATION
# ============================================================

def get_risk_context(district, date):

    risk_result = risk_df[
        (risk_df["District"].str.lower() == district.lower()) &
        (risk_df["Date"].astype(str) == str(date))
    ]

    rainfall_result = ml_df[
        (ml_df["District"].str.lower() == district.lower()) &
        (ml_df["Date"].astype(str) == str(date))
    ]

    if risk_result.empty:
        return None

    if rainfall_result.empty:
        return None

    risk_row = risk_result.iloc[0]
    rainfall_row = rainfall_result.iloc[0]

    return {
        "district": risk_row["District"],
        "date": risk_row["Date"],

        "risk_probability": float(
            risk_row["Risk_Probability"]
        ),

        "risk_category": risk_row["Risk_Category"],

        "rainfall_1d": float(
            rainfall_row["Rainfall_1d"]
        ),

        "rainfall_3d": float(
            rainfall_row["Rainfall_3d"]
        ),

        "rainfall_7d": float(
            rainfall_row["Rainfall_7d"]
        ),

        "rainfall_30d": float(
            rainfall_row["Rainfall_30d"]
        ),

        "explanation": str(
            risk_row.get(
                "Risk_Explanation_Text",
                "No additional rainfall explanation available."
            )
        )
    }


# ============================================================
# 10. BUILD CONTEXT
# ============================================================

def build_context(
    question,
    district=None,
    date=None
):

    retrieved = retrieve_guidance(
        question,
        top_k=3
    )

    context_parts = []

    # --------------------------------------------------------
    # Risk information
    # --------------------------------------------------------

    if district and date:

        risk = get_risk_context(
            district,
            date
        )

        if risk:

            risk_text = f"""
ĀŚRAYA MODEL-DERIVED RISK CONTEXT

District: {risk["district"]}
Date: {risk["date"]}

Risk category: {risk["risk_category"]}
Risk score: {risk["risk_probability"]:.3f}

Rainfall indicators:
- 1-day rainfall: {risk["rainfall_1d"]:.1f} mm
- 3-day rainfall: {risk["rainfall_3d"]:.1f} mm
- 7-day rainfall: {risk["rainfall_7d"]:.1f} mm
- 30-day rainfall: {risk["rainfall_30d"]:.1f} mm

Rainfall context:
{risk["explanation"]}

IMPORTANT:
This is a model-derived historical risk assessment.
It is NOT an official flood warning or evacuation order.
"""

            context_parts.append(
                risk_text
            )

    # --------------------------------------------------------
    # RAG information
    # --------------------------------------------------------

    guidance_text = """
TRUSTED FLOOD PREPAREDNESS INFORMATION
"""

    for item in retrieved:

        guidance_text += (
            f"\nSource: {item['source']}\n"
            f"{item['text']}\n"
        )

    context_parts.append(
        guidance_text
    )

    return "\n".join(
        context_parts
    )


# ============================================================
# 11. GENERATE AI GUIDANCE
# ============================================================

def generate_guidance(
    question,
    district=None,
    date=None
):

    context = build_context(
        question,
        district,
        date
    )

    system_prompt = """
You are Āśraya AI, an AI-powered community disaster
resilience assistant.

Your job is to provide clear, practical and responsible
flood-preparedness guidance.

Use the supplied context as your evidence.

IMPORTANT RULES:

1. Do not invent weather, rainfall, flood events,
   evacuation orders or emergency information.

2. The ML risk score is MODEL-DERIVED.
   Do not present it as an official government warning.

3. Do not issue official evacuation orders.

4. Tell users to follow instructions from relevant
   local authorities and emergency services.

5. If the risk category is HIGH or VERY HIGH, explain
   that the assessment indicates elevated model-derived
   risk and provide appropriate preparedness steps.

6. Use the retrieved preparedness information when
   answering safety questions.

7. If the supplied context does not contain enough
   information, say so rather than making up an answer.

8. Keep the response concise and easy to understand.

9. Prioritize practical actions the user can take.

10. Do not present historical model results as a
    real-time official warning.
"""

    user_prompt = f"""
USER QUESTION:

{question}

ĀŚRAYA CONTEXT:

{context}

Using the supplied context, provide a practical,
clear and safe response to the user.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
    )

    return response.choices[0].message.content


# ============================================================
# 12. TEST 1 — GENERAL QUESTION
# ============================================================

print("\n" + "=" * 70)
print("TEST 1 — GENERAL FLOOD PREPAREDNESS")
print("=" * 70)

question_1 = (
    "What should I do to prepare if flooding may happen tomorrow?"
)

answer_1 = generate_guidance(
    question_1
)

print("\nAI RESPONSE:\n")
print(answer_1)


# ============================================================
# 13. TEST 2 — RISK-AWARE QUESTION
# ============================================================

print("\n" + "=" * 70)
print("TEST 2 — RISK-AWARE GUIDANCE")
print("=" * 70)

question_2 = (
    "The flood risk assessment for my area is very high. "
    "What should I do to prepare?"
)

answer_2 = generate_guidance(
    question_2,
    district="Kottayam",
    date="2021-10-11"
)

print("\nAI RESPONSE:\n")
print(answer_2)


# ============================================================
# 14. FINAL STATUS
# ============================================================

print("\n" + "=" * 70)
print("ĀŚRAYA AI GUIDANCE ENGINE")
print("=" * 70)

print("[OK] Risk assessment connected")
print("[OK] Rainfall features connected")
print("[OK] RAG retrieval connected")
print("[OK] OpenRouter LLM connected")
print("[OK] Context-aware guidance generated")

print("\n[SUCCESS] Āśraya AI guidance pipeline is working.")

print("=" * 70)