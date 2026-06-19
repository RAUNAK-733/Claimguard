"""Generate synthetic emergency and basic-care claim data labeled by rule_engine.py."""

import csv
import random
from collections import Counter, defaultdict
from pathlib import Path

from rule_engine import CONDITION_RULES, SERVICE_CATALOG, validate_claim


ROWS_PER_CONDITION = 2000
NON_CONFLICT_PER_CONDITION = 1000
CONFLICT_PER_CONDITION = 1000
RANDOM_SEED = 42

EMERGENCY_CONDITIONS = ["DROWNING", "SNAKE_BITE", "FALL_INJURY"]
BASIC_CONDITIONS = [
    "HYPERTENSION",
    "FEVER",
    "DIARRHOEA",
    "ANAEMIA",
    "HIV",
    "PROSTATE_SURGERY",
    "TESTICULAR_ULTRASOUND",
    "CIRCUMCISION",
    "ANTENATAL_CARE",
    "NORMAL_DELIVERY",
    "CAESAREAN_SECTION",
]
ALL_CONDITIONS = EMERGENCY_CONDITIONS + BASIC_CONDITIONS

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
    "chest_pain_or_cardiac_risk",
    "uncontrolled_bp",
    "new_patient",
    "travel_or_malaria_area",
    "duration_more_than_3_days",
    "respiratory_symptoms",
    "bacterial_infection_suspected",
    "dehydration_signs",
    "blood_in_stool",
    "amoebiasis_suspected",
    "severe_anaemia_or_instability",
    "b12_deficiency_suspected",
    "severe_iron_deficiency",
    "confirmed_diagnosis",
    "on_art_already",
    "opportunistic_infection_risk",
    "urinary_retention",
    "biopsy_confirmed",
    "palpable_mass",
    "infection_or_mass_suspected",
    "phimosis_confirmed",
    "recurrent_infection",
    "medical_indication",
    "first_visit",
    "high_risk_pregnancy",
    "routine_follow_up",
    "full_term",
    "active_labour",
    "infection_risk",
    "fetal_distress",
    "failed_labour",
    "prior_c_section",
    "maternal_complication_or_shock",
]

ITEMS = sorted(SERVICE_CATALOG.keys())


def _new_claim(condition_code):
    """Create a clean claim shell for one condition."""
    rule = CONDITION_RULES[condition_code]
    required_gender = rule.get("required_gender")
    return {
        "condition_code": condition_code,
        "patient": {
            "gender": required_gender or random.choice(["male", "female"]),
            "age_group": "adult",
            "care_type": "outpatient",
            "care_category": rule["care_category"],
        },
        "clinical_conditions": {flag: False for flag in CLINICAL_FLAGS},
        "services": [],
        "medicines": [],
        "claimed_amount": 0,
    }


def _add_item(claim, item):
    """Add an item into services or medicines without duplicates."""
    metadata = SERVICE_CATALOG.get(item, {})
    target_name = "medicines" if metadata.get("category") == "medicine" else "services"
    if item not in claim[target_name]:
        claim[target_name].append(item)


def _remove_item(claim, item):
    """Remove an item from the claim when present."""
    if item in claim["services"]:
        claim["services"].remove(item)
    if item in claim["medicines"]:
        claim["medicines"].remove(item)


def _catalog_total(claim):
    """Calculate the raw catalog total before validation."""
    total = 0
    for item in claim["services"] + claim["medicines"]:
        total += SERVICE_CATALOG.get(item, {}).get("price", 0)
    return total


def _set_claimed_amount(claim, minimum_ratio, maximum_ratio):
    """Set a random claimed amount relative to the catalog total."""
    expected_total = _catalog_total(claim)
    base_total = expected_total if expected_total > 0 else 500
    claim["claimed_amount"] = round(
        base_total * random.uniform(minimum_ratio, maximum_ratio),
        2,
    )


def _use_inpatient_when_needed(claim):
    """Align care type with inpatient-only procedures when needed."""
    if any(
        SERVICE_CATALOG.get(item, {}).get("care_type") == "inpatient"
        for item in claim["services"] + claim["medicines"]
    ):
        claim["patient"]["care_type"] = "inpatient"


