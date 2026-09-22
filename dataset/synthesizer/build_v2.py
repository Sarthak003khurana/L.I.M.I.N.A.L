import json
import random
from pathlib import Path


# ============================================================
# M5 SYNTHESIZER DATASET V2
# Targeted contrastive augmentation
#
# IMPORTANT:
# - Existing test.jsonl is NEVER read or modified.
# - Existing train/validation data is preserved.
# - New examples are written to a separate v2 directory.
# ============================================================

SEED = 42
random.seed(SEED)

ROOT = Path(__file__).resolve().parents[2]

SOURCE_DIR = ROOT / "dataset" / "synthesizer"

OUTPUT_DIR = ROOT / "dataset" / "synthesizer_v2"

TRAIN_FILE = SOURCE_DIR / "train.jsonl"
VAL_FILE = SOURCE_DIR / "validation.jsonl"


# ------------------------------------------------------------
# Load existing training/validation data
# ------------------------------------------------------------

def load_jsonl(path):
    examples = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line:
                examples.append(json.loads(line))

    return examples


train = load_jsonl(TRAIN_FILE)
validation = load_jsonl(VAL_FILE)

existing = train + validation

existing_texts = {
    example["text"].strip().lower()
    for example in existing
}


print("Existing training examples:", len(train))
print("Existing validation examples:", len(validation))
print("Existing train + validation:", len(existing))


# ------------------------------------------------------------
# Targeted contrastive examples
# ------------------------------------------------------------

