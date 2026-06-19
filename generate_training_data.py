"""Generate synthetic emergency claim data labeled by rule_engine.py."""

import csv
import random
from collections import Counter
from pathlib import Path

from rule_engine import PRICE_CATALOG, SERVICE_CATALOG, validate_claim


ROWS_PER_CONDITION = 4000
NON_CONFLICT_PER_CONDITION = 2000
CONFLICT_PER_CONDITION = 2000
TOTAL_ROWS = ROWS_PER_CONDITION * 3
RANDOM_SEED = 42

CONDITIONS = ["DROWNING", "SNAKE_BITE", "FALL_INJURY"]
GENDERS = ["male", "female"]
AGE_GROUPS = ["adult", "minor"]
CARE_TYPES = ["outpatient", "inpatient"]

CLINICAL_FLAGS = [
    "not_breathing",
    "aspiration_risk",
    "hypovolemia_or_shock",
    "hypothermia",
    "associated_trauma",
    "neurological_concern",
    "neurotoxicity",
    "coagulopathy_or_bleeding",
    "shock",
    "acute_kidney_injury",
    "respiratory_difficulty",
    "wound_infection",
    "fracture_suspected",
    "open_wound",
    "active_bleeding",
    "head_neck_trauma",
    "unconscious_or_low_gcs",
    "organ_injury_suspected",
]

ITEMS = [
    "emergency_assessment",
    "airway_clearance",
    "oxygen_support",
    "cpr",
    "iv_fluids",
    "warming_blanket",
    "referral",
    "avpu_assessment",
    "limb_immobilization",
    "airway_monitoring",
    "wound_cleaning",
    "observation",
    "anti_snake_venom",
    "tetanus_toxoid",
    "paracetamol",
    "antibiotics",
    "abcde_assessment",
    "pain_management",
    "xray",
    "splinting",
    "c_spine_protection",
    "bleeding_control",
    "surgery",
    "icu_stay",
    "mri",
    "morphine",
    "normal_delivery",
    "antenatal_care",
    "cosmetic_surgery",
    "tourniquet",
    "cut_wound",
    "suction_bite",
    "home_remedy",
]

MEDICINE_ITEMS = {
    "anti_snake_venom",
    "tetanus_toxoid",
    "paracetamol",
    "antibiotics",
    "morphine",
}

CORE_SERVICES = {
    "DROWNING": [
        "emergency_assessment",
        "airway_clearance",
        "oxygen_support",
        "avpu_assessment",
        "warming_blanket",
        "referral",
    ],
    "SNAKE_BITE": [
        "emergency_assessment",
        "limb_immobilization",
        "airway_monitoring",
        "wound_cleaning",
        "observation",
    ],
    "FALL_INJURY": [
        "emergency_assessment",
        "abcde_assessment",
        "pain_management",
    ],
}

CONFLICT_PATTERNS = [
    ("DROWNING", "cpr_without_breathing"),
    ("DROWNING", "mri_without_evidence"),
    ("DROWNING", "normal_delivery"),
    ("DROWNING", "antenatal_care"),
    ("DROWNING", "high_amount"),
    ("SNAKE_BITE", "asv_without_evidence"),
    ("SNAKE_BITE", "tourniquet"),
    ("SNAKE_BITE", "cut_wound"),
    ("SNAKE_BITE", "suction_bite"),
    ("SNAKE_BITE", "home_remedy"),
    ("SNAKE_BITE", "antibiotics_without_infection"),
    ("SNAKE_BITE", "high_amount"),
    ("FALL_INJURY", "surgery_without_evidence"),
    ("FALL_INJURY", "icu_without_evidence"),
    ("FALL_INJURY", "mri_without_evidence"),
    ("FALL_INJURY", "high_amount"),
    ("DROWNING", "gender_mismatch"),
    ("SNAKE_BITE", "age_mismatch"),
    ("FALL_INJURY", "care_type_mismatch"),
    ("FALL_INJURY", "multiple_high_cost_weak_evidence"),
]


