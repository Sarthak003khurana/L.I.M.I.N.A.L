# L.I.M.I.N.A.L.

### Linguistic Inference of Missing Information via Networked Agent Logic

> **L.I.M.I.N.A.L. is a multi-agent AI system that analyzes not only what people say, but what they strategically avoid saying.**

---LLL

## 🧠 What Is L.I.M.I.N.A.L.?

Most NLP systems analyze **presence**:

* What words were used?
* Is the message positive or negative?
* What is the topic?
* What sentiment is being expressed?
* What entities or keywords appear?

But real human communication often works differently.

People communicate through:

* Strategic omissions
* Evasion
* Hedging
* Passive language
* Missing accountability
* Unanswered questions
* Suppressed emotion
* Unstated assumptions
* Carefully chosen ambiguity

L.I.M.I.N.A.L. focuses on this **missing information**.

### The Core Idea

Consider:

> **"I'm fine with whatever you decide."**

A traditional sentiment model may interpret this as:

```text
Positive / Neutral
Agreeable
No obvious conflict
```

L.I.M.I.N.A.L. asks a different question:

```text
What is missing from this statement?
```

It may identify:

* No explicit enthusiasm
* No personal preference
* No ownership of the decision
* No alternative proposal
* No timeline or next step
* Possible avoidance of disagreement

The system then generates a **calibrated interpretation**, rather than treating the literal sentence as the complete meaning.

### In Simple Terms

```text
Traditional NLP:

WHAT WAS SAID?
       ↓
Analyze the text
       ↓
Generate result


L.I.M.I.N.A.L.:

WHAT WAS SAID?
       ↓
WHAT SHOULD HAVE BEEN SAID?
       ↓
WHAT IS MISSING?
       ↓
WHY MIGHT THAT MATTER?
       ↓
WHAT DOES THE EVIDENCE SUPPORT?
       ↓
Generate Subtext Dossier
```

---

# 🎯 Problem Statement

### The problem: Presence Bias

Most language-analysis systems are optimized to detect information that **exists inside the input**.

This creates a blind spot.

A message can be grammatically polite, sentimentally neutral, or even positive while still carrying important implicit meaning.

For example:

```text
"I'll think about it."

"I guess that's okay."

"Do whatever you think is best."

"I'm fine with whatever you decide."

"We can discuss it later."
```

The literal words do not necessarily reveal:

* Commitment
* Agreement
* Disagreement
* Accountability
* Emotional state
* Intent
* Unresolved objections

L.I.M.I.N.A.L. attempts to surface these gaps through **structured multi-agent reasoning + retrieval-grounded evidence**.

---

# 🚀 Why L.I.M.I.N.A.L. Is Different

L.I.M.I.N.A.L. is **not simply another AI chatbot or GPT wrapper**.

### Typical AI wrapper

```text
User Input
    ↓
LLM
    ↓
Answer
```

### L.I.M.I.N.A.L.

```text
User Input
    ↓
Document / Screenshot Processing
    ↓
        ┌───────────────────┐
        │   Multi-Agent     │
        │    Forensics      │
        └───────────────────┘
          ↓   ↓   ↓   ↓
       Multiple independent
       analytical perspectives
          ↓
      Evidence Retrieval
          ↓
      Agent Debate / Fusion
          ↓
      Confidence Calibration
          ↓
    SUBTEXT DOSSIER
```

The important difference is that the system does not ask only:

> **"What does this text mean?"**

It asks:

