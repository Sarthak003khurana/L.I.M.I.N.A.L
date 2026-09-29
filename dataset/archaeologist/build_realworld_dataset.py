import json
import random
import re
from pathlib import Path

SEED = 42
random.seed(SEED)

ROOT = Path(__file__).resolve().parent

# ============================================================
# COMPREHENSIVE REAL-WORLD DOMAIN CORPUS GENERATOR FOR M1
# ============================================================

ACTORS = [
    "The engineering team", "Dr. Vance", "Elena Rostova", "The finance committee",
    "Chief Legal Counsel", "The platform architect", "Marcus Chen", "Our DevOps squad",
    "The security taskforce", "Vice President Hayes", "The steering committee",
    "Sarah Jenkins", "The compliance auditor", "David Kim", "The executive board"
]

DEPARTMENTS = [
    "cross-functional working group", "infrastructure division", "global risk council",
    "client success unit", "enterprise sales pod", "regulatory affairs team",
    "product governance committee", "core data systems branch"
]

OBJECTS = [
    "the quarterly financial audit", "the Kubernetes migration schedule", "the merger agreement",
    "the SOC2 compliance attestation", "the Q4 revenue reconciliation", "the multi-region failover protocol",
    "the vendor contract renewal", "the vulnerability disclosure report", "the compensation recalibration",
    "the client onboarding SLA", "the product roadmap revision", "the database schema refactor"
]

DATES = [
    "by 5:00 PM EST this Friday", "prior to the October 15th deadline", "before the end of Q3",
    "on Monday morning at 09:00 UTC", "within the next two business days", "before the opening bell tomorrow",
    "by November 30th", "at the scheduled Thursday milestone review"
]

PREFIXES = [
    "Regarding your inquiry about the project status,",
    "Following up on our executive sync earlier today,",
    "In response to the risk committee's recent memorandum,",
    "After thorough internal deliberations,",
    "To provide an operational update on recent developments,",
    "As discussed during yesterday's stakeholder briefing,",
    "With respect to the outstanding deliverables,",
    "In light of recent regulatory updates,"
]

# ------------------------------------------------------------
# TEMPLATES & VARIANTS
# ------------------------------------------------------------

# 1. HEDGING SAMPLES
HEDGING_TEMPLATES = [
    "We believe that with appropriate runway, {obj} might conceivably be approachable in subsequent phases.",
    "Preliminary assessments suggest that {obj} could perhaps require marginal recalibration.",
    "It appears somewhat likely that the proposed targets may not be entirely achievable under current conditions.",
    "Our initial impression is that the team might possibly be able to revisit {obj} later.",
    "There are indications that the timeline should probably hold, assuming no unexpected complications arise.",
    "While we are cautiously optimistic, {obj} may conceivably face certain minor impediments.",
    "In our estimation, it seems plausible that the deliverables could be adjusted if deemed necessary.",
    "We feel that, to some degree, {obj} might benefit from further exploratory review.",
    "It is reasonably probable that certain milestones could be deferred pending further clarification.",
    "Our tentative hypothesis suggests that the architecture should arguably perform adequately."
]

# 2. MISSING ACTOR & PASSIVE CONSTRUCTION SAMPLES
PASSIVE_NO_ACTOR_TEMPLATES = [
    "The comprehensive audit of {obj} was conducted and all critical findings were logged in the repository.",
    "{obj} was officially deprecated following an internal security mandate.",
    "All outstanding liabilities associated with the account were transferred without prior notification.",
    "The system configuration was modified yesterday and multiple access credentials were revoked.",
    "A formal decision regarding {obj} was finalized during closed executive deliberations.",
    "The codebase was refactored and several legacy endpoints were removed from production.",
    "Budget allocations for the upcoming fiscal quarter were reduced across all operational streams.",
    "The deployment pipeline was temporarily paused while anomalous telemetry was evaluated.",
    "Mandatory compliance standards were deployed across enterprise infrastructure without delay.",
    "The contractual terms governing {obj} were renegotiated to minimize corporate exposure."
]

