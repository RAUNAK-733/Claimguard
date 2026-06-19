"""Rule engine for ClaimGuard emergency and basic care claim validation."""


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
    """Create one readable openIMIS-style catalog entry."""
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
        "medicine", "both", 100, 100,
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
    "caesarean_section": _catalog_entry(
        "caesarean_section", "Caesarean Section",
        "procedure", "inpatient", 24000, 24000,
        gender_categories="female", age_categories="adult",
        high_cost=True,
    ),
    "cosmetic_surgery": _catalog_entry(
        "cosmetic_surgery", "Cosmetic Surgery",
        "procedure", "inpatient", 25000, 25000,
        age_categories="adult", high_cost=True,
    ),
    "tourniquet": _catalog_entry(
        "tourniquet", "Tourniquet Application",
        "procedure", "outpatient", 0, 0,
    ),
    "cut_wound": _catalog_entry(
        "cut_wound", "Cut Bite Wound",
        "procedure", "outpatient", 0, 0,
    ),
    "suction_bite": _catalog_entry(
        "suction_bite", "Suction Bite Wound",
        "procedure", "outpatient", 0, 0,
    ),
    "home_remedy": _catalog_entry(
        "home_remedy", "Home Remedy",
        "item", "outpatient", 0, 0,
    ),
    "consultation": _catalog_entry(
        "consultation", "Consultation",
        "service", "outpatient", 300, 300,
    ),
    "bp_measurement": _catalog_entry(
        "bp_measurement", "Blood Pressure Measurement",
        "investigation", "outpatient", 100, 100,
    ),
    "ecg": _catalog_entry(
        "ecg", "ECG",
        "investigation", "both", 1200, 1200,
    ),
    "urea_creatinine": _catalog_entry(
        "urea_creatinine", "Urea and Creatinine",
        "investigation", "outpatient", 900, 900,
    ),
    "urine_analysis": _catalog_entry(
        "urine_analysis", "Urine Analysis",
        "investigation", "outpatient", 400, 400,
    ),
    "lipid_profile": _catalog_entry(
        "lipid_profile", "Lipid Profile",
        "investigation", "outpatient", 1200, 1200,
    ),
    "blood_glucose": _catalog_entry(
        "blood_glucose", "Blood Glucose",
        "investigation", "outpatient", 300, 300,
    ),
    "amlodipine": _catalog_entry(
        "amlodipine", "Amlodipine",
        "medicine", "outpatient", 150, 150,
    ),
    "enalapril": _catalog_entry(
        "enalapril", "Enalapril",
        "medicine", "outpatient", 180, 180,
    ),
    "losartan": _catalog_entry(
        "losartan", "Losartan",
        "medicine", "outpatient", 220, 220,
    ),
    "hydrochlorothiazide": _catalog_entry(
        "hydrochlorothiazide", "Hydrochlorothiazide",
        "medicine", "outpatient", 120, 120,
    ),
    "atenolol": _catalog_entry(
        "atenolol", "Atenolol",
        "medicine", "outpatient", 140, 140,
    ),
    "cbc": _catalog_entry(
        "cbc", "Complete Blood Count",
        "investigation", "both", 500, 500,
    ),
    "malaria_test": _catalog_entry(
        "malaria_test", "Malaria Test",
        "investigation", "outpatient", 700, 700,
    ),
    "blood_culture": _catalog_entry(
        "blood_culture", "Blood Culture",
        "investigation", "outpatient", 1800, 1800,
    ),
    "urine_routine": _catalog_entry(
        "urine_routine", "Urine Routine",
        "investigation", "outpatient", 400, 400,
    ),
    "chest_xray": _catalog_entry(
        "chest_xray", "Chest X-Ray",
        "investigation", "outpatient", 1000, 1000,
    ),
    "ibuprofen": _catalog_entry(
        "ibuprofen", "Ibuprofen",
        "medicine", "outpatient", 120, 120,
    ),
    "oral_fluids": _catalog_entry(
        "oral_fluids", "Oral Fluids",
        "item", "outpatient", 100, 100,
    ),
    "normal_saline": _catalog_entry(
        "normal_saline", "Normal Saline",
        "item", "both", 400, 400,
    ),
    "ringer_lactate": _catalog_entry(
        "ringer_lactate", "Ringer Lactate",
        "item", "both", 450, 450,
    ),
    "stool_routine": _catalog_entry(
        "stool_routine", "Stool Routine",
        "investigation", "outpatient", 450, 450,
    ),
    "stool_culture": _catalog_entry(
        "stool_culture", "Stool Culture",
        "investigation", "outpatient", 1500, 1500,
    ),
    "serum_electrolytes": _catalog_entry(
        "serum_electrolytes", "Serum Electrolytes",
        "investigation", "outpatient", 900, 900,
    ),
    "dehydration_assessment": _catalog_entry(
        "dehydration_assessment", "Dehydration Assessment",
        "service", "outpatient", 200, 200,
    ),
    "ors": _catalog_entry(
        "ors", "Oral Rehydration Salts",
        "medicine", "outpatient", 80, 80,
    ),
    "zinc_sulfate": _catalog_entry(
        "zinc_sulfate", "Zinc Sulfate",
        "medicine", "outpatient", 120, 120,
    ),
    "metronidazole": _catalog_entry(
        "metronidazole", "Metronidazole",
        "medicine", "outpatient", 220, 220,
    ),
    "azithromycin": _catalog_entry(
        "azithromycin", "Azithromycin",
        "medicine", "outpatient", 300, 300,
    ),
    "haemoglobin_test": _catalog_entry(
        "haemoglobin_test", "Haemoglobin Test",
        "investigation", "outpatient", 300, 300,
    ),
    "peripheral_smear": _catalog_entry(
        "peripheral_smear", "Peripheral Smear",
        "investigation", "outpatient", 500, 500,
    ),
    "serum_ferritin": _catalog_entry(
        "serum_ferritin", "Serum Ferritin",
        "investigation", "outpatient", 1200, 1200,
    ),
    "b12_folate_level": _catalog_entry(
        "b12_folate_level", "B12 and Folate Level",
        "investigation", "outpatient", 1500, 1500,
    ),
    "stool_examination": _catalog_entry(
        "stool_examination", "Stool Examination",
        "investigation", "outpatient", 400, 400,
    ),
    "ferrous_sulfate": _catalog_entry(
        "ferrous_sulfate", "Ferrous Sulfate",
        "medicine", "outpatient", 180, 180,
    ),
    "folic_acid": _catalog_entry(
        "folic_acid", "Folic Acid",
        "medicine", "outpatient", 120, 120,
    ),
    "vitamin_b12": _catalog_entry(
        "vitamin_b12", "Vitamin B12",
        "medicine", "outpatient", 300, 300,
    ),
    "iron_sucrose": _catalog_entry(
        "iron_sucrose", "Iron Sucrose",
        "medicine", "inpatient", 3500, 3500,
        high_cost=True,
    ),
    "blood_transfusion": _catalog_entry(
        "blood_transfusion", "Blood Transfusion",
        "procedure", "inpatient", 8000, 8000,
        high_cost=True,
    ),
    "hiv_rapid_test": _catalog_entry(
        "hiv_rapid_test", "HIV Rapid Test",
        "investigation", "outpatient", 500, 500,
    ),
    "elisa": _catalog_entry(
        "elisa", "ELISA",
        "investigation", "outpatient", 1200, 1200,
    ),
    "cd4_count": _catalog_entry(
        "cd4_count", "CD4 Count",
        "investigation", "outpatient", 1800, 1800,
    ),
    "viral_load": _catalog_entry(
        "viral_load", "Viral Load",
        "investigation", "outpatient", 4500, 4500,
        high_cost=True,
    ),
    "lft": _catalog_entry(
        "lft", "Liver Function Test",
        "investigation", "outpatient", 900, 900,
    ),
    "rft": _catalog_entry(
        "rft", "Renal Function Test",
        "investigation", "outpatient", 900, 900,
    ),
    "hepatitis_screening": _catalog_entry(
        "hepatitis_screening", "Hepatitis Screening",
        "investigation", "outpatient", 1200, 1200,
    ),
    "tld_regimen": _catalog_entry(
        "tld_regimen", "TLD Regimen",
        "medicine", "outpatient", 1800, 1800,
    ),
    "cotrimoxazole": _catalog_entry(
        "cotrimoxazole", "Cotrimoxazole",
        "medicine", "outpatient", 250, 250,
    ),
    "zidovudine": _catalog_entry(
        "zidovudine", "Zidovudine",
        "medicine", "outpatient", 850, 850,
    ),
    "efavirenz": _catalog_entry(
        "efavirenz", "Efavirenz",
        "medicine", "outpatient", 850, 850,
    ),
    "counselling": _catalog_entry(
        "counselling", "Counselling",
        "service", "outpatient", 200, 200,
    ),
    "psa_test": _catalog_entry(
        "psa_test", "PSA Test",
        "investigation", "outpatient", 1400, 1400,
        gender_categories="male", age_categories="adult",
    ),
    "ultrasound_kub_prostate": _catalog_entry(
        "ultrasound_kub_prostate", "Ultrasound KUB Prostate",
        "investigation", "outpatient", 1800, 1800,
        gender_categories="male", age_categories="adult",
    ),
    "prostate_surgery": _catalog_entry(
        "prostate_surgery", "Prostate Surgery",
        "procedure", "inpatient", 26000, 26000,
        gender_categories="male", age_categories="adult",
        high_cost=True,
    ),
    "anesthesia": _catalog_entry(
        "anesthesia", "Anesthesia",
        "procedure", "inpatient", 4000, 4000,
        high_cost=True,
    ),
    "catheter": _catalog_entry(
        "catheter", "Catheter",
        "procedure", "inpatient", 600, 600,
    ),
    "ceftriaxone": _catalog_entry(
        "ceftriaxone", "Ceftriaxone",
        "medicine", "both", 500, 500,
    ),
    "diclofenac": _catalog_entry(
        "diclofenac", "Diclofenac",
        "medicine", "both", 200, 200,
    ),
    "tramadol": _catalog_entry(
        "tramadol", "Tramadol",
        "medicine", "both", 350, 350,
    ),
    "scrotal_ultrasound_doppler": _catalog_entry(
        "scrotal_ultrasound_doppler", "Scrotal Ultrasound Doppler",
        "investigation", "outpatient", 1800, 1800,
        gender_categories="male", age_categories="adult",
    ),
    "tumor_markers": _catalog_entry(
        "tumor_markers", "Tumor Markers",
        "investigation", "outpatient", 2200, 2200,
        gender_categories="male", age_categories="adult",
    ),
    "doxycycline": _catalog_entry(
        "doxycycline", "Doxycycline",
        "medicine", "outpatient", 250, 250,
    ),
    "circumcision": _catalog_entry(
        "circumcision", "Circumcision",
        "procedure", "day_care", 6000, 6000,
        gender_categories="male", age_categories="adult",
    ),
    "bleeding_clotting_time": _catalog_entry(
        "bleeding_clotting_time", "Bleeding and Clotting Time",
        "investigation", "outpatient", 500, 500,
    ),
    "local_anesthesia": _catalog_entry(
        "local_anesthesia", "Local Anesthesia",
        "procedure", "day_care", 800, 800,
    ),
    "wound_care": _catalog_entry(
        "wound_care", "Wound Care",
        "service", "day_care", 600, 600,
    ),
    "lidocaine": _catalog_entry(
        "lidocaine", "Lidocaine",
        "medicine", "day_care", 200, 200,
    ),
    "amoxicillin": _catalog_entry(
        "amoxicillin", "Amoxicillin",
        "medicine", "outpatient", 180, 180,
    ),
    "cloxacillin": _catalog_entry(
        "cloxacillin", "Cloxacillin",
        "medicine", "outpatient", 200, 200,
    ),
    "blood_group_rh": _catalog_entry(
        "blood_group_rh", "Blood Group and Rh",
        "investigation", "outpatient", 500, 500,
        gender_categories="female", age_categories="adult",
    ),
    "blood_sugar": _catalog_entry(
        "blood_sugar", "Blood Sugar",
        "investigation", "outpatient", 300, 300,
    ),
    "hiv_test": _catalog_entry(
        "hiv_test", "HIV Test",
        "investigation", "outpatient", 500, 500,
    ),
    "hbsag_test": _catalog_entry(
        "hbsag_test", "HBsAg Test",
        "investigation", "outpatient", 600, 600,
    ),
    "vdrl_test": _catalog_entry(
        "vdrl_test", "VDRL Test",
        "investigation", "outpatient", 600, 600,
    ),
    "obstetric_ultrasound": _catalog_entry(
        "obstetric_ultrasound", "Obstetric Ultrasound",
        "investigation", "outpatient", 1800, 1800,
        gender_categories="female", age_categories="adult",
    ),
    "iron_folic": _catalog_entry(
        "iron_folic", "Iron Folic",
        "medicine", "outpatient", 180, 180,
        gender_categories="female", age_categories="adult",
    ),
    "calcium_tablets": _catalog_entry(
        "calcium_tablets", "Calcium Tablets",
        "medicine", "outpatient", 150, 150,
        gender_categories="female", age_categories="adult",
    ),
    "albendazole": _catalog_entry(
        "albendazole", "Albendazole",
        "medicine", "outpatient", 100, 100,
        gender_categories="female", age_categories="adult",
    ),
    "tetanus_diphtheria_vaccine": _catalog_entry(
        "tetanus_diphtheria_vaccine", "Tetanus Diphtheria Vaccine",
        "medicine", "outpatient", 300, 300,
        gender_categories="female", age_categories="adult",
    ),
    "urine_examination": _catalog_entry(
        "urine_examination", "Urine Examination",
        "investigation", "outpatient", 400, 400,
    ),
    "fetal_heart_monitoring": _catalog_entry(
        "fetal_heart_monitoring", "Fetal Heart Monitoring",
        "service", "inpatient", 1000, 1000,
        gender_categories="female", age_categories="adult",
    ),
    "delivery_care": _catalog_entry(
        "delivery_care", "Delivery Care",
        "service", "inpatient", 4000, 4000,
        gender_categories="female", age_categories="adult",
    ),
    "newborn_care": _catalog_entry(
        "newborn_care", "Newborn Care",
        "service", "inpatient", 2000, 2000,
        gender_categories="female", age_categories="adult",
    ),
    "oxytocin": _catalog_entry(
        "oxytocin", "Oxytocin",
        "medicine", "inpatient", 350, 350,
        gender_categories="female", age_categories="adult",
    ),
    "blood_group_crossmatch": _catalog_entry(
        "blood_group_crossmatch", "Blood Group and Crossmatch",
        "investigation", "inpatient", 1000, 1000,
        gender_categories="female", age_categories="adult",
    ),
    "cefazolin": _catalog_entry(
        "cefazolin", "Cefazolin",
        "medicine", "inpatient", 500, 500,
    ),
}


