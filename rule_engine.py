"""Rule engine for validating demo emergency claim entries."""


def _catalog_entry(
    code,
    name,
    category,
    care_type,
    price,
    maximum_amount_per_claim,
    frequency_days=0,
    gender_categories="both",
    age_categories="both",
    high_cost=False,
):
    """Create one readable openIMIS-style service catalog entry."""
    return {
        "code": code,
        "name": name,
        "category": category,
        "care_type": care_type,
        "price": price,
        "maximum_amount_per_claim": maximum_amount_per_claim,
        "frequency_days": frequency_days,
        "gender_categories": gender_categories,
        "age_categories": age_categories,
        "high_cost": high_cost,
    }


SERVICE_CATALOG = {
    "emergency_assessment": _catalog_entry(
        "emergency_assessment", "Emergency Assessment",
        "emergency_care", "both", 500, 500,
    ),
    "airway_clearance": _catalog_entry(
        "airway_clearance", "Airway Clearance",
        "emergency_care", "both", 500, 500,
    ),
    "oxygen_support": _catalog_entry(
        "oxygen_support", "Oxygen Support",
        "emergency_care", "both", 1000, 1000,
    ),
    "oxygen": _catalog_entry(
        "oxygen", "Medical Oxygen",
        "item", "both", 1000, 1000,
    ),
    "cpr": _catalog_entry(
        "cpr", "Cardiopulmonary Resuscitation",
        "emergency_care", "both", 2000, 2000,
    ),
    "iv_fluids": _catalog_entry(
        "iv_fluids", "Intravenous Fluids",
        "item", "both", 800, 800,
    ),
    "warming_blanket": _catalog_entry(
        "warming_blanket", "Warming Blanket",
        "item", "both", 300, 300,
    ),
    "referral": _catalog_entry(
        "referral", "Emergency Referral",
        "referral", "both", 1000, 1000,
    ),
    "avpu_assessment": _catalog_entry(
        "avpu_assessment", "AVPU Assessment",
        "emergency_care", "both", 300, 300,
    ),
    "limb_immobilization": _catalog_entry(
        "limb_immobilization", "Limb Immobilization",
        "emergency_care", "both", 500, 500,
    ),
    "airway_monitoring": _catalog_entry(
        "airway_monitoring", "Airway Monitoring",
        "emergency_care", "both", 500, 500,
    ),
    "wound_cleaning": _catalog_entry(
        "wound_cleaning", "Wound Cleaning",
        "service", "outpatient", 500, 500,
    ),
    "observation": _catalog_entry(
        "observation", "Emergency Observation",
        "emergency_care", "both", 1000, 1000,
    ),
    "anti_snake_venom": _catalog_entry(
        "anti_snake_venom", "Anti-Snake Venom",
        "medicine", "both", 15000, 15000,
        high_cost=True,
    ),
    "tetanus_toxoid": _catalog_entry(
        "tetanus_toxoid", "Tetanus Toxoid",
        "medicine", "outpatient", 300, 300, frequency_days=30,
    ),
    "paracetamol": _catalog_entry(
        "paracetamol", "Paracetamol",
        "medicine", "outpatient", 100, 100,
    ),
    "antibiotics": _catalog_entry(
        "antibiotics", "Antibiotics",
        "medicine", "both", 1000, 1000,
    ),
    "abcde_assessment": _catalog_entry(
        "abcde_assessment", "ABCDE Assessment",
        "emergency_care", "both", 700, 700,
    ),
    "pain_management": _catalog_entry(
        "pain_management", "Pain Management",
        "service", "both", 500, 500,
    ),
    "xray": _catalog_entry(
        "xray", "X-Ray",
        "investigation", "both", 800, 800,
    ),
    "splinting": _catalog_entry(
        "splinting", "Splinting",
        "procedure", "both", 700, 700,
    ),
    "c_spine_protection": _catalog_entry(
        "c_spine_protection", "C-Spine Protection",
        "emergency_care", "both", 1000, 1000,
    ),
    "bleeding_control": _catalog_entry(
        "bleeding_control", "Bleeding Control",
        "emergency_care", "both", 600, 600,
    ),
    "surgery": _catalog_entry(
        "surgery", "Emergency Surgery",
        "procedure", "inpatient", 20000, 20000,
        high_cost=True,
    ),
    "icu_stay": _catalog_entry(
        "icu_stay", "Intensive Care Unit Stay",
        "service", "inpatient", 15000, 15000,
        high_cost=True,
    ),
    "mri": _catalog_entry(
        "mri", "MRI",
        "investigation", "both", 10000, 10000,
        high_cost=True,
    ),
    "morphine": _catalog_entry(
        "morphine", "Morphine",
        "medicine", "inpatient", 800, 800,
    ),
    "normal_delivery": _catalog_entry(
        "normal_delivery", "Normal Delivery",
        "procedure", "inpatient", 5000, 5000,
        gender_categories="female", age_categories="adult",
    ),
    "antenatal_care": _catalog_entry(
        "antenatal_care", "Antenatal Care",
        "service", "outpatient", 500, 500, frequency_days=30,
        gender_categories="female", age_categories="adult",
    ),
    "cosmetic_surgery": _catalog_entry(
        "cosmetic_surgery", "Cosmetic Surgery",
        "procedure", "inpatient", 25000, 25000,
        age_categories="adult",
    ),
    "tourniquet": _catalog_entry(
        "tourniquet", "Tourniquet Application",
        "procedure", "outpatient", 0, 0,
    ),
    "cut_wound": _catalog_entry(
        "cut_wound", "Cut the Bite Wound",
        "procedure", "outpatient", 0, 0,
    ),
    "suction_bite": _catalog_entry(
        "suction_bite", "Suction of Bite Wound",
        "procedure", "outpatient", 0, 0,
    ),
    "home_remedy": _catalog_entry(
        "home_remedy", "Home Remedy",
        "item", "outpatient", 0, 0,
    ),
}