def _build_valid_claim(condition_code):
    """Build a clinically consistent ACCEPT or WARNING claim."""
    claim = _new_claim(condition_code)
    evidence = claim["clinical_conditions"]

    if condition_code == "DROWNING":
        evidence["not_breathing"] = random.random() < 0.35
        evidence["aspiration_risk"] = True
        evidence["hypothermia"] = random.random() < 0.45
        evidence["hypovolemia_or_shock"] = random.random() < 0.20
        evidence["associated_trauma"] = random.random() < 0.10
        evidence["neurological_concern"] = random.random() < 0.10
        for item in [
            "emergency_assessment",
            "airway_clearance",
            "oxygen_support",
            "warming_blanket",
            "referral",
            "avpu_assessment",
            "oxygen",
        ]:
            _add_item(claim, item)
        if evidence["not_breathing"]:
            _add_item(claim, "cpr")
        if evidence["hypovolemia_or_shock"]:
            _add_item(claim, "iv_fluids")
        if evidence["associated_trauma"]:
            _add_item(claim, "surgery")
        if evidence["associated_trauma"] or evidence["neurological_concern"]:
            _add_item(claim, "mri")

    elif condition_code == "SNAKE_BITE":
        evidence["neurotoxicity"] = random.random() < 0.30
        evidence["respiratory_difficulty"] = random.random() < 0.30
        evidence["shock"] = random.random() < 0.12
        evidence["wound_infection"] = random.random() < 0.18
        for item in [
            "emergency_assessment",
            "limb_immobilization",
            "airway_monitoring",
            "wound_cleaning",
            "observation",
            "tetanus_toxoid",
            "paracetamol",
        ]:
            _add_item(claim, item)
        if any(
            evidence[flag]
            for flag in [
                "neurotoxicity",
                "coagulopathy_or_bleeding",
                "shock",
                "acute_kidney_injury",
                "respiratory_difficulty",
            ]
        ):
            _add_item(claim, "anti_snake_venom")
            _add_item(claim, "referral")
        if evidence["respiratory_difficulty"]:
            _add_item(claim, "oxygen_support")
        if evidence["shock"]:
            _add_item(claim, "iv_fluids")
        if evidence["wound_infection"]:
            _add_item(claim, "antibiotics")

    elif condition_code == "FALL_INJURY":
        evidence["fracture_suspected"] = random.random() < 0.45
        evidence["open_wound"] = random.random() < 0.25
        evidence["active_bleeding"] = random.random() < 0.20
        evidence["head_neck_trauma"] = random.random() < 0.22
        evidence["organ_injury_suspected"] = random.random() < 0.12
        evidence["neurological_concern"] = random.random() < 0.12
        evidence["unconscious_or_low_gcs"] = random.random() < 0.08
        for item in ["emergency_assessment", "abcde_assessment", "pain_management"]:
            _add_item(claim, item)
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
        if evidence["open_wound"]:
            _add_item(claim, "wound_cleaning")
            _add_item(claim, "tetanus_toxoid")
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
        ) and random.random() < 0.35:
            _add_item(claim, "icu_stay")
        if (
            evidence["head_neck_trauma"]
            or evidence["neurological_concern"]
            or evidence["organ_injury_suspected"]
        ) and random.random() < 0.40:
            _add_item(claim, "mri")
        if (
            evidence["fracture_suspected"]
            or evidence["open_wound"]
            or evidence["organ_injury_suspected"]
        ) and random.random() < 0.35:
            _add_item(claim, "morphine")
        if any(
            evidence[flag]
            for flag in [
                "unconscious_or_low_gcs",
                "shock",
                "organ_injury_suspected",
                "fracture_suspected",
            ]
        ):
            _add_item(claim, "referral")

    elif condition_code == "HYPERTENSION":
        claim["patient"]["gender"] = random.choice(["male", "female"])
        evidence["new_patient"] = random.random() < 0.60
        evidence["uncontrolled_bp"] = random.random() < 0.45
        for item in ["consultation", "bp_measurement"]:
            _add_item(claim, item)
        _add_item(claim, random.choice(["amlodipine", "losartan", "enalapril"]))
        if evidence["new_patient"] or evidence["uncontrolled_bp"]:
            for item in random.sample(
                ["urea_creatinine", "urine_analysis", "lipid_profile", "blood_glucose"],
                k=random.randint(1, 3),
            ):
                _add_item(claim, item)
        if random.random() < 0.20:
            evidence["chest_pain_or_cardiac_risk"] = True
            _add_item(claim, "ecg")

    elif condition_code == "FEVER":
        claim["patient"]["gender"] = random.choice(["male", "female"])
        evidence["bacterial_infection_suspected"] = random.random() < 0.25
        for item in ["consultation", "paracetamol"]:
            _add_item(claim, item)
        if random.random() < 0.60:
            _add_item(claim, "cbc")
        if random.random() < 0.40:
            _add_item(claim, "oral_fluids")
        if random.random() < 0.20:
            evidence["travel_or_malaria_area"] = True
            _add_item(claim, "malaria_test")
        if random.random() < 0.15:
            evidence["duration_more_than_3_days"] = True
            _add_item(claim, "blood_culture")
        if random.random() < 0.18:
            evidence["respiratory_symptoms"] = True
            _add_item(claim, "chest_xray")
        if evidence["bacterial_infection_suspected"]:
            _add_item(claim, "antibiotics")

    elif condition_code == "DIARRHOEA":
        claim["patient"]["gender"] = random.choice(["male", "female"])
        for item in ["consultation", "ors", "dehydration_assessment", "zinc_sulfate"]:
            _add_item(claim, item)
        if random.random() < 0.50:
            _add_item(claim, "stool_routine")
        if random.random() < 0.35:
            evidence["dehydration_signs"] = True
            _add_item(claim, random.choice(["normal_saline", "ringer_lactate", "iv_fluids"]))
        if random.random() < 0.15:
            evidence["blood_in_stool"] = True
            _add_item(claim, "stool_culture")
        if random.random() < 0.10:
            evidence["amoebiasis_suspected"] = True
            _add_item(claim, "metronidazole")
        if random.random() < 0.12:
            evidence["bacterial_infection_suspected"] = True
            _add_item(claim, "azithromycin")

    elif condition_code == "ANAEMIA":
        claim["patient"]["gender"] = random.choice(["male", "female"])
        for item in ["consultation", "cbc", "haemoglobin_test", "ferrous_sulfate"]:
            _add_item(claim, item)
        if random.random() < 0.55:
            _add_item(claim, "serum_ferritin")
        if random.random() < 0.20:
            evidence["b12_deficiency_suspected"] = True
            _add_item(claim, "vitamin_b12")
        if random.random() < 0.18:
            evidence["severe_iron_deficiency"] = True
            claim["patient"]["care_type"] = "inpatient"
            _add_item(claim, "iron_sucrose")

    elif condition_code == "HIV":
        claim["patient"]["gender"] = random.choice(["male", "female"])
        for item in ["consultation", "counselling", "hiv_rapid_test", "elisa"]:
            _add_item(claim, item)
        if random.random() < 0.55:
            evidence["confirmed_diagnosis"] = True
            _add_item(claim, "tld_regimen")
            _add_item(claim, "cd4_count")
        if random.random() < 0.20:
            evidence["on_art_already"] = True
            _add_item(claim, "viral_load")
        if random.random() < 0.20:
            evidence["opportunistic_infection_risk"] = True
            _add_item(claim, "cotrimoxazole")
        if random.random() < 0.40:
            _add_item(claim, "cbc")

    elif condition_code == "PROSTATE_SURGERY":
        claim["patient"]["gender"] = "male"
        claim["patient"]["care_type"] = "inpatient"
        evidence["urinary_retention"] = random.random() < 0.55
        evidence["biopsy_confirmed"] = random.random() < 0.30
        for item in ["consultation", "psa_test", "ultrasound_kub_prostate", "cbc", "urine_analysis"]:
            _add_item(claim, item)
        if evidence["urinary_retention"] or evidence["biopsy_confirmed"]:
            _add_item(claim, "prostate_surgery")
            _add_item(claim, "anesthesia")
        if evidence["urinary_retention"]:
            _add_item(claim, "catheter")
        _add_item(claim, "ceftriaxone")

    elif condition_code == "TESTICULAR_ULTRASOUND":
        claim["patient"]["gender"] = "male"
        for item in ["consultation", "scrotal_ultrasound_doppler", "urine_analysis"]:
            _add_item(claim, item)
        if random.random() < 0.20:
            evidence["palpable_mass"] = True
            _add_item(claim, "tumor_markers")
        if random.random() < 0.20:
            evidence["infection_or_mass_suspected"] = True
            _add_item(claim, random.choice(["doxycycline", "ceftriaxone"]))

    elif condition_code == "CIRCUMCISION":
        claim["patient"]["gender"] = "male"
        claim["patient"]["care_type"] = "outpatient"
        evidence["phimosis_confirmed"] = random.random() < 0.55
        evidence["recurrent_infection"] = random.random() < 0.20
        evidence["medical_indication"] = random.random() < 0.20
        _add_item(claim, "consultation")
        if (
            evidence["phimosis_confirmed"]
            or evidence["recurrent_infection"]
            or evidence["medical_indication"]
        ):
            _add_item(claim, "circumcision")
            _add_item(claim, "local_anesthesia")
            _add_item(claim, "wound_care")
            _add_item(claim, "lidocaine")
        if evidence["recurrent_infection"]:
            _add_item(claim, random.choice(["amoxicillin", "cloxacillin"]))

    elif condition_code == "ANTENATAL_CARE":
        claim["patient"]["gender"] = "female"
        for item in ["consultation", "iron_folic", "cbc", "blood_group_rh", "urine_routine"]:
            _add_item(claim, item)
        if random.random() < 0.40:
            evidence["first_visit"] = True
            _add_item(claim, "obstetric_ultrasound")
            _add_item(claim, "tetanus_diphtheria_vaccine")
        elif random.random() < 0.25:
            evidence["routine_follow_up"] = True
            _add_item(claim, "tetanus_diphtheria_vaccine")

    elif condition_code == "NORMAL_DELIVERY":
        claim["patient"]["gender"] = "female"
        claim["patient"]["care_type"] = "inpatient"
        evidence["active_labour"] = True
        evidence["full_term"] = random.random() < 0.70
        for item in ["consultation", "delivery_care", "cbc", "blood_group_rh", "urine_examination"]:
            _add_item(claim, item)
        if evidence["full_term"]:
            _add_item(claim, "newborn_care")
        if evidence["active_labour"]:
            _add_item(claim, "oxytocin")
        if random.random() < 0.15:
            evidence["infection_risk"] = True
            _add_item(claim, "antibiotics")

    elif condition_code == "CAESAREAN_SECTION":
        claim["patient"]["gender"] = "female"
        claim["patient"]["care_type"] = "inpatient"
        evidence["fetal_distress"] = random.random() < 0.40
        evidence["failed_labour"] = random.random() < 0.30
        evidence["prior_c_section"] = random.random() < 0.20
        for item in ["consultation", "caesarean_section", "anesthesia", "cbc", "blood_group_crossmatch"]:
            _add_item(claim, item)
        _add_item(claim, random.choice(["cefazolin", "ceftriaxone"]))
        _add_item(claim, "iv_fluids")
        if random.random() < 0.60:
            _add_item(claim, "newborn_care")
        if random.random() < 0.12:
            evidence["maternal_complication_or_shock"] = True
            _add_item(claim, "icu_stay")

    _use_inpatient_when_needed(claim)
    _set_claimed_amount(claim, 0.85, 1.30)
    return claim


