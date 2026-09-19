from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

RISK_PATH = Path("models/ai_guidance_context.csv")

EMBEDDINGS_PATH = Path(
    "models/rag/embeddings.npy"
)

CHUNKS_PATH = Path(
    "models/rag/chunks.npy"
)


# ============================================================
# CONFIGURATION
# ============================================================

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

DEFAULT_TOP_K = 3


# ============================================================
# LOAD RISK DATA
# ============================================================

print("Loading AI risk context...")

risk_df = pd.read_csv(
    RISK_PATH
)

risk_df["Date"] = pd.to_datetime(
    risk_df["Date"],
    errors="coerce"
)

risk_df["District"] = (
    risk_df["District"]
    .astype(str)
    .str.strip()
)

print(
    "Risk records:",
    len(risk_df)
)


# ============================================================
# LOAD RAG VECTOR STORE
# ============================================================

print("\nLoading RAG vector store...")

embeddings = np.load(
    EMBEDDINGS_PATH
)

chunks = np.load(
    CHUNKS_PATH,
    allow_pickle=True
)

print(
    "Embeddings shape:",
    embeddings.shape
)

print(
    "Chunks:",
    len(chunks)
)


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("\nLoading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)

print(
    "Embedding model loaded."
)


# ============================================================
# RAG RETRIEVAL
# ============================================================

def retrieve_guidance(
    question,
    top_k=DEFAULT_TOP_K
):
    """
    Retrieve the most relevant preparedness
    passages for a user question.
    """

    query_embedding = embedding_model.encode(
        [question],
        normalize_embeddings=True
    )[0]

    # Because embeddings are normalized,
    # dot product is equivalent to cosine similarity.
    scores = embeddings @ query_embedding

    top_indices = np.argsort(
        scores
    )[::-1][:top_k]

    results = []

    for index in top_indices:

        chunk = chunks[index]

        # ----------------------------------------------------
        # New RAG format:
        # {
        #     "source": "...",
        #     "text": "..."
        # }
        # ----------------------------------------------------

        if isinstance(chunk, dict):

            source = chunk.get(
                "source",
                "unknown"
            )

            text = chunk.get(
                "text",
                ""
            )

        else:

            source = "unknown"

            text = str(
                chunk
            )

        results.append(
            {
                "source": source,
                "text": text,
                "score": float(
                    scores[index]
                )
            }
        )

    return results


# ============================================================
# RISK LOOKUP
# ============================================================

def get_risk_context(
    district,
    date
):
    """
    Retrieve the model-derived risk assessment
    for a specific district and date.
    """

    date = pd.to_datetime(
        date
    )

    district = str(
        district
    ).strip()

    matches = risk_df[
        (
            risk_df["District"].str.lower()
            == district.lower()
        )
        &
        (
            risk_df["Date"] == date
        )
    ]

    if matches.empty:

        return None

    row = matches.iloc[0]

    return {
        "district": row["District"],
        "date": str(
            row["Date"].date()
        ),
        "risk_score": float(
            row["Risk_Probability"]
        ),
        "risk_category": row[
            "Risk_Category"
        ],
        "context": row[
            "AI_Risk_Context"
        ]
    }


# ============================================================
# BUILD GUIDANCE CONTEXT
# ============================================================

def build_guidance_context(
    question,
    district=None,
    date=None,
    top_k=DEFAULT_TOP_K
):
    """
    Combine:

    1. User question
    2. Retrieved trusted guidance
    3. Model-derived flood-risk context

    into a clean context package for the
    future LLM layer.
    """

    print(
        "\nRetrieving relevant guidance..."
    )

    # --------------------------------------------------------
    # Retrieve RAG information
    # --------------------------------------------------------

    retrieved = retrieve_guidance(
        question,
        top_k=top_k
    )

    guidance_sections = []

    for i, item in enumerate(
        retrieved,
        start=1
    ):

        guidance_sections.append(
            f"""
[Guidance {i}]
Source: {item['source']}

{item['text']}
""".strip()
        )

    guidance_text = "\n\n".join(
        guidance_sections
    )

    # --------------------------------------------------------
    # Retrieve risk information
    # --------------------------------------------------------

    risk_context = None

    if (
        district is not None
        and date is not None
    ):

        risk_context = get_risk_context(
            district,
            date
        )

    # --------------------------------------------------------
    # Build final context
    # --------------------------------------------------------

    final_context = f"""
USER QUESTION
-------------
{question}

TRUSTED FLOOD PREPAREDNESS INFORMATION
---------------------------------------
{guidance_text}
""".strip()

    if risk_context is not None:

        final_context += f"""

MODEL-DERIVED FLOOD RISK CONTEXT
--------------------------------
District: {risk_context['district']}
Date: {risk_context['date']}
Risk category: {risk_context['risk_category']}
Risk score: {risk_context['risk_score']:.3f}

{risk_context['context']}
""".rstrip()

    else:

        final_context += """

MODEL-DERIVED FLOOD RISK CONTEXT
--------------------------------
No matching district/date risk assessment was found.
""".rstrip()

    return {
        "question": question,
        "retrieved_guidance": retrieved,
        "risk_context": risk_context,
        "final_context": final_context
    }


# ============================================================
# TEST 1
# ============================================================

print("\n" + "=" * 70)
print("TEST 1: GENERAL FLOOD SAFETY QUESTION")
print("=" * 70)

result = build_guidance_context(
    question="Is it safe to walk through floodwater?"
)

print(
    result["final_context"]
)


# ============================================================
# TEST 2
# ============================================================

print("\n" + "=" * 70)
print("TEST 2: QUESTION WITH RISK CONTEXT")
print("=" * 70)

result = build_guidance_context(
    question=(
        "What should I do if flooding is "
        "expected tomorrow?"
    ),
    district="Kottayam",
    date="2021-10-11"
)

print(
    result["final_context"]
)


# ============================================================
# TEST 3
# ============================================================

print("\n" + "=" * 70)
print("TEST 3: HIGH MODEL SCORE WITH LOW RAINFALL")
print("=" * 70)

result = build_guidance_context(
    question="Why is the flood risk high?",
    district="Wayanad",
    date="2021-03-12"
)

print(
    result["final_context"]
)


# ============================================================
# FINAL STATUS
# ============================================================

print("\n" + "=" * 70)
print("AI GUIDANCE CONTEXT ENGINE READY")
print("=" * 70)

print(
    "RAG retrieval: READY"
)

print(
    "Risk context lookup: READY"
)

print(
    "Context assembly: READY"
)

print(
    "LLM generation: NEXT STEP"
)