PRICE_CATALOG = {
    code: metadata["price"]
    for code, metadata in SERVICE_CATALOG.items()
}


UNRELATED_SERVICES = {"normal_delivery", "antenatal_care", "cosmetic_surgery"}
OBVIOUS_GENDER_MISMATCH_ITEMS = {
    "antenatal_care",
    "normal_delivery",
    "caesarean_section",
    "prostate_surgery",
    "scrotal_ultrasound_doppler",
    "circumcision",
}

SUGGESTED_ACTIONS = {
    "ACCEPT": "Allow claim submission.",
    "WARNING": "Allow submission with justification.",
    "REVIEW_REQUIRED": "Send to medical reviewer before reimbursement.",
    "REJECT_ENTRY": "Prevent submission until claim data is corrected.",
}

EMERGENCY_CONDITION_RULES = {
    "DROWNING": {
        "icd_code": "T75.1",
        "display_name": "Drowning / nonfatal submersion",
        "care_category": "emergency",
        "stp_pathway_name": "Nepal STP 2078 - Drowning Protocol",
        "expected_items": [
            "emergency_assessment",
            "airway_clearance",
            "oxygen_support",
            "avpu_assessment",
            "warming_blanket",
            "referral",
        ],
        "allowed_items": [
            "oxygen",
            "cpr",
            "iv_fluids",
            "surgery",
            "mri",
        ],
        "conditional_items": {
            "cpr": ["not_breathing"],
            "iv_fluids": ["hypovolemia_or_shock"],
            "surgery": ["associated_trauma"],
            "mri": ["associated_trauma", "neurological_concern"],
        },
        "conditional_expected": {},
        "forbidden_items": [],
        "harmful_items": [],
    },
    "SNAKE_BITE": {
        "icd_code": "T63.0",
        "display_name": "Toxic effect of snake venom",
        "care_category": "emergency",
        "stp_pathway_name": "Nepal STP 2078 - Snake Bite Protocol",
        "expected_items": [
            "emergency_assessment",
            "limb_immobilization",
            "airway_monitoring",
            "wound_cleaning",
            "observation",
        ],
        "allowed_items": [
            "anti_snake_venom",
            "tetanus_toxoid",
            "paracetamol",
            "antibiotics",
            "iv_fluids",
            "oxygen_support",
            "oxygen",
            "referral",
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
        "forbidden_items": ["normal_delivery", "antenatal_care", "caesarean_section"],
        "harmful_items": ["tourniquet", "cut_wound", "suction_bite", "home_remedy"],
    },
    "FALL_INJURY": {
        "icd_code": "W00-W19",
        "display_name": "Fall injury event",
        "care_category": "emergency",
        "stp_pathway_name": "Nepal STP 2078 - Fall Injury Protocol",
        "expected_items": [
            "emergency_assessment",
            "abcde_assessment",
            "pain_management",
        ],
        "allowed_items": [
            "xray",
            "splinting",
            "c_spine_protection",
            "surgery",
            "icu_stay",
            "mri",
            "tetanus_toxoid",
            "antibiotics",
            "morphine",
            "bleeding_control",
            "wound_cleaning",
            "referral",
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
        "forbidden_items": [],
        "harmful_items": [],
    },
}

BASIC_CONDITION_RULES = {
    "HYPERTENSION": {
        "icd_code": "I10",
        "display_name": "Hypertension",
        "care_category": "basic",
        "required_gender": None,
        "stp_pathway_name": "Basic Care - Hypertension Follow-up Pathway",
        "expected_items": ["consultation", "bp_measurement"],
        "allowed_items": [
            "amlodipine",
            "enalapril",
            "losartan",
            "hydrochlorothiazide",
            "atenolol",
        ],
        "conditional_items": {
            "ecg": ["chest_pain_or_cardiac_risk"],
            "urea_creatinine": ["uncontrolled_bp", "new_patient"],
            "urine_analysis": ["uncontrolled_bp", "new_patient"],
            "lipid_profile": ["uncontrolled_bp", "new_patient"],
            "blood_glucose": ["uncontrolled_bp", "new_patient"],
        },
        "forbidden_items": [
            "surgery",
            "icu_stay",
            "mri",
            "anti_snake_venom",
            "normal_delivery",
            "caesarean_section",
        ],
    },
    "FEVER": {
        "icd_code": "R50.9",
        "display_name": "Fever",
        "care_category": "basic",
        "required_gender": None,
        "stp_pathway_name": "Basic Care - Fever Evaluation Pathway",
        "expected_items": ["consultation", "paracetamol"],
        "allowed_items": [
            "cbc",
            "urine_routine",
            "ibuprofen",
            "oral_fluids",
            "normal_saline",
            "ringer_lactate",
        ],
        "conditional_items": {
            "malaria_test": ["travel_or_malaria_area"],
            "blood_culture": ["duration_more_than_3_days"],
            "chest_xray": ["respiratory_symptoms"],
            "antibiotics": ["bacterial_infection_suspected"],
        },
        "forbidden_items": [
            "surgery",
            "icu_stay",
            "mri",
            "anti_snake_venom",
        ],
    },
    "DIARRHOEA": {
        "icd_code": "A09",
        "display_name": "Diarrhoea",
        "care_category": "basic",
        "required_gender": None,
        "stp_pathway_name": "Basic Care - Diarrhoea Management Pathway",
        "expected_items": ["consultation", "ors", "dehydration_assessment"],
        "allowed_items": [
            "stool_routine",
            "serum_electrolytes",
            "cbc",
            "zinc_sulfate",
        ],
        "conditional_items": {
            "iv_fluids": ["dehydration_signs"],
            "normal_saline": ["dehydration_signs"],
            "ringer_lactate": ["dehydration_signs"],
            "stool_culture": ["blood_in_stool", "duration_more_than_3_days"],
            "metronidazole": ["amoebiasis_suspected"],
            "azithromycin": ["bacterial_infection_suspected"],
        },
        "forbidden_items": [
            "surgery",
            "icu_stay",
            "mri",
            "anti_snake_venom",
        ],
    },
    "ANAEMIA": {
        "icd_code": "D50.9",
        "display_name": "Anaemia",
        "care_category": "basic",
        "required_gender": None,
        "stp_pathway_name": "Basic Care - Anaemia Workup Pathway",
        "expected_items": ["consultation", "cbc", "haemoglobin_test"],
        "allowed_items": [
            "peripheral_smear",
            "serum_ferritin",
            "b12_folate_level",
            "stool_examination",
            "ferrous_sulfate",
            "folic_acid",
        ],
        "conditional_items": {
            "blood_transfusion": ["severe_anaemia_or_instability"],
            "vitamin_b12": ["b12_deficiency_suspected"],
            "iron_sucrose": ["severe_iron_deficiency"],
        },
        "forbidden_items": [
            "surgery",
            "icu_stay",
            "mri",
            "anti_snake_venom",
        ],
    },
    "HIV": {
        "icd_code": "B20-B24 / Z21",
        "display_name": "HIV",
        "care_category": "basic",
        "required_gender": None,
        "stp_pathway_name": "Basic Care - HIV Care Pathway",
        "expected_items": ["consultation", "counselling"],
        "allowed_items": [
            "hiv_rapid_test",
            "elisa",
            "cbc",
            "lft",
            "rft",
            "hepatitis_screening",
            "zidovudine",
            "efavirenz",
        ],
        "conditional_items": {
            "tld_regimen": ["confirmed_diagnosis"],
            "cd4_count": ["confirmed_diagnosis"],
            "viral_load": ["on_art_already"],
            "cotrimoxazole": ["opportunistic_infection_risk"],
        },
        "forbidden_items": [
            "surgery",
            "icu_stay",
            "mri",
            "anti_snake_venom",
        ],
    },
    "PROSTATE_SURGERY": {
        "icd_code": "N40",
        "display_name": "Prostate Surgery",
        "care_category": "basic",
        "required_gender": "male",
        "stp_pathway_name": "Basic Care - Prostate Surgery Pathway",
        "expected_items": [
            "consultation",
            "psa_test",
            "ultrasound_kub_prostate",
        ],
        "allowed_items": [
            "cbc",
            "urine_analysis",
            "rft",
            "ecg",
            "anesthesia",
            "ceftriaxone",
            "paracetamol",
            "diclofenac",
            "tramadol",
            "iv_fluids",
        ],
        "conditional_items": {
            "prostate_surgery": ["urinary_retention", "biopsy_confirmed"],
            "catheter": ["urinary_retention"],
        },
        "forbidden_items": [
            "normal_delivery",
            "antenatal_care",
            "caesarean_section",
        ],
    },
    "TESTICULAR_ULTRASOUND": {
        "icd_code": "N50.9",
        "display_name": "Testicular Ultrasound",
        "care_category": "basic",
        "required_gender": "male",
        "stp_pathway_name": "Basic Care - Testicular Ultrasound Pathway",
        "expected_items": ["consultation", "scrotal_ultrasound_doppler"],
        "allowed_items": ["urine_analysis", "cbc", "ibuprofen", "paracetamol"],
        "conditional_items": {
            "tumor_markers": ["palpable_mass"],
            "doxycycline": ["infection_or_mass_suspected"],
            "ceftriaxone": ["infection_or_mass_suspected"],
        },
        "forbidden_items": [
            "normal_delivery",
            "antenatal_care",
            "caesarean_section",
        ],
    },
    "CIRCUMCISION": {
        "icd_code": "N47",
        "display_name": "Circumcision",
        "care_category": "basic",
        "required_gender": "male",
        "stp_pathway_name": "Basic Care - Circumcision Pathway",
        "expected_items": ["consultation"],
        "allowed_items": [
            "cbc",
            "bleeding_clotting_time",
            "blood_glucose",
            "local_anesthesia",
            "wound_care",
            "lidocaine",
            "paracetamol",
            "ibuprofen",
        ],
        "conditional_items": {
            "circumcision": [
                "phimosis_confirmed",
                "recurrent_infection",
                "medical_indication",
            ],
            "amoxicillin": ["recurrent_infection"],
            "cloxacillin": ["recurrent_infection"],
        },
        "forbidden_items": [
            "normal_delivery",
            "antenatal_care",
            "caesarean_section",
        ],
    },
    "ANTENATAL_CARE": {
        "icd_code": "Z34",
        "display_name": "Antenatal Care",
        "care_category": "basic",
        "required_gender": "female",
        "stp_pathway_name": "Basic Care - Antenatal Care Pathway",
        "expected_items": ["consultation", "iron_folic"],
        "allowed_items": [
            "cbc",
            "blood_group_rh",
            "urine_routine",
            "blood_sugar",
            "hiv_test",
            "hbsag_test",
            "vdrl_test",
            "calcium_tablets",
            "albendazole",
            "paracetamol",
        ],
        "conditional_items": {
            "obstetric_ultrasound": ["first_visit", "high_risk_pregnancy"],
            "tetanus_diphtheria_vaccine": [
                "first_visit",
                "routine_follow_up",
            ],
        },
        "forbidden_items": [
            "prostate_surgery",
            "scrotal_ultrasound_doppler",
            "circumcision",
        ],
    },
    "NORMAL_DELIVERY": {
        "icd_code": "O80",
        "display_name": "Normal Delivery",
        "care_category": "basic",
        "required_gender": "female",
        "stp_pathway_name": "Basic Care - Normal Delivery Pathway",
        "expected_items": ["consultation", "delivery_care"],
        "allowed_items": [
            "cbc",
            "blood_group_rh",
            "urine_examination",
            "obstetric_ultrasound",
            "fetal_heart_monitoring",
            "iron_folic",
            "paracetamol",
            "normal_saline",
            "ringer_lactate",
        ],
        "conditional_items": {
            "newborn_care": ["full_term"],
            "oxytocin": ["active_labour"],
            "antibiotics": ["infection_risk"],
        },
        "forbidden_items": [
            "prostate_surgery",
            "scrotal_ultrasound_doppler",
            "circumcision",
        ],
    },
    "CAESAREAN_SECTION": {
        "icd_code": "O82",
        "display_name": "Caesarean Section",
        "care_category": "basic",
        "required_gender": "female",
        "stp_pathway_name": "Basic Care - Caesarean Section Pathway",
        "expected_items": ["consultation", "caesarean_section", "anesthesia"],
        "allowed_items": [
            "cbc",
            "blood_group_crossmatch",
            "rft",
            "lft",
            "blood_sugar",
            "ecg",
            "obstetric_ultrasound",
            "newborn_care",
            "cefazolin",
            "ceftriaxone",
            "oxytocin",
            "paracetamol",
            "diclofenac",
            "tramadol",
            "iv_fluids",
        ],
        "conditional_items": {
            "caesarean_section": [
                "fetal_distress",
                "failed_labour",
                "prior_c_section",
            ],
            "icu_stay": ["maternal_complication_or_shock"],
        },
        "forbidden_items": [
            "prostate_surgery",
            "scrotal_ultrasound_doppler",
            "circumcision",
        ],
    },
}

CONDITION_RULES = {}
CONDITION_RULES.update(EMERGENCY_CONDITION_RULES)
CONDITION_RULES.update(BASIC_CONDITION_RULES)


def _normalize_text(value):
    """Convert free text to lowercase snake_case."""
    if value is None:
        return ""
    words = str(value).strip().lower().split()
    return "_".join(words)


def _normalize_list(values):
    """Normalize a list of claimed services or medicines."""
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
    """Normalize dictionary keys and optionally string values."""
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


def _calculate_expected_total(claimed_items):
    """Sum catalog prices for every recognized claimed item."""
    return sum(PRICE_CATALOG.get(item, 0) for item in claimed_items)


def _calculate_maximum_total(claimed_items):
    """Sum maximum claim amounts for every recognized claimed item."""
    return sum(
        SERVICE_CATALOG.get(item, {}).get("maximum_amount_per_claim", 0)
        for item in claimed_items
    )


def _severity_evidence_is_sufficient(condition_code, clinical_conditions):
    """Check whether a condition contains evidence of serious illness."""
    severity_flags = {
        "DROWNING": [
            "not_breathing",
            "hypovolemia_or_shock",
            "associated_trauma",
            "neurological_concern",
        ],
        "SNAKE_BITE": [
            "neurotoxicity",
            "coagulopathy_or_bleeding",
            "shock",
            "acute_kidney_injury",
            "respiratory_difficulty",
        ],
        "FALL_INJURY": [
            "fracture_suspected",
            "open_wound",
            "head_neck_trauma",
            "unconscious_or_low_gcs",
            "shock",
            "organ_injury_suspected",
            "neurological_concern",
        ],
        "CAESAREAN_SECTION": [
            "fetal_distress",
            "failed_labour",
            "prior_c_section",
            "maternal_complication_or_shock",
        ],
        "PROSTATE_SURGERY": ["urinary_retention", "biopsy_confirmed"],
        "ANAEMIA": ["severe_anaemia_or_instability", "severe_iron_deficiency"],
    }
    return _has_any_evidence(
        clinical_conditions,
        severity_flags.get(condition_code, []),
    )


def _insert_priority_reason(reasons, reason):
    """Keep hard rejection reasons near the top of the list."""
    if reason not in reasons:
        reasons.insert(0, reason)


def _basic_forbidden_is_reject(item):
    """Return True when a forbidden item is a strong entry-blocking mismatch."""
    return item in OBVIOUS_GENDER_MISMATCH_ITEMS


def validate_claim(
    condition_code,
    patient,
    clinical_conditions,
    services,
    medicines,
    claimed_amount,
):
    """Validate one claim and return a decision dictionary."""
    normalized_condition = _normalize_text(condition_code).upper()
    normalized_patient = _normalize_dictionary(
        patient,
        normalize_values=True,
    )
    evidence = _normalize_dictionary(clinical_conditions)
    normalized_services = _normalize_list(services)
    normalized_medicines = _normalize_list(medicines)
    claimed_items = normalized_services + normalized_medicines
    all_claimed_items = set(claimed_items)
    rule = CONDITION_RULES.get(normalized_condition)

    if not normalized_patient.get("care_type"):
        normalized_patient["care_type"] = "outpatient"
    if rule is not None and not normalized_patient.get("care_category"):
        normalized_patient["care_category"] = rule["care_category"]

    expected_total = _calculate_expected_total(claimed_items)
    maximum_total = _calculate_maximum_total(claimed_items)
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
    unsupported_claimed_items = []

    if rule is None:
        compliance_score = 0
        reject_entry = True
        rule_hits.append("INVALID_CONDITION_CODE")
        reasons.append("The condition code is not supported by this rule engine.")
    else:
        care_category = rule["care_category"]
        if care_category == "emergency":
            for expected_item in rule["expected_items"]:
                if expected_item in all_claimed_items:
                    continue
                if expected_item == "emergency_assessment":
                    compliance_score -= 20
                    rule_hits.append("MISSING_EMERGENCY_ASSESSMENT")
                    reasons.append(
                        "Emergency assessment is missing from the claimed services."
                    )
                else:
                    compliance_score -= 10
                    rule_hits.append("MISSING_CORE_SERVICE_" + expected_item.upper())
                    reasons.append(
                        f"Expected core service '{expected_item}' is missing."
                    )

            for expected_item, flags in rule["conditional_expected"].items():
                if not _has_any_evidence(evidence, flags):
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

            for item, flags in rule["conditional_items"].items():
                if item not in all_claimed_items:
                    continue
                if _has_any_evidence(evidence, flags):
                    continue
                compliance_score -= 30
                force_review = True
                if PRICE_CATALOG.get(item, 0) >= 10000:
                    rule_hits.append("HIGH_COST_WITHOUT_EVIDENCE_" + item.upper())
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

            for item in normalized_services:
                if item in rule["harmful_items"]:
                    compliance_score -= 60
                    reject_entry = True
                    rule_hits.append("HARMFUL_SERVICE_" + item.upper())
                    _insert_priority_reason(
                        reasons,
                        f"Service '{item}' is contraindicated or harmful for this condition.",
                    )

                if item in UNRELATED_SERVICES or item in rule["forbidden_items"]:
                    compliance_score -= 80
                    reject_entry = True
                    rule_hits.append("UNRELATED_SERVICE_" + item.upper())
                    _insert_priority_reason(
                        reasons,
                        f"Service '{item}' is unrelated to the selected emergency condition.",
                    )

        else:
            required_gender = rule.get("required_gender")
            patient_gender = normalized_patient.get("gender", "")
            if required_gender and patient_gender != required_gender:
                compliance_score -= 80
                reject_entry = True
                gender_mismatch = True
                rule_hits.append(
                    "DIAGNOSIS_GENDER_MISMATCH_" + normalized_condition
                )
                _insert_priority_reason(
                    reasons,
                    f"Diagnosis {normalized_condition} is not applicable for patient gender {patient_gender or 'unspecified'}.",
                )

            for expected_item in rule["expected_items"]:
                if expected_item in all_claimed_items:
                    continue
                compliance_score -= 10
                rule_hits.append("MISSING_BASIC_EXPECTED_" + expected_item.upper())
                reasons.append(
                    f"Expected basic care item '{expected_item}' is missing."
                )

            allowed_pool = set(rule["expected_items"]) | set(rule["allowed_items"])
            allowed_pool.update(rule["conditional_items"].keys())
            allowed_pool.update(rule["forbidden_items"])

            for item, flags in rule["conditional_items"].items():
                if item not in all_claimed_items:
                    continue
                if _has_any_evidence(evidence, flags):
                    continue
                compliance_score -= 25
                force_review = True
                rule_hits.append("CONDITIONAL_ITEM_WITHOUT_EVIDENCE_" + item.upper())
                reasons.append(f"Item '{item}' requires supporting clinical evidence.")

            for item in sorted(all_claimed_items):
                if item in rule["forbidden_items"]:
                    if _basic_forbidden_is_reject(item):
                        compliance_score -= 80
                        reject_entry = True
                        rule_hits.append("FORBIDDEN_ITEM_REJECT_" + item.upper())
                        _insert_priority_reason(
                            reasons,
                            f"Item '{item}' is incompatible with the selected basic care diagnosis.",
                        )
                    elif SERVICE_CATALOG.get(item, {}).get("high_cost", False):
                        compliance_score -= 50
                        force_review = True
                        rule_hits.append("FORBIDDEN_HIGH_COST_" + item.upper())
                        reasons.append(
                            f"High-cost item '{item}' is not appropriate for the selected basic care diagnosis."
                        )
                    else:
                        compliance_score -= 40
                        force_review = True
                        rule_hits.append("FORBIDDEN_ITEM_" + item.upper())
                        reasons.append(
                            f"Item '{item}' is not appropriate for the selected basic care diagnosis."
                        )
                    continue

                if item in allowed_pool:
                    continue

                if item not in SERVICE_CATALOG:
                    continue

                unsupported_claimed_items.append(item)
                compliance_score -= 20
                force_review = True
                rule_hits.append("UNEXPECTED_BASIC_ITEM_" + item.upper())
                reasons.append(
                    f"Item '{item}' is not expected for the selected basic care diagnosis."
                )

    unknown_items = []
    for item in claimed_items:
        if item in SERVICE_CATALOG:
            continue
        unknown_items.append(item)
        compliance_score -= 5
        force_review = True
        rule_hits.append("UNKNOWN_ITEM_" + item.upper())
        reasons.append(
            f"Item '{item}' is not found in the demo service/medicine catalog."
        )

    patient_gender = normalized_patient.get("gender", "")
    patient_age_group = normalized_patient.get("age_group", "")
    patient_care_type = normalized_patient.get("care_type", "outpatient")

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
            _insert_priority_reason(
                reasons,
                f"Item '{item}' is limited to {allowed_gender} patients, but the claim patient is {patient_gender or 'unspecified'}.",
            )

        allowed_age = metadata["age_categories"]
        if allowed_age != "both" and patient_age_group != allowed_age:
            age_mismatch = True
            compliance_score -= 30
            rule_hits.append("AGE_MISMATCH_" + item.upper())
            reasons.append(
                f"Item '{item}' is limited to {allowed_age} patients, but the claim patient is {patient_age_group or 'unspecified'}."
            )

        if metadata["care_type"] == "inpatient" and patient_care_type == "outpatient":
            care_type_mismatch = True
            force_review = True
            compliance_score -= 30
            rule_hits.append("CARE_TYPE_MISMATCH_" + item.upper())
            reasons.append(
                f"Inpatient-only item '{item}' is claimed in outpatient care."
            )

    if maximum_total > 0 and numeric_claimed_amount > maximum_total * 1.5:
        max_amount_violation = True
        force_review = True
        compliance_score -= 30
        rule_hits.append("MAX_AMOUNT_VIOLATION")
        reasons.append(
            "The claimed amount exceeds 150% of the combined maximum amount allowed for the claimed services and items."
        )

    high_cost_count = sum(
        1
        for item in all_claimed_items
        if SERVICE_CATALOG.get(item, {}).get("high_cost", False)
    )
    if (
        high_cost_count >= 2
        and not _severity_evidence_is_sufficient(normalized_condition, evidence)
    ):
        compliance_score -= 20
        force_review = True
        rule_hits.append("MULTIPLE_HIGH_COST_ITEMS_WEAK_EVIDENCE")
        reasons.append(
            "Multiple high-cost items are claimed without sufficient severity evidence."
        )

    if amount_ratio is not None and amount_ratio > 1.5:
        compliance_score -= 15
        force_review = True
        rule_hits.append("AMOUNT_OVER_150_PERCENT")
        reasons.append("The claimed amount is more than 150% of the catalog total.")

    if amount_ratio is not None and amount_ratio > 3.0:
        compliance_score -= 30
        force_review = True
        rule_hits.append("AMOUNT_OVER_300_PERCENT")
        reasons.append("The claimed amount is more than 300% of the catalog total.")

    compliance_score = max(0, min(100, compliance_score))

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
        if rule and rule["care_category"] == "emergency":
            reasons.append(
                "Claim follows the expected emergency care pathway for the selected condition."
            )
        else:
            reasons.append(
                "Claim follows the expected basic care pathway for the selected condition."
            )

    recommended_services = []
    if rule is not None:
        recommended_services.extend(rule["expected_items"])
        recommended_services.extend(rule.get("conditional_expected", {}).keys())
    recommended_services = sorted(set(recommended_services))

    return {
        "condition_code": normalized_condition,
        "patient": normalized_patient,
        "care_category": rule["care_category"] if rule else "",
        "icd_code": rule["icd_code"] if rule else "",
        "display_name": rule["display_name"] if rule else "",
        "stp_pathway_name": rule["stp_pathway_name"] if rule else "",
        "recommended_services": recommended_services,
        "unsupported_claimed_items": sorted(set(unsupported_claimed_items)),
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
            "expected": {"ACCEPT", "WARNING"},
            "condition_code": "DROWNING",
            "patient": {"gender": "male", "age_group": "adult", "care_type": "outpatient"},
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
            "expected": {"REVIEW_REQUIRED"},
            "condition_code": "SNAKE_BITE",
            "patient": {"gender": "male", "age_group": "adult", "care_type": "outpatient"},
            "clinical_conditions": {},
            "services": ["emergency_assessment", "limb_immobilization", "observation"],
            "medicines": ["anti_snake_venom"],
            "claimed_amount": 18000,
        },
        {
            "name": "Test 3: Fall injury without supporting evidence",
            "expected": {"REVIEW_REQUIRED"},
            "condition_code": "FALL_INJURY",
            "patient": {"gender": "female", "age_group": "adult", "care_type": "outpatient"},
            "clinical_conditions": {},
            "services": ["emergency_assessment", "mri", "surgery", "icu_stay"],
            "medicines": ["morphine"],
            "claimed_amount": 45000,
        },
        {
            "name": "Test 4: Snake bite with unrelated service",
            "expected": {"REJECT_ENTRY"},
            "condition_code": "SNAKE_BITE",
            "patient": {"gender": "female", "age_group": "adult", "care_type": "outpatient"},
            "clinical_conditions": {},
            "services": ["normal_delivery"],
            "medicines": [],
            "claimed_amount": 7000,
        },
        {
            "name": "Test 5: Male patient with normal delivery",
            "expected": {"REJECT_ENTRY"},
            "condition_code": "NORMAL_DELIVERY",
            "patient": {"gender": "male", "age_group": "adult", "care_type": "inpatient", "care_category": "basic"},
            "clinical_conditions": {"active_labour": True, "full_term": True},
            "services": ["consultation", "delivery_care", "newborn_care"],
            "medicines": ["oxytocin"],
            "claimed_amount": 9000,
        },
        {
            "name": "Test 6: Female patient with prostate surgery",
            "expected": {"REJECT_ENTRY"},
            "condition_code": "PROSTATE_SURGERY",
            "patient": {"gender": "female", "age_group": "adult", "care_type": "inpatient", "care_category": "basic"},
            "clinical_conditions": {"urinary_retention": True},
            "services": ["consultation", "psa_test", "ultrasound_kub_prostate", "prostate_surgery", "catheter"],
            "medicines": ["ceftriaxone", "paracetamol"],
            "claimed_amount": 32000,
        },
        {
            "name": "Test 7: Valid hypertension",
            "expected": {"ACCEPT", "WARNING"},
            "condition_code": "HYPERTENSION",
            "patient": {"gender": "female", "age_group": "adult", "care_type": "outpatient", "care_category": "basic"},
            "clinical_conditions": {"uncontrolled_bp": True, "new_patient": True},
            "services": ["consultation", "bp_measurement", "urea_creatinine", "lipid_profile"],
            "medicines": ["amlodipine"],
            "claimed_amount": 2650,
        },
        {
            "name": "Test 8: Caesarean section without indication",
            "expected": {"REVIEW_REQUIRED"},
            "condition_code": "CAESAREAN_SECTION",
            "patient": {"gender": "female", "age_group": "adult", "care_type": "inpatient", "care_category": "basic"},
            "clinical_conditions": {
                "fetal_distress": False,
                "failed_labour": False,
                "prior_c_section": False,
                "maternal_complication_or_shock": False,
            },
            "services": ["consultation", "caesarean_section", "anesthesia"],
            "medicines": ["cefazolin", "paracetamol"],
            "claimed_amount": 29000,
        },
    ]

    passed = 0
    for test_case in test_cases:
        name = test_case.pop("name")
        expected = test_case.pop("expected")
        result = validate_claim(**test_case)
        decision = result["decision"]
        status = "PASS" if decision in expected else "FAIL"
        if status == "PASS":
            passed += 1
        print(f"\n{name}")
        print("-" * 60)
        print(f"Decision: {decision} | Expected: {sorted(expected)} | {status}")
        print(result)

    print("\nSummary")
    print("-" * 60)
    print(f"Passed {passed} of {len(test_cases)} rule-engine checks.")
