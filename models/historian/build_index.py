import json
import pickle
from pathlib import Path

import faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

KNOWLEDGE_BASE = (
    ROOT
    / "data"
    / "knowledge_base"
    / "historian_knowledge.jsonl"
)

INDEX_DIR = (
    ROOT
    / "models"
    / "historian"
    / "index"
)

INDEX_FILE = INDEX_DIR / "historian.faiss"
METADATA_FILE = INDEX_DIR / "metadata.pkl"
VECTORIZER_FILE = INDEX_DIR / "vectorizer.pkl"


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

def load_knowledge_base():

    records = []

    with open(
        KNOWLEDGE_BASE,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            records.append(
                json.loads(line)
            )

    return records


# ============================================================
# BUILD DOCUMENT TEXT
# ============================================================

def build_document_text(record):

    return (
        f"Topic: {record.get('topic', '')}. "
        f"Title: {record.get('title', '')}. "
        f"{record.get('text', '')}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("M4 HISTORIAN — BUILDING FAISS INDEX")
    print("=" * 60)

    INDEX_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Load records
    # --------------------------------------------------------

    records = load_knowledge_base()

    print(
        f"Knowledge-base records: {len(records)}"
    )

    if not records:
        raise ValueError(
            "Knowledge base is empty."
        )

    # --------------------------------------------------------
    # Prepare documents
    # --------------------------------------------------------

    documents = [
        build_document_text(record)
        for record in records
    ]

    # --------------------------------------------------------
    # TF-IDF vectorization
    # --------------------------------------------------------

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
        norm="l2"
    )

    vectors = vectorizer.fit_transform(
        documents
    )

    vectors = vectors.toarray().astype(
        np.float32
    )

    print(
        f"Vocabulary size: {len(vectorizer.vocabulary_)}"
    )

    print(
        f"Vector shape: {vectors.shape}"
    )

    # --------------------------------------------------------
    # FAISS index
    # --------------------------------------------------------
    #
    # Because vectors are L2-normalized,
    # inner product is equivalent to cosine similarity.
    # --------------------------------------------------------

    dimension = vectors.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(vectors)

    print(
        f"FAISS vectors indexed: {index.ntotal}"
    )

    # --------------------------------------------------------
    # Save FAISS index
    # --------------------------------------------------------

    faiss.write_index(
        index,
        str(INDEX_FILE)
    )

    # --------------------------------------------------------
    # Save vectorizer
    # --------------------------------------------------------

    with open(
        VECTORIZER_FILE,
        "wb"
    ) as f:

        pickle.dump(
            vectorizer,
            f
        )

    # --------------------------------------------------------
    # Save metadata
    # --------------------------------------------------------

    metadata = []

    for record in records:

        metadata.append({
            "id": record.get("id"),
            "topic": record.get("topic"),
            "title": record.get("title"),
            "text": record.get("text"),
            "source": record.get("source"),
            "url": record.get("url"),
        })

    with open(
        METADATA_FILE,
        "wb"
    ) as f:

        pickle.dump(
            metadata,
            f
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("Index successfully created.")
    print()
    print(
        f"FAISS index:  {INDEX_FILE}"
    )
    print(
        f"Vectorizer:   {VECTORIZER_FILE}"
    )
    print(
        f"Metadata:     {METADATA_FILE}"
    )

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()