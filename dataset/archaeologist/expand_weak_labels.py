import json
import random
import re
from pathlib import Path

SEED = 42
random.seed(SEED)

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "archaeologist_final.jsonl"
OUTPUT_FILE = BASE_DIR / "archaeologist_v2.jsonl"

LABELS = [
    "NO_OMISSION",
    "HEDGING",
    "MISSING_ACTOR",
    "PASSIVE_CONSTRUCTION",
    "MISSING_COMMITMENT",
    "VAGUE_REFERENCE",
    "RESPONSIBILITY_AVOIDANCE",
]


def load_jsonl(path):
    data = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                data.append(json.loads(line))

    return data


def normalize(text):
    text = text.strip()
    text = re.sub(r"\s+", " ", text)

    return text


def make_example(text, labels, source_type, difficulty):
    return {
        "text": normalize(text),
        "labels": sorted(set(labels)),
        "source_type": source_type,
        "difficulty": difficulty,
    }


def generate_responsibility_examples():

    subjects = [
        "I",
        "we",
        "our team",
        "the employee",
        "the developer",
        "the coordinator",
    ]

    responsibility_phrases = [
        "was only following instructions",
        "was simply doing what I was told",
        "was not responsible for that decision",
        "had no authority to make that decision",
        "was not involved in choosing that option",
        "did not have control over the outcome",
        "was acting according to the instructions",
        "was only carrying out the assigned task",
        "had no say in the final decision",
        "was not consulted about the decision",
        "did not decide how the issue was handled",
        "was following the procedure provided",
        "was not authorized to approve the change",
        "had no involvement in the final decision",
        "was only executing the requested task",
    ]

    endings = [
        "",
        " at the time",
        " in this case",
        " during the project",
        " according to the process",
        " as instructed",
        " by the supervisor",
    ]

    generated = []

    for subject in subjects:

        for phrase in responsibility_phrases:

            ending = random.choice(endings)

            text = f"{subject.capitalize()} {phrase}{ending}."

            generated.append(
                make_example(
                    text,
                    ["RESPONSIBILITY_AVOIDANCE"],
                    "weak_label_expansion",
                    "medium",
                )
            )

    return generated


def generate_responsibility_negatives():

    templates = [
        "I followed the instructions and accepted responsibility for the result.",
        "I followed the process and took responsibility for the outcome.",
        "I made the decision after reviewing the available information.",
        "I approved the request and documented my reasoning.",
        "I personally decided to change the schedule.",
        "I chose the final approach for the project.",
        "I accepted responsibility for the mistake.",
        "I authorized the deployment after testing it.",
        "I handled the issue and reported the outcome.",
        "I made the final decision after consulting the team.",
        "We decided together and accepted responsibility for the result.",
        "The manager made the decision and explained the reasoning.",
        "The developer changed the configuration intentionally.",
        "Sarah approved the request after reviewing it.",
        "The project lead accepted responsibility for the delay.",
    ]

    generated = []

    for text in templates:

        generated.append(
            make_example(
                text,
                ["NO_OMISSION"],
                "hard_negative",
                "hard",
            )
        )

    return generated


def generate_commitment_examples():

    subjects = [
        "I",
        "we",
        "the team",
        "someone",
        "the department",
    ]

    actions = [
        "will look into the issue",
        "will review the report",
        "will address the concern",
        "will discuss the problem",
        "will respond to the request",
        "will investigate the matter",
        "will handle the situation",
        "should review the proposal",
        "should discuss the issue",
        "can address the problem",
    ]

    vague_times = [
        "sometime",
        "eventually",
        "later",
        "at some point",
        "when possible",
        "when things settle down",
        "in the future",
        "soon",
    ]

    generated = []

    for subject in subjects:

        for action in actions:

            for time_expression in random.sample(vague_times, 3):

                text = (
                    f"{subject.capitalize()} "
                    f"{action} "
                    f"{time_expression}."
                )

                generated.append(
                    make_example(
                        text,
                        ["MISSING_COMMITMENT"],
                        "weak_label_expansion",
                        "medium",
                    )
                )

    return generated


def generate_commitment_negatives():

    templates = [
        "I will submit the report by Friday.",
        "We will review the proposal tomorrow at ten.",
        "The team will deploy the update tonight.",
        "Sarah will contact the client tomorrow morning.",
        "I will fix the issue before the meeting.",
        "The manager will approve the request by Monday.",
        "We will complete the assignment before Friday.",
        "John will send the document at three o'clock.",
        "The developer will deploy the fix after testing.",
        "I will call the client tomorrow afternoon.",
    ]

    generated = []

    for text in templates:

        generated.append(
            make_example(
                text,
                ["NO_OMISSION"],
                "hard_negative",
                "hard",
            )
        )

    return generated