> **"What information is absent, what reasoning is being skipped, and what interpretations are supported by evidence?"**

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │       USER           │
                         │ Text / PDF / Image   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   INPUT PROCESSING   │
                         │                      │
                         │ OCR / Text Extraction│
                         └──────────┬───────────┘
                                    │
                                    ▼
                   ┌────────────────────────────────┐
                   │       FASTAPI ORCHESTRATOR     │
                   │       Async Agent Pipeline     │
                   └───────────────┬────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
     ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
     │ ARCHAEOLOGIST  │   │  PSYCHOLOGIST  │   │    LOGICIAN    │
     │                │   │                │   │                │
     │ Linguistic     │   │ Affect &       │   │ Reasoning &    │
     │ omissions      │   │ emotional gaps │   │ argument gaps  │
     └───────┬────────┘   └───────┬────────┘   └───────┬────────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                                  ▼
                       ┌────────────────────┐
                       │     HISTORIAN      │
                       │                    │
                       │ RAG / FAISS        │
                       │ Linguistics        │
                       │ Psychology         │
                       │ Negotiation Cases  │
                       └─────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │    SYNTHESIZER     │
                       │                    │
                       │ Compare findings   │
                       │ Resolve conflicts  │
                       │ Confidence scoring │
                       └─────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │  SUBTEXT DOSSIER   │
                       │                    │
                       │ Surface Statement  │
                       │ Missing Elements   │
                       │ Subtext            │
                       │ Confidence         │
                       │ Evidence           │
                       └─────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │   REACT DASHBOARD  │
                       └────────────────────┘
```

---

# 🤖 The Five-Agent Forensic Pipeline

Each agent has a **specific responsibility**.

The goal is not to make five agents give the same answer.

The goal is to make them look at the communication from **different analytical dimensions**.

---

## 1. 🏺 The Archaeologist

### Role

Finds linguistic evidence of what has been omitted, hidden, or softened.

### Looks for

* Lexical hedging
* Passive voice
* Missing actors
* Missing subjects
* Vague language
* Responsibility avoidance
* Unanswered commitments
* Strategic omissions

### Example

```text
"The decision was made."

```

The Archaeologist asks:

```text
Who made the decision?
When?
Why?
Was the speaker involved?
```

Instead of accepting the sentence literally, it identifies the missing structural information.

---

# 2. 🧠 The Psychologist

### Role

Examines emotional and interpersonal signals.

### Looks for

* Affect gaps
* Forced politeness
* Emotional suppression
* Sudden changes in tone
* Lack of expected enthusiasm
* Possible resentment signals
* Emotional incongruence

### Example

```text
"That's completely fine."
```

The system does not automatically conclude that the speaker is angry.

Instead, it may identify:

```text
Observation:
The statement contains explicit acceptance.

Gap:
No positive affect or elaboration accompanies the acceptance.

Interpretation:
Possible emotional disengagement.

Confidence:
Moderate
```

This distinction is important.

**The system should identify evidence and uncertainty rather than present speculation as fact.**

---

# 3. ⚖️ The Logician

### Role

Analyzes the reasoning structure behind the communication.

### Looks for

* Missing premises
* Skipped reasoning
* Unanswered counterarguments
* False dilemmas
* Contradictions
* Unsupported conclusions
* Assumptions
* Logical gaps

### Example

```text
"If we don't approve this proposal today,
the entire project will fail."
```

The Logician asks:

```text
Why are those the only two outcomes?

What evidence connects today's approval
to project failure?
```

This allows the system to detect **reasoning gaps**, not just linguistic gaps.

---

# 4. 📚 The Historian

### Role

Provides external knowledge and contextual grounding.

The Historian queries the **FAISS vector store** containing relevant knowledge such as:

* Communication psychology
* Linguistics
* Gricean Conversational Maxims
* Negotiation principles
* Communication case studies
* Relevant research literature

### Why this agent exists

Without retrieval, an LLM can produce convincing but unsupported explanations.

The Historian gives the system a way to ask:

> "Is there established research or theory that supports this interpretation?"

### Pipeline

```text
Agent Finding
      ↓
Generate Retrieval Query
      ↓
FAISS Similarity Search
      ↓
Retrieve Relevant Sources
      ↓
Return Evidence
      ↓
Provide Context to Synthesizer
```

---

# 5. 🧩 The Synthesizer

### Role

The Synthesizer is the final reasoning layer.

It receives:

```text
Archaeologist findings
        +
Psychologist findings
        +
Logician findings
        +
Historian evidence
```

It then:

1. Compares findings
2. Detects agreement
3. Detects contradictions
4. Separates observations from interpretations
5. Uses retrieved evidence
6. Calibrates confidence
7. Produces the final **Subtext Dossier**

### Important Principle

The Synthesizer should **not blindly combine every agent's conclusion**.

For example:

```text
Archaeologist:
"Preference is missing."

