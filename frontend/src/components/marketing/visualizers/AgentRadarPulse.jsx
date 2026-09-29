import { useState, useEffect } from "react";
import {
  Activity,
  Crosshair,
  Radio,
  Scan,
  ShieldAlert,
  Zap,
} from "lucide-react";
import "./AgentRadarPulse.css";

// 5 Intelligent Agent Detection Targets
const RADAR_TARGETS = [
  {
    id: "m1",
    agent: "M1 Archaeologist",
    label: "HEDGING & MISSING ACTOR",
    finding: "Passive deflection: 'deliverables will be finalized' omits ownership.",
    conf: "99.8%",
    pos: { x: 74, y: 28 }, // percent inside circle
    color: "#38bdf8",
    status: "CRITICAL_GAP",
  },
  {
    id: "m2",
    agent: "M2 Psychologist",
    label: "AFFECT DAMPENING",
    finding: "Interpersonal distance: Forced cordiality masks withheld disagreement.",
    conf: "100%",
    pos: { x: 26, y: 32 },
    color: "#f87171",
    status: "AFFECT_AVOIDANCE",
  },
  {
    id: "m3",
    agent: "M3 Logician",
    label: "UNSTATED ASSUMPTION",
    finding: "Premise gap: 'Once team alignment achieved' presupposes agreement.",
    conf: "90.2%",
    pos: { x: 28, y: 72 },
    color: "#c084fc",
    status: "ENTHYMEME_DETECTED",
  },
  {
    id: "m4",
    agent: "M4 Historian",
    label: "GRICE MAXIM OF QUANTITY",
    finding: "Pragmatic violation: Speaker deliberately provides less than required info.",
    conf: "94.6%",
    pos: { x: 72, y: 70 },
    color: "#fbbf24",
    status: "PRECEDENT_MATCH",
  },
  {
    id: "m5",
    agent: "M5 Synthesizer",
    label: "STRATEGIC DELAY PATTERN",
    finding: "Cross-fusion verdict: 94.2% alignment with planned milestone postponement.",
    conf: "96.4%",
    pos: { x: 50, y: 50 },
    color: "#10b981",
    status: "SYNTHESIS_LOCK",
  },
];

/**
 * Mini animated radar icon for Agent Cards
 */
export function MiniRadarPulse({ color = "#ffffff" }) {
  return (
    <div className="mini-radar-wrap" style={{ color }} title="Autonomous Neural Sonar Active">
      <div className="mini-radar-ring" />
      <div className="mini-radar-sweep" />
      <div className="mini-radar-blip" />
    </div>
  );
}

/**
 * Full Interactive Cyber Radar & Sonar Pulse HUD
 */
export default function AgentRadarPulse() {
  const [selectedTarget, setSelectedTarget] = useState(RADAR_TARGETS[0]);
  const [radarMode, setRadarMode] = useState("sonar"); // "sonar" | "synapse"
  const [sweepSpeed, setSweepSpeed] = useState("normal"); // "normal" | "fast"
  const [pingActive, setPingActive] = useState(false);

  const triggerSonarPing = () => {
    setPingActive(true);
    setTimeout(() => setPingActive(false), 2400);
  };

  // Auto-cycle active target every few seconds if user isn't clicking
  useEffect(() => {
    const timer = setInterval(() => {
      setSelectedTarget((prev) => {
        const nextIdx = (RADAR_TARGETS.findIndex((t) => t.id === prev.id) + 1) % RADAR_TARGETS.length;
        return RADAR_TARGETS[nextIdx];
      });
    }, 4500);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="radar-console">
      {/* Header */}
      <div className="radar-console-header">
        <div className="radar-console-title">
          <span className="radar-status-dot" />
          <span>CYBER FORENSIC SONAR &bull; 5-AGENT DETECTION RADAR</span>
        </div>

        <div className="radar-mode-switcher">
          <button
            type="button"
            className={`radar-mode-btn ${radarMode === "sonar" ? "active" : ""}`}
            onClick={() => setRadarMode("sonar")}
          >
            <Radio size={11} style={{ display: "inline", marginRight: "4px" }} />
            SONAR SWEEP
          </button>
          <button
            type="button"
            className={`radar-mode-btn ${radarMode === "synapse" ? "active" : ""}`}
            onClick={() => setRadarMode("synapse")}
          >
            <Zap size={11} style={{ display: "inline", marginRight: "4px" }} />
            NEURAL SYNAPSE
          </button>
        </div>
      </div>

      {/* Main Body */}
      <div className="radar-body">
        {/* Left: Circular Radar HUD */}
        <div className="radar-screen-wrap">
          <div className="radar-hud-circle">
            {/* Concentric Sonar Rings */}
            <div className="sonar-ring ring-1" />
            <div className="sonar-ring ring-2" />
            <div className="sonar-ring ring-3" />
            <div className="sonar-ring ring-4" />

            {/* Crosshairs */}
            <div className="radar-crosshair-h" />
            <div className="radar-crosshair-v" />

            {/* Sweeping Beam */}
            <div
              className={`radar-sweep-cone ${sweepSpeed === "fast" ? "fast" : ""}`}
              style={{
                filter: radarMode === "synapse" ? "hue-rotate(240deg)" : "none",
              }}
            />

            {/* Expanding Sonar Ping Wave */}
            {pingActive && <div className="sonar-ping-wave" />}

            {/* Target Detection Blips */}
            {RADAR_TARGETS.map((target) => {
              const isSelected = selectedTarget.id === target.id;
              return (
                <div
                  key={target.id}
                  className={`radar-blip blip-${target.id}`}
                  style={{
                    left: `${target.pos.x}%`,
                    top: `${target.pos.y}%`,
                  }}
                  onClick={() => setSelectedTarget(target)}
                  title={`${target.agent}: ${target.label}`}
                >
                  <div className="blip-core" />
                  {isSelected && <div className="blip-pulse-ring" />}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Intel Readout Panel */}
        <div className="radar-intel-panel">
          {/* Telemetry Strip */}
          <div className="radar-telemetry-strip">
            <span className="radar-telemetry-item">
              RADAR FREQ: <strong>2.44 GHz</strong>
            </span>
            <span className="radar-telemetry-item">
              SWEEP: <strong>360&deg; OMNI</strong>
            </span>
            <span className="radar-telemetry-item">
              AGENTS LOCKED: <strong style={{ color: "#10b981" }}>5 / 5</strong>
            </span>
          </div>

          {/* Active Targets List */}
          <div className="radar-targets-list">
            {RADAR_TARGETS.map((t) => {
              const isSelected = selectedTarget.id === t.id;
              return (
                <div
                  key={t.id}
                  className={`target-row ${isSelected ? "selected" : ""}`}
                  onClick={() => setSelectedTarget(t)}
                >
                  <div className="target-left">
                    <span className="target-dot" style={{ background: t.color, boxShadow: `0 0 8px ${t.color}` }} />
                    <div className="target-meta">
                      <strong>{t.agent}</strong>
                      <span>{t.label}</span>
                    </div>
                  </div>
                  <span className="target-confidence" style={{ color: t.color }}>
                    {t.conf}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Target Detail Card */}
          <div className="target-detail-card" style={{ borderColor: `${selectedTarget.color}40` }}>
            <div className="detail-header">
              <span>TARGET INTEL &bull; {selectedTarget.agent.toUpperCase()}</span>
              <span style={{ color: selectedTarget.color, fontWeight: 700 }}>
                {selectedTarget.status}
              </span>
            </div>
            <div className="detail-subtext">
              &ldquo;{selectedTarget.finding}&rdquo;
            </div>
          </div>
        </div>
      </div>

      {/* Footer Controls */}
      <div className="radar-console-footer">
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <button
            type="button"
            className="radar-btn-ping"
            onClick={triggerSonarPing}
          >
            <Activity size={12} />
            TRIGGER SONAR PING
          </button>

          <button
            type="button"
            className="radar-mode-btn"
            onClick={() => setSweepSpeed((s) => (s === "normal" ? "fast" : "normal"))}
          >
            SPEED: {sweepSpeed.toUpperCase()}
          </button>
        </div>

        <div style={{ fontFamily: "monospace", fontSize: "11px", color: "#8e8e9c" }}>
          CLICK ANY RADAR BLIP TO ISOLATE SIGNAL
        </div>
      </div>
    </div>
  );
}