CONTRASTIVE_EXAMPLES = [

    # ========================================================
    # AVOIDING_COMMITMENT
    # ========================================================

    ("AVOIDING_COMMITMENT",
     "We can decide the final option next week."),

    ("AVOIDING_COMMITMENT",
     "I would rather wait before making the final decision."),

    ("AVOIDING_COMMITMENT",
     "Let's keep the decision open until we have more time."),

    ("AVOIDING_COMMITMENT",
     "I am not prepared to make the final call today."),

    ("AVOIDING_COMMITMENT",
     "We do not need to settle this immediately."),

    ("AVOIDING_COMMITMENT",
     "I would prefer to revisit the decision later."),

    ("AVOIDING_COMMITMENT",
     "Let's postpone the final decision for now."),

    ("AVOIDING_COMMITMENT",
     "I need more time before I can commit to one option."),

    ("AVOIDING_COMMITMENT",
     "We can leave the decision open until tomorrow."),

    ("AVOIDING_COMMITMENT",
     "I am still deciding which option to choose."),

    ("AVOIDING_COMMITMENT",
     "Let's wait before we make the final call."),

    ("AVOIDING_COMMITMENT",
     "I do not want to commit to either option yet."),

    ("AVOIDING_COMMITMENT",
     "The final decision can wait until next week."),

    ("AVOIDING_COMMITMENT",
     "I would like some time before confirming the decision."),

    ("AVOIDING_COMMITMENT",
     "We should discuss this again before deciding."),

    ("AVOIDING_COMMITMENT",
     "I am keeping the decision open for now."),

    ("AVOIDING_COMMITMENT",
     "There is no need to make the final choice today."),

    ("AVOIDING_COMMITMENT",
     "I cannot give a final answer yet."),

    ("AVOIDING_COMMITMENT",
     "Let's reconsider the options before committing."),

    ("AVOIDING_COMMITMENT",
     "I would rather not finalize this decision today."),

    ("AVOIDING_COMMITMENT",
     "We can return to the question after the meeting."),

    ("AVOIDING_COMMITMENT",
     "I am not ready to choose one option yet."),

    ("AVOIDING_COMMITMENT",
     "Let's leave the final choice for another discussion."),

    ("AVOIDING_COMMITMENT",
     "I need additional time before confirming anything."),

    ("AVOIDING_COMMITMENT",
     "We should wait and decide once we have reviewed the options."),

    ("AVOIDING_COMMITMENT",
     "I would like to keep both options available for now."),

    ("AVOIDING_COMMITMENT",
     "Let's not finalize the decision at this stage."),

    ("AVOIDING_COMMITMENT",
     "I am still considering whether to proceed."),

    ("AVOIDING_COMMITMENT",
     "We can make the decision after we discuss it again."),

    ("AVOIDING_COMMITMENT",
     "I would rather delay the commitment until later."),

    ("AVOIDING_COMMITMENT",
     "I am not willing to make a final commitment yet."),

    ("AVOIDING_COMMITMENT",
     "Let's give ourselves more time before deciding."),

    ("AVOIDING_COMMITMENT",
     "The decision does not have to be made today."),

    ("AVOIDING_COMMITMENT",
     "I want to consider the alternatives before committing."),

    ("AVOIDING_COMMITMENT",
     "We can postpone the final choice until Friday."),

    ("AVOIDING_COMMITMENT",
     "I will decide after I have had more time to think."),

    ("AVOIDING_COMMITMENT",
     "Let's keep discussing the options without choosing yet."),

    ("AVOIDING_COMMITMENT",
     "I am not ready to confirm which option we will use."),

    ("AVOIDING_COMMITMENT",
     "We can settle the matter at a later point."),

    ("AVOIDING_COMMITMENT",
     "I would like to delay the final decision."),

    ("AVOIDING_COMMITMENT",
     "Let's revisit the decision before making it permanent."),

    ("AVOIDING_COMMITMENT",
     "I need another discussion before I can decide."),

    ("AVOIDING_COMMITMENT",
     "We should hold off on the final choice for now."),

    ("AVOIDING_COMMITMENT",
     "I am considering the options and will decide later."),

    ("AVOIDING_COMMITMENT",
     "Let's not make the final call just yet."),

    ("AVOIDING_COMMITMENT",
     "I cannot commit to a specific option at this time."),

    ("AVOIDING_COMMITMENT",
     "The final choice can remain open for now."),

    ("AVOIDING_COMMITMENT",
     "I would rather revisit this after we gather more information."),

    ("AVOIDING_COMMITMENT",
     "We can postpone deciding until the next meeting."),

    ("AVOIDING_COMMITMENT",
     "I am still weighing the alternatives."),

    ("AVOIDING_COMMITMENT",
     "Let's wait a little longer before deciding."),

    ("AVOIDING_COMMITMENT",
     "I do not want to settle the matter yet."),

    ("AVOIDING_COMMITMENT",
     "We can discuss the decision again before confirming it."),

    ("AVOIDING_COMMITMENT",
     "I would prefer to leave the matter unresolved for now."),

    ("AVOIDING_COMMITMENT",
     "I am still thinking about whether to agree."),

    ("AVOIDING_COMMITMENT",
     "Let's delay the final answer until tomorrow."),

    ("AVOIDING_COMMITMENT",
     "I need more time to decide what I want to do."),

    ("AVOIDING_COMMITMENT",
     "We should not finalize the decision yet."),

    ("AVOIDING_COMMITMENT",
     "I will give you a final answer later."),

    ("AVOIDING_COMMITMENT",
     "Let's keep the question open for now."),


    # ========================================================
    # WITHHELD_CONTEXT
    # ========================================================

    ("WITHHELD_CONTEXT",
     "There are additional details about the decision that I have not shared."),

    ("WITHHELD_CONTEXT",
     "You do not have all the information behind this decision."),

    ("WITHHELD_CONTEXT",
     "Some relevant background has not been explained."),

    ("WITHHELD_CONTEXT",
     "There is additional context that I have not provided."),

    ("WITHHELD_CONTEXT",
     "I have not told you everything that happened before this."),

    ("WITHHELD_CONTEXT",
     "Some important details are missing from my explanation."),

    ("WITHHELD_CONTEXT",
     "There is more information about the situation that I have not mentioned."),

    ("WITHHELD_CONTEXT",
     "I have left out some relevant background."),

    ("WITHHELD_CONTEXT",
     "The full story includes details that I have not described."),

    ("WITHHELD_CONTEXT",
     "There are circumstances behind this decision that I have not explained."),

    ("WITHHELD_CONTEXT",
     "You are missing some context about what happened earlier."),

    ("WITHHELD_CONTEXT",
     "I have not provided the complete background to this situation."),

    ("WITHHELD_CONTEXT",
     "Some relevant information has not been included in my explanation."),

    ("WITHHELD_CONTEXT",
     "There are details from the earlier discussion that I have not shared."),

    ("WITHHELD_CONTEXT",
     "The explanation is missing some important background information."),

    ("WITHHELD_CONTEXT",
     "I have not described everything that led to this decision."),

    ("WITHHELD_CONTEXT",
     "There is context from the earlier events that I have not provided."),

    ("WITHHELD_CONTEXT",
     "Some information about what happened previously remains unmentioned."),

    ("WITHHELD_CONTEXT",
     "The complete situation involves details that I have not discussed."),

    ("WITHHELD_CONTEXT",
     "I have not explained the circumstances that led to this outcome."),

    ("WITHHELD_CONTEXT",
     "There is relevant information that has not been shared with you."),

    ("WITHHELD_CONTEXT",
     "Some of the background behind this decision is still undisclosed."),

    ("WITHHELD_CONTEXT",
     "I have not mentioned everything that happened before the meeting."),

    ("WITHHELD_CONTEXT",
     "The explanation does not include all of the relevant context."),

    ("WITHHELD_CONTEXT",
     "There are earlier events that I have not described."),

    ("WITHHELD_CONTEXT",
     "You do not yet have the complete story."),

    ("WITHHELD_CONTEXT",
     "Some relevant circumstances have not been discussed."),

    ("WITHHELD_CONTEXT",
     "I have not shared the full context surrounding the issue."),

    ("WITHHELD_CONTEXT",
     "There are additional facts about the situation that I have not mentioned."),

    ("WITHHELD_CONTEXT",
     "Part of the background remains unexplained."),

    ("WITHHELD_CONTEXT",
     "I have not told you about everything that happened earlier."),

    ("WITHHELD_CONTEXT",
     "Some details relevant to the decision have been left out."),

    ("WITHHELD_CONTEXT",
     "The reasoning depends on background information I have not provided."),

    ("WITHHELD_CONTEXT",
     "There is more context behind this than I have explained."),

    ("WITHHELD_CONTEXT",
     "Some important information about the incident has not been disclosed."),

    ("WITHHELD_CONTEXT",
     "I have not shared the circumstances that preceded this conversation."),

    ("WITHHELD_CONTEXT",
     "The situation cannot be fully understood from the information I have given."),

    ("WITHHELD_CONTEXT",
     "Some relevant history has not been discussed."),

    ("WITHHELD_CONTEXT",
     "I have not explained what happened before this decision."),

    ("WITHHELD_CONTEXT",
     "There are details about the earlier events that remain unmentioned."),

    ("WITHHELD_CONTEXT",
     "The account I gave does not contain the full background."),

    ("WITHHELD_CONTEXT",
     "Some context surrounding the incident has not been shared."),

    ("WITHHELD_CONTEXT",
     "I have not included all the information relevant to this issue."),

    ("WITHHELD_CONTEXT",
     "The earlier circumstances have not been fully described."),

    ("WITHHELD_CONTEXT",
     "There are facts about the situation that I have not told you."),

    ("WITHHELD_CONTEXT",
     "Part of the story has not been explained."),

    ("WITHHELD_CONTEXT",
     "I have withheld some background information from this explanation."),

    ("WITHHELD_CONTEXT",
     "The decision makes more sense with information that I have not provided."),

    ("WITHHELD_CONTEXT",
     "Some of the relevant context remains unstated."),

    ("WITHHELD_CONTEXT",
     "I have not shared the complete account of what happened."),

    ("WITHHELD_CONTEXT",
     "There is background information missing from what I have said."),

    ("WITHHELD_CONTEXT",
     "The full circumstances have not been explained."),

    ("WITHHELD_CONTEXT",
     "I have not mentioned an important part of the situation."),

    ("WITHHELD_CONTEXT",
     "Some earlier events are relevant but have not been described."),

    ("WITHHELD_CONTEXT",
     "The explanation leaves out some relevant circumstances."),

    ("WITHHELD_CONTEXT",
     "I have not given you the entire context for this decision."),

    ("WITHHELD_CONTEXT",
     "Some information about the incident remains undisclosed."),

    ("WITHHELD_CONTEXT",
     "There is more background to this issue than I have explained."),

    ("WITHHELD_CONTEXT",
     "I have not shared the details that led to this point."),

    ("WITHHELD_CONTEXT",
     "The complete context has not been provided."),


    # ========================================================
    # NO_SIGNIFICANT_OMISSION
    # ========================================================

    ("NO_SIGNIFICANT_OMISSION",
     "The meeting starts at nine tomorrow."),

    ("NO_SIGNIFICANT_OMISSION",
     "The report is due on Friday."),

    ("NO_SIGNIFICANT_OMISSION",
     "The server restarted successfully at noon."),

    ("NO_SIGNIFICANT_OMISSION",
     "The project has three completed modules."),

    ("NO_SIGNIFICANT_OMISSION",
     "The application supports three user roles."),

    ("NO_SIGNIFICANT_OMISSION",
     "The presentation is scheduled for Monday morning."),

    ("NO_SIGNIFICANT_OMISSION",
     "I will send the updated document this afternoon."),

    ("NO_SIGNIFICANT_OMISSION",
     "The team completed the first milestone yesterday."),

    ("NO_SIGNIFICANT_OMISSION",
     "The API returned a successful response during testing."),

    ("NO_SIGNIFICANT_OMISSION",
     "The experiment produced the expected result."),

    ("NO_SIGNIFICANT_OMISSION",
     "I selected option A because it costs less."),

    ("NO_SIGNIFICANT_OMISSION",
     "I recommend using PostgreSQL for this project."),

    ("NO_SIGNIFICANT_OMISSION",
     "I prefer the blue design for the homepage."),

    ("NO_SIGNIFICANT_OMISSION",
     "I can finish the implementation by Wednesday."),

    ("NO_SIGNIFICANT_OMISSION",
     "We should submit the assignment before Friday."),

    ("NO_SIGNIFICANT_OMISSION",
     "The deadline is clearly stated in the project document."),

    ("NO_SIGNIFICANT_OMISSION",
     "The authentication bug must be fixed before deployment."),

    ("NO_SIGNIFICANT_OMISSION",
     "I will take responsibility for the database migration."),

    ("NO_SIGNIFICANT_OMISSION",
     "The server is running normally after the restart."),

    ("NO_SIGNIFICANT_OMISSION",
     "The team completed testing yesterday."),

    ("NO_SIGNIFICANT_OMISSION",
     "The database contains the required records."),

    ("NO_SIGNIFICANT_OMISSION",
     "The application passed all three tests."),

    ("NO_SIGNIFICANT_OMISSION",
     "The meeting is scheduled for ten o'clock."),

    ("NO_SIGNIFICANT_OMISSION",
     "The deployment is planned for Thursday."),

    ("NO_SIGNIFICANT_OMISSION",
     "The current version supports password authentication."),

    ("NO_SIGNIFICANT_OMISSION",
     "The project deadline is next Monday."),

    ("NO_SIGNIFICANT_OMISSION",
     "The first module was completed successfully."),

    ("NO_SIGNIFICANT_OMISSION",
     "The system processed the request successfully."),

    ("NO_SIGNIFICANT_OMISSION",
     "The team will review the results tomorrow."),

    ("NO_SIGNIFICANT_OMISSION",
     "The document contains the final requirements."),

    ("NO_SIGNIFICANT_OMISSION",
     "The presentation begins at ten."),

    ("NO_SIGNIFICANT_OMISSION",
     "The server is available and responding normally."),

    ("NO_SIGNIFICANT_OMISSION",
     "The project currently has three active contributors."),

    ("NO_SIGNIFICANT_OMISSION",
     "The report was submitted yesterday."),

    ("NO_SIGNIFICANT_OMISSION",
     "The test produced the expected output."),

    ("NO_SIGNIFICANT_OMISSION",
     "The meeting will take place tomorrow afternoon."),

    ("NO_SIGNIFICANT_OMISSION",
     "The implementation is complete."),

    ("NO_SIGNIFICANT_OMISSION",
     "The deadline is Friday at five."),

    ("NO_SIGNIFICANT_OMISSION",
     "The application currently supports two authentication methods."),

    ("NO_SIGNIFICANT_OMISSION",
     "The team finished the database migration."),

    ("NO_SIGNIFICANT_OMISSION",
     "The report contains the requested results."),

    ("NO_SIGNIFICANT_OMISSION",
     "The project passed the integration tests."),

    ("NO_SIGNIFICANT_OMISSION",
     "The presentation is scheduled for Monday at ten."),

    ("NO_SIGNIFICANT_OMISSION",
     "The API is responding normally."),

    ("NO_SIGNIFICANT_OMISSION",
     "The application currently supports three user roles."),

    ("NO_SIGNIFICANT_OMISSION",
     "The first milestone was completed yesterday."),

    ("NO_SIGNIFICANT_OMISSION",
     "The updated document will be sent this afternoon."),

    ("NO_SIGNIFICANT_OMISSION",
     "The experiment produced the expected result."),

    ("NO_SIGNIFICANT_OMISSION",
     "The database migration will start tomorrow."),

    ("NO_SIGNIFICANT_OMISSION",
     "The project has completed three modules."),

    ("NO_SIGNIFICANT_OMISSION",
     "The testing process finished successfully."),

    ("NO_SIGNIFICANT_OMISSION",
     "The report deadline is Friday."),

    ("NO_SIGNIFICANT_OMISSION",
     "The meeting starts at nine."),

    ("NO_SIGNIFICANT_OMISSION",
     "The server restart completed successfully."),

    ("NO_SIGNIFICANT_OMISSION",
     "The current implementation uses PostgreSQL."),

    ("NO_SIGNIFICANT_OMISSION",
     "The team will submit the assignment tomorrow."),

    ("NO_SIGNIFICANT_OMISSION",
     "The project documentation is complete."),

    ("NO_SIGNIFICANT_OMISSION",
     "The system supports the required user roles."),

    ("NO_SIGNIFICANT_OMISSION",
     "The deployment completed successfully."),

    ("NO_SIGNIFICANT_OMISSION",
     "The test results match the expected output."),

    ("NO_SIGNIFICANT_OMISSION",
     "The presentation is scheduled for tomorrow."),

    ("NO_SIGNIFICANT_OMISSION",
     "The implementation will be completed by Wednesday."),
]