def _build_conflicting_claim(condition_code, pattern_name):
    """Build a claim containing one known conflict pattern."""
    claim = _new_claim(condition_code)
    evidence = claim["clinical_conditions"]

    if condition_code == "DROWNING":
        for item in ["emergency_assessment", "cpr", "oxygen", "mri", "surgery", "icu_stay"]:
            _add_item(claim, item)
        claim["patient"]["care_type"] = "outpatient"
        if pattern_name == "normal_delivery":
            _add_item(claim, "normal_delivery")
        elif pattern_name == "antenatal_care":
            _add_item(claim, "antenatal_care")
        elif pattern_name == "high_amount":
            _remove_item(claim, "surgery")
        evidence["aspiration_risk"] = True

    elif condition_code == "SNAKE_BITE":
        for item in ["emergency_assessment", "limb_immobilization", "observation", "anti_snake_venom"]:
            _add_item(claim, item)
        if pattern_name == "tourniquet":
            _add_item(claim, "tourniquet")
        elif pattern_name == "cut_wound":
            _add_item(claim, "cut_wound")
        elif pattern_name == "suction_bite":
            _add_item(claim, "suction_bite")
        elif pattern_name == "home_remedy":
            _add_item(claim, "home_remedy")
        elif pattern_name == "normal_delivery":
            _add_item(claim, "normal_delivery")
        elif pattern_name == "antibiotics_without_infection":
            _add_item(claim, "antibiotics")
        elif pattern_name == "high_amount":
            _remove_item(claim, "anti_snake_venom")
            _add_item(claim, "observation")

    elif condition_code == "FALL_INJURY":
        for item in ["emergency_assessment", "mri", "surgery", "icu_stay", "morphine"]:
            _add_item(claim, item)
        claim["patient"]["care_type"] = "outpatient"
        if pattern_name == "care_type_mismatch":
            _add_item(claim, "referral")
        elif pattern_name == "high_amount":
            _remove_item(claim, "morphine")

    elif condition_code == "HYPERTENSION":
        claim["patient"]["gender"] = random.choice(["male", "female"])
        for item in ["consultation", "bp_measurement", "amlodipine"]:
            _add_item(claim, item)
        if pattern_name == "high_amount":
            _add_item(claim, "lipid_profile")
        else:
            _add_item(claim, random.choice(["surgery", "icu_stay", "mri"]))

    elif condition_code == "FEVER":
        claim["patient"]["gender"] = random.choice(["male", "female"])
        for item in ["consultation", "paracetamol"]:
            _add_item(claim, item)
        if pattern_name == "high_amount":
            _add_item(claim, "cbc")
        else:
            _add_item(claim, random.choice(["surgery", "icu_stay", "mri", "anti_snake_venom"]))

    elif condition_code == "DIARRHOEA":
        claim["patient"]["gender"] = random.choice(["male", "female"])
        for item in ["consultation", "ors", "dehydration_assessment"]:
            _add_item(claim, item)
        if pattern_name == "high_amount":
            _add_item(claim, "stool_routine")
        else:
            _add_item(claim, random.choice(["surgery", "mri", "anti_snake_venom"]))

    elif condition_code == "ANAEMIA":
        claim["patient"]["gender"] = random.choice(["male", "female"])
        for item in ["consultation", "cbc", "haemoglobin_test"]:
            _add_item(claim, item)
        if pattern_name == "high_amount":
            _add_item(claim, "serum_ferritin")
        else:
            _add_item(claim, "blood_transfusion")
            claim["patient"]["care_type"] = "inpatient"

    elif condition_code == "HIV":
        claim["patient"]["gender"] = random.choice(["male", "female"])
        for item in ["consultation", "counselling"]:
            _add_item(claim, item)
        if pattern_name == "high_amount":
            _add_item(claim, "viral_load")
        else:
            _add_item(claim, "tld_regimen")

    elif condition_code == "PROSTATE_SURGERY":
        claim["patient"]["gender"] = "female" if pattern_name == "gender_mismatch" else "male"
        claim["patient"]["care_type"] = "inpatient"
        for item in ["consultation", "psa_test", "ultrasound_kub_prostate", "prostate_surgery"]:
            _add_item(claim, item)
        if pattern_name == "high_amount":
            _add_item(claim, "anesthesia")
        evidence["urinary_retention"] = False
        evidence["biopsy_confirmed"] = False

    elif condition_code == "TESTICULAR_ULTRASOUND":
        claim["patient"]["gender"] = "female" if pattern_name == "gender_mismatch" else "male"
        for item in ["consultation", "scrotal_ultrasound_doppler"]:
            _add_item(claim, item)
        if pattern_name == "high_amount":
            _add_item(claim, "tumor_markers")

    elif condition_code == "CIRCUMCISION":
        claim["patient"]["gender"] = "female" if pattern_name == "gender_mismatch" else "male"
        for item in ["consultation", "circumcision"]:
            _add_item(claim, item)
        if pattern_name == "high_amount":
            _add_item(claim, "local_anesthesia")
        evidence["phimosis_confirmed"] = False
        evidence["recurrent_infection"] = False
        evidence["medical_indication"] = False

    elif condition_code == "ANTENATAL_CARE":
        claim["patient"]["gender"] = "male" if pattern_name == "gender_mismatch" else "female"
        for item in ["consultation", "iron_folic"]:
            _add_item(claim, item)
        if pattern_name == "high_amount":
            _add_item(claim, "obstetric_ultrasound")
        else:
            _add_item(claim, random.choice(["prostate_surgery", "circumcision", "scrotal_ultrasound_doppler"]))

    elif condition_code == "NORMAL_DELIVERY":
        claim["patient"]["gender"] = "male" if pattern_name == "gender_mismatch" else "female"
        claim["patient"]["care_type"] = "inpatient"
        for item in ["consultation", "delivery_care"]:
            _add_item(claim, item)
        if pattern_name == "high_amount":
            _add_item(claim, "newborn_care")
        else:
            _add_item(claim, random.choice(["prostate_surgery", "circumcision", "scrotal_ultrasound_doppler"]))

    elif condition_code == "CAESAREAN_SECTION":
        claim["patient"]["gender"] = "male" if pattern_name == "gender_mismatch" else "female"
        claim["patient"]["care_type"] = "inpatient"
        for item in ["consultation", "caesarean_section", "anesthesia"]:
            _add_item(claim, item)
        if pattern_name == "high_amount":
            _add_item(claim, "icu_stay")
        evidence["fetal_distress"] = False
        evidence["failed_labour"] = False
        evidence["prior_c_section"] = False
        evidence["maternal_complication_or_shock"] = False

    if pattern_name == "high_amount":
        _set_claimed_amount(claim, 2.80, 4.20)
    else:
        _set_claimed_amount(claim, 0.95, 1.35)
    return claim


