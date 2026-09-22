import json
import sys
import os

# Make sure the project root is available for imports
PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.services.agent_runner import LIMINALAgentRunner


TEST_CASES = [

    {
        "id": 1,
        "category": "Unstated Preference",
        "text": (
            "I'm fine with whatever you decide. "
            "The current plan should probably work."
        )
    },

    {
        "id": 2,
        "category": "Missing Actor",
        "text": (
            "The report was submitted yesterday, "
            "but nobody mentioned who approved it."
        )
    },

    {
        "id": 3,
        "category": "Hedging",
        "text": (
            "We should probably finish this soon. "
            "I guess the current approach is acceptable."
        )
    },

    {
        "id": 4,
        "category": "False Dilemma",
        "text": (
            "Either we accept this proposal or "
            "the entire project will fail."
        )
    },

    {
        "id": 5,
        "category": "Responsibility Avoidance",
        "text": (
            "The decision was made and the changes were implemented, "
            "but it is unclear who made the final decision."
        )
    },

    {
        "id": 6,
        "category": "Explicit Preference",
        "text": (
            "I strongly prefer option A because it reduces "
            "the project cost and development time."
        )
    },

    {
        "id": 7,
        "category": "Possible Emotional Incongruence",
        "text": (
            "Everything is going perfectly. "
            "I just don't think we need to discuss it anymore."
        )
    },

    {
        "id": 8,
        "category": "Unsupported Conclusion",
        "text": (
            "Everyone uses this system, so it must be "
            "the most reliable solution."
        )
    },

    {
        "id": 9,
        "category": "Clear Statement",
        "text": (
            "I disagree with the proposal. "
            "I recommend choosing option B because it is cheaper."
        )
    },

    {
        "id": 10,
        "category": "Vague Reference",
        "text": (
            "They said it would be handled soon, "
            "but they never explained what 'it' refers to."
        )
    }
]


def print_separator():
    print("=" * 80)


def main():

    print_separator()
    print("L.I.M.I.N.A.L. FULL PIPELINE EVALUATION")
    print_separator()

    print()
    print("Initializing all five components...")
    print()

    runner = LIMINALAgentRunner()

    print()
    print_separator()
    print(f"Running {len(TEST_CASES)} evaluation cases")
    print_separator()

    results = []

    for case in TEST_CASES:

        print()
        print("=" * 80)
        print(
            f"CASE {case['id']} — "
            f"{case['category']}"
        )
        print("=" * 80)

        print()
        print("INPUT:")
        print(case["text"])

        try:

            result = runner.analyze(
                case["text"]
            )

            dossier = result["dossier"]

            # The current agent_runner stores the actual
            # agent findings and Historian evidence inside
            # the generated dossier.
            agent_findings = dossier.get(
                "agent_findings",
                {}
            )

            archaeologist = agent_findings.get(
                "archaeologist",
                []
            )

            psychologist = agent_findings.get(
                "psychologist",
                []
            )

            logician = agent_findings.get(
                "logician",
                []
            )

            evidence = dossier.get(
                "evidence",
                []
            )

            print()
            print("M1 Archaeologist findings:")
            print(
                len(archaeologist)
            )

            print()
            print("M2 Psychologist findings:")
            print(
                len(psychologist)
            )

            print()
            print("M3 Logician findings:")
            print(
                len(logician)
            )

            print()
            print("M4 Historian evidence:")
            print(
                len(evidence)
            )

            print()
            print("M5 Prediction:")
            print(
                dossier.get(
                    "primary_pattern",
                    "UNKNOWN"
                )
            )

            print()
            print("M5 Confidence:")
            print(
                dossier.get(
                    "confidence",
                    "UNKNOWN"
                )
            )

            print()
            print("Possible subtext:")
            print(
                dossier.get(
                    "possible_subtext",
                    ""
                )
            )

            results.append(
                {
                    "id": case["id"],
                    "category": case["category"],
                    "input": case["text"],
                    "m1_findings": archaeologist,
                    "m2_findings": psychologist,
                    "m3_findings": logician,
                    "m4_evidence_count": len(evidence),
                    "prediction": dossier.get(
                        "primary_pattern"
                    ),
                    "confidence": dossier.get(
                        "confidence"
                    ),
                    "possible_subtext": dossier.get(
                        "possible_subtext"
                    ),
                    "strategically_missing":
                        dossier.get(
                            "strategically_missing",
                            []
                        )
                }
            )

        except Exception as error:

            print()
            print("ERROR:")
            print(
                type(error).__name__,
                str(error)
            )

            results.append(
                {
                    "id": case["id"],
                    "category": case["category"],
                    "input": case["text"],
                    "error": str(error)
                }
            )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()
    print()
    print_separator()
    print("EVALUATION SUMMARY")
    print_separator()

    successful = [
        item
        for item in results
        if "error" not in item
    ]

    failed = [
        item
        for item in results
        if "error" in item
    ]

    print()
    print(
        f"Successful cases: "
        f"{len(successful)}/{len(TEST_CASES)}"
    )

    print(
        f"Failed cases: "
        f"{len(failed)}/{len(TEST_CASES)}"
    )

    print()
    print(
        f"{'CASE':<6}"
        f"{'CATEGORY':<30}"
        f"{'PREDICTION':<32}"
        f"{'CONF.':<10}"
    )

    print("-" * 80)

    for item in results:

        if "error" in item:

            print(
                f"{item['id']:<6}"
                f"{item['category']:<30}"
                f"{'ERROR':<32}"
            )

        else:

            confidence = item.get(
                "confidence",
                0
            )

            if isinstance(
                confidence,
                (int, float)
            ):
                confidence_text = (
                    f"{confidence:.2f}%"
                )
            else:
                confidence_text = str(
                    confidence
                )

            print(
                f"{item['id']:<6}"
                f"{item['category']:<30}"
                f"{str(item.get('prediction')):<32}"
                f"{confidence_text:<10}"
            )

    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

    output_path = os.path.join(
        PROJECT_ROOT,
        "pipeline_evaluation_results.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print_separator()
    print(
        "Evaluation results saved to:"
    )
    print(output_path)
    print_separator()


if __name__ == "__main__":
    main()
