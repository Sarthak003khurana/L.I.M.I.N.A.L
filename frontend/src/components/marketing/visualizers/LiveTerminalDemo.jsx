import { useState } from "react";
import { Terminal, Play, ArrowRight, CheckCircle2, Cpu } from "lucide-react";
import BorderBeam from "./BorderBeam";
import "./LiveTerminalDemo.css";

const TERMINAL_PRESETS = [
  {
    name: "Executive Ambiguity",
    text: "While we believe this initiative has solid merit, we might need to revisit certain deliverables as team alignment progresses.",
    logs: [
      { time: "0.01s", tag: "SYS", msg: "Tokenizing 22-token input sequence (vocab: 4,491)..." },
      { time: "0.05s", tag: "M1", msg: "Identified lexical hedge: 'might need to', 'certain deliverables'" },
      { time: "0.09s", tag: "M2", msg: "Affect divergence detected: polite affirmative masking disengagement (p=0.94)" },
      { time: "0.14s", tag: "M3", msg: "Unstated premise: Alignment condition has no operational metric" },
      { time: "0.22s", tag: "M4", msg: "Retrieved Gricean Maxim of Relation & Hirschman EVL dynamic" },
      { time: "0.30s", tag: "M5", msg: "Fused 5-agent latent tensors: PRIMARY PATTERN -> CONDITIONAL_HEDGING (96.4%)" },
    ],
  },
  {
    name: "Contract Avoidance",
    text: "The payment schedule will be addressed in due course once all stakeholder conditions are satisfactorily fulfilled.",
    logs: [
      { time: "0.01s", tag: "SYS", msg: "Tokenizing 17-token input sequence (vocab: 4,491)..." },
      { time: "0.04s", tag: "M1", msg: "Passive agentless clause: 'will be addressed' (zero responsible party)" },
      { time: "0.08s", tag: "M1", msg: "Vague temporal deictic: 'in due course' (indefinite postponement)" },
      { time: "0.15s", tag: "M3", msg: "Circular contingency: undefined satisfaction threshold" },
      { time: "0.24s", tag: "M4", msg: "Retrieved legal forensic precedent: Strategic vagueness defense" },
      { time: "0.32s", tag: "M5", msg: "Fused latent tensors: PRIMARY PATTERN -> COMMITMENT_EVASION (98.1%)" },
    ],
  },
  {
    name: "Interpersonal Consent",
    text: "I'm fine with whatever the leadership decides, honestly.",
    logs: [
      { time: "0.01s", tag: "SYS", msg: "Tokenizing 9-token input sequence (vocab: 4,491)..." },
      { time: "0.03s", tag: "M1", msg: "Over-intensifier marker: 'honestly' flags defensive compliance" },
      { time: "0.07s", tag: "M2", msg: "Affect gap detected: Flat emotional valence with suppressed objection (p=0.986)" },
      { time: "0.12s", tag: "M3", msg: "Premise of abdicated authority: Counterpart forced to absorb risk" },
      { time: "0.20s", tag: "M4", msg: "Retrieved Flouting Maxim of Quantity via pseudo-consent" },
      { time: "0.29s", tag: "M5", msg: "Fused latent tensors: PRIMARY PATTERN -> PSEUDO_CONCURRENCE (97.1%)" },
    ],
  },
];

export default function LiveTerminalDemo({ onLaunchStudio }) {
  const [selectedPreset, setSelectedPreset] = useState(TERMINAL_PRESETS[0]);
  const [inputText, setInputText] = useState(TERMINAL_PRESETS[0].text);
  const [isExecuting, setIsExecuting] = useState(false);
  const [visibleLogs, setVisibleLogs] = useState(TERMINAL_PRESETS[0].logs);

  const handleSelectPreset = (p) => {
    setSelectedPreset(p);
    setInputText(p.text);
    setVisibleLogs(p.logs);
  };

  const handleRunScan = () => {
    setIsExecuting(true);
    setVisibleLogs([]);

    const logsToStream = selectedPreset.logs;
    logsToStream.forEach((log, idx) => {
      setTimeout(() => {
        setVisibleLogs((prev) => [...prev, log]);
        if (idx === logsToStream.length - 1) {
          setIsExecuting(false);
        }
      }, (idx + 1) * 220);
    });
  };

  return (
    <div className="terminal-demo-card">
      <BorderBeam size={280} duration={10} colorFrom="rgba(255, 255, 255, 0.75)" />

      {/* Terminal Title Bar */}
      <div className="terminal-header">
        <div className="terminal-controls">
          <span className="dot dot-red" />
          <span className="dot dot-yellow" />
          <span className="dot dot-green" />
          <span className="terminal-title">
            <Terminal size={13} />
            L.I.M.I.N.A.L. FORENSIC RUNTIME CLI
          </span>
        </div>
        <div className="terminal-badge">
          <Cpu size={12} />
          <span>CUDA: 12.8 READY</span>
        </div>
      </div>

      <div className="terminal-body">
        {/* Preset Selector */}
        <div className="terminal-presets">
          <span className="preset-label">SCENARIO:</span>
          {TERMINAL_PRESETS.map((p) => (
            <button
              key={p.name}
              type="button"
              className={`preset-btn ${selectedPreset.name === p.name ? "active" : ""}`}
              onClick={() => handleSelectPreset(p)}
            >
              {p.name}
            </button>
          ))}
        </div>

        {/* Input box */}
        <div className="terminal-input-wrap">
          <textarea
            className="terminal-textarea"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            rows={2}
            placeholder="Type or paste critical statement to decode..."
          />
          <button
            type="button"
            className="terminal-run-btn"
            onClick={handleRunScan}
            disabled={isExecuting || !inputText.trim()}
          >
            <Play size={13} />
            <span>{isExecuting ? "SCANNING..." : "EXECUTE FORENSIC SCAN"}</span>
          </button>
        </div>

        {/* Terminal Output Log Feed */}
        <div className="terminal-logs-window">
          {visibleLogs.map((item, i) => (
            <div key={i} className="log-line">
              <span className="log-time">[{item.time}]</span>
              <span className={`log-tag tag-${item.tag.toLowerCase()}`}>{item.tag}</span>
              <span className="log-msg">{item.msg}</span>
            </div>
          ))}

          {isExecuting && (
            <div className="log-line log-cursor-line">
              <span className="log-time">[RUN]</span>
              <span className="log-cursor">_</span>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="terminal-footer">
          <div className="terminal-footer-info">
            <CheckCircle2 size={13} className="text-emerald" />
            <span>Inference complete across 5 neural models in 310ms</span>
          </div>

          <button
            type="button"
            className="terminal-launch-btn"
            onClick={() => onLaunchStudio(inputText)}
          >
            <span>Open in Full Studio HUD</span>
            <ArrowRight size={13} />
          </button>
        </div>
      </div>
    </div>
  );
}