CONFLICT_PATTERNS = {
    "DROWNING": ["cpr_without_breathing", "mri_without_evidence", "normal_delivery", "antenatal_care", "high_amount"],
    "SNAKE_BITE": ["asv_without_evidence", "tourniquet", "cut_wound", "suction_bite", "home_remedy", "antibiotics_without_infection", "high_amount", "normal_delivery"],
    "FALL_INJURY": ["surgery_without_evidence", "icu_without_evidence", "mri_without_evidence", "care_type_mismatch", "high_amount"],
    "HYPERTENSION": ["forbidden_high_cost", "high_amount"],
    "FEVER": ["forbidden_high_cost", "high_amount"],
    "DIARRHOEA": ["forbidden_high_cost", "high_amount"],
    "ANAEMIA": ["blood_transfusion_without_evidence", "high_amount"],
    "HIV": ["art_without_confirmed_diagnosis", "high_amount"],
    "PROSTATE_SURGERY": ["gender_mismatch", "missing_indication", "high_amount"],
    "TESTICULAR_ULTRASOUND": ["gender_mismatch", "high_amount"],
    "CIRCUMCISION": ["gender_mismatch", "missing_indication", "high_amount"],
    "ANTENATAL_CARE": ["gender_mismatch", "male_procedure", "high_amount"],
    "NORMAL_DELIVERY": ["gender_mismatch", "male_procedure", "high_amount"],
    "CAESAREAN_SECTION": ["gender_mismatch", "missing_indication", "high_amount"],
}


