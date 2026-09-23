import React, { useState } from "react";
import {
  Brain,
  Check,
  Cpu,
  Database,
  GitBranch,
  Info,
  Layers3,
  Network,
  ScanSearch,
  Search,
  Sparkles,
  Tag,
  X,
  Zap,
} from "lucide-react";
import "./ModelTelemetryModal.css";

// Fallback label spaces and descriptions for all 5 agents
const AGENT_SPECIFICATIONS = {
  archaeologist: {
    vocabSize: 326,
    architecture: "Transformer Encoder (WordPiece, 4-Layer, 8-Head)",
    device: "CUDA / GPU",
    labels: [
      { name: "HEDGING", desc: "Weakening commitment via epistemic dampeners (e.g. 'probably', 'might', 'seems')." },
      { name: "MISSING_ACTOR", desc: "Suppression of the accountable subject (e.g. 'it was agreed', 'procedures are being changed')." },
      { name: "PASSIVE_CONSTRUCTION", desc: "Grammatical shift from active to passive voice to obscure responsibility." },
      { name: "MISSING_COMMITMENT", desc: "Absence of definitive deliverables, deadlines, or binding next steps." },
      { name: "VAGUE_REFERENCE", desc: "Indefinite referents and ambiguous pronouns that resist verification." },
      { name: "RESPONSIBILITY_AVOIDANCE", desc: "Deflecting ownership onto external circumstances or unspecified consensus." },
      { name: "NO_OMISSION", desc: "Standard cooperative syntactic structure with explicit agency." },
    ],
    sampleVocab: [
      "the", "was", "should", "we", "it", "i", "by", "that", "be", "team", "will", "changed",
      "issue", "handle", "proposal", "address", "when", "probably", "report", "handled", "someone",
      "schedule", "review", "project", "because", "department", "might", "decision", "fine",
      "whatever", "plan", "work", "agreed", "decide", "seems", "potentially", "assumed"
    ],
  },
  psychologist: {
    vocabSize: 216,
    architecture: "Affect-Tuned Transformer Encoder (3-Layer, 4-Head)",
    device: "CUDA / GPU",
    labels: [
      { name: "AFFECT_GAP", desc: "Flat or minimal emotional expression in a high-stakes or contentious scenario." },
      { name: "FORCED_POLITENESS", desc: "Exaggerated surface courtesy masking underlying dissent or frustration." },
      { name: "EMOTIONAL_INCONGRUENCE", desc: "Divergence between literal agreeable phrasing and reluctant pragmatic tone." },
      { name: "DISENGAGEMENT_SIGNAL", desc: "Linguistic cues signaling interpersonal withdrawal or minimal investment." },
      { name: "RESENTMENT_SIGNAL", desc: "Subtle indicators of unaddressed grievance or unacknowledged resistance." },
      { name: "EMOTIONAL_AVOIDANCE", desc: "Steering conversational focus away from interpersonal or emotional stakes." },
      { name: "NO_AFFECT_SIGNAL", desc: "Balanced emotional tone congruent with explicit communicative content." },
    ],
    sampleVocab: [
      "i", "feel", "fine", "okay", "agree", "sure", "happy", "frustrated", "concern", "whatever",
      "support", "disappointed", "hope", "sorry", "appreciate", "understand", "glad", "trust",
      "respect", "frankly", "honestly", "personally", "reluctant", "uncomfortable", "comfortable"
    ],
  },
  logician: {
    vocabSize: 466,
    architecture: "Propositional Transformer Encoder (4-Layer, 8-Head)",
    device: "CUDA / GPU",
    labels: [
      { name: "SKIPPED_PREMISE", desc: "Jumping directly to a conclusion without providing necessary evidentiary steps." },
      { name: "UNANSWERED_COUNTERARGUMENT", desc: "Ignoring obvious objections or dismissing counter-evidence without rebuttal." },
      { name: "UNSUPPORTED_CONCLUSION", desc: "Asserting a definitive consequence without demonstrable logical backing." },
      { name: "UNSTATED_ASSUMPTION", desc: "Relying on unverified background premises taken as self-evident truths." },
      { name: "CONTRADICTION", desc: "Internal incompatibility between stated premises, requirements, or objectives." },
      { name: "FALSE_DILEMMA", desc: "Artificially constraining alternatives to force an uncalibrated choice." },
    ],
    sampleVocab: [
      "therefore", "because", "since", "if", "then", "must", "cannot", "either", "or", "unless",
      "proves", "conclusion", "assumption", "fact", "evidence", "result", "fails", "guarantees",
      "premise", "argument", "reason", "obviously", "clearly", "inevitable", "consequence"
    ],
  },
  historian: {
    vocabSize: 18,
    architecture: "FAISS Vector Index (IndexFlatIP) + TF-IDF Precedent Matcher",
    device: "In-Memory / GPU Vector Space",
    labels: [
      { name: "Case 101: Passive Agreement Memo", desc: "Historical dispute involving non-committal concurrence in technical reviews." },
      { name: "Case 204: Transition Accountability Evasion", desc: "Corporate statement omitting responsible actor during organizational restructuring." },
      { name: "Case 305: False Deadline Dilemma", desc: "Contract negotiation tactic artificially truncating decision windows." },
      { name: "Case 409: Hedged Roadmap Endorsement", desc: "Executive communication deferring milestone ownership to unspecified teams." },
      { name: "Case 512: Withheld Performance Deficit", desc: "Status update using passive syntax to suppress operational blockers." },
    ],
    sampleVocab: [
      "precedent", "implicature", "maxim", "grice", "quantity", "relevance", "manner", "corporate",
      "contract", "transition", "dispute", "roadmap", "accountability", "delegation", "audit"
    ],
  },
  synthesizer: {
    vocabSize: 8,
    architecture: "Dual-Stream Cross-Agent Neural Fusion Network (52,459 Parameters)",
    device: "CUDA / GPU",
    labels: [
      { name: "UNSTATED_PREFERENCE", desc: "Leaves actual personal preference unstated while feigning casual agreement." },
      { name: "AVOIDING_COMMITMENT", desc: "Refuses to establish concrete deadlines, milestones, or binding actions." },
      { name: "DISTANCING_FROM_RESPONSIBILITY", desc: "Uses grammatical evasion to shift ownership away from the speaker." },
      { name: "EMOTIONAL_DISENGAGEMENT", desc: "Interpersonal detachment masking unaddressed conflict or apathy." },
      { name: "WITHHELD_CONTEXT", desc: "Strategic omission of essential operational dependencies or context." },
      { name: "UNSUPPORTED_REASONING", desc: "Flawed argumentative structure relying on unstated premises." },
      { name: "AMBIGUOUS_INTENT", desc: "Phrasing engineered to support multiple contradictory future interpretations." },
      { name: "NO_SIGNIFICANT_OMISSION", desc: "Transparent, cooperative communication with explicit ownership." },
    ],
    sampleVocab: [
      "fusion", "features", "weights", "softmax", "cross-agent", "probability", "consensus",
      "calibrated", "subtext", "dossier", "interpretation", "linguistic", "inference"
    ],
  },
};

