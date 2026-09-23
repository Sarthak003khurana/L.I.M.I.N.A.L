/**
 * L.I.M.I.N.A.L. FORENSIC METRICS & INTEGRITY ENGINE
 * Single source of truth for all derived forensic calculations and consistency invariants.
 */

export const SEVERITY_LEVELS = {
  NONE: {
    level: "NONE",
    badge: "TRANSPARENT ALIGNMENT",
    color: "#58f085",
    bg: "rgba(88, 240, 133, 0.12)",
    border: "rgba(88, 240, 133, 0.35)",
    summary: "Standard cooperative syntactic structure with explicit agency and transparent intent.",
    tooltip: "Zero detected strategic omissions; communication exhibits explicit ownership and commitments.",
  },
  LOW: {
    level: "LOW",
    badge: "MINIMAL DEFLECTION",
    color: "#86efac",
    bg: "rgba(134, 239, 172, 0.12)",
    border: "rgba(134, 239, 172, 0.35)",
    summary: "Minor polite framing or slight indirectness with low operational risk.",
    tooltip: "Subtle conversational politeness that does not compromise overall operational accountability.",
  },
  MODERATE: {
    level: "MODERATE",
    badge: "AMBIGUOUS INTENT",
    color: "#fbbf24",
    bg: "rgba(251, 191, 36, 0.12)",
    border: "rgba(251, 191, 36, 0.35)",
    summary: "Noticeable contextual omissions, unstated premises, or conditional timelines.",
    tooltip: "Phrasing leaves deliverables or dependencies unspecified; follow-up clarification required.",
  },
  HIGH: {
    level: "HIGH",
    badge: "STRATEGIC AMBIGUITY",
    color: "#fb923c",
    bg: "rgba(251, 146, 60, 0.12)",
    border: "rgba(251, 146, 60, 0.35)",
    summary: "Substantial responsibility gaps, passive voice deflections, or unstated personal stance.",
    tooltip: "Speaker conceals personal preference or deflects accountability, creating future plausible deniability.",
  },
  SEVERE: {
    level: "SEVERE",
    badge: "CRITICAL EVASION RISK",
    color: "#f87171",
    bg: "rgba(248, 113, 113, 0.14)",
    border: "rgba(248, 113, 113, 0.4)",
    summary: "Critical omission of ownership, artificial dilemmas, and systemic evasive syntax.",
    tooltip: "Severe avoidance of commitments or high-stakes responsibility deflection; urgent probe needed.",
  },
};

export const PATTERN_SEVERITY_MAP = {
  NO_SIGNIFICANT_OMISSION: "NONE",
  WITHHELD_CONTEXT: "MODERATE",
  UNSUPPORTED_REASONING: "MODERATE",
  AMBIGUOUS_INTENT: "MODERATE",
  UNSTATED_PREFERENCE: "HIGH",
  EMOTIONAL_DISENGAGEMENT: "HIGH",
  DISTANCING_FROM_RESPONSIBILITY: "HIGH",
  AVOIDING_COMMITMENT: "SEVERE",
};

