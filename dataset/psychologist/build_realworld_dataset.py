import json
import random
from pathlib import Path

SEED = 42
random.seed(SEED)

ROOT = Path(__file__).resolve().parent

# ============================================================
# COMPREHENSIVE REAL-WORLD DOMAIN CORPUS GENERATOR FOR M2
# ============================================================

CONTEXTS = [
    "Regarding the sudden budget cuts announced today,",
    "In response to the emergency executive meeting,",
    "Following the unexpected cancellation of our product line,",
    "Concerning the merger announcement this morning,",
    "Regarding the team restructuring notice,",
    "After reviewing the client feedback on our sprint,",
    "In light of the performance evaluation results,",
    "Regarding the last-minute scope expansion for Q4,"
]

# 1. FORCED POLITENESS
FORCED_POLITENESS_TEMPLATES = [
    "Thank you so much for the feedback! Happy to rework the entire 45-page proposal from scratch over the weekend as requested.",
    "Always an absolute pleasure to absorb additional responsibilities without any budget or headcount adjustments! 😊",
    "We truly appreciate leadership's thoughtful input and will enthusiastically accommodate whatever changes you prefer.",
    "No worries at all! Thrilled to pivot our entire quarterly roadmap 48 hours before the deployment deadline.",
    "Thank you for this wonderful opportunity to demonstrate agility by discarding six months of validated engineering work.",
    "Delighted to hear your thoughts! It's always great when external stakeholders provide direction without reviewing the requirements.",
    "Of course, that sounds perfectly reasonable! Glad to work overnight to make sure your formatting preferences are met.",
    "I'm more than happy to accommodate everyone's conflicting requests, as always! Thank you for the privilege."
]

# 2. AFFECT GAP (Flat emotional detachment during high-magnitude events)
AFFECT_GAP_TEMPLATES = [
    "The regional office was closed and all 250 personnel were laid off this morning; please note this on the departmental roster.",
    "Our primary data center suffered catastrophic hardware corruption with permanent loss of customer records. Continuing with daily standup.",
    "The clinical trial resulted in severe adverse incidents across three testing cohorts; have forwarded the statistical report to archiving.",
    "The firm has been acquired for $1.2 billion in cash; please ensure all timesheets for this week are logged before Friday.",
    "The lead researcher tragically passed away over the weekend; the meeting room booking has been cancelled accordingly.",
    "We lost our largest enterprise client representing 40% of annual revenue; proceeding to slide four on server latency.",
    "The arbitration panel awarded full damages against our company; acknowledging receipt of the docket."
]

# 3. EMOTIONAL INCONGRUENCE (Mismatch / contradiction between words and underlying emotion)
EMOTIONAL_INCONGRUENCE_TEMPLATES = [
    "I am genuinely thrilled about this promotion, though honestly I have never felt more depleted and numb.",
    "Congratulations on winning the contract; I will be stepping away from the organization immediately.",
    "This is arguably the most exciting milestone in our company's history, but I find myself feeling completely hollow.",
    "I love being part of this collaborative culture, which is why I prefer not to speak to anyone on the team.",
    "Everything is going wonderfully on this account, I just want to log off and never look at a screen again.",
    "We are celebrating our record-breaking fiscal results, yet morale across the engineering floor has collapsed.",
    "I am very grateful for this critical feedback, even as my hands are literally shaking reading it."
]

# 4. DISENGAGEMENT SIGNAL (Silent compliance, apathy, withdrawal)
DISENGAGEMENT_TEMPLATES = [
    "Whatever leadership prefers is fine by me. I have no opinions or recommendations on this matter.",
    "Proceed as you see fit. Moving forward, I won't have capacity to track or contribute to this initiative.",
    "I'll defer entirely to the committee's judgment; my input won't change anything anyway.",
    "You can take whatever decision you consider appropriate. Removing myself from this email thread.",
    "I'm fine with whatever the group decides, honestly. It doesn't matter much either way.",
    "Do whatever needs to be done. I am simply executing the assigned Jira tickets without commentary.",
    "Not my circus anymore. Implement whichever approach management signs off on."
]

# 5. RESENTMENT SIGNAL (Passive-aggressive martyrdom, bitter attribution)
RESENTMENT_TEMPLATES = [
    "I went ahead and resolved the production outage myself at 3 AM, since apparently no one else felt it was their responsibility.",
    "Must be nice to approve sweeping roadmap overhauls without ever having to write or test the actual code.",
    "Fascinating how my original proposal was dismissed last month, only to be presented today under someone else's name.",
    "I'll clean up the database migration mess as usual, while the architects move on to their next visionary concept.",
    "So glad to see our team doing the heavy lifting while other departments claim credit during the all-hands.",
    "Another emergency created by leadership's poor planning that the junior staff is expected to magically fix.",
    "It's fine. I'm used to being the only person who actually delivers on their commitments around here."
]

# 6. EMOTIONAL AVOIDANCE (Rigid deflection away from human sentiment/burnout to cold metrics)
EMOTIONAL_AVOIDANCE_TEMPLATES = [
    "Let us focus strictly on the quarterly spreadsheet figures and avoid discussing team feelings or burnout.",
    "Personal dynamics and emotional responses are completely irrelevant to our engineering velocity and delivery SLAs.",
    "I prefer not to dwell on how the staff is reacting to the restructuring; what matters is hitting our EBITDA target.",
    "Please restrict all future comments in this channel to verifiable code commits, not interpersonal grievances.",
    "Morale is an abstract metric; let's concentrate exclusively on customer churn percentages.",
    "We don't need empathy sessions right now; we need pull requests merged and closed before end of day."
]