def _materialize_conflict_pattern(condition_code, pattern_name):
    """Map named pattern families into a concrete conflicting claim."""
    mapping = {
        "cpr_without_breathing": "cpr_without_breathing",
        "mri_without_evidence": "mri_without_evidence",
        "normal_delivery": "normal_delivery",
        "antenatal_care": "antenatal_care",
        "asv_without_evidence": "asv_without_evidence",
        "tourniquet": "tourniquet",
        "cut_wound": "cut_wound",
        "suction_bite": "suction_bite",
        "home_remedy": "home_remedy",
        "antibiotics_without_infection": "antibiotics_without_infection",
        "surgery_without_evidence": "surgery_without_evidence",
        "icu_without_evidence": "icu_without_evidence",
        "care_type_mismatch": "care_type_mismatch",
        "forbidden_high_cost": "forbidden_high_cost",
        "blood_transfusion_without_evidence": "blood_transfusion_without_evidence",
        "art_without_confirmed_diagnosis": "art_without_confirmed_diagnosis",
        "gender_mismatch": "gender_mismatch",
        "male_procedure": "male_procedure",
        "missing_indication": "missing_indication",
        "high_amount": "high_amount",
    }
    return _build_conflicting_claim(condition_code, mapping[pattern_name])


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
    checks = result["openimis_checks"]
    all_items = set(claim["services"] + claim["medicines"])
    conflict_label = int(result["decision"] in {"REVIEW_REQUIRED", "REJECT_ENTRY"})

    row = {
        "care_category": result.get("care_category", ""),
        "icd_code": result.get("icd_code", ""),
        "condition_code": claim["condition_code"],
        "gender": result["patient"].get("gender", ""),
        "age_group": result["patient"].get("age_group", ""),
        "care_type": result["patient"].get("care_type", ""),
        "claimed_amount": claim["claimed_amount"],
    }

    for flag in CLINICAL_FLAGS:
        row[flag] = int(bool(claim["clinical_conditions"].get(flag, False)))

    for item in ITEMS:
        row["has_" + item] = int(item in all_items)

    row.update(
        {
            "expected_total": result["expected_total"],
            "amount_ratio": result["amount_ratio"] if result["amount_ratio"] is not None else "",
            "service_count": len(claim["services"]),
            "medicine_count": len(claim["medicines"]),
            "high_cost_count": int(checks["high_cost_count"]),
            "gender_mismatch": int(checks["gender_mismatch"]),
            "age_mismatch": int(checks["age_mismatch"]),
            "care_type_mismatch": int(checks["care_type_mismatch"]),
            "max_amount_violation": int(checks["max_amount_violation"]),
            "unknown_item_count": int(checks["unknown_item_count"]),
            "decision": result["decision"],
            "compliance_score": result["compliance_score"],
            "legitimacy_score": result["legitimacy_score"],
            "conflict_label": conflict_label,
        }
    )
    return row