def _add_item(claim, item):
    """Add an item to the correct claim list without duplicates."""
    target = claim["medicines"] if item in MEDICINE_ITEMS else claim["services"]
    if item not in target:
        target.append(item)


def _remove_item(claim, item):
    """Remove an item from services or medicines when present."""
    if item in claim["services"]:
        claim["services"].remove(item)
    if item in claim["medicines"]:
        claim["medicines"].remove(item)


def _catalog_total(claim):
    """Calculate the catalog total before calling the rule engine."""
    items = claim["services"] + claim["medicines"]
    return sum(PRICE_CATALOG.get(item, 0) for item in items)


def _set_claimed_amount(claim, minimum_ratio, maximum_ratio):
    """Set a random claimed amount relative to the catalog total."""
    expected_total = _catalog_total(claim)
    base_total = expected_total if expected_total > 0 else 500
    ratio = random.uniform(minimum_ratio, maximum_ratio)
    claim["claimed_amount"] = round(base_total * ratio, 2)


def _new_claim(condition_code):
    """Create a clean claim with the core pathway for one condition."""
    medicines = []
    if condition_code == "SNAKE_BITE":
        medicines = ["tetanus_toxoid", "paracetamol"]

    return {
        "condition_code": condition_code,
        "patient": {
            "gender": random.choice(GENDERS),
            "age_group": random.choice(AGE_GROUPS),
            "care_type": random.choices(
                CARE_TYPES,
                weights=[80, 20],
                k=1,
            )[0],
        },
        "clinical_conditions": {
            flag: False for flag in CLINICAL_FLAGS
        },
        "services": list(CORE_SERVICES[condition_code]),
        "medicines": medicines,
        "claimed_amount": 0,
    }


def _occasionally_omit_core_services(claim):
    """Create ACCEPT and WARNING variations without creating conflicts."""
    roll = random.random()
    condition_code = claim["condition_code"]

    if roll < 0.70:
        return
    if roll < 0.85:
        removable = [
            item
            for item in CORE_SERVICES[condition_code]
            if item != "emergency_assessment"
        ]
        _remove_item(claim, random.choice(removable))
        return
    if roll < 0.95:
        _remove_item(claim, "emergency_assessment")
        return

    _remove_item(claim, "emergency_assessment")
    removable = [
        item
        for item in CORE_SERVICES[condition_code]
        if item != "emergency_assessment"
    ]
    _remove_item(claim, random.choice(removable))


def _use_inpatient_care_when_required(claim):
    """Keep valid claims consistent with inpatient-only catalog metadata."""
    claimed_items = claim["services"] + claim["medicines"]
    if any(
        SERVICE_CATALOG[item]["care_type"] == "inpatient"
        for item in claimed_items
        if item in SERVICE_CATALOG
    ):
        claim["patient"]["care_type"] = "inpatient"


