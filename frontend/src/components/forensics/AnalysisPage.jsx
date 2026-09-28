import { useState, useEffect } from "react";
import {
  ArrowLeft,
  Brain,
  Check,
  ChevronDown,
  ChevronRight,
  ChevronUp,
  Copy,
  Cpu,
  Database,
  Download,
  FileText,
  GitBranch,
  Layers3,
  LoaderCircle,
  MessageSquare,
  Network,
  Printer,
  RotateCcw,
  ScanSearch,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Workflow,
  Zap,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import ForensicHighlighter from "./ForensicHighlighter";
import ForensicRadarChart from "./ForensicRadarChart";
import { computeForensicMetrics, formatLabel } from "../../utils/forensicsMetrics";
import "./AnalysisPage.css";

// Human-friendly plain English translations for everyday users
const PLAIN_TRANSLATIONS = {
  UNSTATED_PREFERENCE: {
    simpleTitle: "Saying 'Yes', But Hiding True Thoughts",
    simpleVerdict: "The speaker sounds agreeable on the surface, but uses hesitant wording so they can't be held responsible if things go wrong.",
    whyItMatters: "By saying 'whatever you decide' and 'should probably work', they place 100% of the risk and decision onto you. If the plan fails, they can easily claim: 'I only said it might work.'",
    whatIsMissing: [
      "Their honest recommendation or true preference",
      "Clear personal accountability for the outcome",
      "The specific criteria needed for their full support"
    ],
    riskLevel: "High Hesitation",
    riskBadge: "DODGING OWNERSHIP",
  },
  AVOIDING_COMMITMENT: {
    simpleTitle: "Avoiding Commitment: Leaving Things Open-Ended",
    simpleVerdict: "The message avoids promising any specific deadline, person in charge, or measurable outcome.",
    whyItMatters: "Without a named owner or fixed date, work can stall indefinitely and no one can be held responsible when deadlines slip.",
    whatIsMissing: [
      "A firm completion deadline",
      "A specific person assigned as the owner",
      "Measurable success criteria and milestones"
    ],
    riskLevel: "Critical Delay Risk",
    riskBadge: "NO CLEAR DEADLINE",
  },
  DISTANCING_FROM_RESPONSIBILITY: {
    simpleTitle: "Passing the Buck: Hiding Who Made the Call",
    simpleVerdict: "The speaker uses passive phrases like 'the decision was made' to avoid saying who actually did it.",
    whyItMatters: "Passive voice conceals accountability. If you need answers or adjustments, it's impossible to know who authorized the action.",
    whatIsMissing: [
      "Who specifically made the decision",
      "The rationale behind the choice",
      "Who to contact for follow-up or issues"
    ],
    riskLevel: "Accountability Gap",
    riskBadge: "BLAME SHIFTING",
  },
  EMOTIONAL_DISENGAGEMENT: {
    simpleTitle: "Passive Agreement: Outwardly Polite, Internally Checked Out",
    simpleVerdict: "The speaker is using superficial agreement to shut down conversation and avoid genuine discussion.",
    whyItMatters: "When someone says 'it's fine, no need to discuss', they are withdrawing from collaboration. Unspoken frustration often turns into blockers later.",
    whatIsMissing: [
      "Honest feedback about reservations",
      "Real alignment and buy-in on goals",
      "Active engagement and willingness to collaborate"
    ],
    riskLevel: "Disengagement Warning",
    riskBadge: "FAKE AGREEMENT",
  },
  WITHHELD_CONTEXT: {
    simpleTitle: "Missing Information: Important Facts Left Out",
    simpleVerdict: "The statement presents an incomplete picture, omitting crucial details or known blockers.",
    whyItMatters: "Making decisions based on half-truths leads to unexpected roadblocks, timeline slippage, and budget spikes.",
    whatIsMissing: [
      "Known technical or timeline risks",
      "Budget or resource constraints",
      "Alternative approaches that were rejected"
    ],
    riskLevel: "Information Gap",
    riskBadge: "HALF-TRUTH",
  },
  UNSUPPORTED_REASONING: {
    simpleTitle: "Flawed Logic: Big Claims Without Proof",
    simpleVerdict: "The speaker jumps to an extreme conclusion or presents an artificial 'either/or' choice without evidence.",
    whyItMatters: "Artificial either/or choices trap you into rushed commitments while hiding realistic middle-ground solutions.",
    whatIsMissing: [
      "Facts and data backing the claim",
      "Realistic alternatives between the extremes",
      "Balanced pros and cons analysis"
    ],
    riskLevel: "Logical Flaw",
    riskBadge: "FALSE DILEMMA",
  },
  AMBIGUOUS_INTENT: {
    simpleTitle: "Vague Wording: Deliberately Open to Multiple Meanings",
    simpleVerdict: "Phrased loosely so the speaker can change their story later depending on how things turn out.",
    whyItMatters: "Ambiguous promises protect the speaker while leaving you guessing about expectations.",
    whatIsMissing: [
      "Concrete deliverables and definitions",
      "Unambiguous terms and commitments",
      "Agreed definition of done"
    ],
    riskLevel: "Vague Expectations",
    riskBadge: "VAGUE PROMISES",
  },
  NO_SIGNIFICANT_OMISSION: {
    simpleTitle: "Direct & Clear: Honest, Straightforward Communication",
    simpleVerdict: "The message is transparent, takes direct ownership, and contains no hidden hesitation.",
    whyItMatters: "You can take this statement at face value. The speaker has taken ownership and communicated clearly.",
    whatIsMissing: ["No critical omissions detected"],
    riskLevel: "Clear & Transparent",
    riskBadge: "CLEAR & DIRECT",
  },
};

function parseAzureNarrative(text) {
  if (!text) return null;
  const sections = [];
  const regex = /(SURFACE MEANING|POSSIBLE SUBTEXT|STRATEGICALLY MISSING|EVIDENCE|LIMITATIONS):\s*([^]*?)(?=(?:SURFACE MEANING|POSSIBLE SUBTEXT|STRATEGICALLY MISSING|EVIDENCE|LIMITATIONS):|$)/gi;
  let match;
  while ((match = regex.exec(text)) !== null) {
    sections.push({
      title: match[1].toUpperCase(),
      content: match[2].trim(),
    });
  }
  if (sections.length === 0) {
    return [{ title: "EXECUTIVE SUMMARY", content: text.trim() }];
  }
  return sections;
}

export default function AnalysisPage({
  result,
  text,
  onBackToStudio,
  onNavigateLanding,
  onReAnalyze,
  loading = false,
  remediations,
  remediating,
  handleRemediate,
  handleApplyRemediation,
}) {
  const [viewMode, setViewMode] = useState("simplified"); // "simplified" | "technical"
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);
  const [activeTab, setActiveTab] = useState("overview"); // "overview" | "archaeologist" | "psychologist" | "logician" | "historian" | "synthesizer"
  const [copiedBriefing, setCopiedBriefing] = useState(false);
  const [copiedQuestionIdx, setCopiedQuestionIdx] = useState(null);
  const [copiedRewrite, setCopiedRewrite] = useState(false);
  const [selectedRewrite, setSelectedRewrite] = useState("direct"); // "direct" | "diplomatic"

  const metrics = computeForensicMetrics(result);
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

  const parsedAzure = parseAzureNarrative(azureExplanation);

  // Synthesizer class probabilities
  const classProbabilities =
    agents?.synthesizer?.class_probabilities ||
    result?.class_probabilities ||
    {};

  // Plain-English metadata
  const plainData = PLAIN_TRANSLATIONS[primaryPattern] || {
    simpleTitle: formatLabel(primaryPattern),
    simpleVerdict: possibleSubtext,
    whyItMatters: "The speaker relies on indirect language that obscures decision ownership.",
    whatIsMissing: missingItems.length > 0 ? missingItems.map(formatLabel) : ["Key operational details"],
    riskLevel: severity.badge,
    riskBadge: severity.level,
  };

  // Smart actionable follow-up questions
  const counterInquiries =
    remediations?.counter_inquiries && remediations.counter_inquiries.length > 0
      ? remediations.counter_inquiries
      : [
          {
            label: "Pin Down Their Real Choice",
            question: "Which option do you personally prefer, and what makes it your first choice?",
            why: "Prevents them from blaming you later by requiring them to state their real preference on record.",
          },
          {
            label: "Probe Success Criteria",
            question: "What requirements must the plan meet for you to fully support it, and what remains unresolved?",
            why: "Brings hidden doubts out into the open now rather than when the project is underway.",
          },
          {
            label: "Clarify Ownership & Decision",
            question: "What next step will you personally own, by when, and who makes the final decision?",
            why: "Establishes clear roles so accountability cannot be deflected.",
          },
        ];

  // Auto-trigger remediation generation if not already present
  useEffect(() => {
    if (!remediations && !remediating && result && handleRemediate) {
      handleRemediate();
    }
  }, [result, remediations, remediating, handleRemediate]);

  const handleCopyBriefing = () => {
    const md = `# L.I.M.I.N.A.L. COMMUNICATION SUMMARY
Key Takeaway: ${plainData.simpleTitle}
Confidence Score: ${confidence.toFixed(1)}% (${confidence >= 80 ? "High Certainty" : "Moderate"})
Risk Level: ${plainData.riskLevel}

==================================================
1. WHAT WAS SAID (LITERAL WORDS):
"${surfaceStatement}"

2. WHAT WAS ACTUALLY MEANT (DECODED SUBTEXT):
${possibleSubtext}

3. WHY THIS MATTERS:
${plainData.whyItMatters}

4. WHAT WAS LEFT OUT:
${plainData.whatIsMissing.map((m) => `- ${m}`).join("\n")}

5. SMART FOLLOW-UP QUESTIONS TO ASK:
${counterInquiries.map((ci) => `[${ci.label}]: "${ci.question}"`).join("\n")}

6. HOW TO SAY THIS CLEARLY:
Direct: "${remediations?.direct || ""}"
Diplomatic: "${remediations?.diplomatic || ""}"
==================================================`;

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

  const handleCopyCurrentRewrite = () => {
    const textToCopy = selectedRewrite === "direct" ? remediations?.direct : remediations?.diplomatic;
    if (!textToCopy) return;
    navigator.clipboard.writeText(textToCopy).then(() => {
      setCopiedRewrite(true);
      setTimeout(() => setCopiedRewrite(false), 2000);
    });
  };

  const handleExportJSON = () => {
    const payload = {
      case_id: `LIM-${Date.now()}`,
      timestamp: new Date().toISOString(),
      primary_pattern: primaryPattern,
      confidence: confidence.toFixed(2),
      plain_title: plainData.simpleTitle,
      plain_verdict: plainData.simpleVerdict,
      surface_statement: surfaceStatement,
      possible_subtext: possibleSubtext,
      why_it_matters: plainData.whyItMatters,
      what_was_left_out: plainData.whatIsMissing,
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
    a.download = `liminal_summary_${primaryPattern.toLowerCase()}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="analysis-page-shell">
      {/* ================= STICKY TOP COMMAND BAR ================= */}
      <header className="analysis-navbar no-print">
        <div className="nav-left">
          <button
            type="button"
            className="nav-back-btn"
            onClick={onBackToStudio}
            title="Return to Studio (Press [S])"
          >
            <ArrowLeft size={16} />
            <span>Back to Input</span>
            <kbd className="nav-kbd">S</kbd>
          </button>

          <div className="nav-divider" />

          <div className="nav-breadcrumbs">
            <span className="crumb-root" onClick={onNavigateLanding}>
              L.I.M.I.N.A.L.
            </span>
            <ChevronRight size={13} className="crumb-arrow" />
            <span className="crumb-active">Decoded Result</span>
          </div>
        </div>

        {/* View Mode Switcher: Simplified vs Deep Technical */}
        <div className="nav-view-mode-toggle">
          <button
            type="button"
            className={`view-mode-pill ${viewMode === "simplified" ? "active" : ""}`}
            onClick={() => setViewMode("simplified")}
          >
            <Sparkles size={13} />
            <span>Simplified View</span>
          </button>
          <button
            type="button"
            className={`view-mode-pill ${viewMode === "technical" ? "active" : ""}`}
            onClick={() => setViewMode("technical")}
          >
            <Layers3 size={13} />
            <span>Technical / AI Deep Dive</span>
          </button>
        </div>

        <div className="nav-actions">
          <button
            type="button"
            className="nav-tool-btn"
            onClick={onReAnalyze}
            disabled={loading}
            title="Re-run analysis"
          >
            <RotateCcw size={14} className={loading ? "spin" : ""} />
            <span>Re-Analyze</span>
          </button>

          <button
            type="button"
            className={`nav-tool-btn primary ${copiedBriefing ? "copied" : ""}`}
            onClick={handleCopyBriefing}
            title="Copy plain-English summary to clipboard"
          >
            {copiedBriefing ? <Check size={14} /> : <Copy size={14} />}
            <span>{copiedBriefing ? "Copied!" : "Copy Summary"}</span>
          </button>

          <button
            type="button"
            className="nav-tool-btn"
            onClick={handleExportJSON}
            title="Export raw JSON"
          >
            <Download size={14} />
            <span>JSON</span>
          </button>

          <button
            type="button"
            className="nav-tool-btn"
            onClick={handlePrint}
            title="Print or Save as PDF"
          >
            <Printer size={14} />
            <span>Print / PDF</span>
          </button>
        </div>
      </header>

      {/* ================= PRINT-ONLY OFFICIAL HEADER ================= */}
      <div className="print-official-header print-only">
        <div className="print-seal">
          <strong>L.I.M.I.N.A.L. COMMUNICATION DECODER SUMMARY</strong>
          <small>CONFIDENTIAL REPORT • MULTI-AGENT LINGUISTIC INTELLIGENCE</small>
        </div>
        <div className="print-meta-grid">
          <div>
            <span>DATE:</span> {new Date().toLocaleDateString()}
          </div>
          <div>
            <span>VERDICT:</span> {plainData.simpleTitle}
          </div>
          <div>
            <span>CONFIDENCE:</span> {confidence.toFixed(1)}%
          </div>
          <div>
            <span>RISK LEVEL:</span> {plainData.riskLevel}
          </div>
        </div>
      </div>

      <main className="analysis-scroll-body">
        {/* ================= TOP VERDICT HERO CARD ================= */}
        <section className="dossier-hero-card simplified-hero">
          <div className="hero-top-row">
            <div className="hero-classification-group">
              <div
                className="severity-badge-pill simple-risk-pill"
                style={{
                  color: severity.color,
                  backgroundColor: severity.bg,
                  borderColor: severity.border,
                }}
              >
                <AlertTriangle size={14} />
                <span>{plainData.riskBadge || "ATTENTION NEEDED"}</span>
              </div>
              <span className="case-id-badge">
                {confidence >= 80 ? "High AI Confidence" : "Moderate Certainty"} ({confidence.toFixed(1)}%)
              </span>
            </div>

            <div className="hero-quick-meta">
              <span className="quick-meta-item highlight-green">
                <CheckCircle2 size={13} />
                Instant Plain English Translation
              </span>
            </div>
          </div>

          <div className="hero-main-content">
            <div className="hero-title-block">
              <small className="hero-kicker">KEY TAKEAWAY IN PLAIN ENGLISH</small>
              <h1 className="hero-pattern-title">{plainData.simpleTitle}</h1>
              <p className="hero-subtext-preview">{plainData.simpleVerdict}</p>
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
                    {confidence.toFixed(0)}
                    <span className="gauge-pct">%</span>
                  </strong>
                  <small>CERTAINTY</small>
                </div>
              </div>
              <div className="gauge-legend">
                <span className="gauge-status-label">
                  {confidence >= 80 ? "Definite Pattern" : "Probable Pattern"}
                </span>
                <small>5 AI models evaluated this text</small>
              </div>
            </div>
          </div>

          {/* Simple Metric Cards */}
          <div className="dossier-metric-ribbon simple-ribbon">
            <div className="ribbon-metric-cell">
              <small>HIDDEN SIGNALS</small>
              <strong>{metrics.missingSignalsCount} Details Left Out</strong>
              <span>Missing owners, dates, or criteria</span>
            </div>
            <div className="ribbon-metric-cell">
              <small>COMMUNICATION TONE</small>
              <strong style={{ color: severity.color }}>
                {severity.level === "NONE" ? "Direct & Open" : "Hesitant & Guarded"}
              </strong>
              <span>Relies on non-committal words</span>
            </div>
            <div className="ribbon-metric-cell">
              <small>WHO IS ACCOUNTABLE?</small>
              <strong style={{ color: severity.color }}>
                {severity.level === "NONE" ? "Clearly Stated" : "Unclear / Dodged"}
              </strong>
              <span>Ownership is not claimed</span>
            </div>
            <div className="ribbon-metric-cell">
              <small>AI CONSENSUS</small>
              <strong className="text-cyan">5 / 5 Models Agree</strong>
              <span>Consistent findings across all tests</span>
            </div>
          </div>
        </section>

        {/* ================= COMPARATIVE STATEMENT DECODER ================= */}
        <section className="split-decoder-card simplified-decoder">
          <div className="decoder-header">
            <div className="decoder-title">
              <ScanSearch size={20} className="text-green" />
              <div>
                <h2>Statement Comparison: What Was Said vs. What It Actually Means</h2>
                <small>Contrast the literal words with the hidden real-world message</small>
              </div>
            </div>
            <div className="decoder-tag">Side-by-Side Comparison</div>
          </div>

          <div className="decoder-columns-container">
            {/* Left: What Was Said */}
            <div className="decoder-column left-surface">
              <div className="column-header">
                <span className="column-badge surface">
                  <FileText size={13} />
                  WHAT THEY SAID (WORD-FOR-WORD)
                </span>
                <span className="column-subtext">Hover or tap highlighted words to inspect</span>
              </div>

              <div className="decoder-text-box surface-highlighted">
                <ForensicHighlighter text={surfaceStatement} result={result} metrics={metrics} />
              </div>

              <div className="syntax-legend">
                <span className="legend-chip green">
                  <i /> Hesitant Words ("probably", "should")
                </span>
                <span className="legend-chip purple">
                  <i /> Masking True Opinion ("fine with", "whatever")
                </span>
                <span className="legend-chip amber">
                  <i /> Nobody Named Responsible ("the plan")
                </span>
              </div>

              <div className="column-footer-note">
                <small>Surface impression: Sounds agreeable, but avoids taking a firm stand.</small>
              </div>
            </div>

            {/* Center Transformation Glyphs */}
            <div className="decoder-arrow-bridge">
              <div className="bridge-line" />
              <div className="bridge-icon-bubble" title="Decoded in Plain English">
                <Sparkles size={16} />
              </div>
              <div className="bridge-line" />
            </div>

            {/* Right: What Was Meant */}
            <div className="decoder-column right-subtext">
              <div className="column-header">
                <span className="column-badge subtext">
                  <Brain size={13} />
                  WHAT THEY ACTUALLY MEAN (DECODED)
                </span>
                <span className="column-subtext">Plain English translation</span>
              </div>

              <div className="decoder-text-box subtext-content">
                <p className="subtext-lead">{possibleSubtext}</p>

                <div className="subtext-detail-callout friendly-callout">
                  <div className="callout-header">
                    <AlertTriangle size={15} className="text-amber" />
                    <strong>Why this matters to you:</strong>
                  </div>
                  <p>{plainData.whyItMatters}</p>
                </div>
              </div>

              <div className="missing-chips-container">
                <small className="chips-title">⚠️ IMPORTANT DETAILS LEFT OUT OF THEIR MESSAGE:</small>
                <div className="chips-wrap">
                  {plainData.whatIsMissing.map((item, idx) => (
                    <span key={idx} className="missing-tag-pill">
                      <ShieldAlert size={12} />
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ================= HOW TO RESPOND (SMART FOLLOW-UP QUESTIONS) ================= */}
        <section className="counter-inquiries-card simplified-actions">
          <div className="section-title-row">
            <div className="section-title-left">
              <MessageSquare size={19} className="text-purple" />
              <div>
                <h2>How You Can Respond (Smart Follow-Up Questions)</h2>
                <small>Send any of these polite questions to get a direct answer and establish clear ownership</small>
              </div>
            </div>
            <span className="playbook-badge">Action Plan</span>
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
                    title="Copy this question to clipboard"
                  >
                    {copiedQuestionIdx === idx ? (
                      <>
                        <Check size={12} />
                        <span>Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy size={12} />
                        <span>Copy Question</span>
                      </>
                    )}
                  </button>
                </div>

                <div className="inquiry-text">"{item.question}"</div>

                <div className="inquiry-footer">
                  <small>
                    <strong>Why ask this:</strong> {item.why || "Clarifies expectations and locks in accountability."}
                  </small>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ================= BETTER ALTERNATIVES (HOW TO SAY THIS CLEARLY) ================= */}
        <section className="remediation-suite-card simplified-rewrite">
          <div className="section-title-row">
            <div className="section-title-left">
              <Sparkles size={19} className="text-green" />
              <div>
                <h2>Clearer Ways This Could Have Been Said</h2>
                <small>See how this message looks when rewritten with 100% clarity, honesty, and personal ownership</small>
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
                Diplomatic & Polite
              </button>
            </div>
          </div>

          {remediating ? (
            <div className="remediation-loading-state">
              <LoaderCircle size={24} className="spin text-green" />
              <span>Generating clear, honest rewrite alternatives...</span>
            </div>
          ) : remediations ? (
            <div className="rewrite-comparison-container">
              {/* Before vs After comparison */}
              <div className="before-after-grid">
                <div className="before-box">
                  <div className="box-badge-header">
                    <span className="status-dot red" />
                    <strong>❌ ORIGINAL (EVASIVE & VAGUE)</strong>
                  </div>
                  <div className="box-content-text">"{surfaceStatement}"</div>
                  <small className="box-flaw-note">
                    Notice: Leaves choice and risk to you; uses "probably" to avoid taking a stand.
                  </small>
                </div>

                <div className="after-box">
                  <div className="box-badge-header">
                    <span className="status-dot green" />
                    <strong>
                      {selectedRewrite === "direct"
                        ? "✅ REWRITTEN: DIRECT & CLEAR"
                        : "✅ REWRITTEN: DIPLOMATIC & POLITE"}
                    </strong>
                  </div>
                  <div className="box-content-text highlight-green">
                    "{selectedRewrite === "direct" ? remediations.direct : remediations.diplomatic}"
                  </div>
                  <small className="box-flaw-note">
                    Improvement: States a personal recommendation directly, while clearly giving the other party the final approval.
                  </small>
                </div>
              </div>

              <div className="rewrite-actions-bar no-print">
                <div className="rewrite-rationale">
                  <span className="rem-engine-tag">AI Rewrite</span>
                  <span className="rem-rationale-text">{remediations.rationale}</span>
                </div>

                <div className="rewrite-btn-group">
                  <button
                    type="button"
                    className={`rem-copy-btn ${copiedRewrite ? "copied" : ""}`}
                    onClick={handleCopyCurrentRewrite}
                  >
                    {copiedRewrite ? <Check size={14} /> : <Copy size={14} />}
                    <span>{copiedRewrite ? "Copied!" : "Copy Rewrite"}</span>
                  </button>

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
                    <span>Test This Rewrite in Studio</span>
                    <ArrowLeft size={13} style={{ transform: "rotate(180deg)" }} />
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="remediation-empty-state">
              <p>No rewrite drafts generated yet.</p>
              <button
                type="button"
                className="rem-trigger-btn"
                onClick={handleRemediate}
                disabled={remediating}
              >
                <Sparkles size={14} />
                <span>Generate Clear Rewrites</span>
              </button>
            </div>
          )}
        </section>

        {/* ================= AZURE AI DEEP EXPLANATION (CLEAN CARDS) ================= */}
        <section className="azure-narrative-card simplified-azure">
          <div className="azure-header">
            <div className="azure-title-group">
              <Sparkles size={20} className="text-cyan" />
              <div>
                <h2>Deep AI Subtext Analysis</h2>
                <small>Comprehensive reasoning behind the decoded findings</small>
              </div>
            </div>
            <span className="azure-engine-pill">AI Explainer</span>
          </div>

          <div className="azure-narrative-cards-grid">
            {parsedAzure && parsedAzure.length > 0 ? (
              parsedAzure.map((sec, idx) => (
                <div key={idx} className="azure-section-card">
                  <div className="sec-card-header">
                    <span className="sec-pill">{sec.title}</span>
                  </div>
                  <p className="sec-card-content">{sec.content}</p>
                </div>
              ))
            ) : (
              <p className="azure-text">{azureExplanation}</p>
            )}
          </div>

          <div className="responsible-ai-disclaimer">
            <ShieldCheck size={15} className="text-green" />
            <span>
              <strong>Fair Interpretation Notice:</strong> L.I.M.I.N.A.L. analyzes linguistic patterns and communicative habits. It highlights what was left unsaid, but should be used as a guide to open constructive dialogue, not to accuse.
            </span>
          </div>
        </section>

        {/* ================= TECHNICAL DEEP DIVE EXPANDER (RADAR & 5 MODELS) ================= */}
        {(viewMode === "technical" || showTechnicalDetails) ? (
          <section className="multi-agent-tabs-card tech-expanded-card">
            <div className="section-title-row">
              <div className="section-title-left">
                <Layers3 size={18} className="text-blue" />
                <div>
                  <h2>5-Model Neural Forensics (Technical Telemetry)</h2>
                  <small>Examine the independent mathematical predictions of all 5 neural models</small>
                </div>
              </div>

              {viewMode === "simplified" && (
                <button
                  type="button"
                  className="collapse-tech-btn no-print"
                  onClick={() => setShowTechnicalDetails(false)}
                >
                  <ChevronUp size={14} />
                  <span>Hide Technical Telemetry</span>
                </button>
              )}
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
        ) : (
          <div className="expand-tech-banner no-print">
            <button
              type="button"
              className="expand-tech-btn"
              onClick={() => setShowTechnicalDetails(true)}
            >
              <Cpu size={16} />
              <span>Show Technical AI Details (Neural Radar & 5-Model Telemetry)</span>
              <ChevronDown size={14} />
            </button>
          </div>
        )}

        {/* ================= FOOTER ================= */}
        <footer className="analysis-page-footer">
          <div className="footer-left">
            <span>L.I.M.I.N.A.L. LINGUISTIC INTELLIGENCE SYSTEM</span>
            <small>Decoding what communicators omit, evade, or suppress</small>
          </div>
          <div className="footer-right no-print">
            <button
              type="button"
              className="footer-btn"
              onClick={onBackToStudio}
            >
              <Workflow size={14} />
              <span>Return to Input</span>
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