def generate_no_omission_examples():

    actors = [
        "Sarah",
        "James",
        "Rahul",
        "Priya",
        "the manager",
        "the developer",
        "the project lead",
        "the engineering team",
        "the finance department",
        "our team",
    ]

    actions = [
        "approved the proposal",
        "submitted the report",
        "reviewed the document",
        "contacted the client",
        "completed the assignment",
        "fixed the issue",
        "changed the configuration",
        "updated the schedule",
        "rejected the request",
        "explained the decision",
        "completed the deployment",
        "reviewed the application",
    ]

    times = [
        "yesterday",
        "this morning",
        "this afternoon",
        "today",
        "before the meeting",
        "after the review",
        "last Friday",
    ]

    generated = []

    for actor in actors:

        for action in actions:

            time_expression = random.choice(times)

            text = (
                f"{actor.capitalize()} "
                f"{action} "
                f"{time_expression}."
            )

            generated.append(
                make_example(
                    text,
                    ["NO_OMISSION"],
                    "control_generation",
                    "medium",
                )
            )

    return generated


def generate_passive_hard_negatives():

    objects = [
        "The report",
        "The proposal",
        "The request",
        "The application",
        "The document",
        "The payment",
        "The configuration",
        "The schedule",
        "The assignment",
        "The presentation",
    ]

    passive_verbs = [
        "was approved",
        "was submitted",
        "was reviewed",
        "was changed",
        "was completed",
        "was rejected",
        "was discussed",
        "was updated",
        "was modified",
        "was processed",
    ]

    actors = [
        "Sarah",
        "James",
        "Rahul",
        "Priya",
        "the manager",
        "the developer",
        "the project lead",
        "the engineering team",
        "the finance department",
    ]

    generated = []

    for obj in objects:

        for verb in passive_verbs:

            actor = random.choice(actors)

            text = f"{obj} {verb} by {actor}."

            generated.append(
                make_example(
                    text,
                    ["PASSIVE_CONSTRUCTION"],
                    "passive_hard_negative",
                    "hard",
                )
            )

    return generated


def generate_missing_actor_examples():

    actions = [
        "approved the request",
        "changed the schedule",
        "deleted the files",
        "modified the configuration",
        "rejected the proposal",
        "made the decision",
        "updated the document",
        "changed the deadline",
        "reported the issue",
        "cancelled the meeting",
    ]

    vague_actors = [
        "someone",
        "somebody",
        "people",
        "they",
        "everyone",
        "someone from the team",
        "someone in management",
        "people involved",
    ]

    generated = []

    for actor in vague_actors:

        for action in actions:

            text = f"{actor.capitalize()} {action}."

            generated.append(
                make_example(
                    text,
                    ["MISSING_ACTOR"],
                    "weak_label_expansion",
                    "medium",
                )
            )

    return generated


def generate_actor_negatives():

    actions = [
        "approved the request",
        "changed the schedule",
        "deleted the files",
        "modified the configuration",
        "rejected the proposal",
        "made the decision",
        "updated the document",
    ]

    actors = [
        "Sarah",
        "James",
        "Rahul",
        "Priya",
        "the manager",
        "the developer",
        "the project lead",
    ]

    generated = []

    for actor in actors:

        for action in actions:

            generated.append(
                make_example(
                    f"{actor} {action}.",
                    ["NO_OMISSION"],
                    "hard_negative",
                    "hard",
                )
            )

    return generated


def generate_vague_reference_examples():

    references = [
        "that",
        "that issue",
        "that thing",
        "it",
        "the matter",
        "the situation",
        "what happened earlier",
        "the previous issue",
        "the earlier problem",
        "that part",
    ]

    actions = [
        "needs attention",
        "should be reviewed",
        "needs to be fixed",
        "should be discussed",
        "can be handled later",
        "still needs work",
        "should be addressed",
        "needs further discussion",
    ]

    generated = []

    for reference in references:

        for action in actions:

            text = (
                f"We should address {reference} "
                f"because it {action}."
            )

            generated.append(
                make_example(
                    text,
                    ["VAGUE_REFERENCE"],
                    "weak_label_expansion",
                    "medium",
                )
            )

    return generated


def generate_vague_negatives():

    templates = [
        "We should review the security report from Monday.",
        "The manager should address the budget issue identified yesterday.",
        "Sarah should fix the login error reported by the client.",
        "The team should discuss the deployment failure from Tuesday.",
        "I will review the proposal submitted by James.",
        "The developer should fix the authentication error.",
        "We should discuss the deadline for the final presentation.",
        "The department should address the payment issue reported by finance.",
    ]

    generated = []

    for text in templates:

        generated.append(
            make_example(
                text,
                ["NO_OMISSION"],
                "hard_negative",
                "hard",
            )
        )

    return generated