def _build_valid_claim(condition_code):
    """Build a clinically consistent ACCEPT or WARNING claim."""
    claim = _new_claim(condition_code)
    evidence = claim["clinical_conditions"]

    if condition_code == "DROWNING":
        evidence["not_breathing"] = random.random() < 0.25
        evidence["aspiration_risk"] = random.random() < 0.45
        evidence["hypovolemia_or_shock"] = random.random() < 0.20
        evidence["hypothermia"] = random.random() < 0.35
        evidence["associated_trauma"] = random.random() < 0.15
        evidence["neurological_concern"] = random.random() < 0.15

        if evidence["not_breathing"]:
            _add_item(claim, "cpr")
        if evidence["hypovolemia_or_shock"]:
            _add_item(claim, "iv_fluids")
        if evidence["associated_trauma"] and random.random() < 0.45:
            _add_item(claim, "surgery")
        if (
            evidence["associated_trauma"]
            or evidence["neurological_concern"]
        ) and random.random() < 0.55:
            _add_item(claim, "mri")

    elif condition_code == "SNAKE_BITE":
        evidence["neurotoxicity"] = random.random() < 0.18
        evidence["coagulopathy_or_bleeding"] = random.random() < 0.16
        evidence["shock"] = random.random() < 0.12
        evidence["acute_kidney_injury"] = random.random() < 0.10
        evidence["respiratory_difficulty"] = random.random() < 0.15
        evidence["wound_infection"] = random.random() < 0.20

        envenomation_flags = [
            "neurotoxicity",
            "coagulopathy_or_bleeding",
            "shock",
            "acute_kidney_injury",
            "respiratory_difficulty",
        ]
        if any(evidence[flag] for flag in envenomation_flags):
            _add_item(claim, "anti_snake_venom")
            _add_item(claim, "referral")
        if evidence["wound_infection"]:
            _add_item(claim, "antibiotics")
        if evidence["shock"]:
            _add_item(claim, "iv_fluids")
        if evidence["respiratory_difficulty"]:
            _add_item(claim, "oxygen_support")

    else:
        evidence["fracture_suspected"] = random.random() < 0.38
        evidence["open_wound"] = random.random() < 0.25
        evidence["active_bleeding"] = random.random() < 0.18
        evidence["head_neck_trauma"] = random.random() < 0.20
        evidence["unconscious_or_low_gcs"] = random.random() < 0.10
        evidence["shock"] = random.random() < 0.10
        evidence["organ_injury_suspected"] = random.random() < 0.14
        evidence["neurological_concern"] = random.random() < 0.12

        if (
            evidence["fracture_suspected"]
            or evidence["head_neck_trauma"]
            or evidence["organ_injury_suspected"]
        ):
            _add_item(claim, "xray")
        if evidence["fracture_suspected"]:
            _add_item(claim, "splinting")
        if evidence["head_neck_trauma"]:
            _add_item(claim, "c_spine_protection")
        if evidence["active_bleeding"]:
            _add_item(claim, "bleeding_control")
        if (
            evidence["open_wound"]
            or evidence["fracture_suspected"]
            or evidence["organ_injury_suspected"]
        ) and random.random() < 0.35:
            _add_item(claim, "surgery")
        if (
            evidence["unconscious_or_low_gcs"]
            or evidence["shock"]
            or evidence["organ_injury_suspected"]
        ) and random.random() < 0.45:
            _add_item(claim, "icu_stay")
        if (
            evidence["head_neck_trauma"]
            or evidence["neurological_concern"]
            or evidence["organ_injury_suspected"]
        ) and random.random() < 0.45:
            _add_item(claim, "mri")
        if evidence["open_wound"]:
            _add_item(claim, "wound_cleaning")
            _add_item(claim, "tetanus_toxoid")
            if random.random() < 0.70:
                _add_item(claim, "antibiotics")
        if (
            evidence["unconscious_or_low_gcs"]
            or evidence["shock"]
            or evidence["organ_injury_suspected"]
            or evidence["fracture_suspected"]
        ):
            _add_item(claim, "referral")
        if (
            evidence["fracture_suspected"]
            or evidence["open_wound"]
            or evidence["organ_injury_suspected"]
        ) and random.random() < 0.40:
            _add_item(claim, "morphine")

    _occasionally_omit_core_services(claim)
    _use_inpatient_care_when_required(claim)
    _set_claimed_amount(claim, 0.80, 1.40)
    return claim


