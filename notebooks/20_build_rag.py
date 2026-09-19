from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

KNOWLEDGE_BASE_DIR = Path("data/knowledge_base")

OUTPUT_DIR = Path("models/rag")
EMBEDDINGS_PATH = OUTPUT_DIR / "embeddings.npy"
CHUNKS_PATH = OUTPUT_DIR / "chunks.npy"


# ============================================================
# CONFIGURATION
# ============================================================

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Maximum approximate character length for a chunk.
MAX_CHUNK_SIZE = 800

# Number of results to retrieve during testing.
TOP_K = 3


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

def load_documents():
    """
    Load all text files from the knowledge base directory.
    """

    documents = []

    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.txt")):

        text = path.read_text(
            encoding="utf-8"
        ).strip()

        if not text:
            continue

        documents.append({
            "source": path.name,
            "text": text
        })

    return documents


# ============================================================
# CREATE MEANINGFUL CHUNKS
# ============================================================

def create_chunks(text):
    """
    Create paragraph/section-based chunks.

    The previous version used fixed character windows,
    which could split sentences and instructions in the
    middle. This version tries to preserve meaningful
    preparedness instructions.
    """

    # Normalize line endings.
    text = text.replace("\r\n", "\n")

    # Split primarily on blank lines.
    sections = text.split("\n\n")

    chunks = []

    for section in sections:

        section = section.strip()

        if not section:
            continue

        # ----------------------------------------------------
        # Keep normal-sized sections intact.
        # ----------------------------------------------------

        if len(section) <= MAX_CHUNK_SIZE:

            chunks.append(section)

            continue

        # ----------------------------------------------------
        # If a section is too large, split it by sentences.
        # ----------------------------------------------------

        sentences = section.replace(
            "\n",
            " "
        ).split(". ")

        current_chunk = ""

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            # Restore punctuation if necessary.
            if not sentence.endswith("."):
                sentence += "."

            if current_chunk:

                candidate = (
                    current_chunk
                    + " "
                    + sentence
                )

            else:

                candidate = sentence

            # ------------------------------------------------
            # Add sentence if it fits.
            # ------------------------------------------------

            if len(candidate) <= MAX_CHUNK_SIZE:

                current_chunk = candidate

            else:

                if current_chunk:

                    chunks.append(
                        current_chunk.strip()
                    )

                current_chunk = sentence

        # Add remaining text.
        if current_chunk:

            chunks.append(
                current_chunk.strip()
            )

    return chunks


# ============================================================
# BUILD VECTOR STORE
# ============================================================

def build_vector_store():

    print("=" * 70)
    print("BUILDING RAG VECTOR STORE")
    print("=" * 70)

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Load documents
    # --------------------------------------------------------

    print("\nLoading knowledge base...")

    documents = load_documents()

    if not documents:

        raise FileNotFoundError(
            f"No .txt files found in {KNOWLEDGE_BASE_DIR}"
        )

    print(
        f"Documents found: {len(documents)}"
    )

    # --------------------------------------------------------
    # Create chunks
    # --------------------------------------------------------

    all_chunks = []

    for document in documents:

        source = document["source"]
        text = document["text"]

        chunks = create_chunks(text)

        print(
            f"\n{source}: {len(chunks)} chunks"
        )

        for chunk in chunks:

            all_chunks.append({
                "source": source,
                "text": chunk
            })

    print(
        f"\nTotal chunks: {len(all_chunks)}"
    )

    # --------------------------------------------------------
    # Display chunks
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("CREATED CHUNKS")
    print("=" * 70)

    for i, chunk in enumerate(all_chunks):

        print(
            f"\n[Chunk {i + 1}] "
            f"Source: {chunk['source']}"
        )

        print("-" * 70)

        print(
            chunk["text"]
        )

    # --------------------------------------------------------
    # Load embedding model
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("LOADING EMBEDDING MODEL")
    print("=" * 70)

    print(
        f"Model: {EMBEDDING_MODEL}"
    )

    model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    print("Embedding model loaded.")

    # --------------------------------------------------------
    # Extract text for embedding
    # --------------------------------------------------------

    texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    # --------------------------------------------------------
    # Generate embeddings
    # --------------------------------------------------------

    print("\nGenerating embeddings...")

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32
    )

    print(
        "Embedding shape:",
        embeddings.shape
    )

    # --------------------------------------------------------
    # Save embeddings
    # --------------------------------------------------------

    np.save(
        EMBEDDINGS_PATH,
        embeddings
    )

    # --------------------------------------------------------
    # Save chunks
    #
    # We preserve source + text as dictionaries because
    # the guidance engine needs both.
    # --------------------------------------------------------

    chunks_array = np.array(
        all_chunks,
        dtype=object
    )

    np.save(
        CHUNKS_PATH,
        chunks_array
    )

    print("\n" + "=" * 70)
    print("VECTOR STORE SAVED")
    print("=" * 70)

    print(
        "Embeddings:",
        EMBEDDINGS_PATH
    )

    print(
        "Chunks:",
        CHUNKS_PATH
    )


# ============================================================
# TEST RETRIEVAL
# ============================================================

def test_retrieval():

    print("\n" + "=" * 70)
    print("TESTING RAG RETRIEVAL")
    print("=" * 70)

    # --------------------------------------------------------
    # Load vector store
    # --------------------------------------------------------

    embeddings = np.load(
        EMBEDDINGS_PATH
    )

    chunks = np.load(
        CHUNKS_PATH,
        allow_pickle=True
    )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    # --------------------------------------------------------
    # Test questions
    # --------------------------------------------------------

    questions = [
        "What should I keep in an emergency kit?",
        "Is it safe to walk through floodwater?",
        "What should I do before a flood?",
        "What should I do after a flood?"
    ]

    for question in questions:

        print("\n" + "-" * 70)
        print(
            f"QUESTION: {question}"
        )
        print("-" * 70)

        # ----------------------------------------------------
        # Encode question
        # ----------------------------------------------------

        query_embedding = model.encode(
            [question],
            normalize_embeddings=True
        )[0]

        # ----------------------------------------------------
        # Calculate cosine similarity.
        #
        # Because both query and document embeddings are
        # normalized, dot product = cosine similarity.
        # ----------------------------------------------------

        scores = embeddings @ query_embedding

        top_indices = np.argsort(
            scores
        )[::-1][:TOP_K]

        # ----------------------------------------------------
        # Display results
        # ----------------------------------------------------

        for rank, index in enumerate(
            top_indices,
            start=1
        ):

            chunk = chunks[index]

            # Handle dictionary format.
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

            print(
                f"\nResult {rank}"
            )

            print(
                f"Similarity: {scores[index]:.4f}"
            )

            print(
                f"Source: {source}"
            )

            print(
                f"Text: {text}"
            )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    build_vector_store()

    test_retrieval()

    print("\n" + "=" * 70)
    print("RAG BUILD + TEST COMPLETE")
    print("=" * 70)