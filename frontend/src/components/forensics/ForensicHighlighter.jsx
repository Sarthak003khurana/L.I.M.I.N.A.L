import { useState } from "react";
import { ScanSearch, GitBranch, AlertCircle } from "lucide-react";

// Curated linguistic rules matching M1-M3 agent label spaces in plain English
const LINGUISTIC_RULES = [
  {
    regex: /\b(fine|okay|alright|whatever|doesn't matter|no preference)\b/gi,
    type: "evasion",
    label: "Holding Back Real Preference",
    agent: "Tone & Intent",
    color: "#adff4f",
    description: "Appears to agree on the surface, but hides what the speaker actually thinks or prefers.",
    icon: ScanSearch,
  },
  {
    regex: /\b(probably|should|might|maybe|seems|potentially|perhaps|supposedly)\b/gi,
    type: "hedging",
    label: "Hesitant / Non-Committal Word",
    agent: "Commitment Filter",
    color: "#00f0ff",
    description: "Softens statement to dodge blame or ownership if the outcome fails.",
    icon: ScanSearch,
  },
  {
    regex: /\b(current plan|the plan|someone|it was decided|will be done|is expected|was assumed)\b/gi,
    type: "passive",
    label: "No Person Named Responsible",
    agent: "Ownership Gap",
    color: "#f59e0b",
    description: "No specific person is named as the owner or decision-maker.",
    icon: GitBranch,
  },
  {
    regex: /\b(circle back|table this|eventually|at some point|down the line|when numbers are audited)\b/gi,
    type: "delay",
    label: "Delaying / Kicking Down the Road",
    agent: "Follow-up Gap",
    color: "#ec4899",
    description: "Postpones the issue without committing to a concrete deadline or clear action.",
    icon: AlertCircle,
  },
];

export default function ForensicHighlighter({ text = "", result = null, metrics = null }) {
  const [activeTooltip, setActiveTooltip] = useState(null);

  if (!text) return <span className="empty-text">No payload to highlight</span>;

  const isNoOmission =
    metrics?.primaryPattern === "NO_SIGNIFICANT_OMISSION" ||
    result?.dossier?.primary_pattern === "NO_SIGNIFICANT_OMISSION";

  // Split text into matches and non-matches
  const findSpans = () => {
    if (isNoOmission) {
      return [{ id: "plain-full", text, isMatch: false }];
    }

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
  const matchedSpanCount = spans.filter((s) => s.isMatch).length;
  const signalCount = metrics
    ? metrics.linguisticSignalsCount
    : matchedSpanCount;

  return (
    <div className="forensic-highlighter-container">
      <div className="highlighter-meta-bar">
        <span className="highlighter-badge">
          <ScanSearch size={12} />
          {signalCount} {signalCount === 1 ? "FLAGGED PHRASE" : "FLAGGED PHRASES"} DETECTED
        </span>
        <span className="highlighter-hint">
          {signalCount > 0 ? "Hover or tap highlighted words to see what they reveal" : "No hidden hesitation or passive evasion detected"}
        </span>
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
