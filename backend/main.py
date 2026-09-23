from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from typing import Optional
import io
import time
import sys
from pathlib import Path
from pypdf import PdfReader

# Ensure project root and backend directory are in sys.path
ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    from backend.services.agent_runner import LIMINALAgentRunner
except ImportError:
    from services.agent_runner import LIMINALAgentRunner

# ============================================================
# GLOBAL MODEL RUNNER
# ============================================================

runner = None


# ============================================================
# REQUEST MODEL
# ============================================================

class AnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Communication text to analyze"
    )
    include_azure: bool = Field(
        default=True,
        description="Whether to generate the deep Azure GPT-6 explanation"
    )


class RemediateRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Communication text to remediate"
    )
    dossier: Optional[dict] = Field(
        default=None,
        description="Forensic dossier of the original message"
    )


# ============================================================
# LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global runner

    print("\n" + "=" * 70)
    print("STARTING L.I.M.I.N.A.L. API")
    print("=" * 70)

    try:
        runner = LIMINALAgentRunner()

        print("\nL.I.M.I.N.A.L. API READY")
        print("=" * 70)

        yield

    finally:
        print("\nShutting down L.I.M.I.N.A.L. API...")


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="L.I.M.I.N.A.L.",
    description=(
        "Linguistic Inference of Missing Information "
        "via Networked Agent Logic"
    ),
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
async def root():
    return {
        "name": "L.I.M.I.N.A.L.",
        "description": (
            "Linguistic Inference of Missing Information "
            "via Networked Agent Logic"
        ),
        "status": "online",
        "models": 5,
        "pipeline": [
            "Archaeologist",
            "Psychologist",
            "Logician",
            "Historian",
            "Synthesizer"
        ]
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy" if runner is not None else "loading",
        "device": "cuda",
        "models_loaded": runner is not None,
        "agents": {
            "archaeologist": runner is not None,
            "psychologist": runner is not None,
            "logician": runner is not None,
            "historian": runner is not None,
            "synthesizer": runner is not None
        },
        "azure_explainer": (
            runner.azure_status
            if runner is not None
            else "not_loaded"
        )
    }


# ============================================================
# ANALYZE
# ============================================================

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):

    global runner

    if runner is None:
        raise HTTPException(
            status_code=503,
            detail="L.I.M.I.N.A.L. models are still loading."
        )

    text = request.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Input text cannot be empty."
        )

    print("\n" + "=" * 70)
    print("API REQUEST: /analyze")
    print("=" * 70)

    start_time = time.perf_counter()

    try:

        result = runner.analyze(text, include_azure=request.include_azure)

        elapsed = time.perf_counter() - start_time

        result["meta"] = {
            "processing_time_seconds": round(
                elapsed,
                3
            ),
            "device": "cuda",
            "pipeline": [
                "Archaeologist",
                "Psychologist",
                "Logician",
                "Historian",
                "Synthesizer"
            ]
        }

        print(
            f"\nAnalysis completed in "
            f"{elapsed:.2f}s"
        )

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        print(
            f"\nAnalysis error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "L.I.M.I.N.A.L. analysis failed. "
                f"{str(exc)}"
            )
        )


@app.post("/analyze/stream")
async def analyze_stream(request: AnalyzeRequest):
    global runner

    if runner is None:
        raise HTTPException(
            status_code=503,
            detail="L.I.M.I.N.A.L. models are still loading."
        )

    text = request.text.strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail="Input text cannot be empty."
        )

    print("\n" + "=" * 70)
    print("API REQUEST: /analyze/stream")
    print("=" * 70)

    def event_generator():
        import json
        for event in runner.analyze_stream(text, include_azure=request.include_azure):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


# ============================================================
# REMEDIATE (TRANSPARENT REWRITE ENGINE)
# ============================================================

