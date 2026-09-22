import pickle
from pathlib import Path

import faiss
import numpy as np


# ============================================================
# M4 HISTORIAN
# Evidence Retrieval Engine
# ============================================================


class Historian:

    def __init__(self):

        # ----------------------------------------------------
        # Project paths
        # ----------------------------------------------------

        self.root = Path(__file__).resolve().parents[2]

        self.index_dir = (
            self.root
            / "models"
            / "historian"
            / "index"
        )

        self.index_file = (
            self.index_dir
            / "historian.faiss"
        )

        self.vectorizer_file = (
            self.index_dir
            / "vectorizer.pkl"
        )

        self.metadata_file = (
            self.index_dir
            / "metadata.pkl"
        )

        # ----------------------------------------------------
        # Load FAISS index
        # ----------------------------------------------------

        if not self.index_file.exists():

            raise FileNotFoundError(
                f"FAISS index not found:\n"
                f"{self.index_file}"
            )

        self.index = faiss.read_index(
            str(self.index_file)
        )

        # ----------------------------------------------------
        # Load TF-IDF vectorizer
        # ----------------------------------------------------

        if not self.vectorizer_file.exists():

            raise FileNotFoundError(
                f"Vectorizer not found:\n"
                f"{self.vectorizer_file}"
            )

        with open(
            self.vectorizer_file,
            "rb"
        ) as f:

            self.vectorizer = pickle.load(f)

        # ----------------------------------------------------
        # Load metadata
        # ----------------------------------------------------

        if not self.metadata_file.exists():

            raise FileNotFoundError(
                f"Metadata not found:\n"
                f"{self.metadata_file}"
            )

        with open(
            self.metadata_file,
            "rb"
        ) as f:

            self.metadata = pickle.load(f)

        # ----------------------------------------------------
        # Sanity check
        # ----------------------------------------------------

        if self.index.ntotal != len(
            self.metadata
        ):

            raise ValueError(
                "FAISS index and metadata "
                "have different sizes."
            )

    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query,
        top_k=5,
        min_score=0.0
    ):

        """
        Retrieve the most relevant historical
        evidence for a communication query.

        Parameters
        ----------
        query : str
            User/message/query text.

        top_k : int
            Maximum number of results.

        min_score : float
            Minimum similarity score.

        Returns
        -------
        list
            Ranked evidence records.
        """

        # ----------------------------------------------------
        # Validate query
        # ----------------------------------------------------

        if not isinstance(
            query,
            str
        ):

            raise TypeError(
                "Query must be a string."
            )

        query = query.strip()

        if not query:

            return []

        # ----------------------------------------------------
        # Convert query → TF-IDF vector
        # ----------------------------------------------------

        query_vector = (
            self.vectorizer
            .transform([query])
            .toarray()
            .astype(np.float32)
        )

        # ----------------------------------------------------
        # FAISS similarity search
        # ----------------------------------------------------

        search_k = min(
            top_k,
            self.index.ntotal
        )

        scores, indices = (
            self.index.search(
                query_vector,
                search_k
            )
        )

        # ----------------------------------------------------
        # Build results
        # ----------------------------------------------------

        results = []

        for score, index_id in zip(
            scores[0],
            indices[0]
        ):

            if index_id < 0:
                continue

            score = float(score)

            if score < min_score:
                continue

            record = dict(
                self.metadata[index_id]
            )

            record["score"] = round(
                score,
                4
            )

            record["rank"] = (
                len(results) + 1
            )

            results.append(
                record
            )

        return results

    # ========================================================
    # FORMAT EVIDENCE
    # ========================================================

    def format_results(
        self,
        results
    ):

        """
        Convert retrieved records into a clean
        structure for the Synthesizer.
        """

        formatted = []

        for result in results:

            formatted.append({
                "rank": result["rank"],
                "topic": result["topic"],
                "title": result["title"],
                "evidence": result["text"],
                "source": result["source"],
                "url": result["url"],
                "similarity": result["score"],
            })

        return formatted

    # ========================================================
    # ANALYZE / RETRIEVE
    # ========================================================

    def analyze(
        self,
        text,
        top_k=5
    ):

        """
        Main Historian interface.

        The Historian does NOT decide whether a claim
        is true or false. It retrieves relevant evidence
        that can be passed to the Synthesizer.
        """

        results = self.search(
            query=text,
            top_k=top_k
        )

        evidence = self.format_results(
            results
        )

        return {
            "agent": "historian",
            "query": text,
            "retrieved_count": len(
                evidence
            ),
            "evidence": evidence,
        }


# ============================================================
# MANUAL TEST
# ============================================================

if __name__ == "__main__":

    historian = Historian()

    print("=" * 60)
    print("M4 HISTORIAN RETRIEVAL TEST")
    print("=" * 60)

    test_queries = [

        "The application crashed once, "
        "so it is completely unusable.",

        "The speaker avoids giving a direct opinion.",

        "The conclusion is not sufficiently "
        "supported by the evidence.",

        "The argument depends on an unstated assumption.",

        "The speaker leaves information unsaid "
        "during the conversation.",
    ]

    for query in test_queries:

        print()
        print("-" * 60)
        print("QUERY:")
        print(query)
        print("-" * 60)

        output = historian.analyze(
            query,
            top_k=3
        )

        print(
            f"Retrieved: "
            f"{output['retrieved_count']}"
        )

        for evidence in output[
            "evidence"
        ]:

            print()
            print(
                f"{evidence['rank']}. "
                f"{evidence['title']}"
            )

            print(
                f"   Topic: "
                f"{evidence['topic']}"
            )

            print(
                f"   Similarity: "
                f"{evidence['similarity']:.4f}"
            )

            print(
                f"   Source: "
                f"{evidence['source']}"
            )

            print(
                f"   Evidence: "
                f"{evidence['evidence']}"
            )

            print(
                f"   URL: "
                f"{evidence['url']}"
            )

    print()
    print("=" * 60)
    print("M4 HISTORIAN TEST COMPLETE")
    print("=" * 60)