def generate_dataset():
    """Generate a balanced dataset across all supported conditions."""
    random.seed(RANDOM_SEED)
    rows = []

    for condition_code in ALL_CONDITIONS:
        valid_rows = []
        while len(valid_rows) < NON_CONFLICT_PER_CONDITION:
            row = _claim_to_row(_build_valid_claim(condition_code))
            if row["conflict_label"] == 0:
                valid_rows.append(row)

        conflict_rows = []
        patterns = CONFLICT_PATTERNS[condition_code]
        pattern_index = 0
        while len(conflict_rows) < CONFLICT_PER_CONDITION:
            pattern_name = patterns[pattern_index % len(patterns)]
            row = _claim_to_row(_materialize_conflict_pattern(condition_code, pattern_name))
            pattern_index += 1
            if row["conflict_label"] == 1:
                conflict_rows.append(row)

        rows.extend(valid_rows)
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
    """Generate, save, and summarize the combined synthetic dataset."""
    rows = generate_dataset()
    output_path = save_dataset(rows)

    conflict_distribution = Counter(row["conflict_label"] for row in rows)
    decision_distribution = Counter(row["decision"] for row in rows)
    condition_distribution = Counter(row["condition_code"] for row in rows)
    condition_label_distribution = defaultdict(dict)
    for condition_code in ALL_CONDITIONS:
        label_counts = Counter(
            row["conflict_label"] for row in rows if row["condition_code"] == condition_code
        )
        condition_label_distribution[condition_code] = dict(sorted(label_counts.items()))

    print(f"Dataset shape: ({len(rows)}, {len(rows[0])})")
    print(f"Condition distribution: {dict(sorted(condition_distribution.items()))}")
    print(f"Decision distribution: {dict(sorted(decision_distribution.items()))}")
    print(f"Conflict label distribution: {dict(sorted(conflict_distribution.items()))}")
    print(f"Condition-wise label distribution: {dict(condition_label_distribution)}")
    print(f"Saved CSV: {output_path}")


if __name__ == "__main__":
    main()
