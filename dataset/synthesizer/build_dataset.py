import json
import random
import sys
from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================
# PRODUCTION AGENT RUNNER
# ============================================================

from backend.services.agent_runner import LIMINALAgentRunner


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

random.seed(SEED)

OUTPUT_DIR = (
    ROOT
    / "dataset"
    / "synthesizer"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

TRAIN_FILE = (
    OUTPUT_DIR
    / "train.jsonl"
)

VALIDATION_FILE = (
    OUTPUT_DIR
    / "validation.jsonl"
)

TEST_FILE = (
    OUTPUT_DIR
    / "test.jsonl"
)

MANIFEST_FILE = (
    OUTPUT_DIR
    / "manifest.json"
)


# ============================================================
# M5 LABELS
# ============================================================

LABELS = [
    "NO_SIGNIFICANT_OMISSION",
    "UNSTATED_PREFERENCE",
    "AVOIDING_COMMITMENT",
    "DISTANCING_FROM_RESPONSIBILITY",
    "EMOTIONAL_DISENGAGEMENT",
    "WITHHELD_CONTEXT",
    "UNSUPPORTED_REASONING",
    "AMBIGUOUS_INTENT",
]

LABEL_TO_ID = {
    label: index
    for index, label in enumerate(LABELS)
}


# ============================================================
# SCENARIO FAMILIES
#
# 20 families per class
# 8 classes
# 160 families total
#
# Each family creates 4 variants.
#
# Total:
# 160 × 4 = 640 examples
#
# Split:
# 128 train families  -> 512 examples
# 16 validation        -> 64 examples
# 16 test              -> 64 examples
# ============================================================

SCENARIOS = {

    # ========================================================
    # 0 — NO SIGNIFICANT OMISSION
    # ========================================================

    "NO_SIGNIFICANT_OMISSION": [

        "The meeting starts at nine and the report is due tomorrow.",

        "I prefer the blue design for the homepage.",

        "We should submit the assignment before Friday.",

        "The database backup completed successfully this morning.",

        "I will send the updated document this afternoon.",

        "The server is running normally after the restart.",

        "I chose option A because it costs less.",

        "The project has three completed modules.",

        "I disagree with the proposal because the testing data is incomplete.",

        "The presentation is scheduled for Monday at ten.",

        "I can finish the implementation by Wednesday.",

        "The application currently supports three user roles.",

        "I recommend using PostgreSQL for this project.",

        "The experiment produced the expected result.",

        "We need to fix the authentication bug before deployment.",

        "I selected this approach because it is faster.",

        "The team completed the first milestone yesterday.",

        "The API returned a successful response during testing.",

        "I will take responsibility for the database migration.",

        "The deadline is clearly stated in the project document.",
    ],


    # ========================================================
    # 1 — UNSTATED PREFERENCE
    # ========================================================

    "UNSTATED_PREFERENCE": [

        "Either design would probably work, but I would not mind using the darker one.",

        "I am okay with either restaurant, although the first one sounds nicer.",

        "Both approaches are possible, but I suppose the simpler one is fine.",

        "Whatever you choose is acceptable, though I was leaning toward option A.",

        "I do not really care which color we use, maybe blue.",

        "Both dates work for me, although Friday would be easier.",

        "Either laptop should be fine, but I would probably take the lighter one.",

        "I can work with either framework, though React would be my preference.",

        "Any of those topics would work, but the networking one interests me more.",

        "I am fine with whatever you decide, although I had considered option B.",

        "Both plans seem reasonable, but the first one feels better.",

        "I could go with either option, though I would choose the cheaper one.",

        "The choice is yours, but I was slightly more comfortable with the first.",

        "I do not have a strong preference, although the second option seems appealing.",

        "Either schedule is possible, but Tuesday would suit me better.",

        "Both implementations are acceptable, though I prefer the shorter one.",

        "You can choose either design, but the minimal version looks better to me.",

        "I am okay with whichever tool you use, although I like the first one more.",

        "Any approach is fine, but I would probably start with the simpler one.",

        "I can accept either proposal, though the second is closer to what I wanted.",
    ],


    # ========================================================
    # 2 — AVOIDING COMMITMENT
    # ========================================================

    "AVOIDING_COMMITMENT": [

        "I will think about it and get back to you later.",

        "Let us see how things develop before we decide anything.",

        "I am not ready to commit to that yet.",

        "We can discuss the decision again at some point.",

        "I would rather keep our options open for now.",

        "There is no need to decide today.",

        "Maybe we should wait and see what happens.",

        "I do not want to make a final decision right now.",

        "Let us leave that question open for the moment.",

        "I might agree, but I need more time.",

        "We can come back to this later.",

        "I would prefer not to settle this just yet.",

        "Let us not lock ourselves into one choice yet.",

        "I need some time before I can give you a definite answer.",

        "Perhaps we can postpone the decision until next week.",

        "I am still considering the possibilities.",

        "It may be better to wait before making a commitment.",

        "I do not think we need to decide anything permanently yet.",

        "Let us keep discussing it without making the final call.",

        "I cannot give a definite answer at the moment.",
    ],


    # ========================================================
    # 3 — DISTANCING FROM RESPONSIBILITY
    # ========================================================

    "DISTANCING_FROM_RESPONSIBILITY": [

        "Mistakes were made during the process.",

        "The report was submitted late.",

        "The decision was made after reviewing the available information.",

        "The files were deleted during the cleanup.",

        "The deadline was missed because of unexpected circumstances.",

        "The problem was discovered during testing.",

        "The changes were introduced during the previous update.",

        "The issue was apparently overlooked.",

        "It was decided that the project should continue.",

        "The configuration was changed without further explanation.",

        "The error was introduced somewhere during development.",

        "The task was not completed on time.",

        "The requirements were misunderstood.",

        "The deployment failed unexpectedly.",

        "The wrong file was uploaded.",

        "The decision was taken after discussion.",

        "The customer was not informed about the change.",

        "The problem was eventually corrected.",

        "The responsibility was transferred to another department.",

        "The delay occurred because the process did not go as planned.",
    ],


    # ========================================================
    # 4 — EMOTIONAL DISENGAGEMENT
    # ========================================================

    "EMOTIONAL_DISENGAGEMENT": [

        "Sure, whatever works.",

        "Okay. If that is what everyone wants.",

        "Fine, do what you want.",

        "I guess that is okay.",

        "Whatever you decide is fine.",

        "Yeah, that is fine.",

        "I do not really have anything else to say.",

        "It is okay. Just go with it.",

        "Sure. If you think so.",

        "I suppose that works.",

        "Alright, if everyone agrees.",

        "Okay, I do not mind anymore.",

        "Fine. Let us just do it.",

        "Sure, I guess.",

        "It does not matter to me now.",

        "Okay. Whatever.",

        "I suppose we can leave it that way.",

        "Fine, I am okay with it.",

        "Alright. I have nothing else to add.",

        "Sure, let us go with that.",
    ],


    # ========================================================
    # 5 — WITHHELD CONTEXT
    # ========================================================

    "WITHHELD_CONTEXT": [

        "I cannot explain everything that happened before the meeting.",

        "There are some details about the incident that I have not mentioned.",

        "The situation makes more sense if you knew what happened earlier.",

        "I would rather not discuss what happened before that.",

        "There is some background information I have not shared.",

        "You are missing part of the story.",

        "There are reasons for this decision that I have not explained.",

        "I cannot provide the full context right now.",

        "Something happened before this conversation that matters here.",

        "There is more to the situation than what I have told you.",

        "I am leaving out some details for now.",

        "The earlier events are relevant, but I am not going into them.",

        "You do not have all the information behind this decision.",

        "Some important background has not been discussed yet.",

        "There is another part of the situation that I have not described.",

        "I cannot give you the complete story at the moment.",

        "The reason becomes clearer when you consider what happened previously.",

        "I have not shared everything that led to this point.",

        "There are circumstances I have not mentioned yet.",

        "Some context is missing from this explanation.",
    ],


    # ========================================================
    # 6 — UNSUPPORTED REASONING
    # ========================================================

    "UNSUPPORTED_REASONING": [

        "Everyone agrees with this plan, so it must be the correct one.",

        "The application crashed once, therefore the entire architecture is wrong.",

        "Either we launch today or the project will completely fail.",

        "The results look positive, so the method must be scientifically valid.",

        "Nobody complained, therefore everyone must be satisfied.",

        "The first test passed, so the system cannot have any bugs.",

        "If the deadline is moved, the project will obviously become useless.",

        "We used this approach before, therefore it is definitely the best approach.",

        "The model is accurate on this dataset, so it will work everywhere.",

        "Either you support the proposal or you do not care about the project.",

        "The feature is popular, therefore it must be necessary.",

        "The team finished early, so the implementation must have no problems.",

        "This person disagreed once, therefore they oppose the entire project.",

        "The server is online, so the application must be completely reliable.",

        "We have not observed an error, therefore no error exists.",

        "The numbers increased, therefore the new strategy caused the improvement.",

        "Everyone uses this library, so it must be the safest option.",

        "The presentation went well, therefore the project is technically complete.",

        "The test failed, so the entire idea is useless.",

        "Either we choose this solution or there is no possible solution.",
    ],


    # ========================================================
    # 7 — AMBIGUOUS INTENT
    # ========================================================

    "AMBIGUOUS_INTENT": [

        "I see what you mean.",

        "That is something worth considering.",

        "I understand your point.",

        "Maybe that could work.",

        "That is one way to look at it.",

        "I suppose that is possible.",

        "I can see why you would say that.",

        "That might be reasonable.",

        "I understand where you are coming from.",

        "That is certainly something to think about.",

        "I guess that could be an option.",

        "I see the reasoning behind that.",

        "There may be something to that.",

        "I can understand the argument.",

        "That could make sense.",

        "I suppose we could look at it that way.",

        "I hear what you are saying.",

        "That is an interesting perspective.",

        "I can see the possibility.",

        "Perhaps that is worth considering.",
    ],
}


# ============================================================
# VALIDATE SCENARIOS
# ============================================================

def validate_scenarios():

    print("\nChecking scenario families...")

    for label in LABELS:

        if label not in SCENARIOS:

            raise RuntimeError(
                f"Missing scenario class: {label}"
            )

        count = len(
            SCENARIOS[label]
        )

        if count != 20:

            raise RuntimeError(
                f"{label} has {count} scenarios. "
                f"Expected 20."
            )

        print(
            f"  {label:<35} {count}"
        )


# ============================================================
# PRODUCTION FEATURE EXTRACTION
# ============================================================

def build_features(
    runner,
    text,
):
    """
    Run the exact production M1-M4
    feature extraction.

    M1 = 7 probabilities
    M2 = 7 probabilities
    M3 = 6 probabilities
    M4 = 5 retrieval similarities

    Total = 25 features.
    """

    # --------------------------------------------------------
    # M1 — Archaeologist
    # --------------------------------------------------------

    m1 = (
        runner
        ._get_archaeologist_probabilities(
            text
        )
    )

    if len(m1) != 7:

        raise RuntimeError(
            "M1 returned an invalid feature vector. "
            f"Expected 7 values, got {len(m1)}."
        )

    # --------------------------------------------------------
    # M2 — Psychologist
    # --------------------------------------------------------

    m2 = (
        runner
        ._get_psychologist_probabilities(
            text
        )
    )

    if len(m2) != 7:

        raise RuntimeError(
            "M2 returned an invalid feature vector. "
            f"Expected 7 values, got {len(m2)}."
        )

    # --------------------------------------------------------
    # M3 — Logician
    # --------------------------------------------------------

    m3 = (
        runner
        ._get_logician_probabilities(
            text
        )
    )

    if len(m3) != 6:

        raise RuntimeError(
            "M3 returned an invalid feature vector. "
            f"Expected 6 values, got {len(m3)}."
        )

    # --------------------------------------------------------
    # M4 — Historian
    # --------------------------------------------------------

    historian_result = (
        runner.run_historian(
            text
        )
    )

    m4 = (
        runner._get_historian_features(
            historian_result
        )
    )

    if len(m4) != 5:

        raise RuntimeError(
            "M4 returned an invalid feature vector. "
            f"Expected 5 values, got {len(m4)}."
        )

    # --------------------------------------------------------
    # FINAL VECTOR
    # --------------------------------------------------------

    features = (
        m1
        + m2
        + m3
        + m4
    )

    if len(features) != 25:

        raise RuntimeError(
            "M5 feature vector must contain "
            f"25 values, got {len(features)}."
        )

    return [
        float(value)
        for value in features
    ]


# ============================================================
# CREATE VARIANTS
# ============================================================

def create_variants(
    text,
):
    """
    Create four controlled variants.

    The base sentence remains intact.
    Variants are intentionally conservative so that
    the semantic class does not change.
    """

    variants = [
        text,

        f"Honestly, {text[0].lower()}{text[1:]}",

        f"{text} I suppose.",

        f"From my perspective, {text[0].lower()}{text[1:]}",
    ]

    # Remove accidental duplicates.
    unique = []

    for variant in variants:

        variant = variant.strip()

        if variant not in unique:

            unique.append(
                variant
            )

    # Guarantee exactly four variants.
    while len(unique) < 4:

        unique.append(
            text
        )

    return unique[:4]


# ============================================================
# BUILD ALL EXAMPLES
# ============================================================

def build_all_examples(
    runner,
):

    examples = []

    total_families = (
        len(LABELS)
        * 20
    )

    current_family = 0

    for label in LABELS:

        scenarios = SCENARIOS[
            label
        ]

        for scenario_index, text in enumerate(
            scenarios
        ):

            current_family += 1

            family_id = (
                f"{label.lower()}"
                f"_family_{scenario_index:02d}"
            )

            print(
                f"\rGenerating family "
                f"{current_family:03d}/"
                f"{total_families:03d}...",
                end="",
                flush=True,
            )

            variants = create_variants(
                text
            )

            for variant_index, variant in enumerate(
                variants
            ):

                features = build_features(
                    runner,
                    variant,
                )

                label_id = (
                    LABEL_TO_ID[
                        label
                    ]
                )

                target = [
                    1.0
                    if i == label_id
                    else 0.0
                    for i in range(
                        len(LABELS)
                    )
                ]

                difficulty = (
                    "easy"
                    if scenario_index < 7
                    else "medium"
                )

                examples.append(
                    {
                        "text": variant,

                        "family": family_id,

                        "variant_id":
                            variant_index,

                        "difficulty":
                            difficulty,

                        "source_type":
                            "controlled_contrastive_scenario",

                        "features":
                            features,

                        "label":
                            label,

                        "label_id":
                            label_id,

                        "target":
                            target,
                    }
                )

    print()

    return examples


# ============================================================
# SPLIT BY FAMILY
# ============================================================

def split_by_family(
    examples,
):

    family_to_examples = {}

    for example in examples:

        family = example[
            "family"
        ]

        if family not in family_to_examples:

            family_to_examples[
                family
            ] = []

        family_to_examples[
            family
        ].append(
            example
        )

    train_families = []
    validation_families = []
    test_families = []

    # --------------------------------------------------------
    # Exactly:
    #
    # 16 families/class -> train
    # 2 families/class  -> validation
    # 2 families/class  -> test
    # --------------------------------------------------------

    for label in LABELS:

        prefix = (
            label.lower()
            + "_family_"
        )

        label_families = [
            family
            for family in family_to_examples
            if family.startswith(
                prefix
            )
        ]

        if len(label_families) != 20:

            raise RuntimeError(
                f"{label} has "
                f"{len(label_families)} families. "
                f"Expected 20."
            )

        random.shuffle(
            label_families
        )

        train_families.extend(
            label_families[:16]
        )

        validation_families.extend(
            label_families[16:18]
        )

        test_families.extend(
            label_families[18:20]
        )

    train_family_set = set(
        train_families
    )

    validation_family_set = set(
        validation_families
    )

    test_family_set = set(
        test_families
    )

    train = []
    validation = []
    test = []

    for family, items in (
        family_to_examples.items()
    ):

        if family in train_family_set:

            train.extend(
                items
            )

        elif family in validation_family_set:

            validation.extend(
                items
            )

        elif family in test_family_set:

            test.extend(
                items
            )

        else:

            raise RuntimeError(
                f"Family was not assigned: "
                f"{family}"
            )

    random.shuffle(
        train
    )

    random.shuffle(
        validation
    )

    random.shuffle(
        test
    )

    return (
        train,
        validation,
        test,
        train_family_set,
        validation_family_set,
        test_family_set,
    )


# ============================================================
# WRITE JSONL
# ============================================================

def write_jsonl(
    path,
    examples,
):

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:

        for example in examples:

            file.write(
                json.dumps(
                    example,
                    ensure_ascii=False,
                )
                + "\n"
            )


# ============================================================
# CHECK SPLIT
# ============================================================

def check_split(
    name,
    examples,
):

    print(
        f"\n{name}: {len(examples)} examples"
    )

    counts = {
        label: 0
        for label in LABELS
    }

    families = set()

    for example in examples:

        label = example[
            "label"
        ]

        counts[label] += 1

        families.add(
            example[
                "family"
            ]
        )

        if len(
            example["features"]
        ) != 25:

            raise RuntimeError(
                f"Invalid feature count "
                f"in {name}: "
                f"{len(example['features'])}"
            )

        if example[
            "label_id"
        ] != LABEL_TO_ID[label]:

            raise RuntimeError(
                "Label ID mismatch."
            )

    for label in LABELS:

        print(
            f"  {label:<35}"
            f"{counts[label]:>4}"
        )

    print(
        f"  Families: {len(families)}"
    )

    return families


# ============================================================
# CHECK DUPLICATES
# ============================================================

def check_duplicates(
    examples,
):

    texts = [
        example["text"]
        for example in examples
    ]

    duplicates = (
        len(texts)
        - len(set(texts))
    )

    if duplicates > 0:

        raise RuntimeError(
            f"Found {duplicates} "
            f"duplicate texts."
        )

    print(
        "✓ Duplicate text check: 0"
    )


# ============================================================
# CHECK FAMILY LEAKAGE
# ============================================================

def check_family_leakage(
    train_families,
    validation_families,
    test_families,
):

    train_validation = (
        train_families
        & validation_families
    )

    train_test = (
        train_families
        & test_families
    )

    validation_test = (
        validation_families
        & test_families
    )

    if train_validation:

        raise RuntimeError(
            "Family leakage between "
            "train and validation."
        )

    if train_test:

        raise RuntimeError(
            "Family leakage between "
            "train and test."
        )

    if validation_test:

        raise RuntimeError(
            "Family leakage between "
            "validation and test."
        )

    print(
        "✓ Family leakage: 0"
    )


# ============================================================
# MANIFEST
# ============================================================

def create_manifest(
    train,
    validation,
    test,
    train_families,
    validation_families,
    test_families,
):

    return {

        "version":
            "m5_contrastive_v4",

        "seed":
            SEED,

        "total_examples":
            len(train)
            + len(validation)
            + len(test),

        "train_examples":
            len(train),

        "validation_examples":
            len(validation),

        "test_examples":
            len(test),

        "total_families":
            160,

        "train_families":
            len(train_families),

        "validation_families":
            len(validation_families),

        "test_families":
            len(test_families),

        "examples_per_family":
            4,

        "features":
            25,

        "labels":
            LABELS,

        "source_type":
            "controlled_contrastive_scenario",

        "feature_layout":
            {
                "archaeologist":
                    "0-6",

                "psychologist":
                    "7-13",

                "logician":
                    "14-19",

                "historian":
                    "20-24",
            },

        "production_feature_source":
            "LIMINALAgentRunner",

        "family_isolated":
            True,

        "test_used_for_training":
            False,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 70
    )

    print(
        "L.I.M.I.N.A.L. M5 DATASET BUILDER"
    )

    print(
        "Production M1-M4 Feature Extraction"
    )

    print(
        "=" * 70
    )

    print(
        f"\nSeed: {SEED}"
    )

    print(
        "\nChecking scenario definitions..."
    )

    validate_scenarios()

    # --------------------------------------------------------
    # Initialize the REAL production pipeline.
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 70
    )

    print(
        "INITIALIZING PRODUCTION AGENTS"
    )

    print(
        "=" * 70
    )

    runner = LIMINALAgentRunner()

    print(
        "\n✓ Production runner initialized."
    )

    # --------------------------------------------------------
    # Generate examples.
    # --------------------------------------------------------

    print(
        "\nGenerating M5 examples..."
    )

    examples = build_all_examples(
        runner
    )

    expected_total = (
        8
        * 20
        * 4
    )

    if len(examples) != expected_total:

        raise RuntimeError(
            f"Expected {expected_total} "
            f"examples but generated "
            f"{len(examples)}."
        )

    print(
        f"\n✓ Generated "
        f"{len(examples)} examples."
    )

    # --------------------------------------------------------
    # Split.
    # --------------------------------------------------------

    print(
        "\nSplitting by family..."
    )

    (
        train,
        validation,
        test,
        train_families,
        validation_families,
        test_families,
    ) = split_by_family(
        examples
    )

    # --------------------------------------------------------
    # Expected sizes.
    #
    # 128 train families × 4 = 512
    # 16 validation families × 4 = 64
    # 16 test families × 4 = 64
    # --------------------------------------------------------

    if len(train) != 512:

        raise RuntimeError(
            f"Expected 512 train examples, "
            f"got {len(train)}."
        )

    if len(validation) != 64:

        raise RuntimeError(
            f"Expected 64 validation examples, "
            f"got {len(validation)}."
        )

    if len(test) != 64:

        raise RuntimeError(
            f"Expected 64 test examples, "
            f"got {len(test)}."
        )

    # --------------------------------------------------------
    # Validate each split.
    # --------------------------------------------------------

    train_family_check = check_split(
        "TRAIN",
        train,
    )

    validation_family_check = check_split(
        "VALIDATION",
        validation,
    )

    test_family_check = check_split(
        "TEST",
        test,
    )

    # --------------------------------------------------------
    # Verify family counts.
    # --------------------------------------------------------

    if len(
        train_family_check
    ) != 128:

        raise RuntimeError(
            "Train must contain "
            "128 families."
        )

    if len(
        validation_family_check
    ) != 16:

        raise RuntimeError(
            "Validation must contain "
            "16 families."
        )

    if len(
        test_family_check
    ) != 16:

        raise RuntimeError(
            "Test must contain "
            "16 families."
        )

    # --------------------------------------------------------
    # Duplicate check.
    # --------------------------------------------------------

    print(
        "\nChecking duplicate texts..."
    )

    check_duplicates(
        examples
    )

    # --------------------------------------------------------
    # Leakage check.
    # --------------------------------------------------------

    print(
        "\nChecking family leakage..."
    )

    check_family_leakage(
        train_families,
        validation_families,
        test_families,
    )

    # --------------------------------------------------------
    # Write datasets.
    # --------------------------------------------------------

    print(
        "\nWriting dataset files..."
    )

    write_jsonl(
        TRAIN_FILE,
        train,
    )

    write_jsonl(
        VALIDATION_FILE,
        validation,
    )

    write_jsonl(
        TEST_FILE,
        test,
    )

    # --------------------------------------------------------
    # Manifest.
    # --------------------------------------------------------

    manifest = create_manifest(
        train,
        validation,
        test,
        train_families,
        validation_families,
        test_families,
    )

    with open(
        MANIFEST_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            manifest,
            file,
            indent=2,
        )

    # --------------------------------------------------------
    # Final report.
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 70
    )

    print(
        "M5 DATASET BUILD COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"\nTotal examples : "
        f"{len(examples)}"
    )

    print(
        f"Train          : "
        f"{len(train)}"
    )

    print(
        f"Validation     : "
        f"{len(validation)}"
    )

    print(
        f"Blind test     : "
        f"{len(test)}"
    )

    print(
        f"Total families : "
        f"{len(train_families) + len(validation_families) + len(test_families)}"
    )

    print(
        "\nFiles created:"
    )

    print(
        f"  {TRAIN_FILE}"
    )

    print(
        f"  {VALIDATION_FILE}"
    )

    print(
        f"  {TEST_FILE}"
    )

    print(
        f"  {MANIFEST_FILE}"
    )

    print(
        "\n✓ 25 production features per example"
    )

    print(
        "✓ Family-isolated split"
    )

    print(
        "✓ No duplicate texts"
    )

    print(
        "✓ Blind test preserved"
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "DO NOT train M5 yet."
    )

    print(
        "First verify this dataset output."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()