# ------------------------------------------------------------
# Remove exact duplicates
# ------------------------------------------------------------

new_examples = []

for label, text in CONTRASTIVE_EXAMPLES:

    normalized = text.strip().lower()

    if normalized in existing_texts:
        continue

    existing_texts.add(normalized)

    new_examples.append({
        "text": text,
        "label": label,
        "source_type": "targeted_contrastive_v2",
    })


print("\nNew targeted examples:", len(new_examples))

counts = {}

for example in new_examples:
    label = example["label"]
    counts[label] = counts.get(label, 0) + 1

print("\nNew examples by class:")

for label, count in counts.items():
    print(f"{label}: {count}")


# ------------------------------------------------------------
# Convert new examples into the same basic schema.
#
# We intentionally leave the production feature generation
# to the existing dataset pipeline/training preparation.
# ------------------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NEW_FILE = OUTPUT_DIR / "new_contrastive_examples.jsonl"

with open(NEW_FILE, "w", encoding="utf-8") as f:

    for example in new_examples:
        f.write(json.dumps(example, ensure_ascii=False) + "\n")


print("\nCreated:")
print(NEW_FILE)

print("\nIMPORTANT:")
print("Existing train.jsonl was NOT modified.")
print("Existing validation.jsonl was NOT modified.")
print("Existing test.jsonl was NOT modified.")