# 7. NO AFFECT SIGNAL (HARD NEGATIVES: Clean, constructive, authentic, professional communication)
NO_AFFECT_TEMPLATES = [
    "I have reviewed the pull request and identified two areas where caching can optimize query performance.",
    "The infrastructure team deployed the hotfix at 14:00 EST and confirmed database latency is back to normal.",
    "Please send over the updated slides before our 3:00 PM sync so I can review the customer metrics.",
    "We completed the API documentation and published the developer guide to the internal portal.",
    "The meeting will begin promptly at 10:00 AM in Conference Room B, and dial-in links have been sent.",
    "I recommend adopting the Redis caching layer to mitigate load spikes during the upcoming holiday sales period.",
    "The vendor confirmed the delivery date for the replacement hardware is scheduled for next Tuesday.",
    "Our team completed 85% of planned story points this sprint, with the remaining two tasks rolling into Sprint 14."
]

# Multi-label combinations
COMPOUND_AFFECT_TEMPLATES = [
    # Forced Politeness + Resentment
    ("{ctx} so glad to take on another emergency assignment over the weekend, since apparently planning ahead is optional here! 😊",
     ["FORCED_POLITENESS", "RESENTMENT_SIGNAL"]),
    # Disengagement + Forced Politeness
    ("{ctx} whatever you think is best! Happy to step aside and let you run with it completely.",
     ["FORCED_POLITENESS", "DISENGAGEMENT_SIGNAL"]),
    # Emotional Incongruence + Affect Gap
    ("{ctx} the entire department was let go, which is wonderful news for the corporate balance sheet, I suppose.",
     ["EMOTIONAL_INCONGRUENCE", "AFFECT_GAP"]),
    # Resentment + Disengagement
    ("{ctx} I've done everything I could; you all can figure out the rest since nobody listens anyway.",
     ["RESENTMENT_SIGNAL", "DISENGAGEMENT_SIGNAL"]),
    # Emotional Avoidance + Resentment
    ("{ctx} let's not waste time discussing how exhausted people are; just get the work done as mandated.",
     ["EMOTIONAL_AVOIDANCE", "RESENTMENT_SIGNAL"])
]

def generate_psychologist_data(target_count=3600):
    dataset = []

    # 1. Forced Politeness
    for _ in range(500):
        t = random.choice(FORCED_POLITENESS_TEMPLATES)
        if random.random() < 0.35:
            t = f"{random.choice(CONTEXTS)} {t[:1].lower() + t[1:]}"
        dataset.append({"text": t, "labels": ["FORCED_POLITENESS"]})

    # 2. Affect Gap
    for _ in range(500):
        t = random.choice(AFFECT_GAP_TEMPLATES)
        dataset.append({"text": t, "labels": ["AFFECT_GAP"]})

    # 3. Emotional Incongruence
    for _ in range(500):
        t = random.choice(EMOTIONAL_INCONGRUENCE_TEMPLATES)
        if random.random() < 0.3:
            t = f"{random.choice(CONTEXTS)} {t[:1].lower() + t[1:]}"
        dataset.append({"text": t, "labels": ["EMOTIONAL_INCONGRUENCE"]})

    # 4. Disengagement Signal
    for _ in range(500):
        t = random.choice(DISENGAGEMENT_TEMPLATES)
        if random.random() < 0.35:
            t = f"{random.choice(CONTEXTS)} {t[:1].lower() + t[1:]}"
        dataset.append({"text": t, "labels": ["DISENGAGEMENT_SIGNAL"]})

    # 5. Resentment Signal
    for _ in range(500):
        t = random.choice(RESENTMENT_TEMPLATES)
        if random.random() < 0.35:
            t = f"{random.choice(CONTEXTS)} {t[:1].lower() + t[1:]}"
        dataset.append({"text": t, "labels": ["RESENTMENT_SIGNAL"]})

    # 6. Emotional Avoidance
    for _ in range(400):
        t = random.choice(EMOTIONAL_AVOIDANCE_TEMPLATES)
        dataset.append({"text": t, "labels": ["EMOTIONAL_AVOIDANCE"]})

    # 7. No Affect Signal (Hard Negatives)
    for _ in range(700):
        t = random.choice(NO_AFFECT_TEMPLATES)
        dataset.append({"text": t, "labels": ["NO_AFFECT_SIGNAL"]})

    # 8. Compounds
    for _ in range(400):
        tmpl, lbls = random.choice(COMPOUND_AFFECT_TEMPLATES)
        t = tmpl.format(ctx=random.choice(CONTEXTS))
        dataset.append({"text": t, "labels": lbls})

    random.shuffle(dataset)
    return dataset

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)
    
    data = generate_psychologist_data(4000)
    print(f"Total Psychologist samples generated: {len(data)}")
    
    n_train = int(len(data) * 0.8)
    n_val = int(len(data) * 0.1)
    
    train_data = data[:n_train]
    val_data = data[n_train:n_train + n_val]
    test_data = data[n_train + n_val:]
    
    def save_jsonl(path, rows):
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                
    save_jsonl(out_dir / "psychologist_realworld_train.jsonl", train_data)
    save_jsonl(out_dir / "psychologist_realworld_val.jsonl", val_data)
    save_jsonl(out_dir / "psychologist_realworld_test.jsonl", test_data)
    
    print(f"Saved: train={len(train_data)}, val={len(val_data)}, test={len(test_data)}")