PRICE_CATALOG = {
    code: metadata["price"]
    for code, metadata in SERVICE_CATALOG.items()
}


UNRELATED_SERVICES = {
    "normal_delivery",
    "antenatal_care",
    "cosmetic_surgery",
}


SUGGESTED_ACTIONS = {
    "ACCEPT": "Allow claim submission.",
    "WARNING": "Allow submission with justification.",
    "REVIEW_REQUIRED": "Send to medical reviewer before reimbursement.",
    "REJECT_ENTRY": "Prevent submission until claim data is corrected.",
}


def _normalize_text(value):
    """Convert text to lowercase snake_case."""
    if value is None:
        return ""
    words = str(value).strip().lower().split()
    return "_".join(words)


def _normalize_list(values):
    """Normalize a list of service or medicine codes."""
    if not values:
        return []
    return [_normalize_text(value) for value in values]


def _to_boolean(value):
    """Convert common boolean-like values to True or False."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return bool(value)


def _normalize_dictionary(values, normalize_values=False):
    """Normalize dictionary keys and optionally normalize text values."""
    normalized = {}
    for key, value in (values or {}).items():
        normalized_key = _normalize_text(key)
        if normalize_values and isinstance(value, str):
            normalized[normalized_key] = _normalize_text(value)
        else:
            normalized[normalized_key] = value
    return normalized


def _has_any_evidence(clinical_conditions, required_flags):
    """Return True when at least one required clinical flag is true."""
    return any(
        _to_boolean(clinical_conditions.get(flag, False))
        for flag in required_flags
    )


def _calculate_expected_total(services, medicines):
    """Sum catalog prices for every recognized claimed item."""
    return sum(
        PRICE_CATALOG.get(item, 0)
        for item in services + medicines
    )


def _calculate_maximum_total(services, medicines):
    """Sum maximum claim amounts for every recognized claimed item."""
    return sum(
        SERVICE_CATALOG.get(item, {}).get("maximum_amount_per_claim", 0)
        for item in services + medicines
    )


def _severity_evidence_is_sufficient(condition_code, clinical_conditions):
    """Check whether the condition contains evidence of serious illness."""
    severity_flags = {
        "drowning": [
            "not_breathing",
            "hypovolemia_or_shock",
            "associated_trauma",
            "neurological_concern",
        ],
        "snake_bite": [
            "neurotoxicity",
            "coagulopathy_or_bleeding",
            "shock",
            "acute_kidney_injury",
            "respiratory_difficulty",
        ],
        "fall_injury": [
            "fracture_suspected",
            "open_wound",
            "head_neck_trauma",
            "unconscious_or_low_gcs",
            "shock",
            "organ_injury_suspected",
            "neurological_concern",
        ],
    }
    return _has_any_evidence(
        clinical_conditions,
        severity_flags.get(condition_code, []),
    )


def _condition_rules(condition_code):
    """Return the core and conditional rules for a condition."""
    if condition_code == "drowning":
        return {
            "expected_services": [
                "emergency_assessment",
                "airway_clearance",
                "oxygen_support",
                "avpu_assessment",
                "warming_blanket",
                "referral",
            ],
            "conditional_items": {
                "cpr": ["not_breathing"],
                "iv_fluids": ["hypovolemia_or_shock"],
                "surgery": ["associated_trauma"],
                "mri": ["associated_trauma", "neurological_concern"],
            },
            "conditional_expected": {},
            "harmful_services": set(),
        }

    if condition_code == "snake_bite":
        return {
            "expected_services": [
                "emergency_assessment",
                "limb_immobilization",
                "airway_monitoring",
                "wound_cleaning",
                "observation",
            ],
            "conditional_items": {
                "anti_snake_venom": [
                    "neurotoxicity",
                    "coagulopathy_or_bleeding",
                    "shock",
                    "acute_kidney_injury",
                    "respiratory_difficulty",
                ],
                "antibiotics": ["wound_infection"],
                "iv_fluids": ["shock"],
                "oxygen_support": ["respiratory_difficulty"],
                "oxygen": ["respiratory_difficulty"],
            },
            "conditional_expected": {
                "referral": [
                    "neurotoxicity",
                    "coagulopathy_or_bleeding",
                    "shock",
                    "acute_kidney_injury",
                    "respiratory_difficulty",
                ],
            },
            "harmful_services": {
                "tourniquet",
                "cut_wound",
                "suction_bite",
                "home_remedy",
            },
        }

    if condition_code == "fall_injury":
        return {
            "expected_services": [
                "emergency_assessment",
                "abcde_assessment",
                "pain_management",
            ],
            "conditional_items": {
                "xray": [
                    "fracture_suspected",
                    "head_neck_trauma",
                    "organ_injury_suspected",
                ],
                "splinting": ["fracture_suspected"],
                "c_spine_protection": ["head_neck_trauma"],
                "surgery": [
                    "open_wound",
                    "fracture_suspected",
                    "organ_injury_suspected",
                ],
                "icu_stay": [
                    "unconscious_or_low_gcs",
                    "shock",
                    "organ_injury_suspected",
                ],
                "mri": [
                    "head_neck_trauma",
                    "neurological_concern",
                    "organ_injury_suspected",
                ],
                "tetanus_toxoid": ["open_wound"],
                "antibiotics": ["open_wound"],
                "morphine": [
                    "fracture_suspected",
                    "open_wound",
                    "organ_injury_suspected",
                ],
                "bleeding_control": ["active_bleeding"],
                "wound_cleaning": ["open_wound"],
            },
            "conditional_expected": {
                "bleeding_control": ["active_bleeding"],
                "wound_cleaning": ["open_wound"],
                "tetanus_toxoid": ["open_wound"],
                "referral": [
                    "unconscious_or_low_gcs",
                    "shock",
                    "organ_injury_suspected",
                    "fracture_suspected",
                ],
            },
            "harmful_services": set(),
        }

    return None


def validate_claim(
    condition_code,
    patient,
    clinical_conditions,
    services,
    medicines,
    claimed_amount,
):
    """Validate one emergency claim and return a decision dictionary."""
    normalized_condition = _normalize_text(condition_code)
    normalized_patient = _normalize_dictionary(
        patient,
        normalize_values=True,
    )
    if not normalized_patient.get("care_type"):
        normalized_patient["care_type"] = "outpatient"

    evidence = _normalize_dictionary(clinical_conditions)
    normalized_services = _normalize_list(services)
    normalized_medicines = _normalize_list(medicines)
    all_claimed_items = set(normalized_services + normalized_medicines)

    expected_total = _calculate_expected_total(
        normalized_services,
        normalized_medicines,
    )
    maximum_total = _calculate_maximum_total(
        normalized_services,
        normalized_medicines,
    )
    numeric_claimed_amount = float(claimed_amount)
    amount_ratio = (
        numeric_claimed_amount / expected_total
        if expected_total > 0
        else None
    )

    compliance_score = 100
    rule_hits = []
    reasons = []
    reject_entry = False
    force_review = False
    gender_mismatch = False
    age_mismatch = False
    care_type_mismatch = False
    max_amount_violation = False
    rules = _condition_rules(normalized_condition)

    # Unsupported condition codes cannot be safely validated.
    if rules is None:
        compliance_score = 0
        reject_entry = True
        rule_hits.append("INVALID_CONDITION_CODE")
        reasons.append(
            "The emergency condition code is not supported by this rule engine."
        )
    else:
        # Check the expected emergency pathway.
        for expected_service in rules["expected_services"]:
            if expected_service in normalized_services:
                continue

            if expected_service == "emergency_assessment":
                compliance_score -= 20
                rule_hits.append("MISSING_EMERGENCY_ASSESSMENT")
                reasons.append(
                    "Emergency assessment is missing from the claimed services."
                )
            else:
                compliance_score -= 10
                rule_hits.append(
                    "MISSING_CORE_SERVICE_" + expected_service.upper()
                )
                reasons.append(
                    f"Expected core service '{expected_service}' is missing."
                )

        # Check services that become expected when severity evidence is present.
        for expected_item, required_flags in rules["conditional_expected"].items():
            if not _has_any_evidence(evidence, required_flags):
                continue
            if expected_item in all_claimed_items:
                continue

            compliance_score -= 10
            rule_hits.append(
                "MISSING_CONDITIONALLY_EXPECTED_" + expected_item.upper()
            )
            reasons.append(
                f"Item '{expected_item}' is expected for the recorded clinical evidence."
            )

        # Check services and medicines that require clinical evidence.
        for item, required_flags in rules["conditional_items"].items():
            if item not in all_claimed_items:
                continue
            if _has_any_evidence(evidence, required_flags):
                continue

            compliance_score -= 30
            if PRICE_CATALOG.get(item, 0) >= 10000:
                rule_hits.append(
                    "HIGH_COST_WITHOUT_EVIDENCE_" + item.upper()
                )
                reasons.append(
                    f"High-cost item '{item}' lacks the required clinical evidence."
                )
            else:
                rule_hits.append(
                    "CONDITIONAL_ITEM_WITHOUT_EVIDENCE_" + item.upper()
                )
                reasons.append(
                    f"Item '{item}' is not supported by the required clinical evidence."
                )

        # Harmful snake-bite interventions always reject the entry.
        for service in normalized_services:
            if service not in rules["harmful_services"]:
                continue
            compliance_score -= 60
            reject_entry = True
            rule_hits.append("HARMFUL_SERVICE_" + service.upper())
            reasons.insert(
                0,
                f"Service '{service}' is contraindicated or harmful for this condition."
            )

        # Unrelated services always reject the entry.
        for service in normalized_services:
            if service not in UNRELATED_SERVICES:
                continue
            compliance_score -= 80
            reject_entry = True
            rule_hits.append("UNRELATED_SERVICE_" + service.upper())
            reasons.insert(
                0,
                f"Service '{service}' is unrelated to the selected emergency condition."
            )

    # Flag service or medicine codes that are outside the demo catalog.
    unknown_items = []
    for item in normalized_services + normalized_medicines:
        if item in SERVICE_CATALOG:
            continue
        unknown_items.append(item)
        compliance_score -= 5
        rule_hits.append("UNKNOWN_ITEM_" + item.upper())
        reasons.append(
            f"Item '{item}' is not found in the demo service/medicine catalog."
        )

    # Apply openIMIS-style patient and service metadata checks.
    patient_gender = normalized_patient.get("gender", "")
    patient_age_group = normalized_patient.get("age_group", "")
    patient_care_type = normalized_patient["care_type"]

    for item in sorted(all_claimed_items):
        metadata = SERVICE_CATALOG.get(item)
        if metadata is None:
            continue

        allowed_gender = metadata["gender_categories"]
        if allowed_gender != "both" and patient_gender != allowed_gender:
            gender_mismatch = True
            compliance_score -= 40
            reject_entry = True
            rule_hits.append("GENDER_MISMATCH_" + item.upper())
            reasons.insert(
                0,
                f"Item '{item}' is limited to {allowed_gender} patients, "
                f"but the claim patient is {patient_gender or 'unspecified'}.",
            )

        allowed_age = metadata["age_categories"]
        if allowed_age != "both" and patient_age_group != allowed_age:
            age_mismatch = True
            compliance_score -= 30
            rule_hits.append("AGE_MISMATCH_" + item.upper())
            reasons.append(
                f"Item '{item}' is limited to {allowed_age} patients, "
                f"but the claim patient is {patient_age_group or 'unspecified'}.",
            )

        if (
            metadata["care_type"] == "inpatient"
            and patient_care_type == "outpatient"
        ):
            care_type_mismatch = True
            force_review = True
            compliance_score -= 30
            rule_hits.append("CARE_TYPE_MISMATCH_" + item.upper())
            reasons.append(
                f"Inpatient-only item '{item}' is claimed in outpatient care."
            )

    # Compare the total claim against the sum of item-level maximum amounts.
    if (
        maximum_total > 0
        and numeric_claimed_amount > maximum_total * 1.5
    ):
        max_amount_violation = True
        force_review = True
        compliance_score -= 30
        rule_hits.append("MAX_AMOUNT_VIOLATION")
        reasons.append(
            "The claimed amount exceeds 150% of the combined maximum "
            "amount allowed for the claimed services and items."
        )

    high_cost_count = sum(
        1
        for item in all_claimed_items
        if SERVICE_CATALOG.get(item, {}).get("high_cost", False)
    )
    if (
        high_cost_count >= 2
        and not _severity_evidence_is_sufficient(
            normalized_condition,
            evidence,
        )
    ):
        compliance_score -= 20
        rule_hits.append("MULTIPLE_HIGH_COST_ITEMS_WEAK_EVIDENCE")
        reasons.append(
            "Multiple high-cost items are claimed without sufficient severity evidence."
        )

    # Validate the claimed amount only when catalog-priced items are present.
    if amount_ratio is not None and amount_ratio > 1.5:
        compliance_score -= 15
        rule_hits.append("AMOUNT_OVER_150_PERCENT")
        reasons.append(
            "The claimed amount is more than 150% of the catalog total."
        )

    if amount_ratio is not None and amount_ratio > 3.0:
        compliance_score -= 30
        rule_hits.append("AMOUNT_OVER_300_PERCENT")
        reasons.append(
            "The claimed amount is more than 300% of the catalog total."
        )

    compliance_score = max(0, min(100, compliance_score))

    # Determine the final claim-entry decision.
    if reject_entry:
        decision = "REJECT_ENTRY"
        submission_allowed = False
    elif force_review:
        decision = "REVIEW_REQUIRED"
        submission_allowed = True
    elif compliance_score >= 80:
        decision = "ACCEPT"
        submission_allowed = True
    elif compliance_score >= 60:
        decision = "WARNING"
        submission_allowed = True
    else:
        decision = "REVIEW_REQUIRED"
        submission_allowed = True

    if decision == "ACCEPT" and not reasons:
        reasons.append(
            "Claim follows the expected emergency care pathway for the selected condition."
        )

    return {
        "condition_code": normalized_condition.upper(),
        "patient": normalized_patient,
        "decision": decision,
        "submission_allowed": submission_allowed,
        "compliance_score": compliance_score,
        "legitimacy_score": round(compliance_score / 100, 2),
        "expected_total": expected_total,
        "amount_ratio": round(amount_ratio, 2) if amount_ratio is not None else None,
        "openimis_checks": {
            "gender_mismatch": gender_mismatch,
            "age_mismatch": age_mismatch,
            "care_type_mismatch": care_type_mismatch,
            "max_amount_violation": max_amount_violation,
            "high_cost_count": high_cost_count,
            "unknown_item_count": len(unknown_items),
        },
        "rule_hits": rule_hits,
        "reasons": reasons,
        "suggested_action": SUGGESTED_ACTIONS[decision],
    }


if __name__ == "__main__":
    test_cases = [
        {
            "name": "Test 1: Valid drowning pathway",
            "condition_code": "DROWNING",
            "patient": {"gender": "male", "age_group": "adult"},
            "clinical_conditions": {
                "not_breathing": True,
                "aspiration_risk": True,
                "hypovolemia_or_shock": False,
                "hypothermia": True,
                "associated_trauma": False,
                "neurological_concern": False,
            },
            "services": [
                "emergency_assessment",
                "airway_clearance",
                "cpr",
                "oxygen_support",
                "warming_blanket",
                "referral",
                "avpu_assessment",
            ],
            "medicines": ["oxygen"],
            "claimed_amount": 6000,
        },
        {
            "name": "Test 2: Snake bite ASV misuse",
            "condition_code": "SNAKE_BITE",
            "patient": {"gender": "male", "age_group": "adult"},
            "clinical_conditions": {
                "neurotoxicity": False,
                "coagulopathy_or_bleeding": False,
                "shock": False,
                "acute_kidney_injury": False,
                "respiratory_difficulty": False,
                "wound_infection": False,
            },
            "services": [
                "emergency_assessment",
                "limb_immobilization",
                "observation",
            ],
            "medicines": ["anti_snake_venom"],
            "claimed_amount": 18000,
        },
        {
            "name": "Test 3: Fall injury without supporting evidence",
            "condition_code": "FALL_INJURY",
            "patient": {"gender": "female", "age_group": "adult"},
            "clinical_conditions": {
                "fracture_suspected": False,
                "open_wound": False,
                "active_bleeding": False,
                "head_neck_trauma": False,
                "unconscious_or_low_gcs": False,
                "shock": False,
                "organ_injury_suspected": False,
                "neurological_concern": False,
            },
            "services": [
                "emergency_assessment",
                "mri",
                "surgery",
                "icu_stay",
            ],
            "medicines": ["morphine"],
            "claimed_amount": 45000,
        },
        {
            "name": "Test 4: Snake bite with unrelated service",
            "condition_code": "SNAKE_BITE",
            "patient": {"gender": "female", "age_group": "adult"},
            "clinical_conditions": {
                "neurotoxicity": False,
                "coagulopathy_or_bleeding": False,
                "shock": False,
                "acute_kidney_injury": False,
                "respiratory_difficulty": False,
                "wound_infection": False,
            },
            "services": ["normal_delivery"],
            "medicines": [],
            "claimed_amount": 7000,
        },
    ]

    for test_case in test_cases:
        print("\n" + test_case.pop("name"))
        print("-" * 60)
        print(validate_claim(**test_case))