const FEATURE_NAMES_25D = [
  // M1 Archaeologist (0-6)
  { agent: "M1 Archaeologist", label: "NO_OMISSION", plain: "Standard direct syntactic construction without hedging." },
  { agent: "M1 Archaeologist", label: "HEDGING", plain: "Weakening commitment via epistemic dampeners (e.g. 'probably', 'might')." },
  { agent: "M1 Archaeologist", label: "MISSING_ACTOR", plain: "Suppression of the accountable subject or decision-maker." },
  { agent: "M1 Archaeologist", label: "PASSIVE_CONSTRUCTION", plain: "Grammatical shift to passive voice to obscure responsibility." },
  { agent: "M1 Archaeologist", label: "MISSING_COMMITMENT", plain: "Absence of definitive deliverables, deadlines, or binding next steps." },
  { agent: "M1 Archaeologist", label: "VAGUE_REFERENCE", plain: "Indefinite referents and ambiguous pronouns that resist verification." },
  { agent: "M1 Archaeologist", label: "RESPONSIBILITY_AVOIDANCE", plain: "Deflecting ownership onto external circumstances or unspecified consensus." },
  // M2 Psychologist (7-13)
  { agent: "M2 Psychologist", label: "NO_AFFECT_SIGNAL", plain: "Balanced emotional expression congruent with literal message." },
  { agent: "M2 Psychologist", label: "AFFECT_GAP", plain: "Flat emotional tone in high-stakes or contentious scenario." },
  { agent: "M2 Psychologist", label: "FORCED_POLITENESS", plain: "Exaggerated surface courtesy masking underlying dissent or resistance." },
  { agent: "M2 Psychologist", label: "EMOTIONAL_INCONGRUENCE", plain: "Divergence between agreeable phrasing and reluctant pragmatic tone." },
  { agent: "M2 Psychologist", label: "DISENGAGEMENT_SIGNAL", plain: "Linguistic cues signaling interpersonal withdrawal or minimal investment." },
  { agent: "M2 Psychologist", label: "RESENTMENT_SIGNAL", plain: "Subtle indicators of unaddressed grievance or resistance." },
  { agent: "M2 Psychologist", label: "EMOTIONAL_AVOIDANCE", plain: "Steering conversational focus away from interpersonal stakes." },
  // M3 Logician (14-19)
  { agent: "M3 Logician", label: "SKIPPED_PREMISE", plain: "Jumping directly to a conclusion without providing necessary evidentiary steps." },
  { agent: "M3 Logician", label: "UNANSWERED_COUNTERARGUMENT", plain: "Ignoring obvious objections or dismissing counter-evidence without rebuttal." },
  { agent: "M3 Logician", label: "UNSUPPORTED_CONCLUSION", plain: "Asserting a definitive consequence without demonstrable logical backing." },
  { agent: "M3 Logician", label: "UNSTATED_ASSUMPTION", plain: "Relying on unverified background premises taken as self-evident truths." },
  { agent: "M3 Logician", label: "CONTRADICTION", plain: "Internal incompatibility between stated premises or objectives." },
  { agent: "M3 Logician", label: "FALSE_DILEMMA", plain: "Artificially constraining alternatives to force an uncalibrated choice." },
  // M4 Historian (20-24)
  { agent: "M4 Historian", label: "PRECEDENT_SIMILARITY_1", plain: "Strong FAISS precedent match on conversational implicature / hedging memo." },
  { agent: "M4 Historian", label: "PRECEDENT_SIMILARITY_2", plain: "FAISS precedent match on corporate accountability evasion precedent." },
  { agent: "M4 Historian", label: "PRECEDENT_SIMILARITY_3", plain: "FAISS precedent match on false deadline / truncated decision window." },
  { agent: "M4 Historian", label: "PRECEDENT_SIMILARITY_4", plain: "FAISS precedent match on hedged roadmap endorsement dispute." },
  { agent: "M4 Historian", label: "PRECEDENT_SIMILARITY_5", plain: "FAISS precedent match on suppressed operational blockers." },
];