# 3. PASSIVE WITH ACTOR (HARD NEGATIVE FOR MISSING_ACTOR)
PASSIVE_WITH_ACTOR_TEMPLATES = [
    "{obj} was thoroughly audited by {actor} yesterday.",
    "The production configuration was updated by {actor} at 02:00 UTC.",
    "A formal veto regarding {obj} was officially issued by {actor}.",
    "The incident postmortem was compiled and signed by {actor}.",
    "All security patches were deployed across staging environments by {actor}.",
    "The budget reforecast was approved and authorized by {actor}.",
    "The legacy architecture was decommissioned by {actor} ahead of schedule."
]

# 4. MISSING COMMITMENT SAMPLES
MISSING_COMMITMENT_TEMPLATES = [
    "The working group will address {obj} in due course once overarching priorities are aligned.",
    "Efforts are currently underway to establish a viable pathway forward for {obj}.",
    "We intend to revisit the execution cadence as soon as bandwidth and resources permit.",
    "Further discussions regarding {obj} will be scheduled at an appropriate juncture.",
    "The committee plans to evaluate potential next steps when circumstances warrant.",
    "We will explore possible remedies for {obj} as part of our ongoing operational reviews.",
    "Dialogue concerning {obj} remains ongoing, with updates to follow when meaningful progress occurs.",
    "Action items relating to {obj} have been taken under advisement for future deliberation."
]

# 5. RESPONSIBILITY AVOIDANCE SAMPLES
RESPONSIBILITY_AVOIDANCE_TEMPLATES = [
    "Given unforeseen macroeconomic headwinds and vendor delays, the missed target was inevitable.",
    "The breakdown in {obj} was largely precipitated by directives issued outside our team's operational purview.",
    "Our squad executed strictly according to legacy specifications provided by external consultants.",
    "Shifting organizational mandates left our engineering unit with virtually no latitude to prevent the delay.",
    "The outcome regarding {obj} was dictated entirely by third-party infrastructure failures.",
    "We were merely implementing decisions that had already been ratified by prior leadership.",
    "Resource starvation and shifting executive priorities compromised our ability to sustain {obj}."
]

# 6. VAGUE REFERENCE SAMPLES
VAGUE_REFERENCE_TEMPLATES = [
    "We are actively coordinating with relevant parties to resolve that specific matter.",
    "Appropriate measures are being instituted to manage those aforementioned concerns.",
    "The team is diligently looking into that situation through established operational channels.",
    "Certain developments have necessitated a reconsideration of our tactical posture.",
    "We will monitor the ongoing dynamics surrounding those issues as events unfold.",
    "Actions have been taken regarding that matter, and subsequent reviews will follow."
]

# 7. NO OMISSION (HARD NEGATIVES: EXPLICIT, ACTIVE, ACCOUNTABLE)
NO_OMISSION_TEMPLATES = [
    "I personally approved the release of {obj} yesterday, and I assume full responsibility for the deployment.",
    "{actor} will deliver the completed verification report to the steering committee {date}.",
    "I disagree with the revised architecture, and I have scheduled a technical review for tomorrow morning.",
    "Our team identified 4 memory leaks in {obj}, and Marcus Chen will push the hotfix {date}.",
    "{actor} explicitly rejected the vendor contract because the indemnification clause exceeded our risk threshold.",
    "I made the decision to cancel the legacy integration, and I have reallocated the engineering budget accordingly.",
    "{actor} reviewed the pull request, approved the database migration, and merged the branch into main.",
    "I will personally conduct the customer briefing on {obj} {date}."
]

# Multi-label combinations (Very common in real world)
COMPOUND_TEMPLATES = [
    # Hedging + Passive + Missing Actor
    ("{prefix} it seems that {obj} was probably finalized without necessary validations.",
     ["HEDGING", "PASSIVE_CONSTRUCTION", "MISSING_ACTOR"]),
    # Passive + Missing Actor + Missing Commitment
    ("{prefix} {obj} was postponed, and follow-up reviews will occur in due course.",
     ["PASSIVE_CONSTRUCTION", "MISSING_ACTOR", "MISSING_COMMITMENT"]),
    # Hedging + Missing Commitment + Vague Reference
    ("{prefix} we might perhaps revisit those matters when additional context becomes available.",
     ["HEDGING", "MISSING_COMMITMENT", "VAGUE_REFERENCE"]),
    # Responsibility Avoidance + Hedging
    ("{prefix} external vendor friction arguably contributed to the timeline discrepancy on {obj}.",
     ["RESPONSIBILITY_AVOIDANCE", "HEDGING"]),
    # Responsibility Avoidance + Passive + Missing Actor
    ("{prefix} the deadline was missed because necessary documentation was withheld by external groups.",
     ["RESPONSIBILITY_AVOIDANCE", "PASSIVE_CONSTRUCTION", "MISSING_ACTOR"]),
    # Missing Commitment + Vague Reference
    ("{prefix} that matter will be handled when appropriate opportunities arise.",
     ["MISSING_COMMITMENT", "VAGUE_REFERENCE"]),
]