Psychologist:
"Possible emotional disengagement."

Logician:
"No explicit disagreement."

Historian:
"Indirect disagreement can occur through
hedging and avoidance, but context matters."
```

The Synthesizer should preserve that uncertainty.

---

# 🔄 Complete Agent Flow

```text
                  INPUT
                    │
                    ▼
             OCR / TEXT EXTRACTION
                    │
                    ▼
            ┌─────────────────┐
            │ FASTAPI SERVER  │
            └────────┬────────┘
                     │
             Parallel Processing
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
 Archaeologist   Psychologist   Logician
       │             │             │
       └─────────────┼─────────────┘
                     │
                     ▼
                Historian
                 (RAG)
                     │
                     ▼
               Evidence Set
                     │
                     ▼
              ┌──────────────┐
              │ Synthesizer  │
              └──────┬───────┘
                     │
                     ▼
          Confidence Calibration
                     │
                     ▼
             SUBTEXT DOSSIER
                     │
                     ▼
             REACT DASHBOARD
```

---

# 🧰 Tech Stack

## Frontend

| Technology           | Purpose                        |
| -------------------- | ------------------------------ |
| React                | UI architecture                |
| Vite                 | Development/build tooling      |
| TypeScript           | Type-safe frontend development |
| Tailwind CSS         | Styling                        |
| Dark Intelligence UI | Visualization and presentation |

---

## Backend

| Technology   | Purpose                      |
| ------------ | ---------------------------- |
| Python 3.11+ | Core backend language        |
| FastAPI      | REST API                     |
| Asyncio      | Parallel agent orchestration |
| Pydantic     | Request/response validation  |

---

## AI / Cloud

| Technology                     | Purpose                       |
| ------------------------------ | ----------------------------- |
| Azure OpenAI                   | LLM inference                 |
| GPT-6 Astra                    | Agent reasoning and synthesis |
| text-embedding-3-large         | Semantic embeddings           |
| Azure AI Document Intelligence | OCR / document extraction     |
| Azure Content Safety           | Input/output guardrails       |

---

## RAG / Vector Search

| Technology | Purpose                                     |
| ---------- | ------------------------------------------- |
| FAISS      | Vector similarity search                    |
| Embeddings | Convert research into semantic vectors      |
| RAG        | Ground agent findings in external knowledge |

---

# 🧠 RAG Architecture

```text
        RESEARCH MATERIAL
               │
               ▼
        Document Processing
               │
               ▼
          Text Chunking
               │
               ▼
       Azure Embeddings
               │
               ▼
         FAISS Index
               │
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
User Analysis       Agent Finding
       │                │
       └───────┬────────┘
               ▼
        Semantic Search
               │
               ▼
       Relevant Evidence
               │
               ▼
          Synthesizer
```

---

# 📊 Final Output — Subtext Report Card

The user should not receive a giant block of AI-generated text.

Instead, the system produces a **visual forensic report**.

### Conceptual UI

```text
┌─────────────────────────────────────────────────────┐
│              L.I.M.I.N.A.L. REPORT                  │ 
├─────────────────────────────────────────────────────┤
│                                                     │
│  SURFACE STATEMENT                                  │
│  "I'm fine with whatever you decide."               │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  POSSIBLE UNSAID SUBTEXT                            │
│                                                     │
│  "The speaker does not explicitly state a           │
│   preference or take ownership of the decision."    │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  MISSING ELEMENTS                                   │
│                                                     │
│  • No explicit preference                           │
│  • No alternative proposal                          │
│  • No ownership of the decision                     │
│  • No next step or timeline                         │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  CONFIDENCE                                         │
│                                                     │
│                    78%                              │
│                                                     │
│  Evidence strength: Moderate                        │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  AGENT FINDINGS                                     │
│                                                     │
│  🏺 Archaeologist     Linguistic omission detected │
│  🧠 Psychologist      Affect gap detected          │
│  ⚖️ Logician          No explicit contradiction    │
│  📚 Historian         Supporting research found    │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  GROUNDED EVIDENCE                                  │
│                                                     │
│  📚 Communication Theory                            │
│  📚 Gricean Conversational Maxims                   │
│  📚 Negotiation Research                            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