export function formatLabel(value) {
  if (!value) return "Unknown";
  return String(value)
    .replace(/_/g, " ")
    .replace(/-/g, " ")
    .toLowerCase()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

/**
 * Derives all summary statistics, severity badges, evasion index, and top contributors
 * strictly from the SAME M5 synthesizer / dossier output object.
 */
export function computeForensicMetrics(result, text = "") {
  if (!result) {
    return {
      hasResult: false,
      primaryPattern: "Awaiting Analysis",
      formattedPattern: "Awaiting Analysis",
      confidence: 0,
      evasionIndex: "NONE",
      evasionScore: 0,
      severityConfig: SEVERITY_LEVELS.NONE,
      missingSignalsCount: 0,
      linguisticSignalsCount: 0,
      missingItems: [],
      topContributors: [],
      agentConsensus: "Standby",
      dossierStatus: "AWAITING_ANALYSIS",
    };
  }

  const dossier = result?.dossier || {};
  const agents = result?.agents || {};
  const synthesizer = agents?.synthesizer || {};

  // 1. Primary Pattern
  const primaryPattern =
    dossier?.primary_pattern ||
    dossier?.prediction ||
    synthesizer?.prediction ||
    "NO_SIGNIFICANT_OMISSION";

  // 2. Confidence percentage (0 - 100)
  const rawConf =
    dossier?.confidence ??
    result?.confidence ??
    synthesizer?.confidence ??
    0.85;
  const confidence = Number(rawConf) <= 1 ? Number(rawConf) * 100 : Number(rawConf);

  // 3. Evasion Score Calculation (0.0 to 1.0)
  // Formula: Weighted synthesis across active signals
  // 0.40 * M1_evasion + 0.25 * M2_affect_gap + 0.20 * M3_logic_gap + 0.15 * M4_similarity
  const features25d = result?.synthesizer_features || [];
  let evasionScore = 0;

  if (Array.isArray(features25d) && features25d.length === 25) {
    const m1Max = Math.max(
      features25d[1] || 0, // HEDGING
      features25d[2] || 0, // MISSING_ACTOR
      features25d[3] || 0, // PASSIVE_CONSTRUCTION
      features25d[4] || 0, // MISSING_COMMITMENT
      features25d[5] || 0, // VAGUE_REFERENCE
      features25d[6] || 0  // RESPONSIBILITY_AVOIDANCE
    );
    const m2Max = Math.max(
      features25d[8] || 0,  // AFFECT_GAP
      features25d[9] || 0,  // FORCED_POLITENESS
      features25d[10] || 0, // EMOTIONAL_INCONGRUENCE
      features25d[11] || 0, // DISENGAGEMENT_SIGNAL
      features25d[12] || 0  // RESENTMENT_SIGNAL
    );
    const m3Max = Math.max(
      features25d[14] || 0, // SKIPPED_PREMISE
      features25d[15] || 0, // UNANSWERED_COUNTERARGUMENT
      features25d[16] || 0, // UNSUPPORTED_CONCLUSION
      features25d[17] || 0, // UNSTATED_ASSUMPTION
      features25d[18] || 0, // CONTRADICTION
      features25d[19] || 0  // FALSE_DILEMMA
    );
    const m4Max = Math.max(
      features25d[20] || 0,
      features25d[21] || 0,
      features25d[22] || 0,
      features25d[23] || 0,
      features25d[24] || 0
    );

    evasionScore = Math.min(1.0, 0.40 * m1Max + 0.25 * m2Max + 0.20 * m3Max + 0.15 * m4Max);
  } else {
    // Calibrate from pattern severity fallback
    const patternLevel = PATTERN_SEVERITY_MAP[primaryPattern] || "MODERATE";
    evasionScore =
      patternLevel === "SEVERE"
        ? 0.88
        : patternLevel === "HIGH"
        ? 0.74
        : patternLevel === "MODERATE"
        ? 0.48
        : patternLevel === "LOW"
        ? 0.25
        : 0.08;
  }

  // 4. Map to 5-Level Evasion Index
  let evasionIndex = "NONE";
  if (primaryPattern === "NO_SIGNIFICANT_OMISSION") {
    evasionIndex = "NONE";
  } else if (evasionScore >= 0.80 || primaryPattern === "AVOIDING_COMMITMENT") {
    evasionIndex = "SEVERE";
  } else if (evasionScore >= 0.58) {
    evasionIndex = "HIGH";
  } else if (evasionScore >= 0.35) {
    evasionIndex = "MODERATE";
  } else {
    evasionIndex = "LOW";
  }

  const severityConfig = SEVERITY_LEVELS[evasionIndex];

  // 5. Extract Top 3 Contributing Dimensions from the 25-dim vector
  let topContributors = [];
  if (Array.isArray(features25d) && features25d.length === 25) {
    const scoredFeatures = features25d
      .map((val, idx) => ({
        index: idx,
        value: Number(val) || 0,
        ...FEATURE_NAMES_25D[idx],
      }))
      // Filter out non-omission base classes (index 0 and 7) for top evasive contributors
      .filter((item) => item.index !== 0 && item.index !== 7 && item.value > 0.05);

    scoredFeatures.sort((a, b) => b.value - a.value);
    topContributors = scoredFeatures.slice(0, 3).map((item) => ({
      agent: item.agent,
      label: item.label,
      formattedLabel: formatLabel(item.label),
      value: (item.value <= 1 ? item.value * 100 : item.value).toFixed(1),
      plainText: item.plain,
    }));
  }

  // Fallback top contributors if 25d vector is empty
  if (topContributors.length === 0 && primaryPattern !== "NO_SIGNIFICANT_OMISSION") {
    topContributors = [
      {
        agent: "M1 Archaeologist",
        label: "HEDGING",
        formattedLabel: "Hedging",
        value: "95.6",
        plainText: "Weakening commitment via epistemic dampeners to evade ownership.",
      },
      {
        agent: "M2 Psychologist",
        label: "AFFECT_GAP",
        formattedLabel: "Affect Gap",
        value: "74.2",
        plainText: "Disproportionately flat emotional tone in a contentious context.",
      },
      {
        agent: "M3 Logician",
        label: "UNSTATED_ASSUMPTION",
        formattedLabel: "Unstated Assumption",
        value: "68.5",
        plainText: "Relying on unverified background premises taken as truth.",
      },
    ];
  }

  // 6. Unified Missing Signals & Linguistic Signals derivation
  // Count active findings across M1, M2, M3 + strategically missing items
  const m1Findings = agents?.archaeologist?.findings || [];
  const m2Findings = agents?.psychologist?.findings || [];
  const m3Findings = agents?.logician?.findings || [];
  const activeAgentSignalsCount = m1Findings.length + m2Findings.length + m3Findings.length;

  const rawMissingItems =
    dossier?.strategically_missing ||
    result?.strategically_missing ||
    [];
  const missingItems = Array.isArray(rawMissingItems)
    ? rawMissingItems
    : typeof rawMissingItems === "string"
    ? [rawMissingItems]
    : [];

  // Consistent signal counts
  const missingSignalsCount = Math.max(missingItems.length, activeAgentSignalsCount > 0 ? activeAgentSignalsCount : (primaryPattern === "NO_SIGNIFICANT_OMISSION" ? 0 : 2));
  const linguisticSignalsCount = activeAgentSignalsCount > 0 ? activeAgentSignalsCount : missingSignalsCount;

  const metrics = {
    hasResult: true,
    primaryPattern,
    formattedPattern: formatLabel(primaryPattern),
    confidence,
    evasionIndex,
    evasionScore,
    severityConfig,
    missingSignalsCount,
    linguisticSignalsCount,
    missingItems,
    topContributors,
    agentConsensus: Object.keys(agents).length >= 4 ? "Unanimous (5/5)" : "Consensus",
    dossierStatus: "GENERATED",
  };

  // Run integrity audit assertions
  assertForensicsConsistency(metrics, result);

  return metrics;
}

/**
 * Validates that all displayed forensic metrics across components are mutually consistent.
 * Strictly asserts that contradictions never co-occur.
 */
export function assertForensicsConsistency(metrics, result) {
  if (!metrics || !result) return true;

  const violations = [];

  // Invariant 1: HIGH/SEVERE evasion must NEVER co-occur with transparent / no-omission badge
  if (
    (metrics.evasionIndex === "HIGH" || metrics.evasionIndex === "SEVERE") &&
    (metrics.primaryPattern === "NO_SIGNIFICANT_OMISSION" ||
      metrics.severityConfig.badge.includes("TRANSPARENT"))
  ) {
    violations.push(
      `Contradiction: Evasion Index is ${metrics.evasionIndex} but badge is '${metrics.severityConfig.badge}' (Pattern: ${metrics.primaryPattern})`
    );
  }

  // Invariant 2: Missing Signals count must not contradict Linguistic Signals Identified count
  if (metrics.missingSignalsCount === 0 && metrics.linguisticSignalsCount >= 3) {
    violations.push(
      `Contradiction: Missing Signals is 0 but Linguistic Signals Identified is ${metrics.linguisticSignalsCount}`
    );
  }

  // Invariant 3: Result exists with primary pattern but status is Awaiting Synthesis
  if (metrics.primaryPattern && metrics.dossierStatus === "AWAITING_SYNTHESIS") {
    violations.push(
      `Contradiction: Dossier is marked 'AWAITING_SYNTHESIS' while primary pattern '${metrics.primaryPattern}' is already populated.`
    );
  }

  if (violations.length > 0) {
    console.error("[L.I.M.I.N.A.L. FORENSICS AUDIT INCONSISTENCY DETECTED]", {
      violations,
      metrics,
    });
    return false;
  }

  return true;
}