def _build_conflicting_claim(condition_code, pattern):
    """Build a claim containing a known conflict pattern."""
    claim = _new_claim(condition_code)
    evidence = claim["clinical_conditions"]

    if pattern == "cpr_without_breathing":
        evidence["not_breathing"] = False
        _add_item(claim, "cpr")
        _remove_item(claim, "emergency_assessment")
        _remove_item(claim, "airway_clearance")

    elif pattern == "mri_without_evidence":
        evidence["associated_trauma"] = False
        evidence["neurological_concern"] = False
        evidence["head_neck_trauma"] = False
        evidence["organ_injury_suspected"] = False
        _add_item(claim, "mri")
        _remove_item(claim, "emergency_assessment")
        second_core = (
            "airway_clearance"
            if condition_code == "DROWNING"
            else "abcde_assessment"
        )
        _remove_item(claim, second_core)

    elif pattern in {
        "normal_delivery",
        "antenatal_care",
        "tourniquet",
        "cut_wound",
        "suction_bite",
        "home_remedy",
    }:
        _add_item(claim, pattern)

    elif pattern == "asv_without_evidence":
        _add_item(claim, "anti_snake_venom")
        _remove_item(claim, "airway_monitoring")
        _remove_item(claim, "wound_cleaning")

    elif pattern == "antibiotics_without_infection":
        evidence["wound_infection"] = False
        _add_item(claim, "antibiotics")
        _remove_item(claim, "emergency_assessment")

    elif pattern == "surgery_without_evidence":
        evidence["fracture_suspected"] = False
        evidence["open_wound"] = False
        evidence["organ_injury_suspected"] = False
        _add_item(claim, "surgery")
        _remove_item(claim, "abcde_assessment")
        _remove_item(claim, "pain_management")

    elif pattern == "icu_without_evidence":
        evidence["unconscious_or_low_gcs"] = False
        evidence["shock"] = False
        evidence["organ_injury_suspected"] = False
        _add_item(claim, "icu_stay")
        _remove_item(claim, "abcde_assessment")
        _remove_item(claim, "pain_management")

    elif pattern == "gender_mismatch":
        claim["patient"]["gender"] = "male"
        claim["patient"]["age_group"] = "adult"
        claim["patient"]["care_type"] = "inpatient"
        _add_item(claim, "normal_delivery")

    elif pattern == "age_mismatch":
        claim["patient"]["gender"] = "female"
        claim["patient"]["age_group"] = "minor"
        _add_item(claim, "antenatal_care")

    elif pattern == "care_type_mismatch":
        claim["patient"]["care_type"] = "outpatient"
        evidence["fracture_suspected"] = True
        _add_item(claim, "xray")
        _add_item(claim, "splinting")
        _add_item(claim, "surgery")
        _add_item(claim, "referral")

    elif pattern == "multiple_high_cost_weak_evidence":
        claim["patient"]["care_type"] = "outpatient"
        _add_item(claim, "mri")
        _add_item(claim, "surgery")

    if pattern == "high_amount":
        _set_claimed_amount(claim, 3.20, 4.80)
    elif pattern == "antibiotics_without_infection":
        _set_claimed_amount(claim, 1.60, 2.20)
    else:
        _set_claimed_amount(claim, 0.90, 1.30)

    return claim


def _claim_to_row(claim):
    """Call the rule engine and convert a claim into one CSV row."""
    result = validate_claim(
        claim["condition_code"],
        claim["patient"],
        claim["clinical_conditions"],
        claim["services"],
        claim["medicines"],
        claim["claimed_amount"],
    )

    all_items = set(claim["services"] + claim["medicines"])
    catalog_entries = [
        SERVICE_CATALOG[item]
        for item in all_items
        if item in SERVICE_CATALOG
    ]
    openimis_checks = result["openimis_checks"]
    conflict_label = int(
        result["decision"] in {"REVIEW_REQUIRED", "REJECT_ENTRY"}
    )

    row = {
        "condition_code": claim["condition_code"],
        "gender": claim["patient"]["gender"],
        "age_group": claim["patient"]["age_group"],
        "care_type": result["patient"]["care_type"],
        "claimed_amount": claim["claimed_amount"],
    }

    for flag in CLINICAL_FLAGS:
        row[flag] = int(bool(claim["clinical_conditions"].get(flag, False)))

    for item in ITEMS:
        row["has_" + item] = int(item in all_items)

    row.update(
        {
            "expected_total": result["expected_total"],
            "amount_ratio": (
                result["amount_ratio"]
                if result["amount_ratio"] is not None
                else ""
            ),
            "service_count": len(claim["services"]),
            "medicine_count": len(claim["medicines"]),
            "has_gender_mismatch": int(
                openimis_checks["gender_mismatch"]
            ),
            "has_age_mismatch": int(
                openimis_checks["age_mismatch"]
            ),
            "has_care_type_mismatch": int(
                openimis_checks["care_type_mismatch"]
            ),
            "has_max_amount_violation": int(
                openimis_checks["max_amount_violation"]
            ),
            "high_cost_count": openimis_checks["high_cost_count"],
            "has_multiple_high_cost_items": int(
                openimis_checks["high_cost_count"] >= 2
            ),
            "has_inpatient_only_service": int(
                any(
                    metadata["care_type"] == "inpatient"
                    for metadata in catalog_entries
                )
            ),
            "has_outpatient_service": int(
                any(
                    metadata["care_type"] == "outpatient"
                    for metadata in catalog_entries
                )
            ),
            "has_emergency_service": int(
                any(
                    metadata["category"] == "emergency_care"
                    for metadata in catalog_entries
                )
            ),
            "has_investigation": int(
                any(
                    metadata["category"] == "investigation"
                    for metadata in catalog_entries
                )
            ),
            "has_procedure": int(
                any(
                    metadata["category"] == "procedure"
                    for metadata in catalog_entries
                )
            ),
            "has_medicine": int(
                any(
                    metadata["category"] == "medicine"
                    for metadata in catalog_entries
                )
            ),
            "has_referral": int(
                any(
                    metadata["category"] == "referral"
                    for metadata in catalog_entries
                )
            ),
            "decision": result["decision"],
            "compliance_score": result["compliance_score"],
            "legitimacy_score": result["legitimacy_score"],
            "conflict_label": conflict_label,
        }
    )
    return row


