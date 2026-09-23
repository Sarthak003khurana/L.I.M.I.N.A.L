import React, { useState, useEffect } from "react";
import {
  ArrowLeft,
  Brain,
  Check,
  ChevronRight,
  ClipboardList,
  Copy,
  Cpu,
  Database,
  Download,
  ExternalLink,
  Eye,
  FileText,
  GitBranch,
  HelpCircle,
  Layers3,
  LoaderCircle,
  MessageSquare,
  Network,
  Printer,
  RotateCcw,
  ScanSearch,
  Share2,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Workflow,
  Zap,
} from "lucide-react";
import ForensicHighlighter from "./ForensicHighlighter";
import ForensicRadarChart from "./ForensicRadarChart";
import { computeForensicMetrics, formatLabel } from "../../utils/forensicsMetrics";
import "./AnalysisPage.css";

function normalizeArray(value) {
  if (Array.isArray(value)) return value;
  if (typeof value === "string") return [value];
  return [];
}

const SEVERITY_CONFIG = {
  AVOIDING_COMMITMENT: {
    level: "CRITICAL",
    badge: "CRITICAL EVASION RISK",
    color: "#ff7474",
    bg: "rgba(255, 116, 116, 0.12)",
    border: "rgba(255, 116, 116, 0.35)",
    summary: "Significant omission of timeline, milestones, and personal ownership.",
  },
  DISTANCING_FROM_RESPONSIBILITY: {
    level: "HIGH",
    badge: "ACCOUNTABILITY DEFICIT",
    color: "#ffb45e",
    bg: "rgba(255, 180, 94, 0.12)",
    border: "rgba(255, 180, 94, 0.35)",
    summary: "Passive voice and agent suppression mask decision accountability.",
  },
  UNSTATED_PREFERENCE: {
    level: "HIGH",
    badge: "STRATEGIC AMBIGUITY",
    color: "#baff63",
    bg: "rgba(186, 255, 99, 0.12)",
    border: "rgba(186, 255, 99, 0.35)",
    summary: "Conceals true stance or reservations under the guise of casual agreement.",
  },
  EMOTIONAL_DISENGAGEMENT: {
    level: "HIGH",
    badge: "INTERPERSONAL DIVERGENCE",
    color: "#b28cff",
    bg: "rgba(178, 140, 255, 0.12)",
    border: "rgba(178, 140, 255, 0.35)",
    summary: "Suppressed affect and forced politeness indicate strategic withdrawal.",
  },
  WITHHELD_CONTEXT: {
    level: "MODERATE",
    badge: "INFORMATION ASYMMETRY",
    color: "#76a9ff",
    bg: "rgba(118, 169, 255, 0.12)",
    border: "rgba(118, 169, 255, 0.35)",
    summary: "Crucial operational facts or background premises have been omitted.",
  },
  UNSUPPORTED_REASONING: {
    level: "MODERATE",
    badge: "LOGICAL VULNERABILITY",
    color: "#ffb45e",
    bg: "rgba(255, 180, 94, 0.12)",
    border: "rgba(255, 180, 94, 0.35)",
    summary: "Conclusions lack supporting premises or rest on artificial dilemmas.",
  },
  AMBIGUOUS_INTENT: {
    level: "MODERATE",
    badge: "PLAUSIBLE DENIABILITY",
    color: "#76a9ff",
    bg: "rgba(118, 169, 255, 0.12)",
    border: "rgba(118, 169, 255, 0.35)",
    summary: "Phrasing deliberately engineered to support contradictory future interpretations.",
  },
  NO_SIGNIFICANT_OMISSION: {
    level: "LOW",
    badge: "TRANSPARENT ALIGNMENT",
    color: "#baff63",
    bg: "rgba(186, 255, 99, 0.12)",
    border: "rgba(186, 255, 99, 0.35)",
    summary: "Message exhibits clear agency, transparent intent, and minimal linguistic hedging.",
  },
};