def generate_archaeologist_data(target_count=4500):
    dataset = []

    # 1. Generate clean single-label Hedging
    for _ in range(600):
        t = random.choice(HEDGING_TEMPLATES).format(obj=random.choice(OBJECTS))
        if random.random() < 0.4:
            t = f"{random.choice(PREFIXES)} {t[:1].lower() + t[1:]}"
        dataset.append({"text": t, "labels": ["HEDGING"]})

    # 2. Generate Missing Actor & Passive Construction
    for _ in range(700):
        t = random.choice(PASSIVE_NO_ACTOR_TEMPLATES).format(obj=random.choice(OBJECTS))
        if random.random() < 0.4:
            t = f"{random.choice(PREFIXES)} {t[:1].lower() + t[1:]}"
        dataset.append({"text": t, "labels": ["MISSING_ACTOR", "PASSIVE_CONSTRUCTION"]})

    # 3. Generate Passive WITH Actor (Hard negative for missing actor)
    for _ in range(400):
        t = random.choice(PASSIVE_WITH_ACTOR_TEMPLATES).format(obj=random.choice(OBJECTS), actor=random.choice(ACTORS))
        dataset.append({"text": t, "labels": ["PASSIVE_CONSTRUCTION"]})

    # 4. Generate Missing Commitment
    for _ in range(600):
        t = random.choice(MISSING_COMMITMENT_TEMPLATES).format(obj=random.choice(OBJECTS))
        if random.random() < 0.4:
            t = f"{random.choice(PREFIXES)} {t[:1].lower() + t[1:]}"
        dataset.append({"text": t, "labels": ["MISSING_COMMITMENT"]})

    # 5. Generate Responsibility Avoidance
    for _ in range(500):
        t = random.choice(RESPONSIBILITY_AVOIDANCE_TEMPLATES).format(obj=random.choice(OBJECTS))
        if random.random() < 0.4:
            t = f"{random.choice(PREFIXES)} {t[:1].lower() + t[1:]}"
        dataset.append({"text": t, "labels": ["RESPONSIBILITY_AVOIDANCE"]})

    # 6. Generate Vague Reference
    for _ in range(400):
        t = random.choice(VAGUE_REFERENCE_TEMPLATES).format(obj=random.choice(OBJECTS))
        dataset.append({"text": t, "labels": ["VAGUE_REFERENCE"]})

    # 7. Generate No Omission (Hard Negatives)
    for _ in range(800):
        t = random.choice(NO_OMISSION_TEMPLATES).format(obj=random.choice(OBJECTS), actor=random.choice(ACTORS), date=random.choice(DATES))
        dataset.append({"text": t, "labels": ["NO_OMISSION"]})

    # 8. Generate Multi-label Compounds
    for _ in range(600):
        tmpl, lbls = random.choice(COMPOUND_TEMPLATES)
        t = tmpl.format(prefix=random.choice(PREFIXES), obj=random.choice(OBJECTS))
        dataset.append({"text": t, "labels": lbls})

    random.shuffle(dataset)
    return dataset

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)
    
    data = generate_archaeologist_data(4600)
    print(f"Total Archaeologist samples generated: {len(data)}")
    
    # Split: 80% train, 10% val, 10% test
    n_train = int(len(data) * 0.8)
    n_val = int(len(data) * 0.1)
    
    train_data = data[:n_train]
    val_data = data[n_train:n_train + n_val]
    test_data = data[n_train + n_val:]
    
    def save_jsonl(path, rows):
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                
    save_jsonl(out_dir / "archaeologist_realworld_train.jsonl", train_data)
    save_jsonl(out_dir / "archaeologist_realworld_val.jsonl", val_data)
    save_jsonl(out_dir / "archaeologist_realworld_test.jsonl", test_data)
    
    print(f"Saved: train={len(train_data)}, val={len(val_data)}, test={len(test_data)}")