function formatLabel(value) {
  if (!value) return "Unknown";
  return String(value)
    .replace(/_/g, " ")
    .replace(/-/g, " ")
    .toLowerCase()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export default function ModelTelemetryModal({
  isOpen,
  onClose,
  agentId = "archaeologist",
  agent = null,
  agentData = null,
  initialTab = "labels",
  text = "",
}) {
  const [activeTab, setActiveTab] = useState(initialTab); // "labels" | "vocab" | "architecture"
  const [vocabSearch, setVocabSearch] = useState("");

  if (!isOpen) return null;

  const spec = AGENT_SPECIFICATIONS[agentId] || AGENT_SPECIFICATIONS.archaeologist;
  const agentName = agent?.name || formatLabel(agentId);
  const agentNumber = agent?.number || "01";
  const agentColor = agent?.color || "green";

  // Live or fallback labels
  const allLabels =
    agentData?.all_labels && agentData.all_labels.length > 0
      ? agentData.all_labels
      : spec.labels.map((l) => ({
          label: l.name,
          probability: 0.0,
          active: false,
        }));

  // Token breakdown from text or agentData
  const rawTokens =
    agentData?.tokens && agentData.tokens.length > 0
      ? agentData.tokens
      : text
      ? text
          .toLowerCase()
          .replace(/[^\w\s']/g, " ")
          .trim()
          .split(/\s+/)
          .filter(Boolean)
      : ["i'm", "fine", "with", "whatever", "you", "decide", "the", "current", "plan", "should", "probably", "work"];

  const inVocabTokens =
    agentData?.in_vocab_tokens ||
    rawTokens.filter((t) => spec.sampleVocab.includes(t.toLowerCase()));

  const vocabSize = agentData?.vocab_size || spec.vocabSize;

  const filteredVocab = spec.sampleVocab.filter((w) =>
    w.toLowerCase().includes(vocabSearch.toLowerCase())
  );

  return (
    <div className="telemetry-modal-backdrop" onClick={onClose}>
      <div
        className={`telemetry-modal-shell ${agentColor}`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <header className="telemetry-modal-header">
          <div className="telemetry-header-left">
            <span className="telemetry-agent-num">{agentNumber}</span>
            <div>
              <h3>
                {agentName.toUpperCase()} • TELEMETRY & SPECIFICATION
              </h3>
              <small>
                {agent?.subtitle || "Neural Architecture & Signal Breakdown"}
              </small>
            </div>
          </div>

          <button
            type="button"
            className="telemetry-close-btn"
            onClick={onClose}
            title="Close [Esc]"
          >
            <X size={16} />
          </button>
        </header>

        {/* Tab Navigation */}
        <div className="telemetry-tabs-nav">
          <button
            type="button"
            className={`telemetry-tab-btn ${activeTab === "labels" ? "active" : ""}`}
            onClick={() => setActiveTab("labels")}
          >
            <Tag size={13} />
            <span>Label Space & Probabilities</span>
            <span className="tab-count-badge">
              {allLabels.filter((l) => l.active).length} / {allLabels.length} Active
            </span>
          </button>

          <button
            type="button"
            className={`telemetry-tab-btn ${activeTab === "vocab" ? "active" : ""}`}
            onClick={() => setActiveTab("vocab")}
          >
            <Search size={13} />
            <span>Vocabulary & Tokens</span>
            <span className="tab-count-badge">
              {rawTokens.length} Tokens / {vocabSize} Vocab
            </span>
          </button>

          <button
            type="button"
            className={`telemetry-tab-btn ${activeTab === "architecture" ? "active" : ""}`}
            onClick={() => setActiveTab("architecture")}
          >
            <Cpu size={13} />
            <span>Neural Architecture</span>
            <span className="tab-count-badge">CUDA • GPU</span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="telemetry-modal-body">
          {/* TAB 1: LABELS */}
          {activeTab === "labels" && (
            <div className="telemetry-tab-panel">
              <div className="panel-intro-bar">
                <div>
                  <strong>Agent Label Space & Thresholds</strong>
                  <small>
                    Threshold $\ge 50.0\%$ triggers an active forensic finding.
                  </small>
                </div>
                <span className="telemetry-pill">
                  {allLabels.filter((l) => l.active).length} Activated
                </span>
              </div>

              <div className="labels-telemetry-list">
                {allLabels.map((item, idx) => {
                  const prob = Number(item.probability || 0);
                  const pct = (prob <= 1 ? prob * 100 : prob).toFixed(1);
                  const isActive = item.active || prob >= 0.5;
                  const labelDesc =
                    spec.labels.find((l) => l.name === item.label)?.desc ||
                    "Calibrated multi-agent output probability for this communicative dimension.";

                  return (
                    <div
                      key={idx}
                      className={`telemetry-label-row ${isActive ? "active" : ""}`}
                    >
                      <div className="label-meta-col">
                        <div className="label-name-row">
                          <span className={`label-status-dot ${isActive ? "active" : ""}`} />
                          <strong>{formatLabel(item.label)}</strong>
                          <span className={`label-state-tag ${isActive ? "active" : ""}`}>
                            {isActive ? "ACTIVE (≥ 50%)" : "INACTIVE (< 50%)"}
                          </span>
                        </div>
                        <p className="label-desc-text">{labelDesc}</p>
                      </div>

                      <div className="label-meter-col">
                        <div className="label-meter-track">
                          <div
                            className={`label-meter-fill ${isActive ? "active" : ""}`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <span className={`label-prob-val ${isActive ? "active" : ""}`}>
                          {pct}%
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 2: VOCABULARY & TOKENS */}
          {activeTab === "vocab" && (
            <div className="telemetry-tab-panel">
              <div className="vocab-stats-ribbon">
                <div className="v-stat-card">
                  <small>TOTAL MODEL VOCAB</small>
                  <strong>{vocabSize} Tokens</strong>
                  <span>Trained Subword/WordPiece</span>
                </div>
                <div className="v-stat-card">
                  <small>INPUT TOKENS</small>
                  <strong>{rawTokens.length} Processed</strong>
                  <span>Parsed from active message</span>
                </div>
                <div className="v-stat-card">
                  <small>IN-VOCAB MATCH</small>
                  <strong className="text-green">
                    {inVocabTokens.length} Tokens
                  </strong>
                  <span>Recognized vocabulary subset</span>
                </div>
              </div>

              <div className="tokenized-input-section">
                <span className="token-section-title">
                  TOKENS EXTRACTED FROM CURRENT MESSAGE:
                </span>
                <div className="token-chips-wrap">
                  {rawTokens.map((token, i) => {
                    const isMatched = inVocabTokens.includes(token.toLowerCase());
                    return (
                      <span
                        key={i}
                        className={`token-chip ${isMatched ? "matched" : "unk"}`}
                        title={
                          isMatched
                            ? `In-Vocabulary: '${token}' matches model token table`
                            : `Out-of-Vocabulary / Generic token: '${token}'`
                        }
                      >
                        {isMatched ? <Check size={10} /> : <Info size={10} />}
                        <span>{token}</span>
                      </span>
                    );
                  })}
                </div>
              </div>

              <div className="vocab-explorer-section">
                <div className="vocab-search-row">
                  <span className="token-section-title">
                    EXPLORE MODEL VOCABULARY WORDS:
                  </span>
                  <div className="vocab-search-box">
                    <Search size={13} />
                    <input
                      type="text"
                      placeholder="Search vocabulary tokens..."
                      value={vocabSearch}
                      onChange={(e) => setVocabSearch(e.target.value)}
                    />
                  </div>
                </div>

                <div className="vocab-sample-grid">
                  {filteredVocab.map((w, idx) => (
                    <span key={idx} className="vocab-sample-item">
                      {w}
                    </span>
                  ))}
                  {filteredVocab.length === 0 && (
                    <span className="empty-vocab-msg">
                      No matching vocabulary tokens found.
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: NEURAL ARCHITECTURE */}
          {activeTab === "architecture" && (
            <div className="telemetry-tab-panel">
              <div className="arch-specs-grid">
                <div className="spec-card">
                  <small>MODEL TOPOLOGY</small>
                  <strong>{spec.architecture}</strong>
                  <span>Bidirectional Transformer Encoder</span>
                </div>
                <div className="spec-card">
                  <small>HARDWARE ACCELERATION</small>
                  <strong className="text-cyan">
                    NVIDIA RTX 3050 (CUDA 12.8)
                  </strong>
                  <span>Direct GPU Tensor Ingestion</span>
                </div>
                <div className="spec-card">
                  <small>MAX SEQUENCE LENGTH</small>
                  <strong>128 Tokens</strong>
                  <span>With &lt;PAD&gt;, &lt;BOS&gt;, &lt;EOS&gt; framing</span>
                </div>
                <div className="spec-card">
                  <small>OPTIMIZATION & LOSS</small>
                  <strong>BCEWithLogitsLoss</strong>
                  <span>Independent multi-label classification</span>
                </div>
              </div>

              <div className="pipeline-flow-callout">
                <div className="flow-callout-header">
                  <Sparkles size={14} className="text-green" />
                  <strong>How {agentName} Connects in the Pipeline:</strong>
                </div>
                <p>
                  This agent executes concurrently inside the FastAPI ThreadPoolExecutor on GPU CUDA streams. Its raw logits are mapped via sigmoid activation into the 25-dimensional feature tensor which directly feeds into <strong>M5 Synthesizer</strong> for calibrated multi-agent subtext resolution.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="telemetry-modal-footer">
          <small>
            L.I.M.I.N.A.L. Neural Telemetry Engine • PyTorch CUDA 12.8
          </small>
          <button
            type="button"
            className="telemetry-done-btn"
            onClick={onClose}
          >
            Done
          </button>
        </footer>
      </div>
    </div>
  );
}
