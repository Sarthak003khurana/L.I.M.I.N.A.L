import { useState } from "react";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  Bot,
  Brain,
  Check,
  ChevronRight,
  Cpu,
  Database,
  ExternalLink,
  FileText,
  GitBranch,
  Layers3,
  LoaderCircle,
  Lock,
  LogOut,
  MessageSquare,
  Network,
  Play,
  Scale,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  Table,
  User,
  UserCheck,
  Workflow,
} from "lucide-react";
import { PRESETS } from "../../constants/presets";
import "./LandingPage.css";

export default function LandingPage({
  onLaunchStudio,
  onNavigateLogin,
  backendStatus,
  currentUser,
  onLogout,
}) {
  const [selectedPreset, setSelectedPreset] = useState(PRESETS[0]);
  const [demoText, setDemoText] = useState(PRESETS[0].text);
  const [scanning, setScanning] = useState(false);
  const [scanComplete, setScanComplete] = useState(false);
  const [activeFlowNode, setActiveFlowNode] = useState("center");

  const isOnline = backendStatus?.online;

  const handleSelectPreset = (preset) => {
    setSelectedPreset(preset);
    setDemoText(preset.text);
    setScanComplete(false);
  };

  const handleRunDemoScan = () => {
    if (!demoText.trim()) return;
    setScanning(true);
    setScanComplete(false);
    setTimeout(() => {
      setScanning(false);
      setScanComplete(true);
    }, 1200);
  };

  return (
    <div className="marketing-page">
      <div className="ambient-glow-1" />
      <div className="ambient-glow-2" />

      {/* ------------------------------------------------------------
          NAVIGATION BAR
      ------------------------------------------------------------ */}
      <nav className="m-navbar">
        <div className="m-container m-nav-inner">
          <div className="m-brand" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
            <div className="m-brand-mark">
              <i />
            </div>
            <div className="m-brand-text">
              <strong>L.I.M.I.N.A.L.</strong>
              <small>INTELLIGENCE ENGINE • AI-103</small>
            </div>
          </div>

          <div className="m-nav-links">
            <a href="#" className="m-nav-link" onClick={(e) => { e.preventDefault(); window.scrollTo({ top: 0, behavior: "smooth" }); }}>Home</a>
            <a href="#agents" className="m-nav-link">AI Agents</a>
            <a href="#comparison" className="m-nav-link">About</a>
            <a href="#usecases" className="m-nav-link">Blog</a>
            <a href="#pricing" className="m-nav-link">Pricing</a>
          </div>

          <div className="m-nav-actions">
            <div className={`m-status-pill ${isOnline ? "" : "offline"}`}>
              <i className={isOnline ? "online-dot" : "offline-dot"} />
              <span>{isOnline ? "SYSTEM ONLINE" : "SYSTEM OFFLINE"}</span>
            </div>

            {currentUser ? (
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <div
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "7px 12px",
                    borderRadius: "8px",
                    background: "rgba(255, 255, 255, 0.05)",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    fontSize: "12px",
                    color: "#f5f5f7",
                  }}
                  title={`Logged in as ${currentUser.email || currentUser.displayName}`}
                >
                  <User size={13} />
                  <span>
                    {currentUser.displayName ||
                      (currentUser.email ? currentUser.email.split("@")[0] : "Analyst")}
                  </span>
                </div>

                <button
                  type="button"
                  onClick={onLogout}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "7px 13px",
                    borderRadius: "8px",
                    background: "rgba(239, 68, 68, 0.1)",
                    border: "1px solid rgba(239, 68, 68, 0.28)",
                    color: "#fca5a5",
                    fontSize: "12px",
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                  title="Log out and switch account"
                >
                  <LogOut size={12} />
                  <span>Log Out</span>
                </button>

                <button
                  className="m-btn-primary"
                  onClick={() => onLaunchStudio(demoText)}
                >
                  <span>Open Console</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            ) : (
              <>
                <button
                  type="button"
                  className="m-btn-signin"
                  onClick={onNavigateLogin || (() => onLaunchStudio(demoText))}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "8px 16px",
                    borderRadius: "8px",
                    background: "rgba(255, 255, 255, 0.05)",
                    border: "1px solid rgba(255, 255, 255, 0.15)",
                    color: "#f5f5f7",
                    fontSize: "13px",
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  <Lock size={13} />
                  <span>Sign In</span>
                </button>

                <button
                  className="m-btn-primary"
                  onClick={() => onLaunchStudio(demoText)}
                >
                  <span>Get Started</span>
                  <ArrowRight size={14} />
                </button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* ------------------------------------------------------------
          HERO SECTION
      ------------------------------------------------------------ */}
      <section className="m-hero">
        <div className="m-container">
          <div className="m-hero-badge">
            <Sparkles size={12} />
            <span>Intelligence 2.0 first Preview</span>
          </div>

          <h1>
            Intelligent Agents<br />
            <span>Real Results</span>
          </h1>

          <p className="m-hero-sub">
            Deploy AI agents that think, learn, and act to uncover strategic omissions,
            evasive commitments, and unstated intent across critical communications.
          </p>

          <div className="m-hero-ctas">
            <button
              className="m-btn-primary hero-cta-btn"
              onClick={() => onLaunchStudio(demoText)}
            >
              <span>Deploy Your Agent</span>
              <ArrowRight size={14} />
            </button>

            <a href="#agents" className="m-btn-secondary hero-sec-btn">
              <span>Explore 5 Agents</span>
              <ChevronRight size={14} />
            </a>
          </div>

          {/* ------------------------------------------------------------
              HERO AGENT ARCHITECTURE FLOW (Aivora Reference Design)
          ------------------------------------------------------------ */}
          <div className="m-hero-flow-wrapper">
            <div className="m-flow-card-glow" />
            <div className="m-hero-flow-diagram">
              {/* Fine tile grid background */}
              <div className="m-flow-grid-bg" />

              {/* Main Workflow Row: Gmail Trigger -> AI Agent -> Right Branches */}
              <div className="m-flow-top-row">
                {/* Left: Gmail Trigger */}
                <div
                  className={`m-flow-node m-flow-trigger ${activeFlowNode === "trigger" ? "active" : ""}`}
                  onClick={() => setActiveFlowNode("trigger")}
                >
                  <div className="m-flow-node-icon gmail-icon">
                    <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
                      <path d="M2 6.5l10 7.5 10-7.5V19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6.5z" fill="rgba(255,255,255,0.06)" />
                      <path d="M22 6.5l-10 7.5L2 6.5 4 5h16l2 1.5z" fill="#ea4335" />
                      <path d="M2 6.5V19c0 1.1.9 2 2 2h3V9.5L2 6.5z" fill="#c5221f" />
                      <path d="M22 6.5V19c0 1.1-.9 2-2 2h-3V9.5l5-3z" fill="#4285f4" />
                      <path d="M7 21h10V11l-5-3.75L7 11v10z" fill="#fbbc04" />
                      <path d="M7 11l5-3.75L17 11V9.5L12 5.75 7 9.5V11z" fill="#34a853" />
                    </svg>
                  </div>
                  <div className="m-flow-node-text">
                    <div className="m-flow-node-title">Gmail Trigger</div>
                    <div className="m-flow-node-sub">When an email is received</div>
                  </div>
                  <div className="m-flow-port port-right" />
                </div>

                {/* Animated connecting wire to Center */}
                <div className="m-flow-wire-horizontal">
                  <div className="wire-line">
                    <span className="pulse-packet packet-to-right" />
                  </div>
                </div>

                {/* Center: AI Agent / Tools Agent */}
                <div
                  className={`m-flow-node m-flow-center-agent ${activeFlowNode === "center" ? "active" : ""}`}
                  onClick={() => setActiveFlowNode("center")}
                >
                  <div className="m-flow-center-header">
                    <div className="m-flow-agent-badge">
                      <Sparkles size={11} />
                      <span>Tools Agent</span>
                    </div>
                    <span className="m-flow-live-tag">
                      <i className="live-dot" /> Active
                    </span>
                  </div>
                  <div className="m-flow-agent-main">
                    <div className="m-flow-agent-avatar">
                      <Bot size={22} />
                    </div>
                    <div className="m-flow-center-info">
                      <div className="m-flow-agent-name">AI Agent</div>
                      <div className="m-flow-agent-desc">
                        Orchestrating agent workflows & analyzing omissions
                      </div>
                    </div>
                  </div>
                  <div className="m-flow-port port-left" />
                  <div className="m-flow-port port-right" />
                  <div className="m-flow-port port-bottom" />
                </div>

                {/* Animated connecting wires branching to Right */}
                <div className="m-flow-wire-fork">
                  <div className="fork-branch branch-top">
                    <span className="fork-condition-chip">Is Managers?</span>
                    <span className="pulse-packet packet-to-top-right" />
                  </div>
                  <div className="fork-branch branch-bottom">
                    <span className="pulse-packet packet-to-bottom-right" />
                  </div>
                </div>

                {/* Right: Output Actions */}
                <div className="m-flow-outputs-stack">
                  <div
                    className={`m-flow-node m-flow-output ${activeFlowNode === "slack" ? "active" : ""}`}
                    onClick={() => setActiveFlowNode("slack")}
                  >
                    <div className="m-flow-port port-left" />
                    <div className="m-flow-node-icon slack-icon">
                      <MessageSquare size={16} />
                    </div>
                    <div className="m-flow-node-text">
                      <div className="m-flow-node-title">Add to channel</div>
                      <div className="m-flow-node-sub">#leadership-briefing</div>
                    </div>
                  </div>

                  <div
                    className={`m-flow-node m-flow-output ${activeFlowNode === "profile" ? "active" : ""}`}
                    onClick={() => setActiveFlowNode("profile")}
                  >
                    <div className="m-flow-port port-left" />
                    <div className="m-flow-node-icon user-icon">
                      <UserCheck size={16} />
                    </div>
                    <div className="m-flow-node-text">
                      <div className="m-flow-node-title">Update Profile</div>
                      <div className="m-flow-node-sub">Flag omission risk level</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Bottom Row: Models & Connected Tools */}
              <div className="m-flow-bottom-section">
                <div className="m-flow-wire-down">
                  <div className="vertical-stem" />
                  <div className="horizontal-bus" />
                </div>

                <div className="m-flow-tools-row">
                  <div
                    className={`m-flow-tool-card ${activeFlowNode === "openai" ? "active" : ""}`}
                    onClick={() => setActiveFlowNode("openai")}
                  >
                    <div className="m-flow-port port-top" />
                    <div className="m-flow-tool-icon openai-badge">
                      <Cpu size={16} />
                    </div>
                    <div className="m-flow-tool-title">Open AI Chat Model</div>
                    <div className="m-flow-tool-sub">GPT-4.5 Astra Reasoning</div>
                  </div>

                  <div
                    className={`m-flow-tool-card ${activeFlowNode === "memory" ? "active" : ""}`}
                    onClick={() => setActiveFlowNode("memory")}
                  >
                    <div className="m-flow-port port-top" />
                    <div className="m-flow-tool-icon memory-badge">
                      <Brain size={16} />
                    </div>
                    <div className="m-flow-tool-title">Memory</div>
                    <div className="m-flow-tool-sub">FAISS Semantic Index</div>
                  </div>

                  <div
                    className={`m-flow-tool-card ${activeFlowNode === "docs" ? "active" : ""}`}
                    onClick={() => setActiveFlowNode("docs")}
                  >
                    <div className="m-flow-port port-top" />
                    <div className="m-flow-tool-icon docs-badge">
                      <FileText size={16} />
                    </div>
                    <div className="m-flow-tool-title">Google Docs</div>
                    <div className="m-flow-tool-sub">Auto-generate Dossier</div>
                  </div>

                  <div
                    className={`m-flow-tool-card ${activeFlowNode === "sheets" ? "active" : ""}`}
                    onClick={() => setActiveFlowNode("sheets")}
                  >
                    <div className="m-flow-port port-top" />
                    <div className="m-flow-tool-icon sheets-badge">
                      <Table size={16} />
                    </div>
                    <div className="m-flow-tool-title">Google Sheets</div>
                    <div className="m-flow-tool-sub">Audit Evidence Table</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Interactive Demo Card */}
          <div className="m-hero-demo-card">
            <div className="m-demo-header">
              <div className="m-demo-window-dots">
                <span /><span /><span />
              </div>
              <div className="m-demo-title">
                Interactive Forensics Sandbox
              </div>
              <span style={{ fontSize: "10px", color: "#56655c" }}>CUDA ENGINE</span>
            </div>

            <div className="m-demo-body">
              <span className="m-demo-presets-label">COMMUNICATION SCENARIOS:</span>
              <div className="m-demo-presets">
                {PRESETS.map((p) => (
                  <button
                    key={p.id}
                    className={`m-preset-chip ${selectedPreset?.id === p.id ? "active" : ""}`}
                    onClick={() => handleSelectPreset(p)}
                  >
                    {p.title}
                  </button>
                ))}
              </div>

              <div className="m-demo-input-box">
                <textarea
                  value={demoText}
                  onChange={(e) => {
                    setDemoText(e.target.value);
                    setScanComplete(false);
                  }}
                  placeholder="Paste or type an email, memo, or high-stakes statement..."
                />
              </div>

              <div className="m-demo-action-bar">
                <div className="m-demo-pipeline-preview">
                  <span>5-Agent Pipeline:</span>
                  <div className="m-demo-dots">
                    <span className={`m-demo-dot ${scanning || scanComplete ? "active" : ""}`} title="Archaeologist" />
                    <span className={`m-demo-dot ${scanning || scanComplete ? "active" : ""}`} title="Psychologist" />
                    <span className={`m-demo-dot ${scanning || scanComplete ? "active" : ""}`} title="Logician" />
                    <span className={`m-demo-dot ${scanning || scanComplete ? "active" : ""}`} title="Historian" />
                    <span className={`m-demo-dot ${scanning || scanComplete ? "active" : ""}`} title="Synthesizer" />
                  </div>
                </div>

                <div style={{ display: "flex", gap: "10px" }}>
                  <button
                    className="m-btn-secondary"
                    onClick={handleRunDemoScan}
                    disabled={scanning}
                    style={{ padding: "8px 14px", fontSize: "12px" }}
                  >
                    {scanning ? (
                      <>
                        <LoaderCircle size={13} className="spin" />
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <Play size={12} fill="currentColor" />
                        <span>Quick Scan</span>
                      </>
                    )}
                  </button>

                  <button
                    className="m-btn-primary"
                    onClick={() => onLaunchStudio(demoText)}
                    style={{ padding: "8px 16px", fontSize: "12px" }}
                  >
                    <span>Inspect in Studio</span>
                    <ArrowUpRight size={13} />
                  </button>
                </div>
              </div>

              {scanComplete && (
                <div className="m-quick-results">
                  <div className="m-quick-res-header">
                    <span className="m-quick-pattern">
                      DETECTED: {selectedPreset.highlightPattern.replace(/_/g, " ")}
                    </span>
                    <span className="m-quick-conf">{selectedPreset.confidence}% CONFIDENCE</span>
                  </div>
                  <p className="m-quick-subtext">
                    {selectedPreset.previewSubtext}
                  </p>
                  <button
                    className="m-quick-open-btn"
                    onClick={() => onLaunchStudio(demoText)}
                  >
                    <span>View 5-Agent Neural Findings & Azure Explanation</span>
                    <ArrowRight size={13} />
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------
          TELEMETRY TICKER BAR
      ------------------------------------------------------------ */}
      <div className="m-ticker-wrap">
        <div className="m-ticker-track">
          <div className="m-ticker-item">
            <Cpu size={14} />
            <span>COMPUTE:</span>
            <strong className="highlight">RTX 3050 / CUDA 12.8</strong>
          </div>
          <div className="m-ticker-item">
            <Layers3 size={14} />
            <span>NEURAL AGENTS:</span>
            <strong>5 MODELS LOADED & SYNCHRONIZED</strong>
          </div>
          <div className="m-ticker-item">
            <Database size={14} />
            <span>VECTOR DB:</span>
            <strong className="highlight">FAISS INDEXED</strong>
          </div>
          <div className="m-ticker-item">
            <Sparkles size={14} />
            <span>EXPLAINABILITY:</span>
            <strong>AZURE GPT-6 ASTRA CONNECTED</strong>
          </div>
          <div className="m-ticker-item">
            <Activity size={14} />
            <span>FEATURE VECTOR:</span>
            <strong className="highlight">25 CROSS-AGENT DIMENSIONS</strong>
          </div>
          {/* Repeat for seamless infinite ticker */}
          <div className="m-ticker-item">
            <Cpu size={14} />
            <span>COMPUTE:</span>
            <strong className="highlight">RTX 3050 / CUDA 12.8</strong>
          </div>
          <div className="m-ticker-item">
            <Layers3 size={14} />
            <span>NEURAL AGENTS:</span>
            <strong>5 MODELS LOADED & SYNCHRONIZED</strong>
          </div>
          <div className="m-ticker-item">
            <Database size={14} />
            <span>VECTOR DB:</span>
            <strong className="highlight">FAISS INDEXED</strong>
          </div>
          <div className="m-ticker-item">
            <Sparkles size={14} />
            <span>EXPLAINABILITY:</span>
            <strong>AZURE GPT-6 ASTRA CONNECTED</strong>
          </div>
          <div className="m-ticker-item">
            <Activity size={14} />
            <span>FEATURE VECTOR:</span>
            <strong className="highlight">25 CROSS-AGENT DIMENSIONS</strong>
          </div>
        </div>
      </div>

      {/* ------------------------------------------------------------
          PRESENCE BIAS VS ABSENCE DEMO SECTION
      ------------------------------------------------------------ */}
      <section className="m-section" id="comparison">
        <div className="m-container">
          <div className="m-section-header">
            <span className="m-section-tag">PARADIGM SHIFT</span>
            <h2 className="m-section-title">The Problem: Presence Bias in NLP</h2>
            <p className="m-section-desc">
              Standard language models only analyze what was explicitly typed.
              In high-stakes diplomacy, leadership, and negotiations, the true meaning
              lies in what was deliberately omitted.
            </p>
          </div>

          <div className="m-comparison-grid">
            <div className="m-comp-card">
              <span className="m-comp-badge traditional">TRADITIONAL SENTIMENT MODEL</span>
              <div className="m-comp-quote">
                "I'm fine with whatever you decide. The current plan should probably work."
              </div>
              <div className="m-comp-findings">
                <div className="m-finding-row">
                  <span>Sentiment Classification</span>
                  <strong className="green">Positive / Agreeable (97.4%)</strong>
                </div>
                <div className="m-finding-row">
                  <span>Conflict Detection</span>
                  <strong>None Detected (0.0%)</strong>
                </div>
                <div className="m-finding-row">
                  <span>Subject Ownership</span>
                  <strong>Present ("I am fine")</strong>
                </div>
                <div className="m-finding-row">
                  <span>Strategic Gap</span>
                  <strong className="red">Undetected (Blind to omission)</strong>
                </div>
              </div>
            </div>

            <div className="m-comp-card liminal">
              <span className="m-comp-badge liminal">L.I.M.I.N.A.L. MULTI-AGENT INFERENCE</span>
              <div className="m-comp-quote">
                "I'm fine with whatever you decide. The current plan should probably work."
              </div>
              <div className="m-comp-findings">
                <div className="m-finding-row">
                  <span>Archaeologist (M1 Forensics)</span>
                  <strong className="green">Hedging Detected (95.6%)</strong>
                </div>
                <div className="m-finding-row">
                  <span>Psychologist (M2 Affect)</span>
                  <strong className="green">Forced Politeness / Affect Gap (74.2%)</strong>
                </div>
                <div className="m-finding-row">
                  <span>Logician (M3 Reasoning)</span>
                  <strong className="green">Unstated Assumption (90.2%)</strong>
                </div>
                <div className="m-finding-row">
                  <span>Synthesizer (M5 Fusion)</span>
                  <strong className="green">Emotional Disengagement / Withheld Preference</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------
          THE 5 AGENTS ARCHITECTURE
      ------------------------------------------------------------ */}
      <section className="m-section" id="agents">
        <div className="m-container">
          <div className="m-section-header">
            <span className="m-section-tag">NEURAL ARCHITECTURE</span>
            <h2 className="m-section-title">Five Specialized Autonomous Agents</h2>
            <p className="m-section-desc">
              Rather than relying on a single black-box model, L.I.M.I.N.A.L. partitions
              linguistic forensics across 5 focused neural models trained for distinct dimensions.
            </p>
          </div>

          <div className="m-agents-grid">
            <div className="m-agent-card green">
              <div className="m-agent-top">
                <span className="m-agent-num">AGENT 01</span>
                <div className="m-agent-icon-wrap">
                  <ScanSearch size={18} />
                </div>
              </div>
              <h3 className="m-agent-name">Archaeologist</h3>
              <div className="m-agent-sub">Linguistic Forensics</div>
              <p className="m-agent-desc">
                Excavates missing actors, passive constructions, responsibility gaps,
                and linguistic hedging markers.
              </p>
              <div className="m-agent-tags">
                <span className="m-agent-tag">Transformer</span>
                <span className="m-agent-tag">326 vocab</span>
                <span className="m-agent-tag">7 labels</span>
              </div>
            </div>

            <div className="m-agent-card violet">
              <div className="m-agent-top">
                <span className="m-agent-num">AGENT 02</span>
                <div className="m-agent-icon-wrap">
                  <Brain size={18} />
                </div>
              </div>
              <h3 className="m-agent-name">Psychologist</h3>
              <div className="m-agent-sub">Affect & Interpersonal</div>
              <p className="m-agent-desc">
                Dissects emotional incongruence, forced politeness, disengagement signals,
                and affect avoidance.
              </p>
              <div className="m-agent-tags">
                <span className="m-agent-tag">Transformer</span>
                <span className="m-agent-tag">216 vocab</span>
                <span className="m-agent-tag">7 labels</span>
              </div>
            </div>

            <div className="m-agent-card blue">
              <div className="m-agent-top">
                <span className="m-agent-num">AGENT 03</span>
                <div className="m-agent-icon-wrap">
                  <GitBranch size={18} />
                </div>
              </div>
              <h3 className="m-agent-name">Logician</h3>
              <div className="m-agent-sub">Reasoning Analysis</div>
              <p className="m-agent-desc">
                Identifies skipped premises, unsupported conclusions, unstated assumptions,
                and logical contradictions.
              </p>
              <div className="m-agent-tags">
                <span className="m-agent-tag">Transformer</span>
                <span className="m-agent-tag">466 vocab</span>
                <span className="m-agent-tag">6 labels</span>
              </div>
            </div>

            <div className="m-agent-card amber">
              <div className="m-agent-top">
                <span className="m-agent-num">AGENT 04</span>
                <div className="m-agent-icon-wrap">
                  <Database size={18} />
                </div>
              </div>
              <h3 className="m-agent-name">Historian</h3>
              <div className="m-agent-sub">Evidence Retrieval Engine</div>
              <p className="m-agent-desc">
                Retrieves authoritative linguistic theory, pragmatic maxims, and evidentiary
                grounding using FAISS vector search.
              </p>
              <div className="m-agent-tags">
                <span className="m-agent-tag">FAISS Index</span>
                <span className="m-agent-tag">TF-IDF</span>
                <span className="m-agent-tag">Top-5 Retrieval</span>
              </div>
            </div>

            <div className="m-agent-card green">
              <div className="m-agent-top">
                <span className="m-agent-num">AGENT 05</span>
                <div className="m-agent-icon-wrap">
                  <Network size={18} />
                </div>
              </div>
              <h3 className="m-agent-name">Synthesizer</h3>
              <div className="m-agent-sub">Cross-Agent Fusion</div>
              <p className="m-agent-desc">
                Fuses the 25-dimensional feature vectors from upstream models into a calibrated,
                provable Subtext Dossier.
              </p>
              <div className="m-agent-tags">
                <span className="m-agent-tag">Cross-Fusion</span>
                <span className="m-agent-tag">25 features</span>
                <span className="m-agent-tag">8 classes</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------
          ENTERPRISE USE CASES
      ------------------------------------------------------------ */}
      <section className="m-section" id="usecases">
        <div className="m-container">
          <div className="m-section-header">
            <span className="m-section-tag">APPLICATIONS</span>
            <h2 className="m-section-title">Designed for Critical Communications</h2>
            <p className="m-section-desc">
              Where strategic omission carries financial, legal, or geopolitical consequences.
            </p>
          </div>

          <div className="m-usecases-grid">
            <div className="m-usecase-card">
              <div className="m-usecase-icon">
                <FileText size={20} />
              </div>
              <h3 className="m-usecase-title">Executive & Board Memos</h3>
              <p className="m-usecase-desc">
                Detect hidden dissent, withheld project risks, and unowned timeline commitments
                in leadership correspondence.
              </p>
              <span className="m-usecase-badge">
                <Check size={12} /> Responsibility Mapping
              </span>
            </div>

            <div className="m-usecase-card">
              <div className="m-usecase-icon">
                <Scale size={20} />
              </div>
              <h3 className="m-usecase-title">Legal & Deposition Discovery</h3>
              <p className="m-usecase-desc">
                Analyze witness statements and discovery documents to flag evasive phrasing,
                passive actor omissions, and unstated assumptions.
              </p>
              <span className="m-usecase-badge">
                <Check size={12} /> Forensics Audit Trail
              </span>
            </div>

            <div className="m-usecase-card">
              <div className="m-usecase-icon">
                <Lock size={20} />
              </div>
              <h3 className="m-usecase-title">M&A Due Diligence</h3>
              <p className="m-usecase-desc">
                Surface vague representations, skipped valuation premises, and evasive disclosures
                during acquisition reviews.
              </p>
              <span className="m-usecase-badge">
                <Check size={12} /> Premise Validation
              </span>
            </div>

            <div className="m-usecase-card">
              <div className="m-usecase-icon">
                <ShieldCheck size={20} />
              </div>
              <h3 className="m-usecase-title">Diplomacy & Crisis Negotiation</h3>
              <p className="m-usecase-desc">
                Map non-committal language, hedging markers, and subtextual disengagement
                in multilateral high-stakes dialogue.
              </p>
              <span className="m-usecase-badge">
                <Check size={12} /> Calibrated Grounding
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------
          PRICING SECTION (Aivora Style)
      ------------------------------------------------------------ */}
      <section className="m-section" id="pricing">
        <div className="m-container">
          <div className="m-section-header">
            <div className="m-section-badge">
              <span>PRICING PLANS</span>
            </div>
            <h2>Simple, transparent pricing</h2>
            <p>
              Choose the forensic intelligence plan that matches your investigation volume.
              All plans include local multi-agent inference.
            </p>
          </div>

          <div className="m-pricing-grid">
            {/* Starter Plan */}
            <div className="m-pricing-card">
              <div className="m-pricing-tier">Starter / Community</div>
              <div className="m-pricing-price">
                <span className="amount">$0</span>
                <span className="period">/ forever</span>
              </div>
              <p className="m-pricing-desc">
                Ideal for individual researchers, academics, and exploratory linguistic omission analysis.
              </p>
              <ul className="m-pricing-features">
                <li><Check size={14} /> 5-Agent Local Forensic Pipeline</li>
                <li><Check size={14} /> CUDA Acceleration (RTX 3050+)</li>
                <li><Check size={14} /> Pre-loaded High-Stakes Scenarios</li>
                <li><Check size={14} /> Basic JSON & Markdown Export</li>
                <li><Check size={14} /> Community GitHub Support</li>
              </ul>
              <button className="m-pricing-btn" onClick={() => onLaunchStudio(demoText)}>
                Launch Free Studio
              </button>
            </div>

            {/* Pro Plan - Featured */}
            <div className="m-pricing-card featured">
              <div className="m-pricing-popular-badge">MOST POPULAR</div>
              <div className="m-pricing-tier">Pro Forensics</div>
              <div className="m-pricing-price">
                <span className="amount">$49</span>
                <span className="period">/ month</span>
              </div>
              <p className="m-pricing-desc">
                Comprehensive omission forensics for corporate teams, lawyers, and investigative journalists.
              </p>
              <ul className="m-pricing-features">
                <li><Check size={14} /> Everything in Starter</li>
                <li><Check size={14} /> Unlimited Live Statement Analysis</li>
                <li><Check size={14} /> Azure AI Foundry GPT-4.5 Verification</li>
                <li><Check size={14} /> Deep FAISS Vector Evidence Search</li>
                <li><Check size={14} /> PDF & Forensic Dossier Generation</li>
                <li><Check size={14} /> Remediation & Inquiry Generator</li>
              </ul>
              <button className="m-pricing-btn primary" onClick={() => onLaunchStudio(demoText)}>
                Get Started with Pro
              </button>
            </div>

            {/* Enterprise Plan */}
            <div className="m-pricing-card">
              <div className="m-pricing-tier">Enterprise Intelligence</div>
              <div className="m-pricing-price">
                <span className="amount">Custom</span>
              </div>
              <p className="m-pricing-desc">
                Air-gapped deployment, custom fine-tuned weights, and compliance auditing for enterprise orgs.
              </p>
              <ul className="m-pricing-features">
                <li><Check size={14} /> Air-gapped on-premise deployment</li>
                <li><Check size={14} /> Custom Fine-Tuned Domain Models</li>
                <li><Check size={14} /> SOC2 Type II & HIPAA Compliance</li>
                <li><Check size={14} /> Multi-seat Collaborative Workspace</li>
                <li><Check size={14} /> 24/7 Dedicated Forensic Engineer</li>
              </ul>
              <button className="m-pricing-btn" onClick={() => onLaunchStudio(demoText)}>
                Contact Enterprise
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------
          RESPONSIBLE AI & CTA BANNER
      ------------------------------------------------------------ */}
      <section className="m-section" id="architecture">
        <div className="m-container">
          <div className="m-cta-banner">
            <h2>Ready to inspect what's missing?</h2>
            <p>
              Access the interactive multi-agent canvas studio. Zoom into individual neural
              activations, inspect FAISS evidence citations, and generate full Subtext Dossiers.
            </p>
            <button
              className="m-btn-primary"
              onClick={() => onLaunchStudio(demoText)}
              style={{ padding: "14px 28px", fontSize: "15px" }}
            >
              <Workflow size={16} />
              <span>Launch Studio Canvas</span>
            </button>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------
          FOOTER
      ------------------------------------------------------------ */}
      <footer className="m-footer">
        <div className="m-container">
          <div className="m-footer-inner">
            <div className="m-footer-col" style={{ maxWidth: "320px" }}>
              <div className="m-brand" style={{ marginBottom: "14px" }}>
                <div className="m-brand-mark">
                  <i />
                </div>
                <div className="m-brand-text">
                  <strong>L.I.M.I.N.A.L.</strong>
                  <small>AI-103 INTELLIGENCE ENGINE</small>
                </div>
              </div>
              <p style={{ fontSize: "12px", color: "#6a796e", lineHeight: "1.6" }}>
                Linguistic Inference of Missing Information via Networked Agent Logic.
                Multi-agent omission forensics powered by PyTorch, CUDA, and Azure AI Foundry.
              </p>
            </div>

            <div className="m-footer-col">
              <h4>System Pipeline</h4>
              <ul>
                <li><a href="#agents">Archaeologist (M1)</a></li>
                <li><a href="#agents">Psychologist (M2)</a></li>
                <li><a href="#agents">Logician (M3)</a></li>
                <li><a href="#agents">Historian (M4)</a></li>
                <li><a href="#agents">Synthesizer (M5)</a></li>
              </ul>
            </div>

            <div className="m-footer-col">
              <h4>Platform</h4>
              <ul>
                <li><a href="#" onClick={(e) => { e.preventDefault(); onLaunchStudio(demoText); }}>Studio Workspace</a></li>
                <li><a href="#comparison">Presence vs Absence</a></li>
                <li><a href="#usecases">Enterprise Use Cases</a></li>
                <li><a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">FastAPI Docs <ExternalLink size={11} style={{ display: "inline" }} /></a></li>
              </ul>
            </div>

            <div className="m-footer-col">
              <h4>Responsible AI</h4>
              <ul>
                <li><span style={{ fontSize: "12px", color: "#8a9a8e" }}>Observable Signal Grounding</span></li>
                <li><span style={{ fontSize: "12px", color: "#8a9a8e" }}>Probabilistic Calibration</span></li>
                <li><span style={{ fontSize: "12px", color: "#8a9a8e" }}>Azure GPT-6 Astra Audit</span></li>
              </ul>
            </div>
          </div>

          <div className="m-footer-bottom">
            <span>© 2026 L.I.M.I.N.A.L. Project. All rights reserved.</span>
            <span>Running on local CUDA device • NVIDIA RTX 3050</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