@app.post("/remediate")
async def remediate(request: RemediateRequest):
    global runner
    if runner is None:
        raise HTTPException(
            status_code=503,
            detail="L.I.M.I.N.A.L. models are still loading."
        )

    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    dossier = request.dossier or {}
    pattern = dossier.get("primary_pattern", "UNSTATED_PREFERENCE")
    missing = dossier.get("strategically_missing", ["Explicit preference", "Definite ownership"])

    print("\n" + "=" * 70)
    print("API REQUEST: /remediate")
    print("=" * 70)

    # Use Azure GPT-6 Astra if available
    if runner.azure_explainer is not None:
        try:
            client = runner.azure_explainer.client
            deployment = runner.azure_explainer.deployment
            import json as pyjson

            prompt = (
                f"You are the L.I.M.I.N.A.L. Subtext Remediation & Tactical Forensics Engine.\n"
                f"Original Communication:\n\"{text}\"\n"
                f"Detected Subtext Pattern: {pattern}\n"
                f"Strategically Missing Information: {missing}\n\n"
                f"Provide two improved rephrasings that eliminate hedging, ambiguity, passive construction, or responsibility gaps:\n"
                f"1. Direct & Assertive: Unambiguous personal ownership, definitive timeline/preference, zero hedging.\n"
                f"2. Diplomatic & Constructive: Polite, professional, yet completely transparent about criteria and responsibility.\n"
                f"3. Counter-Inquiries: Exactly three strategic questions the recipient can ask the speaker to probe the missing commitments or unstated preferences safely.\n\n"
                f"Respond ONLY with valid JSON with keys 'direct', 'diplomatic', 'rationale', and 'counter_inquiries' (array of 3 objects with 'label' and 'question'):\n"
                f'{{"direct": "...", "diplomatic": "...", "rationale": "...", "counter_inquiries": [{{"label": "...", "question": "..."}}, {{"label": "...", "question": "..."}}, {{"label": "...", "question": "..."}}]}}'
            )

            try:
                resp = client.chat.completions.create(
                    model=deployment,
                    messages=[
                        {"role": "system", "content": "You are a communication forensics consultant. Output only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=600
                )
            except Exception:
                resp = client.chat.completions.create(
                    model=deployment,
                    messages=[
                        {"role": "system", "content": "You are a communication forensics consultant. Output only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600
                )

            raw = resp.choices[0].message.content.strip()
            if raw.startswith("```json"):
                raw = raw[7:]
            if raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]

            parsed = pyjson.loads(raw.strip())
            return {
                "direct": parsed.get("direct", ""),
                "diplomatic": parsed.get("diplomatic", ""),
                "rationale": parsed.get("rationale", ""),
                "counter_inquiries": parsed.get("counter_inquiries", []),
                "engine": "Azure GPT-6 Astra"
            }
        except Exception as exc:
            print(f"[REMEDIATE] Azure fallback triggered: {exc}")

    # Fallback rule-based remediation
    direct = text.replace("I'm fine with whatever you decide", "I prefer Option A")
    direct = direct.replace("probably work", "work effectively")
    direct = direct.replace("should probably", "will")
    direct = direct.replace("might be", "is")
    if direct == text:
        direct = f"Here is my clear recommendation: {text.strip('.')} with full commitment to execution."

    diplomatic = f"To ensure transparency and shared ownership, {text.strip('.')} with designated owners and measurable deliverables."

    fallback_inquiries = [
        {
            "label": "Ownership Probe",
            "question": "Who will be designated as the primary owner accountable for this outcome?"
        },
        {
            "label": "Preference Clarification",
            "question": "Between our available options, what is your specific recommendation and rationale?"
        },
        {
            "label": "Milestone & Boundary Check",
            "question": "What concrete criteria or timeline will indicate whether this plan is succeeding?"
        }
    ]

    return {
        "direct": direct,
        "diplomatic": diplomatic,
        "rationale": "Transformed passive hedging and omitted accountability into explicit ownership and definite commitments.",
        "counter_inquiries": fallback_inquiries,
        "engine": "Local Remediation Rules"
    }


# ============================================================
# PDF DOCUMENT EXTRACTION
# ============================================================

@app.post("/extract-pdf")
async def extract_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a .pdf document."
        )

    try:
        contents = await file.read()
        reader = PdfReader(io.BytesIO(contents))
        num_pages = len(reader.pages)

        extracted_parts = []
        for idx, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            if txt.strip():
                extracted_parts.append(txt.strip())

        full_text = "\n\n".join(extracted_parts).strip()
        if not full_text:
            raise ValueError(
                "No readable text could be extracted from this PDF. It may contain scanned image scans without OCR."
            )

        truncated = False
        if len(full_text) > 5000:
            full_text = full_text[:4980] + "..."
            truncated = True

        print(f"[PDF] Extracted {len(full_text)} chars from {file.filename} ({num_pages} pages)")

        return {
            "filename": file.filename,
            "pages": num_pages,
            "characters": len(full_text),
            "text": full_text,
            "truncated": truncated
        }

    except HTTPException:
        raise
    except Exception as exc:
        print(f"[PDF] Extraction error: {exc}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process PDF: {str(exc)}"
        )


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )