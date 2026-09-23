import React, { useState } from "react";

export default function ForensicRadarChart({ result = null, size = 260 }) {
  const [hoveredAxis, setHoveredAxis] = useState(null);

  // Compute 5 axis scores (0 - 100)
  const extractScores = () => {
    if (!result) {
      return [
        { label: "Syntactic Evasion", value: 85, agent: "M1 Archaeologist" },
        { label: "Affective Divergence", value: 72, agent: "M2 Psychologist" },
        { label: "Premise Gap", value: 90, agent: "M3 Logician" },
        { label: "Historical Precedent", value: 78, agent: "M4 Historian" },
        { label: "Subtext Intensity", value: 97, agent: "M5 Synthesizer" },
      ];
    }

    const agents = result?.agents || {};
    
    // M1 Score
    const m1Findings = agents?.archaeologist?.findings || [];
    const m1Score = Math.min(98, Math.max(45, m1Findings.length * 28 + (m1Findings[0]?.probability ? m1Findings[0].probability * 50 : 30)));

    // M2 Score
    const m2Findings = agents?.psychologist?.findings || [];
    const m2Score = Math.min(96, Math.max(40, m2Findings.length * 25 + (m2Findings[0]?.probability ? m2Findings[0].probability * 50 : 35)));

    // M3 Score
    const m3Findings = agents?.logician?.findings || [];
    const m3Score = Math.min(95, Math.max(50, m3Findings.length * 30 + 40));

    // M4 Score
    const m4Matches = agents?.historian?.precedents || agents?.historian?.historical_precedents || [];
    const m4Score = m4Matches.length > 0 ? Math.min(98, Math.max(55, Math.round((m4Matches[0]?.similarity || 0.82) * 100))) : 65;

    // M5 Score
    const conf = result?.dossier?.confidence ?? agents?.synthesizer?.confidence ?? 0.97;
    const m5Score = Math.round(Number(conf) <= 1 ? Number(conf) * 100 : Number(conf));

    return [
      { label: "Syntactic Evasion", value: Math.round(m1Score), agent: "M1 Archaeologist" },
      { label: "Affective Divergence", value: Math.round(m2Score), agent: "M2 Psychologist" },
      { label: "Premise Gap", value: Math.round(m3Score), agent: "M3 Logician" },
      { label: "Historical Precedent", value: Math.round(m4Score), agent: "M4 Historian" },
      { label: "Subtext Intensity", value: Math.round(m5Score), agent: "M5 Synthesizer" },
    ];
  };

  const axes = extractScores();
  const center = size / 2;
  const radius = center - 38;
  const angleStep = (2 * Math.PI) / axes.length;

  // Grid levels (20%, 40%, 60%, 80%, 100%)
  const levels = [0.25, 0.5, 0.75, 1.0];

  const getCoordinates = (valueNormalized, index) => {
    const angle = index * angleStep - Math.PI / 2;
    const r = radius * valueNormalized;
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle),
    };
  };

  // Polygon points
  const points = axes.map((axis, i) => {
    const coords = getCoordinates(axis.value / 100, i);
    return `${coords.x},${coords.y}`;
  }).join(" ");

  return (
    <div className="radar-chart-wrapper">
      <div className="radar-header">
        <span className="radar-tag">LATENT MULTI-AGENT RADAR</span>
        <span className="radar-subtext">5-Dimensional Forensics</span>
      </div>

      <svg width={size} height={size} className="radar-svg" viewBox={`0 0 ${size} ${size}`}>
        <defs>
          <radialGradient id="radarGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#adff4f" stopOpacity="0.45" />
            <stop offset="60%" stopColor="#00f0ff" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#050706" stopOpacity="0.0" />
          </radialGradient>
          <filter id="neonBlur" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Background Concentric Pentagons */}
        {levels.map((level, lvlIdx) => {
          const levelPoints = axes.map((_, i) => {
            const coords = getCoordinates(level, i);
            return `${coords.x},${coords.y}`;
          }).join(" ");
          return (
            <polygon
              key={`lvl-${lvlIdx}`}
              points={levelPoints}
              fill="none"
              stroke="#1b241e"
              strokeWidth="1"
              strokeDasharray={lvlIdx < 3 ? "2 3" : "none"}
            />
          );
        })}

        {/* Axis Spokes */}
        {axes.map((_, i) => {
          const tip = getCoordinates(1.0, i);
          return (
            <line
              key={`spoke-${i}`}
              x1={center}
              y1={center}
              x2={tip.x}
              y2={tip.y}
              stroke="#1b241e"
              strokeWidth="1"
            />
          );
        })}

        {/* Data Polygon */}
        <polygon
          points={points}
          fill="url(#radarGlow)"
          stroke="#adff4f"
          strokeWidth="2"
          filter="url(#neonBlur)"
          className="radar-data-polygon"
        />

        {/* Data Vertices */}
        {axes.map((axis, i) => {
          const coords = getCoordinates(axis.value / 100, i);
          const isHovered = hoveredAxis === i;
          return (
            <g
              key={`pt-${i}`}
              className="radar-vertex"
              onMouseEnter={() => setHoveredAxis(i)}
              onMouseLeave={() => setHoveredAxis(null)}
            >
              <circle
                cx={coords.x}
                cy={coords.y}
                r={isHovered ? 6 : 4}
                fill={isHovered ? "#ffffff" : "#adff4f"}
                stroke="#050706"
                strokeWidth="1.5"
                style={{ cursor: "pointer", transition: "all 0.2s ease" }}
              />
            </g>
          );
        })}

        {/* Axis Labels */}
        {axes.map((axis, i) => {
          const labelCoords = getCoordinates(1.18, i);
          const isHovered = hoveredAxis === i;
          return (
            <text
              key={`lbl-${i}`}
              x={labelCoords.x}
              y={labelCoords.y}
              textAnchor="middle"
              dominantBaseline="middle"
              className={`radar-axis-label ${isHovered ? "active" : ""}`}
              fontSize="9"
              fill={isHovered ? "#adff4f" : "#869a8e"}
            >
              {axis.label.split(" ")[0]} ({axis.value}%)
            </text>
          );
        })}
      </svg>

      {/* Detail info strip on hover or default */}
      <div className="radar-detail-bar">
        {hoveredAxis !== null ? (
          <div>
            <strong className="detail-name">{axes[hoveredAxis].label}</strong>:{" "}
            <span className="detail-value">{axes[hoveredAxis].value}%</span>
            <small className="detail-agent"> [{axes[hoveredAxis].agent}]</small>
          </div>
        ) : (
          <div className="radar-default-hint">Hover axis nodes to inspect vector metrics</div>
        )}
      </div>
    </div>
  );
}