# 🎯 Core Output Structure

The backend should ideally return structured JSON similar to:

```json
{
  "surface_statement": "...",
  "possible_subtext": "...",
  "missing_elements": [
    "...",
    "...",
    "..."
  ],
  "confidence": 78,
  "confidence_level": "moderate",
  "agent_findings": {
    "archaeologist": [],
    "psychologist": [],
    "logician": [],
    "historian": []
  },
  "evidence": [
    {
      "title": "...",
      "source": "...",
      "relevance": "..."
    }
  ]
}
```

The frontend then converts this structured response into the visual report.

---

# 👥 Team Work Breakdown

The project should be developed as **three major workstreams**.

```text
                    L.I.M.I.N.A.L.
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    FRONTEND          BACKEND       AI / PROMPTS
        │                │                │
     React UI        FastAPI        Agent Logic
     Dashboard       APIs           Prompts
     Report Card     Orchestrator   RAG
     Components      Asyncio        Evaluation
```

---

# 🎨 Team 1 — Frontend

### Main Responsibility

Build the **dark intelligence dashboard** and convert backend results into an intuitive forensic report.

### Tasks

#### 1. Dashboard

Create:

```text
Input
 ↓
Analysis State
 ↓
Agent Activity
 ↓
Final Report
```

---

### 2. Input Interface

Support:

* Text input
* Screenshot upload
* PDF upload
* Analyze button
* Loading state
* Error state

Example:

```text
┌─────────────────────────────────────┐
│ Paste communication or upload file  │
│                                     │
│                                     │
│                                     │
└─────────────────────────────────────┘

        [ ANALYZE SUBTEXT ]
```

---

### 3. Agent Visualization

Show the five agents working.

Example:

```text
🏺 Archaeologist      ✓ Complete
🧠 Psychologist       ✓ Complete
⚖️ Logician           ✓ Complete
📚 Historian          ✓ Complete
🧩 Synthesizer        ⟳ Processing
```

This makes the multi-agent architecture visible to evaluators.

---

### 4. Report Card

Build reusable components:

```text
<SurfaceStatement />
<SubtextAnalysis />
<MissingElements />
<ConfidenceScore />
<AgentFindings />
<EvidenceSources />
```

---

### 5. Frontend API Integration

Frontend sends:

```http
POST /analyze
```

Example request:

```json
{
  "text": "I'm fine with whatever you decide."
}
```

Then receives the structured dossier.

---

# ⚙️ Team 2 — Backend

### Main Responsibility

Build the API and orchestration layer connecting the frontend, AI agents, RAG system, OCR, and safety layer.

---

## Backend Structure

Suggested structure:

```text
backend/
│
├── main.py
│
├── agents/
│   ├── archaeologist.py
│   ├── psychologist.py
│   ├── logician.py
│   ├── historian.py
│   └── synthesizer.py
│
├── rag/
│   ├── embeddings.py
│   ├── vector_store.py
│   └── retriever.py
│
├── services/
│   ├── ocr.py
│   ├── azure_openai.py
│   └── content_safety.py
│
├── models/
│   └── schemas.py
│
└── utils/
    └── helpers.py
```

---

## Backend Responsibilities

### API Endpoints

Potential endpoints:

```text
POST /analyze
POST /analyze/image
POST /analyze/pdf
GET  /health
```

---

### Agent Orchestration

The backend should execute independent agents concurrently where possible.

Conceptually:

```python
results = await asyncio.gather(
    archaeologist.analyze(text),
    psychologist.analyze(text),
    logician.analyze(text)
)
```

Then:

```text
Agent Results
     ↓
Historian / RAG
     ↓
Synthesizer
     ↓
Final JSON
```

---

### Backend Must Handle

* API validation
* File handling
* OCR
* Agent execution
* Async orchestration
* Error handling
* Timeouts
* Structured JSON responses
* Azure API integration
* Content Safety
* RAG retrieval

---

# 🤖 Team 3 — AI / Prompt Engineering

### Main Responsibility

Design the intelligence behind the system.

This is one of the most important parts of L.I.M.I.N.A.L.

---

# Agent Prompt Design

Each agent should have a **strict role**.

