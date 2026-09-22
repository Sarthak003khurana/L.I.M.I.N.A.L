from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import time

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

        result = runner.analyze(text)

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


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )