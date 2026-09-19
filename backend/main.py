from pathlib import Path
import os

import numpy as np
import pandas as pd

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from sentence_transformers import SentenceTransformer


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RISK_PATH = PROJECT_ROOT / "models" / "ai_guidance_context.csv"
ML_DATASET_PATH = PROJECT_ROOT / "data" / "kerala_ml_dataset.csv"

EMBEDDINGS_PATH = PROJECT_ROOT / "models" / "rag" / "embeddings.npy"
CHUNKS_PATH = PROJECT_ROOT / "models" / "rag" / "chunks.npy"


# ============================================================
# 2. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENROUTER_API_KEY was not found in the .env file."
    )


# ============================================================
# 3. OPENROUTER CLIENT
# ============================================================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

MODEL = "openrouter/free"


# ============================================================
# 4. LOAD DATA
# ============================================================

print("[INFO] Loading Āśraya data...")

risk_df = pd.read_csv(RISK_PATH)

ml_df = pd.read_csv(ML_DATASET_PATH)

print(f"[OK] Risk records: {len(risk_df)}")
print(f"[OK] ML records: {len(ml_df)}")


# ============================================================
# 5. LOAD RAG MODEL
# ============================================================

print("[INFO] Loading RAG embedding model...")

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

print(f"[OK] RAG embeddings: {embeddings.shape}")
print(f"[OK] RAG chunks: {len(chunks)}")


# ============================================================
# 6. FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Āśraya AI API",
    description="Flood risk assessment and AI preparedness guidance API",
    version="1.0.0"
)


# ============================================================
# 7. CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 8. REQUEST MODELS
# ============================================================

class GuidanceRequest(BaseModel):
    question: str
    district: str | None = None
    date: str | None = None


# ============================================================
# 9. HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "name": "Āśraya AI",
        "status": "running",
        "message": "Flood risk and AI guidance API is active."
    }


# ============================================================
# 10. GET AVAILABLE DISTRICTS
# ============================================================

@app.get("/districts")
def get_districts():

    districts = sorted(
        risk_df["District"]
        .dropna()
        .unique()
        .tolist()
    )

    return {
        "districts": districts
    }


# ============================================================
# 11. GET RISK ASSESSMENT
# ============================================================

@app.get("/risk")
def get_risk(
    district: str,
    date: str
):

    risk_result = risk_df[
        (risk_df["District"].str.lower() == district.lower()) &
        (risk_df["Date"].astype(str) == str(date))
    ]

    rainfall_result = ml_df[
        (ml_df["District"].str.lower() == district.lower()) &
        (ml_df["Date"].astype(str) == str(date))
    ]

    if risk_result.empty:
        raise HTTPException(
            status_code=404,
            detail="Risk assessment not found for this district and date."
        )

    if rainfall_result.empty:
        raise HTTPException(
            status_code=404,
            detail="Rainfall information not found for this district and date."
        )

    risk_row = risk_result.iloc[0]
    rainfall_row = rainfall_result.iloc[0]

    return {
        "district": risk_row["District"],
        "date": risk_row["Date"],

        "risk_category": risk_row["Risk_Category"],

        "risk_score": round(
            float(risk_row["Risk_Probability"]),
            3
        ),

        "rainfall": {
            "1_day_mm": round(
                float(rainfall_row["Rainfall_1d"]),
                1
            ),

            "3_day_mm": round(
                float(rainfall_row["Rainfall_3d"]),
                1
            ),

            "7_day_mm": round(
                float(rainfall_row["Rainfall_7d"]),
                1
            ),

            "30_day_mm": round(
                float(rainfall_row["Rainfall_30d"]),
                1
            )
        },

        "explanation": str(
            risk_row.get(
                "Risk_Explanation_Text",
                ""
            )
        ),

        "disclaimer": (
            "This is a model-derived historical risk assessment, "
            "not an official flood warning or evacuation order."
        )
    }


# ============================================================
# 12. RAG RETRIEVAL
# ============================================================

def retrieve_guidance(
    question: str,
    top_k: int = 3
):

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
# 13. BUILD RISK CONTEXT
# ============================================================

def get_risk_context(
    district: str | None,
    date: str | None
):

    if not district or not date:
        return ""

    try:

        risk_response = get_risk(
            district,
            date
        )

    except HTTPException:

        return ""

    rainfall = risk_response["rainfall"]

    return f"""
ĀŚRAYA MODEL-DERIVED RISK CONTEXT

District: {risk_response["district"]}
Date: {risk_response["date"]}

Risk category: {risk_response["risk_category"]}
Model-derived risk score: {risk_response["risk_score"]}

Rainfall indicators:
- 1-day rainfall: {rainfall["1_day_mm"]} mm
- 3-day rainfall: {rainfall["3_day_mm"]} mm
- 7-day rainfall: {rainfall["7_day_mm"]} mm
- 30-day rainfall: {rainfall["30_day_mm"]} mm

Rainfall context:
{risk_response["explanation"]}

IMPORTANT:
This is a model-derived historical assessment.
It is not an official government flood warning
or evacuation order.
"""


# ============================================================
# 14. GENERATE AI GUIDANCE
# ============================================================

def generate_guidance(
    question: str,
    district: str | None = None,
    date: str | None = None
):

    retrieved = retrieve_guidance(
        question,
        top_k=3
    )

    risk_context = get_risk_context(
        district,
        date
    )

    rag_context = "\nTRUSTED FLOOD PREPAREDNESS INFORMATION\n"

    for item in retrieved:

        rag_context += (
            f"\nSource: {item['source']}\n"
            f"{item['text']}\n"
        )

    context = risk_context + rag_context

    system_prompt = """
You are Āśraya AI, an AI-powered community disaster
resilience assistant.

Your purpose is to help people understand flood risk
assessments and prepare safely.

Use the supplied context as your evidence.

RULES:

1. Do not invent weather, rainfall, flood events,
   evacuation orders, shelters, or emergency information.

2. The risk score is MODEL-DERIVED and based on
   historical data. Never present it as an official
   government warning.

3. Do not issue official evacuation orders.

4. Always prioritize instructions from local authorities
   and emergency services.

5. When risk is HIGH or VERY HIGH, recommend practical
   preparedness actions based on the trusted information.

6. Use the RAG information as the source for safety advice.

7. If the context does not contain enough information,
   clearly say that the information is unavailable.

8. Keep responses concise and easy to understand.

9. Give practical actions before lengthy explanations.

10. Do not present historical results as real-time
    observations.

11. Do not provide unsupported medical advice.
"""

    user_prompt = f"""
USER QUESTION:

{question}

ĀŚRAYA CONTEXT:

{context}

Provide a clear, practical and safe response.
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
# 15. GUIDANCE API ENDPOINT
# ============================================================

@app.post("/guidance")
def guidance(
    request: GuidanceRequest
):

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    answer = generate_guidance(
        question=request.question,
        district=request.district,
        date=request.date
    )

    return {
        "question": request.question,
        "district": request.district,
        "date": request.date,
        "answer": answer
    }


# ============================================================
# 16. SERVER STARTUP MESSAGE
# ============================================================

@app.on_event("startup")
def startup_event():

    print("\n" + "=" * 60)
    print("ĀŚRAYA AI BACKEND")
    print("=" * 60)

    print("[OK] FastAPI started")
    print("[OK] Risk data loaded")
    print("[OK] Rainfall data loaded")
    print("[OK] RAG system loaded")
    print("[OK] OpenRouter configured")

    print("\nAvailable endpoints:")
    print("GET  /")
    print("GET  /districts")
    print("GET  /risk")
    print("POST /guidance")

    print("=" * 60 + "\n")