Do not give every agent a generic:

```text
"Analyze this text."
```

Instead:

```text
You are the Archaeologist.

Your responsibility is to identify linguistic
information that is absent, suppressed, vague,
or structurally avoided.

Analyze:
- hedging
- passive constructions
- missing actors
- vague references
- omitted commitments
- unanswered linguistic expectations

Separate:
1. Direct observations
2. Possible interpretations
3. Confidence

Never present an inference as a confirmed fact.
```

The same principle should be applied to every agent.

---

# 🧪 Agent Evaluation

The AI team should create test cases covering:

### Explicit Agreement

```text
"I completely agree with your proposal."
```

### Explicit Disagreement

```text
"I disagree with this approach."
```

### Ambiguous Agreement

```text
"Whatever works for you."
```

### Evasion

```text
"Let's not get into that right now."
```

### Missing Accountability

```text
"The issue was handled."
```

### Missing Reasoning

```text
"This is clearly the only option."
```

### Emotional Incongruence

```text
"Sure, that's totally fine."
```

The goal is to test whether the system identifies **observable gaps without overclaiming hidden intent**.

---

# 📏 Confidence Model

Confidence should not mean:

> "The AI knows what this person is thinking."

Instead:

> **How strongly does the available evidence support the identified interpretation?**

A possible conceptual scale:

```text
0–20%    Very weak evidence
21–40%   Weak evidence
41–60%   Moderate evidence
61–80%   Strong evidence
81–100%  Very strong evidence
```

The exact scoring methodology should be finalized during implementation and evaluation.

---

# 🛡️ Safety & Responsible Interpretation

L.I.M.I.N.A.L. deals with human communication, so **false certainty is a major risk**.

The system should distinguish:

```text
OBSERVATION
"What is directly visible in the message?"

        ↓

INFERENCE
"What interpretation could explain it?"

        ↓

EVIDENCE
"What research/context supports this?"

        ↓

CONFIDENCE
"How strongly is the interpretation supported?"
```

### Important Rule

The system should **never claim to know someone's private thoughts**.

Instead of:

```text
❌ "The person secretly hates your proposal."
```

Prefer:

```text
✓ "The message does not explicitly express
   agreement and contains no alternative proposal.

   This may indicate disengagement or avoidance,
   but the available text does not establish
   the speaker's underlying intent."
```

This makes the system more credible and reduces hallucinated psychological conclusions.

---

# 🔐 Privacy Considerations

Communication data can contain sensitive information.

The implementation should consider:

* Secure file handling
* Minimal data retention
* API key protection
* No unnecessary storage of analyzed messages
* Input validation
* Content Safety checks
* Clear separation between user content and system prompts

Never expose:

```text
AZURE_API_KEY
```

or other secrets in frontend code.

Use environment variables:

```text
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT=
```

---

# 🔄 End-to-End Example

### Input

```text
"I'm fine with whatever you decide.
You probably know what's best."
```

### Archaeologist

```text
Possible findings:

- Explicit personal preference is absent.
- Decision ownership is transferred to the recipient.
- No alternative option is proposed.
```

### Psychologist

```text
Possible findings:

- Low affective elaboration.
- Acceptance language is present.
- Emotional state cannot be established from text alone.
```

### Logician

```text
Possible findings:

- The claim that the recipient knows best
  is not supported by an explicit premise.
```

### Historian

```text
Retrieves relevant material concerning:

- conversational implicature
- hedging
- indirect disagreement
- conversational expectations
```

### Synthesizer

Produces:

```text
SURFACE
"I'm fine with whatever you decide."

POSSIBLE SUBTEXT
The speaker does not state a preference and
places the decision responsibility on the recipient.

MISSING ELEMENTS
• Personal preference
• Alternative proposal
• Explicit ownership
• Concrete next step

CONFIDENCE
Moderate

IMPORTANT LIMITATION
The text alone cannot establish the speaker's
actual private intention.
```

---

# 📁 Suggested Repository Structure

