from services.azure_explainer import AzureExplainer


def main():
    dossier = {
        "surface_statement": "I'm fine with whatever you decide.",
        "possible_subtext": (
            "The message leaves the speaker's actual preference unspecified."
        ),
        "confidence": 0.72,
        "strategically_missing": [
            "Explicit preference",
            "Conditions or boundaries",
            "Reason for delegating the decision",
        ],
        "agent_findings": {
            "archaeologist": {
                "hedging": 0.81,
                "missing_commitment": 0.74,
            },
            "psychologist": {
                "affect_gap": 0.61,
            },
            "logician": {
                "unstated_assumption": 0.48,
            },
        },
        "evidence": [
            {
                "topic": "conversational implicature",
                "similarity": 0.82,
            }
        ],
    }

    explainer = AzureExplainer()

    result = explainer.explain(dossier)

    print("\n" + "=" * 70)
    print("L.I.M.I.N.A.L. — GPT-6 ASTRA EXPLANATION")
    print("=" * 70)
    print(result)
    print("=" * 70)


if __name__ == "__main__":
    main()