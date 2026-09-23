import React, { useState } from "react";
import { ScanSearch, HeartPulse, GitBranch, AlertCircle, Info } from "lucide-react";

// Curated linguistic rules matching M1-M3 agent label spaces
const LINGUISTIC_RULES = [
  {
    regex: /\b(fine|okay|alright|whatever|doesn't matter|no preference)\b/gi,
    type: "evasion",
    label: "Unstated Preference / Passive Acquiescence",
    agent: "M1 Archaeologist & M2 Psychologist",
    color: "#adff4f",
    description: "Apparent compliance that conceals genuine personal stance or reservations.",
    icon: ScanSearch,
  },
  {
    regex: /\b(probably|should|might|maybe|seems|potentially|perhaps|supposedly)\b/gi,
    type: "hedging",
    label: "Epistemic Hedging",
    agent: "M1 Archaeologist",
    color: "#00f0ff",
    description: "Softening commitment to avoid epistemic accountability if outcome deviates.",
    icon: ScanSearch,
  },
  {
    regex: /\b(current plan|the plan|someone|it was decided|will be done|is expected|was assumed)\b/gi,
    type: "passive",
    label: "Agent Omission / Responsibility Gap",
    agent: "M3 Logician & M1 Archaeologist",
    color: "#f59e0b",
    description: "Omission of the designated executive actor or decision-maker.",
    icon: GitBranch,
  },
  {
    regex: /\b(circle back|table this|eventually|at some point|down the line|when numbers are audited)\b/gi,
    type: "delay",
    label: "Temporal Deferral / Evasion",
    agent: "M1 Archaeologist",
    color: "#ec4899",
    description: "Strategic postponement designed to diffuse immediate stakeholder scrutiny.",
    icon: AlertCircle,
  },
];

export default function ForensicHighlighter({ text = "", result = null }) {
  const [activeTooltip, setActiveTooltip] = useState(null);

  if (!text) return <span className="empty-text">No payload to highlight</span>;

  // Split text into matches and non-matches
  const findSpans = () => {
    let spans = [];
    let matches = [];

    LINGUISTIC_RULES.forEach((rule) => {
      let match;
      const re = new RegExp(rule.regex.source, "gi");
      while ((match = re.exec(text)) !== null) {
        matches.push({
          start: match.index,
          end: match.index + match[0].length,
          text: match[0],
          rule,
        });
      }
    });

    // Sort matches by start position
    matches.sort((a, b) => a.start - b.start);

    // Filter overlapping matches
    const filteredMatches = [];
    let lastEnd = -1;
    matches.forEach((m) => {
      if (m.start >= lastEnd) {
        filteredMatches.push(m);
        lastEnd = m.end;
      }
    });

    let cursor = 0;
    filteredMatches.forEach((m, idx) => {
      if (m.start > cursor) {
        spans.push({
          id: `plain-${cursor}`,
          text: text.slice(cursor, m.start),
          isMatch: false,
        });
      }
      spans.push({
        id: `match-${idx}`,
        text: m.text,
        isMatch: true,
        rule: m.rule,
      });
      cursor = m.end;
    });

    if (cursor < text.length) {
      spans.push({
        id: `plain-${cursor}`,
        text: text.slice(cursor),
        isMatch: false,
      });
    }

    return spans;
  };

  const spans = findSpans();
  const matchCount = spans.filter((s) => s.isMatch).length;

  return (
    <div className="forensic-highlighter-container">
      <div className="highlighter-meta-bar">
        <span className="highlighter-badge">
          <ScanSearch size={12} />
          {matchCount} LINGUISTIC SIGNALS IDENTIFIED
        </span>
        <span className="highlighter-hint">Hover highlighted spans to inspect</span>
      </div>

      <div className="highlighter-body">
        {spans.map((span) => {
          if (!span.isMatch) {
            return <span key={span.id}>{span.text}</span>;
          }

          const { rule } = span;
          const Icon = rule.icon;
          const isHovered = activeTooltip === span.id;

          return (
            <span
              key={span.id}
              className={`forensic-token token-${rule.type}`}
              style={{
                borderColor: rule.color,
                backgroundColor: `${rule.color}18`,
                color: rule.color,
              }}
              onMouseEnter={() => setActiveTooltip(span.id)}
              onMouseLeave={() => setActiveTooltip(null)}
            >
              {span.text}

              {isHovered && (
                <div className="token-popover" style={{ borderColor: rule.color }}>
                  <div className="popover-header">
                    <span className="popover-badge" style={{ color: rule.color }}>
                      <Icon size={12} />
                      {rule.agent}
                    </span>
                    <span className="popover-type">{rule.type.toUpperCase()}</span>
                  </div>
                  <strong className="popover-label">{rule.label}</strong>
                  <p className="popover-desc">{rule.description}</p>
                </div>
              )}
            </span>
          );
        })}
      </div>
    </div>
  );
}