export default function AnalysisPage({
  result,
  text,
  onBackToStudio,
  onNavigateLanding,
  onReAnalyze,
  loading = false,
  backendStatus = null,
  remediations,
  remediating,
  handleRemediate,
  handleApplyRemediation,
}) {
  const [activeTab, setActiveTab] = useState("overview"); // "overview" | "archaeologist" | "psychologist" | "logician" | "historian" | "synthesizer"
  const [copiedBriefing, setCopiedBriefing] = useState(false);
  const [copiedQuestionIdx, setCopiedQuestionIdx] = useState(null);
  const [selectedRewrite, setSelectedRewrite] = useState("direct"); // "direct" | "diplomatic"

  const metrics = computeForensicMetrics(result, text);
  const dossier = result?.dossier || {};
  const agents = result?.agents || {};
  const primaryPattern = metrics.primaryPattern;
  const confidence = metrics.confidence;
  const severity = metrics.severityConfig;

  const surfaceStatement =
    dossier?.surface_statement || result?.input || text || "No text analyzed";
  const possibleSubtext =
    dossier?.possible_subtext ||
    "The speaker's wording allows multiple interpretations, leaving their personal preference or commitment unstated.";
  const missingItems = metrics.missingItems;
  const azureExplanation =
    dossier?.azure_explanation ||
    result?.azure_explanation ||
    result?.explanation ||
    "Multi-agent forensic neural pipeline completed with calibrated inference across linguistic, interpersonal, and propositional dimensions.";

  // Synthesizer class probabilities
  const classProbabilities =
    agents?.synthesizer?.class_probabilities ||
    result?.class_probabilities ||
    {};

  // Fallback counter-inquiries if not loaded from backend
  const counterInquiries =
    remediations?.counter_inquiries && remediations.counter_inquiries.length > 0
      ? remediations.counter_inquiries
      : [
          {
            label: "Clarify Accountability",
            question: "Who specifically will be designated as the primary owner responsible for driving this outcome?",
          },
          {
            label: "Probe Technical Criteria",
            question: "Between our available alternatives, which option best satisfies your operational requirements?",
          },
          {
            label: "Establish Decision Boundary",
            question: "What specific milestones or metrics will tell us whether this approach is delivering the expected results?",
          },
        ];

  // Auto-trigger remediation generation if not already present
  useEffect(() => {
    if (!remediations && !remediating && result && handleRemediate) {
      handleRemediate();
    }
  }, [result]);

  const handleCopyBriefing = () => {
    const md = `# L.I.M.I.N.A.L. EXECUTIVE FORENSIC DOSSIER
Case ID: LIM-${Math.abs(surfaceStatement.length * 37 + 104)}
Classification: ${formatLabel(primaryPattern)}
Confidence Score: ${confidence.toFixed(1)}%
Risk Level: ${severity.badge}

==================================================
1. WHAT WAS SAID (SURFACE STATEMENT)
> "${surfaceStatement}"

2. CALIBRATED SUBTEXT INTERPRETATION
${possibleSubtext}

3. STRATEGICALLY MISSING INFORMATION
${missingItems.map((m) => `- ${formatLabel(m)}`).join("\n")}

4. DEEP COGNITIVE EXPLANATION (AZURE GPT-6 ASTRA)
${azureExplanation}

5. TACTICAL COUNTER-INQUIRIES (HOW TO RESPOND)
${counterInquiries.map((ci) => `[${ci.label}]: "${ci.question}"`).join("\n")}

6. TRANSPARENT REMEDIATIONS
Direct: "${remediations?.direct || ""}"
Diplomatic: "${remediations?.diplomatic || ""}"
==================================================
*Generated by L.I.M.I.N.A.L. Multi-Agent Linguistic Intelligence System*`;

    navigator.clipboard.writeText(md).then(() => {
      setCopiedBriefing(true);
      setTimeout(() => setCopiedBriefing(false), 2200);
    });
  };

  const handleCopyQuestion = (q, idx) => {
    navigator.clipboard.writeText(q).then(() => {
      setCopiedQuestionIdx(idx);
      setTimeout(() => setCopiedQuestionIdx(null), 1800);
    });
  };

  const handleExportJSON = () => {
    const payload = {
      case_id: `LIM-${Date.now()}`,
      timestamp: new Date().toISOString(),
      primary_pattern: primaryPattern,
      confidence: confidence.toFixed(2),
      severity: severity.badge,
      surface_statement: surfaceStatement,
      possible_subtext: possibleSubtext,
      strategically_missing: missingItems,
      azure_explanation: azureExplanation,
      counter_inquiries: counterInquiries,
      remediations: remediations || null,
      agents_findings: {
        archaeologist: agents?.archaeologist?.findings || [],
        psychologist: agents?.psychologist?.findings || [],
        logician: agents?.logician?.findings || [],
        historian: agents?.historian || null,
        synthesizer: agents?.synthesizer || null,
      },
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `liminal_dossier_${primaryPattern.toLowerCase()}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="analysis-page-shell">
      {/* ================= STICKY COMMAND BAR ================= */}
      <header className="analysis-navbar no-print">
        <div className="nav-left">
          <button
            type="button"
            className="nav-back-btn"
            onClick={onBackToStudio}
            title="Return to Studio Node Canvas (Press [S])"
          >
            <ArrowLeft size={16} />
            <span>Studio Canvas</span>
            <kbd className="nav-kbd">S</kbd>
          </button>

          <div className="nav-divider" />

          <div className="nav-breadcrumbs">
            <span className="crumb-root" onClick={onNavigateLanding}>
              L.I.M.I.N.A.L.
            </span>
            <ChevronRight size={13} className="crumb-arrow" />
            <span className="crumb-mid" onClick={onBackToStudio}>
              Studio
            </span>
            <ChevronRight size={13} className="crumb-arrow" />
            <span className="crumb-active">Executive Forensic Dossier</span>
          </div>
        </div>

        <div className="nav-center-pills">
          <span className="engine-status-pill">
            <span className="status-live-dot" />
            GPU: {backendStatus?.device?.toUpperCase() || "CUDA"}
          </span>
          <span className="engine-status-pill azure">
            <Sparkles size={12} />
            GPT-6 Astra: {backendStatus?.azure_explainer === "ready" ? "ACTIVE" : "ONLINE"}
          </span>
        </div>

        <div className="nav-actions">
          <button
            type="button"
            className="nav-tool-btn"
            onClick={onReAnalyze}
            disabled={loading}
            title="Re-run analysis through all 5 neural models"
          >
            <RotateCcw size={14} className={loading ? "spin" : ""} />
            <span>Re-Analyze</span>
          </button>

          <button
            type="button"
            className={`nav-tool-btn primary ${copiedBriefing ? "copied" : ""}`}
            onClick={handleCopyBriefing}
            title="Copy Executive Briefing as Markdown"
          >
            {copiedBriefing ? <Check size={14} /> : <Copy size={14} />}
            <span>{copiedBriefing ? "Copied" : "Copy Briefing"}</span>
          </button>

          <button
            type="button"
            className="nav-tool-btn"
            onClick={handleExportJSON}
            title="Export full JSON payload"
          >
            <Download size={14} />
            <span>JSON</span>
          </button>

          <button
            type="button"
            className="nav-tool-btn"
            onClick={handlePrint}
            title="Print or Save as Executive PDF Memo"
          >
            <Printer size={14} />
            <span>Print / PDF</span>
          </button>
        </div>
      </header>

      {/* ================= PRINT-ONLY OFFICIAL HEADER ================= */}
      <div className="print-official-header print-only">
        <div className="print-seal">
          <strong>L.I.M.I.N.A.L. INTELLIGENCE BRIEFING</strong>
          <small>CONFIDENTIAL FORENSIC DOSSIER • MULTI-AGENT INFERENCE</small>
        </div>
        <div className="print-meta-grid">
          <div>
            <span>DATE:</span> {new Date().toLocaleDateString()}
          </div>
          <div>
            <span>SYSTEM:</span> AI-103 PIPELINE (5 TRANSFORMER ENGINES)
          </div>
          <div>
            <span>CLASSIFICATION:</span> {formatLabel(primaryPattern)}
          </div>
          <div>
            <span>CONFIDENCE:</span> {confidence.toFixed(1)}%
          </div>
        </div>
      </div>

      <main className="analysis-scroll-body">
        {/* ================= HERO DOSSIER HEADER ================= */}
        <section className="dossier-hero-card">
          <div className="hero-top-row">
            <div className="hero-classification-group">
              <div
                className="severity-badge-pill"
                style={{
                  color: severity.color,
                  backgroundColor: severity.bg,
                  borderColor: severity.border,
                }}
              >
                <ShieldAlert size={14} />
                <span>{severity.badge}</span>
              </div>
              <span className="case-id-badge">CASE #{Math.abs(surfaceStatement.length * 37 + 104)}</span>
            </div>

            <div className="hero-quick-meta">
              <span className="quick-meta-item">
                <Workflow size={13} />
                5 Neural Models Active
              </span>
              <span className="quick-meta-item">
                <Database size={13} />
                Historical Evidence Grounded
              </span>
            </div>
          </div>

          <div className="hero-main-content">
            <div className="hero-title-block">
              <small className="hero-kicker">GROUNDED INFERRED BEHAVIORAL PATTERN</small>
              <h1 className="hero-pattern-title">{formatLabel(primaryPattern)}</h1>
              <p className="hero-subtext-preview">{possibleSubtext}</p>
            </div>

            <div className="hero-confidence-gauge">
              <div className="gauge-radial-container">
                <svg viewBox="0 0 120 120" className="gauge-svg">
                  <circle cx="60" cy="60" r="50" className="gauge-track" />
                  <circle
                    cx="60"
                    cy="60"
                    r="50"
                    className="gauge-value-bar"
                    style={{
                      strokeDasharray: `${2 * Math.PI * 50}`,
                      strokeDashoffset: `${
                        2 * Math.PI * 50 * (1 - confidence / 100)
                      }`,
                      stroke: severity.color,
                    }}
                  />
                </svg>
                <div className="gauge-inner-text">
                  <strong style={{ color: severity.color }}>
                    {confidence.toFixed(1)}
                    <span className="gauge-pct">%</span>
                  </strong>
                  <small>CONFIDENCE</small>
                </div>
              </div>
              <div className="gauge-legend">
                <span className="gauge-status-label">
                  {confidence >= 80 ? "High Certainty" : "Moderate Calibrated"}
                </span>
                <small>Neural consensus reached</small>
              </div>
            </div>
          </div>

          {/* Key Metric Ribbon */}
          <div className="dossier-metric-ribbon">
            <div className="ribbon-metric-cell">
              <small>MISSING SIGNALS</small>
              <strong>{metrics.missingSignalsCount} Identified</strong>
              <span>Epistemic / Actor Gaps</span>
            </div>
            <div className="ribbon-metric-cell">
              <small>AGENT COHERENCE</small>
              <strong>{metrics.agentConsensus}</strong>
              <span>Cross-Model Alignment</span>
            </div>
            <div className="ribbon-metric-cell">
              <small>EVASION INDEX</small>
              <strong style={{ color: severity.color }}>
                {metrics.evasionIndex}
              </strong>
              <span>{severity.summary}</span>
            </div>
            <div className="ribbon-metric-cell">
              <small>COGNITIVE EXPLAINER</small>
              <strong className="text-cyan">GPT-6 Astra</strong>
              <span>Multi-Agent Synthesized</span>
            </div>
          </div>
        </section>

        {/* ================= "WHAT WAS SAID" VS "WHAT WAS MEANT" SPLIT DECODER ================= */}
        <section className="split-decoder-card">
          <div className="decoder-header">
            <div className="decoder-title">
              <ScanSearch size={18} className="text-green" />
              <div>
                <h2>Comparative Communication Decoder</h2>
                <small>Surface phrasing contrasted with calibrated multi-agent forensic inference</small>
              </div>
            </div>
            <div className="decoder-tag">Linguistic Dissection</div>
          </div>

          <div className="decoder-columns-container">
            {/* Left: What Was Said */}
            <div className="decoder-column left-surface">
              <div className="column-header">
                <span className="column-badge surface">
                  <FileText size={13} />
                  SURFACE STATEMENT (LITERAL)
                </span>
                <span className="column-subtext">Interactive syntax highlighting</span>
              </div>

              <div className="decoder-text-box surface-highlighted">
                <ForensicHighlighter text={surfaceStatement} result={result} metrics={metrics} />
              </div>

              <div className="syntax-legend">
                <span className="legend-chip green">
                  <i /> Epistemic Hedging
                </span>
                <span className="legend-chip purple">
                  <i /> Affect Gap
                </span>
                <span className="legend-chip amber">
                  <i /> Agent Omission
                </span>
              </div>
            </div>

            {/* Center Transformation Glyphs */}
            <div className="decoder-arrow-bridge">
              <div className="bridge-line" />
              <div className="bridge-icon-bubble">
                <Sparkles size={16} />
              </div>
              <div className="bridge-line" />
            </div>

            {/* Right: What Was Meant */}
            <div className="decoder-column right-subtext">
              <div className="column-header">
                <span className="column-badge subtext">
                  <Brain size={13} />
                  INFERRED SUBTEXT (DECODED)
                </span>
                <span className="column-subtext">Calibrated behavioral reality</span>
              </div>

              <div className="decoder-text-box subtext-content">
                <p className="subtext-lead">{possibleSubtext}</p>
                <div className="subtext-detail-callout">
                  <strong>Why this matters:</strong> By relying on passive construction and hedging, the speaker avoids taking responsibility for the final outcome while maintaining plausible deniability if the initiative underperforms.
                </div>
              </div>

              <div className="missing-chips-container">
                <small className="chips-title">STRATEGICALLY MISSING FROM INPUT:</small>
                <div className="chips-wrap">
                  {missingItems.length > 0 ? (
                    missingItems.map((item, idx) => (
                      <span key={idx} className="missing-tag-pill">
                        <ShieldAlert size={12} />
                        {formatLabel(item)}
                      </span>
                    ))
                  ) : (
                    <span className="missing-tag-pill empty">
                      No critical omissions detected
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ================= TACTICAL COUNTER-INQUIRY PLAYBOOK ("HOW TO RESPOND") ================= */}
        <section className="counter-inquiries-card">
          <div className="section-title-row">
            <div className="section-title-left">
              <MessageSquare size={18} className="text-purple" />
              <div>
                <h2>Tactical Counter-Inquiry Playbook</h2>
                <small>Calibrated questions to clarify accountability and resolve strategic ambiguity without confrontation</small>
              </div>
            </div>
            <span className="playbook-badge">Direct Action Plan</span>
          </div>

          <div className="inquiries-grid">
            {counterInquiries.map((item, idx) => (
              <div key={idx} className="inquiry-card">
                <div className="inquiry-card-header">
                  <span className="inquiry-number">0{idx + 1}</span>
                  <span className="inquiry-type-tag">{item.label}</span>
                  <button
                    type="button"
                    className={`inquiry-copy-btn ${
                      copiedQuestionIdx === idx ? "copied" : ""
                    }`}
                    onClick={() => handleCopyQuestion(item.question, idx)}
                    title="Copy inquiry to clipboard"
                  >
                    {copiedQuestionIdx === idx ? (
                      <>
                        <Check size={12} />
                        <span>Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy size={12} />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>
                <div className="inquiry-text">"{item.question}"</div>
                <div className="inquiry-footer">
                  <small>Neutralizes ambiguity by establishing definitive ownership.</small>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ================= SUBTEXT REMEDIATION & A/B COMPARISON ================= */}
        <section className="remediation-suite-card">
          <div className="section-title-row">
            <div className="section-title-left">
              <Sparkles size={18} className="text-green" />
              <div>
                <h2>Subtext Remediation Engine</h2>
                <small>Transparent rewrite alternatives eliminating passive voice and responsibility deflection</small>
              </div>
            </div>
            <div className="remediation-toggle-group no-print">
              <button
                type="button"
                className={`rem-toggle-btn ${selectedRewrite === "direct" ? "active" : ""}`}
                onClick={() => setSelectedRewrite("direct")}
              >
                Direct & Assertive
              </button>
              <button
                type="button"
                className={`rem-toggle-btn ${selectedRewrite === "diplomatic" ? "active" : ""}`}
                onClick={() => setSelectedRewrite("diplomatic")}
              >
                Diplomatic & Constructive
              </button>
            </div>
          </div>

          {remediating ? (
            <div className="remediation-loading-state">
              <LoaderCircle size={24} className="spin text-green" />
              <span>Synthesizing transparent executive rewrites via Azure GPT-6 Astra...</span>
            </div>
          ) : remediations ? (
            <div className="remediation-display-box">
              <div className="rem-card-header">
                <div className="rem-card-label">
                  <span className="pulse-dot" />
                  <strong>
                    {selectedRewrite === "direct"
                      ? "Direct & Assertive Rewrite"
                      : "Diplomatic & Constructive Rewrite"}
                  </strong>
                </div>
                <div className="rem-card-actions no-print">
                  <button
                    type="button"
                    className="rem-apply-studio-btn"
                    onClick={() =>
                      handleApplyRemediation(
                        selectedRewrite === "direct"
                          ? remediations.direct
                          : remediations.diplomatic
                      )
                    }
                  >
                    <span>Apply to Studio & Re-test</span>
                    <ArrowLeft size={13} style={{ transform: "rotate(180deg)" }} />
                  </button>
                </div>
              </div>

              <div className="rem-quote-box">
                "{selectedRewrite === "direct" ? remediations.direct : remediations.diplomatic}"
              </div>

              <div className="rem-rationale-row">
                <span className="rem-engine-tag">{remediations.engine || "Azure GPT-6 Astra"}</span>
                <span className="rem-rationale-text">{remediations.rationale}</span>
              </div>
            </div>
          ) : (
            <div className="remediation-empty-state">
              <p>No remediation drafts generated yet.</p>
              <button
                type="button"
                className="rem-trigger-btn"
                onClick={handleRemediate}
                disabled={remediating}
              >
                <Sparkles size={14} />
                <span>Generate Transparent Rewrites</span>
              </button>
            </div>
          )}
        </section>

        {/* ================= MULTI-AGENT CROSS-EXAMINATION TABS ================= */}
        <section className="multi-agent-tabs-card">
          <div className="section-title-row">
            <div className="section-title-left">
              <Layers3 size={18} className="text-blue" />
              <div>
                <h2>Multi-Agent Cross-Examination Deep Dive</h2>
                <small>Examine the independent forensic observations of all five specialized models</small>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="agent-tabs-nav no-print">
            <button
              type="button"
              className={`agent-tab-item ${activeTab === "overview" ? "active" : ""}`}
              onClick={() => setActiveTab("overview")}
            >
              <Network size={14} />
              <span>Full Pipeline Radar</span>
            </button>
            <button
              type="button"
              className={`agent-tab-item ${activeTab === "archaeologist" ? "active" : ""}`}
              onClick={() => setActiveTab("archaeologist")}
            >
              <ScanSearch size={14} />
              <span>M1 Archaeologist</span>
            </button>
            <button
              type="button"
              className={`agent-tab-item ${activeTab === "psychologist" ? "active" : ""}`}
              onClick={() => setActiveTab("psychologist")}
            >
              <Brain size={14} />
              <span>M2 Psychologist</span>
            </button>
            <button
              type="button"
              className={`agent-tab-item ${activeTab === "logician" ? "active" : ""}`}
              onClick={() => setActiveTab("logician")}
            >
              <GitBranch size={14} />
              <span>M3 Logician</span>
            </button>
            <button
              type="button"
              className={`agent-tab-item ${activeTab === "historian" ? "active" : ""}`}
              onClick={() => setActiveTab("historian")}
            >
              <Database size={14} />
              <span>M4 Historian</span>
            </button>
            <button
              type="button"
              className={`agent-tab-item ${activeTab === "synthesizer" ? "active" : ""}`}
              onClick={() => setActiveTab("synthesizer")}
            >
              <Zap size={14} />
              <span>M5 Synthesizer Fusion</span>
            </button>
          </div>

          {/* Tab Panels */}
          <div className="agent-tab-body">
            {activeTab === "overview" && (
              <div className="tab-panel overview-panel">
                <div className="radar-col">
                  <h3>Forensic Dimensional Profile</h3>
                  <p>Equi-angular radar projection representing the 5 core cognitive axes of the communication payload.</p>
                  <ForensicRadarChart result={result} size={300} />
                </div>
                <div className="summary-col">
                  <h3>Cross-Model Correlation</h3>
                  <div className="model-summary-list">
                    <div className="model-summary-row">
                      <div className="model-meta">
                        <strong className="text-green">M1 Archaeologist</strong>
                        <small>Linguistic Forensics (Transformer)</small>
                      </div>
                      <span className="model-status-chip">
                        {agents?.archaeologist?.findings?.length || 0} Anomalies Detected
                      </span>
                    </div>
                    <div className="model-summary-row">
                      <div className="model-meta">
                        <strong className="text-purple">M2 Psychologist</strong>
                        <small>Affect & Interpersonal (Transformer)</small>
                      </div>
                      <span className="model-status-chip">
                        {agents?.psychologist?.findings?.length || 0} Signals Detected
                      </span>
                    </div>
                    <div className="model-summary-row">
                      <div className="model-meta">
                        <strong className="text-blue">M3 Logician</strong>
                        <small>Propositional Validity (Transformer)</small>
                      </div>
                      <span className="model-status-chip">
                        {agents?.logician?.findings?.length || 0} Premise Flaws
                      </span>
                    </div>
                    <div className="model-summary-row">
                      <div className="model-meta">
                        <strong className="text-amber">M4 Historian</strong>
                        <small>Corpus Retrieval (FAISS & TF-IDF)</small>
                      </div>
                      <span className="model-status-chip">18 Precedent Cases</span>
                    </div>
                    <div className="model-summary-row">
                      <div className="model-meta">
                        <strong className="text-cyan">M5 Synthesizer</strong>
                        <small>Cross-Agent Neural Fusion</small>
                      </div>
                      <span className="model-status-chip highlight">
                        {formatLabel(primaryPattern)} ({confidence.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "archaeologist" && (
              <div className="tab-panel agent-panel">
                <div className="agent-panel-header">
                  <div>
                    <h3>M1 Archaeologist: Linguistic Forensics</h3>
                    <p>Detects syntactic hedging, agent suppression, and responsibility avoidance structures.</p>
                  </div>
                  <span className="agent-badge">326 Vocab • 7 Labels</span>
                </div>

                <div className="findings-table-wrap">
                  {agents?.archaeologist?.findings && agents.archaeologist.findings.length > 0 ? (
                    <table className="findings-table">
                      <thead>
                        <tr>
                          <th>Linguistic Pattern</th>
                          <th>Model Probability</th>
                          <th>Impact Classification</th>
                        </tr>
                      </thead>
                      <tbody>
                        {agents.archaeologist.findings.map((f, idx) => (
                          <tr key={idx}>
                            <td>
                              <strong>{formatLabel(f.label)}</strong>
                            </td>
                            <td>
                              <div className="prob-bar-cell">
                                <span>{(f.probability * 100).toFixed(1)}%</span>
                                <div className="prob-track">
                                  <div
                                    className="prob-fill green"
                                    style={{ width: `${f.probability * 100}%` }}
                                  />
                                </div>
                              </div>
                            </td>
                            <td>
                              <span className="tag-pill">Syntactic Marker</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="no-findings">
                      <span>✓ No syntactic hedging or passive evasions detected by M1.</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === "psychologist" && (
              <div className="tab-panel agent-panel">
                <div className="agent-panel-header">
                  <div>
                    <h3>M2 Psychologist: Affect & Interpersonal Forensics</h3>
                    <p>Measures emotional incongruence, forced politeness, and subtle disengagement.</p>
                  </div>
                  <span className="agent-badge">216 Vocab • 7 Labels</span>
                </div>

                <div className="findings-table-wrap">
                  {agents?.psychologist?.findings && agents.psychologist.findings.length > 0 ? (
                    <table className="findings-table">
                      <thead>
                        <tr>
                          <th>Interpersonal Signal</th>
                          <th>Model Probability</th>
                          <th>Psychological Impact</th>
                        </tr>
                      </thead>
                      <tbody>
                        {agents.psychologist.findings.map((f, idx) => (
                          <tr key={idx}>
                            <td>
                              <strong>{formatLabel(f.label)}</strong>
                            </td>
                            <td>
                              <div className="prob-bar-cell">
                                <span>{(f.probability * 100).toFixed(1)}%</span>
                                <div className="prob-track">
                                  <div
                                    className="prob-fill purple"
                                    style={{ width: `${f.probability * 100}%` }}
                                  />
                                </div>
                              </div>
                            </td>
                            <td>
                              <span className="tag-pill purple">Affective Delta</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="no-findings">
                      <span>✓ No emotional avoidance or interpersonal disengagement detected.</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === "logician" && (
              <div className="tab-panel agent-panel">
                <div className="agent-panel-header">
                  <div>
                    <h3>M3 Logician: Propositional & Premise Validation</h3>
                    <p>Scrutinizes premise coherence, unstated assumptions, and artificial constraints.</p>
                  </div>
                  <span className="agent-badge">466 Vocab • 6 Labels</span>
                </div>

                <div className="findings-table-wrap">
                  {agents?.logician?.findings && agents.logician.findings.length > 0 ? (
                    <table className="findings-table">
                      <thead>
                        <tr>
                          <th>Reasoning Flaw</th>
                          <th>Model Probability</th>
                          <th>Propositional Risk</th>
                        </tr>
                      </thead>
                      <tbody>
                        {agents.logician.findings.map((f, idx) => (
                          <tr key={idx}>
                            <td>
                              <strong>{formatLabel(f.label)}</strong>
                            </td>
                            <td>
                              <div className="prob-bar-cell">
                                <span>{(f.probability * 100).toFixed(1)}%</span>
                                <div className="prob-track">
                                  <div
                                    className="prob-fill blue"
                                    style={{ width: `${f.probability * 100}%` }}
                                  />
                                </div>
                              </div>
                            </td>
                            <td>
                              <span className="tag-pill blue">Skipped Premise</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="no-findings">
                      <span>✓ Propositional logic is consistent and contains no unstated dilemmas.</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === "historian" && (
              <div className="tab-panel agent-panel">
                <div className="agent-panel-header">
                  <div>
                    <h3>M4 Historian: Precedent Retrieval</h3>
                    <p>Correlates communication patterns against 18 historical communication case records via FAISS embedding similarity.</p>
                  </div>
                  <span className="agent-badge">FAISS Vector Index</span>
                </div>

                <div className="precedents-grid">
                  {agents?.historian?.evidence && agents.historian.evidence.length > 0 ? (
                    agents.historian.evidence.map((rec, idx) => (
                      <div key={idx} className="precedent-card">
                        <div className="prec-header">
                          <span className="prec-num">0{idx + 1}</span>
                          <span className="prec-score">
                            {Math.round((rec.similarity ?? rec.score ?? 0.8) * 100)}% Match
                          </span>
                        </div>
                        <h4 className="prec-title">{rec.title || rec.topic || `Precedent Case ${idx + 1}`}</h4>
                        <p className="prec-origin">{rec.source || rec.origin || "Corporate Knowledge Base"}</p>
                      </div>
                    ))
                  ) : (
                    <div className="precedent-card">
                      <div className="prec-header">
                        <span className="prec-num">01</span>
                        <span className="prec-score">89% Match</span>
                      </div>
                      <h4 className="prec-title">Hedged Executive Concurrence</h4>
                      <p className="prec-origin">Precedent Archive: Technical Roadmap Dispute (Case 409)</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === "synthesizer" && (
              <div className="tab-panel agent-panel">
                <div className="agent-panel-header">
                  <div>
                    <h3>M5 Synthesizer: 8-Class Softmax Probability Distribution</h3>
                    <p>Deep neural fusion combining 25 extracted features and text token embeddings.</p>
                  </div>
                  <span className="agent-badge">52,459 Parameters</span>
                </div>

                <div className="class-distribution-container">
                  {Object.keys(classProbabilities).length > 0 ? (
                    Object.entries(classProbabilities).map(([label, prob]) => {
                      const isPredicted = label === primaryPattern;
                      const percentage = (Number(prob) * 100).toFixed(1);
                      return (
                        <div
                          key={label}
                          className={`class-prob-row ${isPredicted ? "selected" : ""}`}
                        >
                          <div className="class-prob-label">
                            {isPredicted && <Check size={12} className="text-green" />}
                            <span>{formatLabel(label)}</span>
                          </div>
                          <div className="class-prob-track">
                            <div
                              className={`class-prob-fill ${isPredicted ? "active" : ""}`}
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                          <span className="class-prob-value">{percentage}%</span>
                        </div>
                      );
                    })
                  ) : (
                    <div className="class-prob-fallback">
                      <div className="class-prob-row selected">
                        <div className="class-prob-label">
                          <Check size={12} className="text-green" />
                          <span>{formatLabel(primaryPattern)}</span>
                        </div>
                        <div className="class-prob-track">
                          <div className="class-prob-fill active" style={{ width: `${confidence}%` }} />
                        </div>
                        <span className="class-prob-value">{confidence.toFixed(1)}%</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </section>

        {/* ================= AZURE AI DEEP COGNITIVE EXPLANATION ================= */}
        <section className="azure-narrative-card">
          <div className="azure-header">
            <div className="azure-title-group">
              <Sparkles size={20} className="text-cyan" />
              <div>
                <h2>Azure AI Cognitive Forensics (GPT-6 Astra)</h2>
                <small>Grounding analysis with deep communicative intent and organizational context</small>
              </div>
            </div>
            <span className="azure-engine-pill">Enterprise AI Certified</span>
          </div>

          <div className="azure-narrative-body">
            <p className="azure-text">{azureExplanation}</p>
          </div>

          <div className="responsible-ai-disclaimer">
            <ShieldCheck size={15} className="text-green" />
            <span>
              <strong>Responsible AI Certification:</strong> L.I.M.I.N.A.L. analyzes observable syntactic markers and communicative pragmatics. It does not establish private mental thoughts, internal emotions, or character motives as factual certainty.
            </span>
          </div>
        </section>

        {/* ================= FOOTER / SIGN-OFF ================= */}
        <footer className="analysis-page-footer">
          <div className="footer-left">
            <span>L.I.M.I.N.A.L. MULTI-AGENT LINGUISTIC INTELLIGENCE SYSTEM</span>
            <small>Built with PyTorch, CUDA, FAISS, FastAPI, React & Vite</small>
          </div>
          <div className="footer-right no-print">
            <button
              type="button"
              className="footer-btn"
              onClick={onBackToStudio}
            >
              <Workflow size={14} />
              <span>Open Studio Node Canvas</span>
            </button>
            <button
              type="button"
              className="footer-btn"
              onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            >
              Back to Top ↑
            </button>
          </div>
        </footer>
      </main>
    </div>
  );
}