def generate_dataset():
    """Generate an exactly balanced dataset for every diagnosis."""
    random.seed(RANDOM_SEED)
    rows = []

    for condition_code in CONDITIONS:
        non_conflict_rows = []
        while len(non_conflict_rows) < NON_CONFLICT_PER_CONDITION:
            row = _claim_to_row(_build_valid_claim(condition_code))
            if row["conflict_label"] == 0:
                non_conflict_rows.append(row)

        condition_patterns = [
            pattern
            for pattern_condition, pattern in CONFLICT_PATTERNS
            if pattern_condition == condition_code
        ]
        conflict_rows = []
        conflict_index = 0
        while len(conflict_rows) < CONFLICT_PER_CONDITION:
            pattern = condition_patterns[
                conflict_index % len(condition_patterns)
            ]
            claim = _build_conflicting_claim(condition_code, pattern)
            row = _claim_to_row(claim)
            conflict_index += 1
            if row["conflict_label"] == 1:
                conflict_rows.append(row)

        rows.extend(non_conflict_rows)
        rows.extend(conflict_rows)

    random.shuffle(rows)
    return rows


def save_dataset(rows):
    """Save generated rows to data/training_data.csv."""
    output_directory = Path(__file__).resolve().parent / "data"
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / "training_data.csv"

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def main():
    """Generate, save, and summarize the synthetic dataset."""
    rows = generate_dataset()
    output_path = save_dataset(rows)

    conflict_distribution = Counter(
        row["conflict_label"] for row in rows
    )
    decision_distribution = Counter(row["decision"] for row in rows)
    condition_label_distribution = {
        condition_code: dict(
            sorted(
                Counter(
                    row["conflict_label"]
                    for row in rows
                    if row["condition_code"] == condition_code
                ).items()
            )
        )
        for condition_code in CONDITIONS
    }
    mismatch_counts = {
        "gender_mismatch": sum(
            row["has_gender_mismatch"] for row in rows
        ),
        "age_mismatch": sum(
            row["has_age_mismatch"] for row in rows
        ),
        "care_type_mismatch": sum(
            row["has_care_type_mismatch"] for row in rows
        ),
        "max_amount_violation": sum(
            row["has_max_amount_violation"] for row in rows
        ),
        "multiple_high_cost_items": sum(
            row["has_multiple_high_cost_items"] for row in rows
        ),
    }

    print(f"Dataset shape: ({len(rows)}, {len(rows[0])})")
    print(f"Decision distribution: {dict(sorted(decision_distribution.items()))}")
    print(f"Conflict label distribution: {dict(sorted(conflict_distribution.items()))}")
    print(f"Condition-wise label distribution: {condition_label_distribution}")
    print(f"openIMIS mismatch counts: {mismatch_counts}")
    print(f"Saved CSV: {output_path}")


if __name__ == "__main__":
    main()
