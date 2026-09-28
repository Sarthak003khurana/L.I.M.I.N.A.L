# L.I.M.I.N.A.L.

### **Linguistic Inference of Missing Information via Networked Agent Logic**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/PyTorch-2.5+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-19.0+-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React 19" />
  <img src="https://img.shields.io/badge/Vite-8.0+-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/CUDA-12.8_Accelerated-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="CUDA" />
  <img src="https://img.shields.io/badge/Azure_AI-Foundry_Ready-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white" alt="Azure AI" />
  <img src="https://img.shields.io/badge/Architecture-Custom_Neural_Ensemble-blueviolet?style=for-the-badge" alt="Architecture" />
</p>

> **L.I.M.I.N.A.L.** is a multi-agent AI forensic framework engineered to analyze not merely what communicators state, but what they strategically omit, evade, hedge, or suppress. By unifying scratch-trained neural transformers, vector-retrieval pragmatics, and calibrated LLM epistemic reasoning, L.I.M.I.N.A.L. converts ambiguous discourse into verifiable forensic subtext dossiers.

---

## 📑 Table of Contents

- [The Core Problem: Overcoming Presence Bias](#-the-core-problem-overcoming-presence-bias)
- [System Architecture](#-system-architecture)
- [The Five-Agent Forensic Ensemble](#-the-five-agent-forensic-ensemble)
  - [M1: The Archaeologist (Linguistic Omission)](#1-m1--the-archaeologist-structural--lexical-omissions)
  - [M2: The Psychologist (Affect & Interpersonal Gaps)](#2-m2--the-psychologist-affect-gaps--emotional-suppression)
  - [M3: The Logician (Premise & Fallacy Forensics)](#3-m3--the-logician-argument-structure--fallacies)
  - [M4: The Historian (RAG Grounded in Pragmatic Theory)](#4-m4--the-historian-dense-rag-knowledge-grounding)
  - [M5: The Synthesizer (Neural Multi-Agent Fusion)](#5-m5--the-synthesizer-multi-modal-neural-fusion)
  - [Cognitive Explainer: Azure GPT-6 Astra Integration](#cognitive-explainer-azure-gpt-6-astra-layer)
- [Key Platform Features](#-key-platform-features)
- [Empirical Evaluation & Benchmarks](#-empirical-evaluation--benchmarks)
- [Repository Structure](#-repository-structure)
- [Installation & Environment Setup](#-installation--environment-setup)
- [Execution & Developer Workflows](#-execution--developer-workflows)
- [API Reference](#-api-reference)
- [Comprehensive Deployment Guide](#-comprehensive-deployment-guide)
  - [Docker Production Build](#docker-containerized-deployment)
  - [Cloud GPU Virtual Machine (Ubuntu 22.04 + NVIDIA CUDA)](#cloud-vm--gpu-host-deployment-aws-ec2--azure-vm)
  - [Decoupled Microservices Architecture](#decoupled-microservices-deployment)
- [Safety, Ethics & Responsible Interpretation](#-safety-ethics--responsible-interpretation)
- [Troubleshooting & FAQ](#-troubleshooting--faq)
- [License & Citation](#-license--citation)

---

## 🧠 The Core Problem: Overcoming Presence Bias

Traditional Natural Language Processing models (sentiment analysis, named entity recognition, intent extraction, extractive QA) suffer from an inherent **Presence Bias**: they are computationally constrained to analyze tokens that *exist* within the lexical window.

In strategic human communication—such as executive correspondence, policy negotiations, high-stakes contracts, and interpersonal conflict—crucial meaning is rarely conveyed through explicit assertions. Instead, meaning resides in **strategic absence**:

```
        TRADITIONAL NLP                     L.I.M.I.N.A.L. FORENSICS
┌─────────────────────────────┐         ┌─────────────────────────────┐
│      What was said?         │         │      What was said?         │
│             ↓               │         │             ↓               │
│ Analyze explicit tokens     │         │ What should have been said? │
│             ↓               │         │             ↓               │
│ Positive/Neutral Sentiment  │         │   What was omitted/hedged?  │
│             ↓               │         │             ↓               │
│ Literal Meaning Accepted    │         │  What does evidence back?   │
└─────────────────────────────┘         │             ↓               │
                                        │    Calibrated Subtext       │
                                        └─────────────────────────────┘
```

### Case Study: *"I'm fine with whatever you decide."*
* **Standard LLM / Sentiment Engine**: Predicts `Positive/Neutral`, `Agreeable`, `Low Conflict Risk`.
* **L.I.M.I.N.A.L. Forensic Pipeline**:
  - `M1 Archaeologist`: Identifies lexical hedging (`"fine with"`), missing decision ownership, and zero explicit commitments.
  - `M2 Psychologist`: Detects affect gap and emotional disengagement signals ($p = 0.986$).
  - `M3 Logician`: Flags unstated premise that the counterpart possesses superior decision context ($p = 0.996$).
  - `M4 Historian`: Retrieves Gricean Maxim of Quantity violation (Flouting Quantity via under-informative consent) and Hirschman's Exit-Voice-Loyalty dynamic.
  - `M5 Synthesizer`: Resolves multi-agent tensors into macro pattern `UNSTATED_PREFERENCE` with 97.14% calibrated confidence.

---

## 🏗️ System Architecture

L.I.M.I.N.A.L. executes a hybrid neuro-symbolic pipeline combining scratch-trained neural networks running concurrently via PyTorch CUDA acceleration, dense vector search via FAISS, and an asynchronous FastAPI orchestration runtime delivering Server-Sent Events (SSE) to a React HUD frontend.

```mermaid
flowchart TD
    User([User Ingestion: Raw Text / PDF / OCR]) --> Gateway[FastAPI Orchestrator :8000]
    
    subgraph Parallel Stage 1: Independent Neural Forensics
        Gateway --> M1[M1 Archaeologist<br/>4-Layer Transformer<br/>Vocab: 4,491 | d_model: 256]
        Gateway --> M2[M2 Psychologist<br/>4-Layer Transformer<br/>Affect & Incongruence Engine]
        Gateway --> M3[M3 Logician<br/>3-Layer Transformer<br/>6 Attention Heads | d_model: 192]
    end

    M1 --> HistTrigger{Query Generation}
    M2 --> HistTrigger
    M3 --> HistTrigger

    subgraph Stage 2: Knowledge Grounding & Pragmatic Retrieval
        HistTrigger --> M4[M4 Historian<br/>Dense FAISS Vector Store<br/>Linguistics & Pragmatics Knowledge Base]
    end

    subgraph Stage 3: Neural Fusion & Calibration
        M1 --> M5[M5 Synthesizer<br/>Multi-Head Cross-Agent Tensor Fusion]
        M2 --> M5
        M3 --> M5
        M4 --> M5
        M5 --> DossierGen[Subtext Dossier Tensor]
    end

    subgraph Stage 4: Qualitative Synthesis & Remediation
        DossierGen --> AzureLayer[Azure GPT-6 Astra / OpenAI Layer<br/>Epistemic Calibration & Reasoning]
        DossierGen --> RemedEngine[Transparent Rewrite Engine<br/>Assertive & Diplomatic Variants]
    end

    AzureLayer --> EventStream[SSE Event Stream / Response Schema]
    RemedEngine --> EventStream
    EventStream --> Frontend[React 19 Cyberpunk Intelligence UI]
```

---

## 🤖 The Five-Agent Forensic Ensemble

Every model in L.I.M.I.N.A.L. addresses a discrete dimensional plane of language analysis. **M1, M2, M3, and M5 are custom PyTorch models trained from scratch without off-the-shelf fine-tuning dependencies**, guaranteeing reproducible, low-latency, deterministic forensic feature extraction.

| Agent | Architecture | Input / Vocab | Parameter Scale | Target Forensic Domain |
|---|---|---|---|---|
| **M1 Archaeologist** | 4-Layer Encoder Transformer | Custom Tokenizer (`vocab: 4,491`) | 256 emb, 8 heads, 1024 FFN | Structural omission, passive voice, missing actors |
| **M2 Psychologist** | 4-Layer Encoder Transformer | Regex Word/Punctuation (`vocab: 4,491`) | 256 emb, 8 heads, 1024 FFN | Affect gaps, forced politeness, disengagement |
| **M3 Logician** | 3-Layer Self-Attention Encoder | Alphanumeric Tokenizer (`vocab: 4,491`) | 192 emb, 6 heads, 768 FFN | Unstated assumptions, false dilemmas, fallacies |
| **M4 Historian** | Dense Retrieval / FAISS | JSONL Knowledge Corpus | Vector embeddings + Cosine Sim | Pragmatics, Gricean maxims, negotiation theory |
| **M5 Synthesizer** | Multi-Head Fusion Classifier | Concatenated Agent Tensors + Text Hash | Deep Fusion FFN + Softmax | Primary subtext pattern, confidence calibration |

---

### 1. 🏺 M1 — The Archaeologist (Structural & Lexical Omissions)
* **Objective**: Detects the syntactic and lexical indicators of suppressed accountability and intentional ambiguity.
* **Architecture**: 4-Layer Transformer Encoder, 8 Multi-Head Attention heads, Learnable Positional Encodings, Dropout 0.10.
* **Output Classification Classes (7)**:
  1. `NO_OMISSION`: Explicit, direct, active sentence construction.
  2. `HEDGING`: Epistemic softening terms (*"probably"*, *"perhaps"*, *"should work"*).
  3. `MISSING_ACTOR`: Agentless passive clauses (*"the report was submitted"* without attribution).
  4. `PASSIVE_CONSTRUCTION`: Syntactic deflection of action away from the subject.
  5. `MISSING_COMMITMENT`: Ambiguity regarding timelines, deliverables, or execution pledges.
  6. `VAGUE_REFERENCE`: Deictic ambiguities (*"that matter"*, *"those concerns"*).
  7. `RESPONSIBILITY_AVOIDANCE`: Shifting locus of accountability to abstract entities or counterparts.

---

### 2. 🧠 M2 — The Psychologist (Affect Gaps & Emotional Suppression)
* **Objective**: Dissects interpersonal tone and emotional incongruity between communicative form and underlying affect.
* **Architecture**: 4-Layer Transformer Encoder with dedicated affect classification heads.
* **Output Classification Classes (7)**:
  1. `NO_AFFECT_SIGNAL`: Sincere, affectively aligned communicative state.
  2. `AFFECT_GAP`: Flat linguistic affect where enthusiasm or concern is standardly expected.
  3. `FORCED_POLITENESS`: Superficial honorifics masking resistance or condescension.
  4. `EMOTIONAL_INCONGRUENCE`: Explicit optimism juxtaposed against abrupt termination of dialogue.
  5. `DISENGAGEMENT_SIGNAL`: Conversational withdrawal, apathy, or conversational surrender.
  6. `RESENTMENT_SIGNAL`: Passive-aggressive linguistic markers.
  7. `EMOTIONAL_AVOIDANCE`: Evasion of affective confrontation through administrative tone.

---

### 3. ⚖️ M3 — The Logician (Argument Structure & Fallacies)
* **Objective**: Uncovers missing dialectical premises, skipped reasoning leaps, and structural informal fallacies.
* **Architecture**: 3-Layer Transformer Encoder, 6 Attention Heads, 192 embedding dimension, 768 feed-forward dimension.
* **Output Classification Classes (6)**:
  1. `SKIPPED_PREMISE`: Conclusions asserted without inferential justification.
  2. `UNANSWERED_COUNTERARGUMENT`: Deliberate disregard of known opposing contentions.
  3. `UNSUPPORTED_CONCLUSION`: Non-sequitur or overextended inductive assertions.
  4. `UNSTATED_ASSUMPTION`: Unverified axiomatic presuppositions required for the statement to hold.
  5. `CONTRADICTION`: Incompatibility between adjacent communicative premises.
  6. `FALSE_DILEMMA`: Artificial bifurcation into binary choices (*"either this or disaster"*).

---

### 4. 📚 M4 — The Historian (Dense RAG Knowledge Grounding)
* **Objective**: Prevents ungrounded hallucination by validating observed patterns against established academic corpora in linguistics, cognitive psychology, and game-theoretic negotiation literature.
* **Corpus & Index**: Dense vector store built from `data/knowledge_base/historian_knowledge.jsonl` utilizing FAISS.
* **Theoretical Frameworks Included**:
  - **Grice's Cooperative Principle**: Violations and floutings of the Maxims of Quantity, Quality, Relation, and Manner.
  - **Brown & Levinson Politeness Theory**: Negative Face preservation through indirect speech acts.
  - **Speech Act Theory (Austin & Searle)**: Discrepancies between Locutionary and Illocutionary forces.
  - **Hirschman's Exit, Voice, and Loyalty**: Suppression of Voice leading to pseudo-Loyalty.

---

### 5. 🧩 M5 — The Synthesizer (Multi-Modal Neural Fusion)
* **Objective**: Collects activations from M1, M2, M3, and retrieved embeddings from M4, performs cross-agent conflict resolution, and emits calibrated macro subtext predictions.
* **Architecture**: Concatenated feature projection layer combining agent probability distributions, text token hash embeddings, and multi-layer perceptual fusion heads.
* **Output Classification Classes (8)**:
  1. `NO_SIGNIFICANT_OMISSION`
  2. `UNSTATED_PREFERENCE`
  3. `AVOIDING_COMMITMENT`
  4. `DISTANCING_FROM_RESPONSIBILITY`
  5. `EMOTIONAL_DISENGAGEMENT`
  6. `WITHHELD_CONTEXT`
  7. `UNSUPPORTED_REASONING`
  8. `AMBIGUOUS_INTENT`

---

### Cognitive Explainer: Azure GPT-6 Astra Layer
While models M1–M5 extract mathematical forensic features, the optional **Azure GPT-6 Astra / OpenAI Layer** translates these findings into an executive-grade narrative dossier adhering to strict epistemic constraints:
- **Surface Meaning**: Literal semantic statement.
- **Possible Subtext**: Scientifically calibrated inference.
- **Strategically Missing**: Specific omitted elements (owners, criteria, metrics).
- **Grounded Evidence**: Citations linking findings to Gricean linguistics or organizational psychology.
- **Epistemic Uncertainty**: Transparent statement of analytical boundaries and alternative interpretations.

---

## ⚡ Key Platform Features

- **Real-Time SSE Streaming (`/analyze/stream`)**: Server-Sent Events allow the user interface to stream live telemetry updates as each individual agent initializes, runs inference, and passes representations to downstream layers.
- **Transparent Rewrite Engine (`/remediate`)**: Transforms evasive messages into:
  - *Direct & Assertive*: Eliminates hedging and enforces unambiguous personal ownership.
  - *Diplomatic & Constructive*: Maintains executive rapport while requiring concrete milestones and accountability.
  - *Tactical Counter-Inquiries*: Three calibrated probing questions allowing the recipient to gently surface unstated assumptions.
- **Forensic Radar Chart & Highlighter**: Interactive DOM token highlighting that color-codes tokens triggering M1 hedging, M2 emotional disengagement, and M3 fallacy detections.
- **Document & PDF Ingestion (`/extract-pdf`)**: Integrated `pypdf` extraction allowing analysis of executive memos, legal briefs, and corporate slide decks up to 5,000 characters per analysis run.
- **Dossier History Drawer**: Persists previous analyses in client local storage with instant recall, delta comparisons, and export options.

---

## 📊 Empirical Evaluation & Benchmarks

The L.I.M.I.N.A.L. pipeline was evaluated against a rigorous test battery of authentic corporate, diplomatic, and interpersonal communications. Ground-truth evaluation files are accessible in `pipeline_evaluation_results.json`.

### Benchmark Results Across Test Categories

| ID | Input Communication Sample | Predicted Category | Calibrated Confidence | Primary Triggered Agents |
|---|---|---|---|---|
| **01** | *"I'm fine with whatever you decide. The current plan should probably work."* | `UNSTATED_PREFERENCE` | **97.14%** | M1 Hedging (1.0), M2 Disengagement (0.98), M3 Assumption (0.99) |
| **02** | *"The report was submitted yesterday, but nobody mentioned who approved it."* | `DISTANCING_FROM_RESPONSIBILITY` | **86.49%** | M1 Missing Actor (0.99), M1 Passive Voice (0.99) |
| **03** | *"We should probably finish this soon. I guess the current approach is acceptable."* | `UNSTATED_PREFERENCE` | **89.26%** | M1 Hedging (1.0), M2 Emotional Incongruence (0.86) |
| **04** | *"Either we accept this proposal or the entire project will fail."* | `UNSUPPORTED_REASONING` | **94.80%** | M3 False Dilemma (0.99), M3 Skipped Premise (0.88) |
| **05** | *"The decision was made and changes implemented, but it is unclear who made it."* | `DISTANCING_FROM_RESPONSIBILITY` | **91.12%** | M1 Responsibility Avoidance (0.99), M1 Missing Actor (0.99) |
| **06** | *"I strongly prefer option A because it reduces project cost and development time."* | `NO_SIGNIFICANT_OMISSION` | **98.20%** | All Agents Report Clear Affirmative Signal |
| **07** | *"Everything is going perfectly. I just don't think we need to discuss it anymore."* | `EMOTIONAL_DISENGAGEMENT` | **93.45%** | M2 Disengagement (0.97), M2 Forced Politeness (0.82) |
| **08** | *"Everyone uses this system, so it must be the most reliable solution."* | `UNSUPPORTED_REASONING` | **92.30%** | M3 Unsupported Conclusion (0.99), Bandwagon Fallacy |

### Latency & GPU Acceleration (CUDA vs. CPU)
* **Average Full Pipeline Inference (CUDA 12.8, RTX 40-Series / A100)**: **~85ms - 140ms** per sample (M1-M5 concurrent execution).
* **Average Full Pipeline Inference (CPU fallback, 8-Core Intel/AMD)**: **~320ms - 480ms**.
* **With Azure GPT-6 Explainer Generation**: **~1.4s - 2.8s** (streamed incrementally via SSE).

---

## 📁 Repository Structure

```
L.I.M.I.N.A.L/
├── backend/
│   ├── main.py                         # FastAPI orchestrator, CORS, routes & lifespan
│   ├── evaluate_pipeline.py            # Automated multi-agent validation test harness
│   ├── evaluate_m5_blind.py            # Blind test suite across real-world edge cases
│   ├── gpu_test.py                     # PyTorch CUDA tensor & hardware validation script
│   ├── m3_gpu_benchmark.py             # Dedicated GPU benchmark for M3 Logician
│   ├── test_api_integration.py         # End-to-end integration test suite
│   └── services/
│       ├── agent_runner.py             # LIMINALAgentRunner: models M1-M5 concurrent loader
│       └── azure_explainer.py          # Azure AI Foundry & DefaultAzureCredential client
│
├── checkpoints/                        # Serialized PyTorch Model Checkpoints (.pt)
│   ├── archaeologist/best_model.pt     # M1 Transformer Checkpoint
│   ├── psychologist/best_model.pt      # M2 Affect Transformer Checkpoint
│   ├── logician/best_model.pt          # M3 Logician Transformer Checkpoint
│   └── synthesizer/best_model.pt       # M5 Fusion Classifier Checkpoint
│
├── models/                             # Model Definitions & Custom Tokenizers
│   ├── archaeologist/
│   │   ├── model.py                    # 4-Layer PyTorch Transformer Architecture
│   │   └── tokenizer/vocab.json        # 4,491 Token Custom Vocabulary
│   ├── psychologist/
│   │   ├── model.py                    # Affect Classification Transformer
│   │   └── tokenizer/vocab.json        # Custom Vocabulary
│   ├── logician/
│   │   ├── model.py                    # 3-Layer Logician Self-Attention Encoder
│   │   └── tokenizer/vocab.json        # Custom Vocabulary
│   ├── historian/
│   │   └── historian.py                # Dense FAISS Knowledge Retrieval Engine
│   └── synthesizer/
│       └── model.py                    # Multi-Head Agent Tensor Fusion Architecture
│
├── data/
│   └── knowledge_base/
│       └── historian_knowledge.jsonl   # Curated Pragmatics & Linguistics RAG Corpus
│
├── frontend/                           # React 19 + Vite 8 Intelligence HUD
│   ├── package.json                    # Frontend dependencies & scripts
│   ├── vite.config.js                  # Vite server & proxy configuration
│   ├── index.html                      # Entry HTML with custom font imports
│   └── src/
│       ├── main.jsx                    # React root mount
│       ├── App.jsx                     # Top-level state, shortcuts & routing
│       ├── index.css                   # Cyberpunk / Dark Intelligence HUD design tokens
│       ├── App.css                     # Global view styling & animations
│       ├── components/
│       │   ├── forensics/              # AnalysisPage, RadarChart, TokenHighlighter
│       │   ├── marketing/              # High-conversion product LandingPage
│       │   ├── modals/                 # ModelTelemetryModal & ShortcutsModal
│       │   └── canvas/                 # Interactive Canvas Minimap
│       ├── constants/presets.js        # Built-in forensic test scenarios
│       └── utils/forensicsMetrics.js   # Client-side radar calculations
│
├── .env.example                        # Template for environment configuration
├── .gitignore                          # Clean repository rules
├── requirements.txt                    # Standardized Python backend dependencies
└── pipeline_evaluation_results.json    # Verified evaluation benchmark output
```

---

## 💻 Installation & Environment Setup

### 1. Prerequisites
- **Python**: `3.11.x` or `3.12.x` (64-bit recommended)
- **Node.js**: `v18.0.0` or later (`v20+` recommended)
- **Package Managers**: `pip` and `npm`
- **Optional GPU**: NVIDIA GPU with CUDA 12.x drivers installed for hardware acceleration (CPU execution is fully supported automatically).

### 2. Clone the Repository
```bash
git clone https://github.com/Sarthak003khurana/L.I.M.I.N.A.L.git
cd L.I.M.I.N.A.L
```

### 3. Backend Environment Setup
Create and activate an isolated Python virtual environment:

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

*(Optional PyTorch CUDA 12.8 install if you have an NVIDIA GPU):*
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` in the root directory:
```bash
cp .env.example .env
```
Open `.env` and fill in your Azure AI Foundry or OpenAI credentials:
```ini
# Azure AI Foundry & Model Deployment Configuration
FOUNDRY_PROJECT_ENDPOINT=https://<your-foundry-resource-name>.services.ai.azure.com/api/projects/<project-id>
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Optional Azure Identity override credentials (if not running 'az login')
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
AZURE_TENANT_ID=

# Server Configuration
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=*
```
> **Note**: Even without Azure credentials, the core pipeline (M1, M2, M3, M4, and M5) and local rule remediation operate completely offline and without cloud reliance.

### 5. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

---

## 🚀 Execution & Developer Workflows

### 1. Run the Backend API Server
With `.venv` activated in the repository root:
```bash
python backend/main.py
```
* The API will initialize all 5 models into GPU VRAM (or CPU RAM) and bind to `http://localhost:8000`.
* Interactive OpenAPI Swagger documentation will be available at `http://localhost:8000/docs`.

### 2. Run the Frontend Development Server
In a separate terminal:
```bash
cd frontend
npm run dev
```
* The React Intelligence HUD will spin up at `http://localhost:5173`.

### 3. Verify Hardware & CUDA Acceleration
Validate your PyTorch CUDA device and VRAM availability:
```bash
python backend/gpu_test.py
```

### 4. Execute Benchmark & Evaluation Harnesses
Execute the standardized end-to-end evaluation pipeline:
```bash
python backend/evaluate_pipeline.py
```
Run the blind evaluation suite across real-world edge cases:
```bash
python backend/evaluate_m5_blind.py
```
Benchmark M3 Logician tensor throughput:
```bash
python backend/m3_gpu_benchmark.py
```
Run automated API integration tests against a live server:
```bash
python backend/test_api_integration.py
```

---

## 📡 API Reference

### 1. Health Check
`GET /health`
* **Description**: Returns operational status, model weights readiness, CUDA device status, and Azure connection status.
* **Response**:
```json
{
  "status": "healthy",
  "device": "cuda",
  "models_loaded": true,
  "agents": {
    "archaeologist": true,
    "psychologist": true,
    "logician": true,
    "historian": true,
    "synthesizer": true
  },
  "azure_explainer": "ready"
}
```

---

### 2. Analyze Communication (Synchronous)
`POST /analyze`
* **Headers**: `Content-Type: application/json`
* **Body**:
```json
{
  "text": "I'm fine with whatever you decide. The current plan should probably work.",
  "include_azure": true
}
```
* **Response**:
```json
{
  "surface_meaning": "I'm fine with whatever you decide. The current plan should probably work.",
  "primary_pattern": "UNSTATED_PREFERENCE",
  "confidence": 97.14,
  "confidence_level": "very_high",
  "possible_subtext": "The message may leave the speaker's actual preference or position unstated.",
  "strategically_missing": [
    "Explicit preference",
    "Clear personal position",
    "Definite ownership"
  ],
  "agents": {
    "archaeologist": {
      "findings": [{ "label": "HEDGING", "probability": 1.0 }]
    },
    "psychologist": {
      "findings": [{ "label": "DISENGAGEMENT_SIGNAL", "probability": 0.9861 }]
    },
    "logician": {
      "findings": [{ "label": "UNSTATED_ASSUMPTION", "probability": 0.9965 }]
    },
    "historian": {
      "evidence_count": 5,
      "sources": [
        {
          "title": "Gricean Conversational Maxims",
          "concept": "Maxim of Quantity",
          "relevance": "High"
        }
      ]
    },
    "synthesizer": {
      "prediction": "UNSTATED_PREFERENCE",
      "calibrated_confidence": 97.14
    }
  },
  "meta": {
    "processing_time_seconds": 1.482,
    "device": "cuda"
  }
}
```

---

### 3. Real-Time Streaming Analysis (SSE)
`POST /analyze/stream`
* **Headers**: `Content-Type: application/json`, `Accept: text/event-stream`
* **Body**:
```json
{
  "text": "The report was submitted yesterday, but nobody mentioned who approved it.",
  "include_azure": true
}
```
* **Stream Events**:
  - `{"event": "start", "message": "Initializing forensic pipeline..."}`
  - `{"event": "agent_complete", "agent": "archaeologist", "findings": [...]}`
  - `{"event": "agent_complete", "agent": "psychologist", "findings": [...]}`
  - `{"event": "agent_complete", "agent": "logician", "findings": [...]}`
  - `{"event": "agent_complete", "agent": "historian", "evidence": [...]}`
  - `{"event": "synthesizer_complete", "dossier": {...}}`
  - `{"event": "complete", "result": {...}}`

---

### 4. Transparent Rewrite Remediation
`POST /remediate`
* **Headers**: `Content-Type: application/json`
* **Body**:
```json
{
  "text": "I'm fine with whatever you decide. The current plan should probably work.",
  "dossier": {
    "primary_pattern": "UNSTATED_PREFERENCE",
    "strategically_missing": ["Explicit preference", "Definite ownership"]
  }
}
```
* **Response**:
```json
{
  "direct": "I prefer Option A because it provides predictable delivery. I will take ownership of executing the timeline.",
  "diplomatic": "To ensure shared alignment, my recommendation is Option A based on our resource targets. Let's designate clear accountability before proceeding.",
  "rationale": "Transformed passive compliance into proactive ownership while articulating rationale.",
  "counter_inquiries": [
    {
      "label": "Ownership Probe",
      "question": "Who will be designated as the accountable owner for this outcome?"
    },
    {
      "label": "Preference Clarification",
      "question": "Between our available alternatives, what is your specific recommendation?"
    },
    {
      "label": "Boundary Check",
      "question": "What concrete milestones will indicate this plan is succeeding?"
    }
  ],
  "engine": "Azure GPT-6 Astra"
}
```

---

### 5. Document & PDF Parsing
`POST /extract-pdf`
* **Content-Type**: `multipart/form-data`
* **Payload**: Form field `file` containing a `.pdf` document binary.
* **Response**:
```json
{
  "filename": "sample_executive_memo.pdf",
  "pages": 1,
  "characters": 1284,
  "text": "MEMORANDUM\nTo: Steering Committee...",
  "truncated": false
}
```

---

## 🌐 Comprehensive Deployment Guide

### Docker Containerized Deployment

Deploy L.I.M.I.N.A.L. using Docker and Docker Compose for zero-configuration, production-grade isolation.

#### 1. Backend `Dockerfile`
Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy model checkpoints, knowledge base, models, and backend code
COPY checkpoints/ ./checkpoints/
COPY models/ ./models/
COPY data/ ./data/
COPY backend/ ./backend/

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Frontend `Dockerfile`
Create `frontend/Dockerfile`:
```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### 3. Orchestration with `docker-compose.yml`
In the project root:
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - FOUNDRY_PROJECT_ENDPOINT=${FOUNDRY_PROJECT_ENDPOINT}
      - AZURE_OPENAI_DEPLOYMENT=${AZURE_OPENAI_DEPLOYMENT}
      - PORT=8000
      - HOST=0.0.0.0
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

Launch with:
```bash
docker compose up -d --build
```

---

### Cloud VM / GPU Host Deployment (AWS EC2 / Azure VM)

For high-throughput enterprise deployments on an NVIDIA GPU virtual machine (e.g., Azure `Standard_NC4as_T4_v3` or AWS `g4dn.xlarge` running Ubuntu 22.04 LTS):

1. **System & Driver Preparation**:
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   sudo apt-get install -y nvidia-driver-535 nvidia-utils-535 python3-pip python3-venv git
   sudo reboot
   ```
2. **Clone & Environment Setup**:
   ```bash
   git clone https://github.com/Sarthak003khurana/L.I.M.I.N.A.L.git /opt/liminal
   cd /opt/liminal
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install torch --index-url https://download.pytorch.org/whl/cu128
   ```
3. **Configure Systemd Service**:
   Create `/etc/systemd/system/liminal-backend.service`:
   ```ini
   [Unit]
   Description=L.I.M.I.N.A.L. FastAPI Backend Service
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/opt/liminal
   EnvironmentFile=/opt/liminal/.env
   ExecStart=/opt/liminal/.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
   Start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable liminal-backend
   sudo systemctl start liminal-backend
   ```
4. **Nginx Reverse Proxy & SSL**:
   ```nginx
   server {
       listen 80;
       server_name api.liminal-forensics.io;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
           
           # Required for SSE Streaming
           proxy_buffering off;
           proxy_read_timeout 300s;
       }
   }
   ```

---

### Decoupled Microservices Deployment

- **Backend**: Deploy container to **Azure Container Apps** (with GPU profile or 2 vCPU / 4GB RAM) or **AWS ECS Fargate**.
- **Frontend**: Deploy `frontend/dist` directly to **Vercel**, **Netlify**, or **AWS S3 + CloudFront**:
  ```bash
  cd frontend
  npm run build
  # Set VITE_API_URL in production environment variables to point to the backend domain
  ```

---

## 🛡️ Safety, Ethics & Responsible Interpretation

1. **Epistemic Modesty**: L.I.M.I.N.A.L. is architected with strict mathematical constraints preventing psychological certainty claims. The system never states *"The user is deceitful"*; it states *"Observable linguistic hedging ($p=1.0$) correlates with unstated decision preferences."*
2. **Clear Separation of Levels**:
   - **Level 1 (Direct Observation)**: Verifiable structural elements (passive verbs, absent names, hedge words).
   - **Level 2 (Inference)**: Pragmatic interpretations supported by conversational maxims.
   - **Level 3 (Evidence)**: Empirical theoretical citations retrieved from peer-reviewed literature.
   - **Level 4 (Confidence)**: Explicit numerical probability calibrated across the multi-agent ensemble.
3. **Data Minimization & Privacy**: Input communications are processed in memory and never logged, retained, or utilized for unauthorized model training.

---

## 🔧 Troubleshooting & FAQ

#### Q1: `CUDA out of memory` during startup
* **Solution**: Ensure no other processes are consuming VRAM. If utilizing a GPU with < 4GB VRAM, reduce batch size or set `DEVICE = torch.device("cpu")` in `backend/services/agent_runner.py`. The models will automatically execute on standard CPU RAM with negligible latency difference.

#### Q2: `FOUNDRY_PROJECT_ENDPOINT is missing` warning
* **Solution**: If you do not have active Azure AI credentials, the system will seamlessly run using the local neural models (M1, M2, M3, M4, M5) and local rule remediation without interrupting core functionality.

#### Q3: `EventSource` connection errors in frontend
* **Solution**: Ensure your reverse proxy has disabled response buffering (`proxy_buffering off;` in Nginx) and that `CORS` in `backend/main.py` permits requests from your frontend origin.

#### Q4: How does L.I.M.I.N.A.L. prevent false accusations?
* **Solution**: All synthesized outputs are explicitly framed around what is *structurally missing* rather than speculating on internal psychological intent. The presence of hedging is reported as a stylistic trait, allowing human decision-makers to formulate polite, clarifying counter-questions.

---

## 📜 License & Citation

Distributed under the Apache 2.0 License. See `LICENSE` for more information.

```bibtex
@software{liminal2026,
  author = {Khurana, Sarthak and Contributors},
  title = {L.I.M.I.N.A.L.: Linguistic Inference of Missing Information via Networked Agent Logic},
  year = {2026},
  url = {https://github.com/Sarthak003khurana/L.I.M.I.N.A.L}
}
```

<p align="center">
  <b>L.I.M.I.N.A.L. — Analyze the words. Investigate the gaps. Calibrate the unsaid.</b>
</p>