def generate_hedging_examples():

    hedges = [
        "maybe",
        "perhaps",
        "possibly",
        "probably",
        "I guess",
        "I suppose",
        "it might be",
        "it could be",
        "it seems",
        "I am not entirely sure",
        "there is a chance",
        "it is possible",
    ]

    propositions = [
        "we should review the proposal",
        "we need another option",
        "the project needs more time",
        "the schedule may need to change",
        "the client might agree",
        "we should postpone the meeting",
        "the approach could work",
        "the issue may be resolved soon",
        "the team should reconsider the plan",
        "the report might need revision",
    ]

    generated = []

    for hedge in hedges:

        for proposition in propositions:

            generated.append(
                make_example(
                    f"{hedge.capitalize()}, {proposition}.",
                    ["HEDGING"],
                    "controlled_generation",
                    "medium",
                )
            )

    return generated


def generate_multilabel_examples():

    generated = []

    templates = [
        (
            "Maybe the issue will be handled later.",
            [
                "HEDGING",
                "VAGUE_REFERENCE",
                "MISSING_COMMITMENT",
                "PASSIVE_CONSTRUCTION",
                "MISSING_ACTOR",
            ],
        ),
        (
            "Perhaps someone will look into that sometime.",
            [
                "HEDGING",
                "MISSING_ACTOR",
                "VAGUE_REFERENCE",
                "MISSING_COMMITMENT",
            ],
        ),
        (
            "The decision was probably made by someone.",
            [
                "HEDGING",
                "PASSIVE_CONSTRUCTION",
                "MISSING_ACTOR",
            ],
        ),
        (
            "I guess that will be handled eventually.",
            [
                "HEDGING",
                "VAGUE_REFERENCE",
                "MISSING_COMMITMENT",
                "PASSIVE_CONSTRUCTION",
                "MISSING_ACTOR",
            ],
        ),
        (
            "It was probably changed without anyone explaining why.",
            [
                "HEDGING",
                "VAGUE_REFERENCE",
                "PASSIVE_CONSTRUCTION",
                "MISSING_ACTOR",
            ],
        ),
        (
            "Someone should probably deal with that later.",
            [
                "MISSING_ACTOR",
                "HEDGING",
                "VAGUE_REFERENCE",
                "MISSING_COMMITMENT",
            ],
        ),
        (
            "The issue was handled, but I was only following instructions.",
            [
                "PASSIVE_CONSTRUCTION",
                "MISSING_ACTOR",
                "RESPONSIBILITY_AVOIDANCE",
            ],
        ),
        (
            "Maybe the decision was made before I became involved.",
            [
                "HEDGING",
                "PASSIVE_CONSTRUCTION",
                "MISSING_ACTOR",
                "RESPONSIBILITY_AVOIDANCE",
            ],
        ),
    ]

    for text, labels in templates:

        generated.append(
            make_example(
                text,
                labels,
                "multi_label_seed",
                "hard",
            )
        )

    return generated


print("=" * 60)
print("GENERATING ARCHAEOLOGIST DATASET V2")
print("=" * 60)

existing = load_jsonl(INPUT_FILE)

generated = []

generated.extend(generate_responsibility_examples())
generated.extend(generate_responsibility_negatives())
generated.extend(generate_commitment_examples())
generated.extend(generate_commitment_negatives())
generated.extend(generate_no_omission_examples())
generated.extend(generate_passive_hard_negatives())
generated.extend(generate_missing_actor_examples())
generated.extend(generate_actor_negatives())
generated.extend(generate_vague_reference_examples())
generated.extend(generate_vague_negatives())
generated.extend(generate_hedging_examples())
generated.extend(generate_multilabel_examples())

for example in existing:

    generated.append(
        make_example(
            example["text"],
            example["labels"],
            example.get("source_type", "existing"),
            example.get("difficulty", "medium"),
        )
    )


unique = {}

for example in generated:

    key = (
        example["text"].lower(),
        tuple(example["labels"]),
    )

    if key not in unique:
        unique[key] = example


generated = list(unique.values())

random.shuffle(generated)

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    for example in generated:

        file.write(
            json.dumps(
                example,
                ensure_ascii=False,
            )
            + "\n"
        )


counts = {
    label: 0
    for label in LABELS
}


for example in generated:

    for label in example["labels"]:
        counts[label] += 1


print()
print("=" * 60)
print("ARCHAEOLOGIST V2 DATASET")
print("=" * 60)

print()
print(f"Existing examples : {len(existing)}")
print(f"Final examples    : {len(generated)}")

print()
print("Label distribution:")
print("-" * 60)

for label in LABELS:

    print(
        f"{label:<28} : {counts[label]}"
    )


print()
print("Output:")
print(OUTPUT_FILE)

print()
print("DATASET V2 COMPLETE.")