```text
LIMINAL/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── types/
│   ├── package.json
│   └── README.md
│
├── backend/
│   ├── agents/
│   ├── rag/
│   ├── services/
│   ├── models/
│   ├── utils/
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
│
├── data/
│   └── knowledge_base/
│
├── tests/
│   ├── agent_tests/
│   ├── api_tests/
│   └── evaluation_cases/
│
├── .env.example
├── .gitignore
└── README.md
```

---

# 🌿 Git Workflow

To prevent everyone from breaking the main branch:

```text
main
 │
 ├── feature/frontend-dashboard
 ├── feature/backend-api
 ├── feature/agent-archaeologist
 ├── feature/agent-psychologist
 ├── feature/agent-logician
 ├── feature/rag-historian
 └── feature/synthesizer
```

### Recommended workflow

```bash
git checkout -b feature/your-feature
```

Work → commit → push → Pull Request → review → merge.

Avoid directly pushing experimental code to `main`.

---

# 🧩 Integration Contract

The most important agreement between teams is the **API contract**.

Frontend should not depend on how the agents internally work.

Frontend only needs:

```text
INPUT
  ↓
API
  ↓
STRUCTURED DOSSIER
```

For example:

```json
{
  "surface_statement": "I'm fine with whatever you decide.",
  "subtext": {
    "text": "The speaker does not state a preference...",
    "confidence": 0.78
  },
  "missing_elements": [
    "Explicit preference",
    "Alternative proposal",
    "Decision ownership"
  ],
  "agents": {
    "archaeologist": {
      "status": "complete",
      "findings": []
    },
    "psychologist": {
      "status": "complete",
      "findings": []
    },
    "logician": {
      "status": "complete",
      "findings": []
    },
    "historian": {
      "status": "complete",
      "sources": []
    }
  }
}
```

This lets frontend and backend teams work **independently**.

---

# 🏁 MVP Definition

The first working version does **not** need every possible feature.

### MVP must support:

* [ ] Text input
* [ ] FastAPI backend
* [ ] Azure OpenAI integration
* [ ] 5-agent architecture
* [ ] Parallel execution of independent agents
* [ ] FAISS RAG
* [ ] Synthesizer
* [ ] Confidence score
* [ ] Structured JSON response
* [ ] React dashboard
* [ ] Visual Subtext Report Card
* [ ] Basic Content Safety

### After MVP

Potential extensions:

* [ ] Screenshot OCR
* [ ] PDF analysis
* [ ] Conversation-level analysis
* [ ] Timeline/context comparison
* [ ] Multi-message contradiction detection
* [ ] More specialized knowledge bases
* [ ] Advanced evaluation framework

---

# 🏆 What We Want Evaluators to See

When someone opens L.I.M.I.N.A.L., they should immediately understand:

```text
This is not:

"Ask GPT anything."

This is:

"Give us a piece of communication,
and our specialized AI agents investigate
what information may be missing from it."
```

The demo should visually communicate:

```text
INPUT
  ↓
FORENSIC ANALYSIS
  ↓
5 SPECIALIZED AGENTS
  ↓
RAG-GROUNDED EVIDENCE
  ↓
SYNTHESIS
  ↓
CONFIDENCE
  ↓
SUBTEXT DOSSIER
```

---

# 💡 The One-Line Pitch

> **L.I.M.I.N.A.L. is a multi-agent AI forensic system that detects the meaning hiding in communication gaps—analyzing what was said, what was omitted, why the omission may matter, and how strongly the evidence supports the interpretation.**

---

# 👨‍💻 Team Mission

We are not building another chatbot.

We are building an **AI investigation pipeline for linguistic absence**.

Every component should answer one question:

> **What important information is missing from this communication, and what evidence supports that observation?**

```text
        WHAT WAS SAID?
              │
              ▼
        WHAT IS MISSING?
              │
              ▼
       WHAT WAS AVOIDED?
              │
              ▼
       WHAT DOES LOGIC SAY?
              │
              ▼
       WHAT DOES RESEARCH SAY?
              │
              ▼
        WHAT CAN WE ACTUALLY
          CONFIDENTLY INFER?
              │
              ▼
        ┌───────────────┐
        │ L.I.M.I.N.A.L.│
        │SUBTEXT DOSSIER│
        └───────────────┘
```

**L.I.M.I.N.A.L. — Analyze the words. Investigate the gaps.**
