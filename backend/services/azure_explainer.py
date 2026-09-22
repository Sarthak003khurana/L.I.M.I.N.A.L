import os
import json

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


load_dotenv()


class AzureExplainer:
    """
    Azure AI Foundry explanation layer for L.I.M.I.N.A.L.

    M1-M5 perform the actual structured analysis.
    Azure only converts those structured findings into
    a cautious, human-readable explanation.
    """

    REQUIRED_SECTIONS = [
        "SURFACE MEANING:",
        "POSSIBLE SUBTEXT:",
        "STRATEGICALLY MISSING:",
        "EVIDENCE:",
        "UNCERTAINTY:",
    ]

    def __init__(self):
        self.project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        if not self.project_endpoint:
            raise ValueError("FOUNDRY_PROJECT_ENDPOINT is missing")

        if not self.deployment:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT is missing")

        self.project_client = AIProjectClient(
            endpoint=self.project_endpoint,
            credential=DefaultAzureCredential(),
        )

        self.client = self.project_client.get_openai_client()

    # ============================================================
    # TEXT NORMALIZATION
    # ============================================================

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Normalize text returned by Azure.

        This handles common mojibake artifacts and normalizes
        line endings/whitespace.
        """

        if not text:
            return ""

        replacements = {
            # Common UTF-8 -> Windows-1252 mojibake
            "â€™": "'",
            "â€œ": '"',
            "â€\x9d": '"',
            "â€“": "-",
            "â€”": "-",
            "â€¦": "...",
            "â€¢": "-",
            "Â": "",

            # Correct Unicode punctuation
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u2013": "-",
            "\u2014": "-",
            "\u2026": "...",
            "\u2022": "-",
            "\u00a0": " ",
        }

        for bad, good in replacements.items():
            text = text.replace(bad, good)

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        return "\n".join(
            line.rstrip()
            for line in text.split("\n")
        ).strip()

    @staticmethod
    def _sanitize_output(text: str) -> str:
        """
        Final output sanitization.

        The Azure client itself supports Unicode correctly. However,
        the application can encounter encoding problems later in the
        Windows/PowerShell/API display path.

        Therefore the final explanation is normalized to plain ASCII.
        This prevents characters such as curly quotes and em-dashes
        from becoming mojibake such as 'â€™' or 'â€œ'.
        """

        if not text:
            return ""

        # First normalize known Unicode punctuation.
        replacements = {
            "\u2018": "'",
            "\u2019": "'",
            "\u201a": "'",
            "\u201b": "'",

            "\u201c": '"',
            "\u201d": '"',
            "\u201e": '"',
            "\u201f": '"',

            "\u2013": "-",
            "\u2014": "-",
            "\u2212": "-",

            "\u2026": "...",
            "\u2022": "-",

            "\u00a0": " ",
            "\ufeff": "",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        # Handle common mojibake explicitly.
        mojibake_replacements = {
            "â€™": "'",
            "â€œ": '"',
            "â€\x9d": '"',
            "â€“": "-",
            "â€”": "-",
            "â€¦": "...",
            "â€¢": "-",
            "Â": "",
        }

        for bad, good in mojibake_replacements.items():
            text = text.replace(bad, good)

        # Normalize line endings.
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Remove any remaining non-ASCII characters.
        text = text.encode("ascii", errors="ignore").decode("ascii")

        # Clean trailing whitespace while preserving section structure.
        text = "\n".join(
            line.rstrip()
            for line in text.split("\n")
        ).strip()

        return text

    # ============================================================
    # SAFE VALUE HELPERS
    # ============================================================

    @staticmethod
    def _format_findings(findings) -> str:
        """
        Convert agent findings into a compact readable representation.
        """

        if not findings:
            return "None detected."

        lines = []

        for finding in findings:
            if not isinstance(finding, dict):
                continue

            label = finding.get("label", "UNKNOWN")
            probability = finding.get("probability")

            if probability is None:
                lines.append(f"- {label}")
            else:
                try:
                    percentage = float(probability) * 100
                    lines.append(
                        f"- {label}: {percentage:.2f}%"
                    )
                except (TypeError, ValueError):
                    lines.append(f"- {label}")

        return "\n".join(lines) if lines else "None detected."

    @staticmethod
    def _format_evidence(evidence) -> str:
        """
        Convert Historian retrieval results into clean evidence.

        Similarity values are explicitly identified as retrieval
        similarity, NOT confidence.
        """

        if not evidence:
            return "No retrieved evidence."

        lines = []

        for item in evidence[:5]:
            if not isinstance(item, dict):
                continue

            title = str(item.get("title", "Untitled"))
            topic = str(item.get("topic", "Unknown topic"))
            source = str(item.get("source", "Unknown source"))
            similarity = item.get("similarity")

            lines.append(f"- Topic: {topic}")
            lines.append(f"  Title: {title}")
            lines.append(f"  Source: {source}")

            if similarity is not None:
                try:
                    lines.append(
                        f"  Retrieval similarity: "
                        f"{float(similarity):.4f}"
                    )
                except (TypeError, ValueError):
                    pass

        return "\n".join(lines)

    # ============================================================
    # BUILD CLEAN AZURE PAYLOAD
    # ============================================================

    def _build_explanation_payload(self, dossier: dict) -> str:
        """
        Extract only the information Azure needs.

        Raw nested JSON, URLs, and unnecessary internal fields are
        intentionally excluded.
        """

        surface = dossier.get("surface_statement", "")

        primary_pattern = dossier.get(
            "primary_pattern",
            "UNKNOWN",
        )

        confidence = dossier.get("confidence", 0)

        agent_findings = dossier.get(
            "agent_findings",
            {},
        )

        evidence = dossier.get(
            "evidence",
            [],
        )

        archaeologist = agent_findings.get(
            "archaeologist",
            [],
        )

        psychologist = agent_findings.get(
            "psychologist",
            [],
        )

        logician = agent_findings.get(
            "logician",
            [],
        )

        payload = f"""
INPUT:
{surface}

ARCHAEOLOGIST FINDINGS:
{self._format_findings(archaeologist)}

PSYCHOLOGIST FINDINGS:
{self._format_findings(psychologist)}

LOGICIAN FINDINGS:
{self._format_findings(logician)}

HISTORIAN RETRIEVED EVIDENCE:
{self._format_evidence(evidence)}

SYNTHESIZER PREDICTION:
{primary_pattern}

SYNTHESIZER CONFIDENCE:
{float(confidence):.2f}%

RESPONSIBLE-AI CONSTRAINT:
The result describes observable communication patterns and
possible interpretations. It does not establish private thoughts,
emotions, intentions, motives, or mental states as facts.
"""

        return self._clean_text(payload)

    # ============================================================
    # RESPONSE VALIDATION
    # ============================================================

    def _validate_sections(self, text: str) -> str:
        """
        Ensure the Azure response has the five required sections.
        """

        text = self._clean_text(text)

        if not text:
            return (
                "SURFACE MEANING:\n"
                "No explanation was returned.\n\n"
                "POSSIBLE SUBTEXT:\n"
                "No interpretation was generated.\n\n"
                "STRATEGICALLY MISSING:\n"
                "Not available.\n\n"
                "EVIDENCE:\n"
                "Not available.\n\n"
                "UNCERTAINTY:\n"
                "The explanation layer returned insufficient information."
            )

        missing = [
            section
            for section in self.REQUIRED_SECTIONS
            if section not in text
        ]

        if missing:
            text += "\n\n"

            for section in missing:

                if section == "SURFACE MEANING:":
                    text += (
                        "SURFACE MEANING:\n"
                        "See the structured L.I.M.I.N.A.L. analysis.\n\n"
                    )

                elif section == "POSSIBLE SUBTEXT:":
                    text += (
                        "POSSIBLE SUBTEXT:\n"
                        "No additional interpretation was returned.\n\n"
                    )

                elif section == "STRATEGICALLY MISSING:":
                    text += (
                        "STRATEGICALLY MISSING:\n"
                        "None clearly identified by the explanation layer.\n\n"
                    )

                elif section == "EVIDENCE:":
                    text += (
                        "EVIDENCE:\n"
                        "Refer to the structured agent findings and retrieved evidence.\n\n"
                    )

                elif section == "UNCERTAINTY:":
                    text += (
                        "UNCERTAINTY:\n"
                        "Interpretations are probabilistic and should not be treated as facts.\n"
                    )

        return self._clean_text(text)

    # ============================================================
    # AZURE EXPLANATION
    # ============================================================

    def explain(self, dossier: dict) -> str:
        """
        Generate a human-readable explanation from the existing
        M1-M5 structured analysis.
        """

        explanation_payload = self._build_explanation_payload(
            dossier
        )

        system_prompt = """
You are the explanation layer for L.I.M.I.N.A.L.
(Linguistic Inference of Missing Information via Networked Agent Logic).

The local M1-M5 models have already performed the analysis.

Your job is ONLY to explain those results clearly.

The Synthesizer prediction is authoritative.
DO NOT replace it with another classification.

DO NOT:
- invent labels
- invent evidence
- invent citations
- invent facts
- override M1-M5 findings
- diagnose a person's mental state
- claim to know private thoughts
- claim to know intentions or motives
- treat probability as certainty
- treat retrieval similarity as confidence
- introduce information that is not present in the supplied analysis

If the evidence is weak, say so.

If different agents identify different patterns,
describe the disagreement.

If the Synthesizer says NO_SIGNIFICANT_OMISSION,
do not manufacture a hidden meaning.

Use cautious wording:
"may indicate"
"could suggest"
"possibly"
"the text leaves open the possibility"

IMPORTANT OUTPUT RULES:
- Use plain ASCII characters only.
- Do not use curly quotes.
- Do not use em-dashes or en-dashes.
- Do not use special Unicode symbols.
- Do not reproduce long quotations from the input.
- When referring to a phrase from the input, paraphrase it instead.
- Do not create malformed quoted fragments.
- Keep every section concise and readable.

Return EXACTLY these five sections:

SURFACE MEANING:
Describe only what the message explicitly communicates.

POSSIBLE SUBTEXT:
Explain the Synthesizer prediction using the agent findings.
Do not introduce a different classification.

STRATEGICALLY MISSING:
Identify information left unspecified by the message.
If none is clearly supported, say so.

EVIDENCE:
Mention relevant observed linguistic findings and
retrieved evidence. Retrieval similarity is NOT confidence.

UNCERTAINTY:
Explain what cannot be established from the message alone.

Do not output JSON.
Do not output markdown code fences.
Do not add a title before SURFACE MEANING.
"""

        user_prompt = f"""
Use the following structured L.I.M.I.N.A.L. analysis:

{explanation_payload}

Explain it faithfully.

Remember:
- The Synthesizer prediction must remain unchanged.
- Do not invent a hidden meaning when the Synthesizer predicts NO_SIGNIFICANT_OMISSION.
- Use only the supplied findings.
- Do not claim private thoughts, emotions, intentions, or motives as facts.
- Use plain ASCII punctuation only.
"""

        response = self.client.responses.create(
            model=self.deployment,
            instructions=system_prompt,
            input=user_prompt,
            max_output_tokens=700,
        )

        output_text = getattr(response, "output_text", "")

        # Validate the five required sections first.
        validated_text = self._validate_sections(output_text)

        # FINAL OUTPUT BOUNDARY:
        # Normalize Unicode/mojibake and force ASCII so the text
        # remains safe through FastAPI, Windows and PowerShell.
        return self._sanitize_output(validated_text)