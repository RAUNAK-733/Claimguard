import React, { useEffect, useRef, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:5000";

const PAGE_KEYS = {
  home: "home",
  claimEntry: "claimEntry",
  claimReview: "claimReview",
  flaggedClaims: "flaggedClaims",
  about: "about",
};

const CARE_CATEGORY_OPTIONS = [
  { key: "emergency", label: "Emergency Care" },
  { key: "basic", label: "Basic Care" },
];

const DIAGNOSES = [
  {
    icd: "T75.1",
    condition: "DROWNING",
    careCategory: "emergency",
    label: "T75.1 - Drowning / nonfatal submersion",
    pathway: "Nepal STP 2078 - Drowning Emergency Protocol",
    genderScope: "all",
    evidenceFlags: [
      "not_breathing",
      "aspiration_risk",
      "hypovolemia_or_shock",
      "hypothermia",
      "associated_trauma",
      "neurological_concern",
    ],
    recommended: {
      expected: [
        "emergency_assessment",
        "airway_clearance",
        "oxygen_support",
        "avpu_assessment",
        "warming_blanket",
        "referral",
      ],
      common: [],
      conditional: [
        "cpr only if not_breathing",
        "iv_fluids only if hypovolemia_or_shock",
        "mri only if trauma/neuro concern",
        "surgery only if trauma evidence",
      ],
    },
  },
  {
    icd: "T63.0",
    condition: "SNAKE_BITE",
    careCategory: "emergency",
    label: "T63.0 - Toxic effect of snake venom",
    pathway: "Nepal STP 2078 - Snake Bite Emergency Protocol",
    genderScope: "all",
    evidenceFlags: [
      "neurotoxicity",
      "coagulopathy_or_bleeding",
      "shock",
      "acute_kidney_injury",
      "respiratory_difficulty",
      "wound_infection",
    ],
    recommended: {
      expected: [
        "emergency_assessment",
        "limb_immobilization",
        "airway_monitoring",
        "wound_cleaning",
        "observation",
        "tetanus_toxoid",
        "paracetamol",
      ],
      common: [],
      conditional: [
        "anti_snake_venom only with envenomation evidence",
        "antibiotics only with wound infection",
        "oxygen_support only with respiratory difficulty",
        "iv_fluids only with shock",
      ],
    },
  },
  {
    icd: "W00-W19",
    condition: "FALL_INJURY",
    careCategory: "emergency",
    label: "W00-W19 - Fall injury event",
    pathway: "Nepal STP 2078 - Fall Injury Emergency Protocol",
    genderScope: "all",
    evidenceFlags: [
      "fracture_suspected",
      "open_wound",
      "active_bleeding",
      "head_neck_trauma",
      "unconscious_or_low_gcs",
      "shock",
      "organ_injury_suspected",
      "neurological_concern",
    ],
    recommended: {
      expected: [
        "emergency_assessment",
        "abcde_assessment",
        "pain_management",
      ],
      common: [],
      conditional: [
        "xray if fracture/head-neck/organ injury suspected",
        "splinting if fracture suspected",
        "c_spine_protection if head/neck trauma",
        "bleeding_control if active bleeding",
        "wound_cleaning/tetanus if open wound",
        "surgery/icu/mri only with severity evidence",
      ],
    },
  },
  {
    icd: "I10",
    condition: "HYPERTENSION",
    careCategory: "basic",
    label: "I10 - Hypertension",
    pathway: "Nepal STP 2078 - Hypertension Basic Care Pathway",
    genderScope: "all",
    evidenceFlags: [
      "chest_pain_or_cardiac_risk",
      "uncontrolled_bp",
      "new_patient",
    ],
    recommended: {
      expected: ["consultation", "bp_measurement"],
      common: [
        "ecg",
        "blood_glucose",
        "lipid_profile",
        "amlodipine",
        "enalapril",
        "losartan",
      ],
      conditional: [],
    },
  },
  {
    icd: "R50.9",
    condition: "FEVER",
    careCategory: "basic",
    label: "R50.9 - Fever (Unspecified)",
    pathway: "Nepal STP 2078 - Fever Basic Care Pathway",
    genderScope: "all",
    evidenceFlags: [
      "temp_over_38",
      "duration_more_than_3_days",
      "travel_or_malaria_area",
      "outbreak_or_low_platelet",
      "respiratory_symptoms",
      "bacterial_infection_suspected",
    ],
    recommended: {
      expected: ["consultation", "paracetamol"],
      common: ["cbc", "malaria_test", "blood_culture", "antibiotics if bacterial infection suspected"],
      conditional: [],
    },
  },
  {
    icd: "A09",
    condition: "DIARRHOEA",
    careCategory: "basic",
    label: "A09 - Diarrhoea",
    pathway: "Nepal STP 2078 - Diarrhoea Basic Care Pathway",
    genderScope: "all",
    evidenceFlags: [
      "watery_stool",
      "blood_in_stool",
      "dehydration_signs",
      "duration_more_than_3_days",
      "amoebiasis_suspected",
      "bacterial_infection_suspected",
    ],
    recommended: {
      expected: ["consultation", "ors", "dehydration_assessment"],
      common: [
        "zinc_sulfate",
        "stool_routine",
        "stool_culture",
        "normal_saline if dehydration",
      ],
      conditional: [],
    },
  },
  {
    icd: "D50.9",
    condition: "ANAEMIA",
    careCategory: "basic",
    label: "D50.9 - Anaemia",
    pathway: "Nepal STP 2078 - Anaemia Basic Care Pathway",
    genderScope: "all",
    evidenceFlags: [
      "pallor_confirmed",
      "hb_under_10_confirmed",
      "fatigue_or_weakness",
      "severe_anaemia_or_instability",
      "b12_deficiency_suspected",
      "severe_iron_deficiency",
    ],
    recommended: {
      expected: ["consultation", "cbc", "haemoglobin_test"],
      common: [
        "ferrous_sulfate",
        "folic_acid",
        "vitamin_b12",
        "blood_transfusion only if severe evidence",
      ],
      conditional: [],
    },
  },
  {
    icd: "B20",
    condition: "HIV",
    careCategory: "basic",
    label: "B20 - HIV/AIDS",
    pathway: "Nepal STP 2078 - HIV/AIDS Basic Care Pathway",
    genderScope: "all",
    evidenceFlags: [
      "confirmed_diagnosis",
      "on_art_already",
      "cd4_test_done",
      "opportunistic_infection_risk",
    ],
    recommended: {
      expected: ["consultation", "counselling"],
      common: [
        "hiv_rapid_test",
        "elisa",
        "cd4_count",
        "viral_load",
        "tld_regimen if confirmed",
      ],
      conditional: [],
    },
  },
  {
    icd: "N40",
    condition: "PROSTATE_SURGERY",
    careCategory: "basic",
    label: "N40 - Prostate Surgery",
    pathway: "Nepal STP 2078 - Prostate Surgery Male Care Pathway",
    genderScope: "male",
    evidenceFlags: ["psa_elevated", "urinary_retention", "biopsy_confirmed"],
    recommended: {
      expected: ["consultation", "psa_test", "ultrasound_kub_prostate"],
      common: [],
      conditional: ["surgery if urinary_retention or biopsy_confirmed"],
    },
  },
  {
    icd: "N50.9",
    condition: "TESTICULAR_ULTRASOUND",
    careCategory: "basic",
    label: "N50.9 - Testicular Ultrasound",
    pathway: "Nepal STP 2078 - Testicular Ultrasound Male Care Pathway",
    genderScope: "male",
    evidenceFlags: [
      "scrotal_pain",
      "palpable_mass",
      "trauma_history",
      "infection_or_mass_suspected",
    ],
    recommended: {
      expected: ["consultation", "scrotal_ultrasound_doppler"],
      common: ["tumor_markers if palpable_mass", "doxycycline/ceftriaxone if infection_or_mass_suspected"],
      conditional: [],
    },
  },
  {
    icd: "N47",
    condition: "CIRCUMCISION",
    careCategory: "basic",
    label: "N47 - Circumcision",
    pathway: "Nepal STP 2078 - Circumcision Male Care Pathway",
    genderScope: "male",
    evidenceFlags: [
      "medical_indication",
      "phimosis_confirmed",
      "recurrent_infection",
    ],
    recommended: {
      expected: ["consultation"],
      common: [],
      conditional: ["circumcision if phimosis_confirmed or recurrent_infection or medical_indication"],
    },
  },
  {
    icd: "Z34",
    condition: "ANTENATAL_CARE",
    careCategory: "basic",
    label: "Z34 - Antenatal Care",
    pathway: "Nepal STP 2078 - Antenatal Care Female Care Pathway",
    genderScope: "female",
    evidenceFlags: ["first_visit", "high_risk_pregnancy", "routine_follow_up"],
    recommended: {
      expected: ["consultation", "iron_folic"],
      common: ["cbc", "blood_group_rh", "urine_routine", "obstetric_ultrasound"],
      conditional: [],
    },
  },
  {
    icd: "O80",
    condition: "NORMAL_DELIVERY",
    careCategory: "basic",
    label: "O80 - Normal Delivery",
    pathway: "Nepal STP 2078 - Normal Delivery Female Care Pathway",
    genderScope: "female",
    evidenceFlags: [
      "full_term",
      "no_complications",
      "spontaneous_labour",
      "active_labour",
      "infection_risk",
    ],
    recommended: {
      expected: ["consultation", "delivery_care"],
      common: [],
      conditional: ["newborn_care if full_term", "oxytocin if active_labour"],
    },
  },
  {
    icd: "O82",
    condition: "CAESAREAN_SECTION",
    careCategory: "basic",
    label: "O82 - Caesarean Section",
    pathway: "Nepal STP 2078 - Caesarean Section Female Care Pathway",
    genderScope: "female",
    evidenceFlags: [
      "fetal_distress",
      "failed_labour",
      "prior_c_section",
      "maternal_complication_or_shock",
    ],
    recommended: {
      expected: ["consultation", "surgery", "anesthesia"],
      common: [],
      conditional: [
        "surgery needs fetal_distress / failed_labour / prior_c_section",
        "icu_stay needs maternal complication or shock",
      ],
    },
  },
];

const BASIC_COMMON_DIAGNOSIS_CODES = ["I10", "R50.9", "A09", "D50.9", "B20"];
const BASIC_MALE_DIAGNOSIS_CODES = ["N40", "N50.9", "N47"];
const BASIC_FEMALE_DIAGNOSIS_CODES = ["Z34", "O80", "O82"];

const GROUPS = {
  emergencyServices: [
    {
      title: "Emergency Services",
      items: [
        { code: "emergency_assessment", label: "emergency_assessment" },
        { code: "airway_clearance", label: "airway_clearance" },
        { code: "oxygen_support", label: "oxygen_support" },
        { code: "cpr", label: "cpr" },
        { code: "iv_fluids", label: "iv_fluids" },
        { code: "referral", label: "referral" },
        { code: "avpu_assessment", label: "avpu_assessment" },
        { code: "limb_immobilization", label: "limb_immobilization" },
        { code: "airway_monitoring", label: "airway_monitoring" },
        { code: "wound_cleaning", label: "wound_cleaning" },
        { code: "observation", label: "observation" },
        { code: "abcde_assessment", label: "abcde_assessment" },
        { code: "pain_management", label: "pain_management" },
        { code: "xray", label: "xray" },
        { code: "splinting", label: "splinting" },
        { code: "c_spine_protection", label: "c_spine_protection" },
        { code: "bleeding_control", label: "bleeding_control" },
        { code: "warming_blanket", label: "warming_blanket" },
      ],
    },
    {
      title: "Emergency Medicines / Items",
      items: [
        { code: "oxygen", label: "oxygen" },
        { code: "anti_snake_venom", label: "anti_snake_venom" },
        { code: "tetanus_toxoid", label: "tetanus_toxoid" },
        { code: "paracetamol", label: "paracetamol" },
        { code: "antibiotics", label: "antibiotics" },
        { code: "morphine", label: "morphine" },
      ],
    },
    // {
    //   title: "High-cost / Invalid Demo",
    //   items: [
    //     { code: "surgery", label: "surgery" },
    //     { code: "icu_stay", label: "icu_stay" },
    //     { code: "mri", label: "mri" },
    //     { code: "normal_delivery", label: "normal_delivery" },
    //     { code: "antenatal_care", label: "antenatal_care" },
    //     { code: "cosmetic_surgery", label: "cosmetic_surgery" },
    //     { code: "tourniquet", label: "tourniquet" },
    //     { code: "cut_wound", label: "cut_wound" },
    //     { code: "suction_bite", label: "suction_bite" },
    //     { code: "home_remedy", label: "home_remedy" },
    //   ],
    // },
  ],
  basicCare: [
    {
      title: "Basic Investigations",
      items: [
        { code: "consultation", label: "consultation" },
        { code: "bp_measurement", label: "bp_measurement" },
        { code: "blood_test", label: "blood_test" },
        { code: "cbc", label: "cbc" },
        { code: "ecg", label: "ecg" },
        { code: "urea_creatinine", label: "urea_creatinine" },
        { code: "urine_analysis", label: "urine_analysis" },
        { code: "lipid_profile", label: "lipid_profile" },
        { code: "blood_glucose", label: "blood_glucose" },
        { code: "malaria_test", label: "malaria_test" },
        { code: "blood_culture", label: "blood_culture" },
        { code: "urine_routine", label: "urine_routine" },
        { code: "chest_xray", label: "chest_xray" },
        { code: "stool_routine", label: "stool_routine" },
        { code: "stool_culture", label: "stool_culture" },
        { code: "serum_electrolytes", label: "serum_electrolytes" },
        { code: "haemoglobin_test", label: "haemoglobin_test" },
        { code: "peripheral_smear", label: "peripheral_smear" },
        { code: "serum_ferritin", label: "serum_ferritin" },
        { code: "b12_folate_level", label: "b12_folate_level" },
        { code: "stool_examination", label: "stool_examination" },
        { code: "hiv_rapid_test", label: "hiv_rapid_test" },
        { code: "elisa", label: "elisa" },
        { code: "cd4_count", label: "cd4_count" },
        { code: "viral_load", label: "viral_load" },
        { code: "lft", label: "lft" },
        { code: "rft", label: "rft" },
        { code: "hepatitis_screening", label: "hepatitis_screening" },
        { code: "psa_test", label: "psa_test" },
        { code: "ultrasound_kub_prostate", label: "ultrasound_kub_prostate" },
        { code: "scrotal_ultrasound_doppler", label: "testicular_ultrasound" },
        { code: "tumor_markers", label: "tumor_markers" },
        { code: "bleeding_clotting_time", label: "bleeding_clotting_time" },
        { code: "blood_group_rh", label: "blood_group_rh" },
        { code: "obstetric_ultrasound", label: "obstetric_ultrasound" },
        { code: "fetal_heart_monitoring", label: "fetal_heart_monitoring" },
        { code: "blood_group_crossmatch", label: "blood_group_crossmatch" },
      ],
    },
    {
      title: "Basic Medicines",
      items: [
        { code: "amlodipine", label: "amlodipine" },
        { code: "enalapril", label: "enalapril" },
        { code: "losartan", label: "losartan" },
        { code: "hydrochlorothiazide", label: "hydrochlorothiazide" },
        { code: "atenolol", label: "atenolol" },
        { code: "paracetamol", label: "paracetamol" },
        { code: "ibuprofen", label: "ibuprofen" },
        { code: "oral_fluids", label: "oral_fluids" },
        { code: "normal_saline", label: "normal_saline" },
        { code: "ringer_lactate", label: "ringer_lactate" },
        { code: "antibiotics", label: "antibiotics" },
        { code: "ors", label: "ors" },
        { code: "zinc_sulfate", label: "zinc_sulfate" },
        { code: "metronidazole", label: "metronidazole" },
        { code: "azithromycin", label: "azithromycin" },
        { code: "ferrous_sulfate", label: "ferrous_sulfate" },
        { code: "folic_acid", label: "folic_acid" },
        { code: "vitamin_b12", label: "vitamin_b12" },
        { code: "iron_sucrose", label: "iron_sucrose" },
        { code: "tld_regimen", label: "tld_regimen" },
        { code: "cotrimoxazole", label: "cotrimoxazole" },
        { code: "zidovudine", label: "zidovudine" },
        { code: "efavirenz", label: "efavirenz" },
        { code: "ceftriaxone", label: "ceftriaxone" },
        { code: "diclofenac", label: "diclofenac" },
        { code: "tramadol", label: "tramadol" },
        { code: "doxycycline", label: "doxycycline" },
        { code: "lidocaine", label: "lidocaine" },
        { code: "amoxicillin", label: "amoxicillin" },
        { code: "cloxacillin", label: "cloxacillin" },
        { code: "iron_folic", label: "iron_folic" },
        { code: "calcium_tablets", label: "calcium_tablets" },
        { code: "albendazole", label: "albendazole" },
        { code: "tetanus_diphtheria_vaccine", label: "tetanus_diphtheria_vaccine" },
        { code: "oxytocin", label: "oxytocin" },
        { code: "cefazolin", label: "cefazolin" },
      ],
    },
    {
      title: "Basic Procedures",
      items: [
        { code: "prostate_surgery", label: "prostate_surgery" },
        { code: "scrotal_ultrasound_doppler", label: "testicular_ultrasound" },
        { code: "circumcision", label: "circumcision" },
        { code: "caesarean_section", label: "caesarean_section" },
        { code: "delivery_care", label: "delivery_care" },
        { code: "newborn_care", label: "newborn_care" },
        { code: "surgery", label: "surgery" },
        { code: "anesthesia", label: "anesthesia" },
        { code: "catheter", label: "catheter" },
        { code: "wound_care", label: "wound_care" },
        { code: "local_anesthesia", label: "local_anesthesia" },
        { code: "blood_transfusion", label: "blood_transfusion" },
        { code: "iv_fluids", label: "iv_fluids" },
      ],
    },
  ],
};

const DEMO_SCENARIOS = [
  {
    label: "Normal Snakebite Claim",
    validationId: "VAL-201",
    careCategory: "emergency",
    icdCode: "T63.0",
    value: {
      condition_code: "SNAKE_BITE",
      patient: {
        gender: "male",
        age_group: "adult",
        care_type: "outpatient",
        care_category: "emergency",
      },
      clinical_conditions: {
        neurotoxicity: true,
        respiratory_difficulty: true,
      },
      services: [
        "emergency_assessment",
        "limb_immobilization",
        "airway_monitoring",
        "wound_cleaning",
        "observation",
        "oxygen_support",
        "referral",
      ],
      medicines: ["anti_snake_venom", "tetanus_toxoid", "paracetamol"],
      claimed_amount: 20500,
    },
  },
  {
    label: "Drowning Upcoding",
    validationId: "VAL-202",
    careCategory: "emergency",
    icdCode: "T75.1",
    value: {
      condition_code: "DROWNING",
      patient: {
        gender: "male",
        age_group: "adult",
        care_type: "outpatient",
        care_category: "emergency",
      },
      clinical_conditions: {
        aspiration_risk: true,
      },
      services: ["emergency_assessment", "cpr", "icu_stay", "mri", "surgery"],
      medicines: ["oxygen"],
      claimed_amount: 50000,
    },
  },
  {
    label: "Suspicious Fall Injury",
    validationId: "VAL-203",
    careCategory: "emergency",
    icdCode: "W00-W19",
    value: {
      condition_code: "FALL_INJURY",
      patient: {
        gender: "female",
        age_group: "adult",
        care_type: "outpatient",
        care_category: "emergency",
      },
      clinical_conditions: {},
      services: ["emergency_assessment", "mri", "surgery", "icu_stay"],
      medicines: ["morphine"],
      claimed_amount: 45000,
    },
  },
  {
    label: "Male + Normal Delivery",
    validationId: "VAL-204",
    careCategory: "basic",
    icdCode: "O80",
    value: {
      condition_code: "NORMAL_DELIVERY",
      patient: {
        gender: "male",
        age_group: "adult",
        care_type: "inpatient",
        care_category: "basic",
      },
      clinical_conditions: {
        full_term: true,
        spontaneous_labour: true,
      },
      services: ["consultation", "delivery_care"],
      medicines: [],
      claimed_amount: 7000,
    },
  },
  {
    label: "Female + Prostate Surgery",
    validationId: "VAL-205",
    careCategory: "basic",
    icdCode: "N40",
    value: {
      condition_code: "PROSTATE_SURGERY",
      patient: {
        gender: "female",
        age_group: "adult",
        care_type: "inpatient",
        care_category: "basic",
      },
      clinical_conditions: {
        urinary_retention: true,
      },
      services: ["consultation", "ultrasound_kub_prostate", "surgery"],
      medicines: [],
      claimed_amount: 25000,
    },
  },
];

const CLAIM_REVIEW_ROWS = [
  ["VAL-101", "T63.0", "Dhulikhel Hospital", "REVIEW_REQUIRED", "HIGH", "Medical Officer Review"],
  ["VAL-102", "I10", "Dhulikhel Hospital", "ACCEPT", "LOW", "Ready for Adjudication"],
  ["VAL-103", "O80", "Dhulikhel Hospital", "REJECT_ENTRY", "CRITICAL", "Entry Blocked"],
];

const FLAGGED_ROWS = [
  ["2026-06-19", "T63.0", "ASV without envenomation evidence", "HIGH", "Assign to Medical Officer"],
  ["2026-06-19", "O80", "Male patient with normal delivery claim", "CRITICAL", "Block Entry"],
  ["2026-06-18", "N40", "Female patient with prostate surgery claim", "CRITICAL", "Manual Review"],
];

const MALE_ONLY_BASIC_CODES = new Set([
  "prostate_surgery",
  "testicular_ultrasound",
  "circumcision",
  "psa_test",
  "ultrasound_kub_prostate",
  "scrotal_ultrasound_doppler",
  "tumor_markers",
]);

const FEMALE_ONLY_BASIC_CODES = new Set([
  "antenatal_care",
  "normal_delivery",
  "caesarean_section",
  "delivery_care",
  "newborn_care",
  "obstetric_ultrasound",
  "fetal_heart_monitoring",
  "blood_group_crossmatch",
  "oxytocin",
]);

function prettyLabel(value = "") {
  return String(value)
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function findDiagnosisByIcd(icdCode) {
  return DIAGNOSES.find((item) => item.icd === icdCode) || null;
}

function getDiagnosesForCategory(careCategory, gender) {
  if (careCategory === "emergency") {
    return DIAGNOSES.filter((item) => item.careCategory === "emergency");
  }

  const allowedDiagnosisCodes = new Set([
    ...BASIC_COMMON_DIAGNOSIS_CODES,
    ...(gender === "female" ? BASIC_FEMALE_DIAGNOSIS_CODES : BASIC_MALE_DIAGNOSIS_CODES),
  ]);

  return DIAGNOSES.filter(
    (item) => item.careCategory === "basic" && allowedDiagnosisCodes.has(item.icd),
  );
}

function buildEmptyClinicalFlags(diagnosis) {
  if (!diagnosis) {
    return {};
  }
  return Object.fromEntries(diagnosis.evidenceFlags.map((flag) => [flag, false]));
}

function buildDefaultForm() {
  const defaultDiagnosis = getDiagnosesForCategory("emergency", "male")[0];
  return {
    careCategory: "emergency",
    icdCode: defaultDiagnosis ? defaultDiagnosis.icd : "",
    condition_code: defaultDiagnosis ? defaultDiagnosis.condition : "",
    patient: {
      gender: "male",
      age_group: "adult",
      care_type: "outpatient",
      care_category: "emergency",
    },
    clinical_conditions: buildEmptyClinicalFlags(defaultDiagnosis),
    services: [],
    medicines: [],
    claimed_amount: 0,
  };
}

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "Not available";
  }
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function getDecisionTone(value) {
  return {
    ACCEPT: "accept",
    WARNING: "warning",
    REVIEW_REQUIRED: "review",
    REJECT_ENTRY: "reject",
  }[value] || "neutral";
}

function getRiskTone(value) {
  return {
    LOW: "accept",
    MEDIUM: "warning",
    HIGH: "review",
    CRITICAL: "reject",
  }[value] || "neutral";
}

function getComplianceTone(score) {
  if (score <= 40) {
    return "low";
  }
  if (score <= 70) {
    return "mid";
  }
  return "high";
}

function splitClaimItems(items) {
  const services = [];
  const medicines = [];
  items.forEach((item) => {
    if (["medicine", "item"].includes((GROUP_ITEM_CATEGORY[item] || ""))) {
      medicines.push(item);
    } else {
      services.push(item);
    }
  });
  return { services, medicines };
}

function filterBasicCodesByGender(items, gender) {
  return items.filter((item) => {
    if (gender === "male") {
      return !FEMALE_ONLY_BASIC_CODES.has(item);
    }
    if (gender === "female") {
      return !MALE_ONLY_BASIC_CODES.has(item);
    }
    return true;
  });
}

function filterGroupItemsByGender(items, careCategory, gender) {
  if (careCategory !== "basic") {
    return items;
  }

  return items.filter((item) => {
    const code = typeof item === "string" ? item : item.code;
    if (gender === "male") {
      return !FEMALE_ONLY_BASIC_CODES.has(code);
    }
    if (gender === "female") {
      return !MALE_ONLY_BASIC_CODES.has(code);
    }
    return true;
  });
}

const GROUP_ITEM_CATEGORY = {};
[
  ...GROUPS.emergencyServices.flatMap((group) => group.items),
  ...GROUPS.basicCare.flatMap((group) => group.items),
].forEach((item) => {
  const code = item.code;
  const medicineCodes = new Set([
    "oxygen",
    "anti_snake_venom",
    "tetanus_toxoid",
    "paracetamol",
    "antibiotics",
    "morphine",
    "amlodipine",
    "enalapril",
    "losartan",
    "hydrochlorothiazide",
    "atenolol",
    "ibuprofen",
    "oral_fluids",
    "normal_saline",
    "ringer_lactate",
    "ors",
    "zinc_sulfate",
    "metronidazole",
    "azithromycin",
    "ferrous_sulfate",
    "folic_acid",
    "vitamin_b12",
    "iron_sucrose",
    "tld_regimen",
    "cotrimoxazole",
    "zidovudine",
    "efavirenz",
    "ceftriaxone",
    "diclofenac",
    "tramadol",
    "doxycycline",
    "lidocaine",
    "amoxicillin",
    "cloxacillin",
    "iron_folic",
    "calcium_tablets",
    "albendazole",
    "tetanus_diphtheria_vaccine",
    "oxytocin",
    "cefazolin",
  ]);
  GROUP_ITEM_CATEGORY[code] = medicineCodes.has(code) ? "medicine" : "service";
});

function Field({ label, children }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
    </label>
  );
}

function SectionHeading({ number, title, helper, subtitle }) {
  return (
    <div className="section-heading">
      <span className="step-number">{number}</span>
      <div>
        <h3>{title}</h3>
        {subtitle ? <strong>{subtitle}</strong> : null}
        {helper ? <p>{helper}</p> : null}
      </div>
    </div>
  );
}

function CheckboxGrid({ items, selected, onToggle }) {
  return (
    <div className="checkbox-grid">
      {items.map((item) => {
        const code = typeof item === "string" ? item : item.code;
        const label = typeof item === "string" ? item : item.label;
        const checked = Array.isArray(selected)
          ? selected.includes(code)
          : Boolean(selected[code]);
        return (
          <label className="checkbox-item" key={code}>
            <input checked={checked} onChange={() => onToggle(code)} type="checkbox" />
            <span>{prettyLabel(label)}</span>
          </label>
        );
      })}
    </div>
  );
}

function ResultMetric({ label, value, tone }) {
  return (
    <div className="result-metric">
      <span>{label}</span>
      <strong className={tone ? `text-${tone}` : ""}>{value}</strong>
    </div>
  );
}

function ValidationCard({ result, emptyText }) {
  if (!result) {
    return (
      <div className="result-panel-content">
        <p className="empty-state small">{emptyText}</p>
      </div>
    );
  }

  const decisionTone = getDecisionTone(result.rule_decision);
  const riskTone = getRiskTone(result.risk_level);
  const complianceScore = Number(result.compliance_score || 0);
  const pathway = result.stp_pathway_name || "Not available";

  return (
    <div className="result-panel-content">
      <div className={`decision-banner ${decisionTone}`}>
        <strong>
          {result.rule_decision === "REJECT_ENTRY"
            ? "CLAIM REJECTED — Entry Blocked"
            : prettyLabel(result.rule_decision)}
        </strong>
        <span>{result.suggested_action}</span>
      </div>

      {result.rule_decision === "REJECT_ENTRY" ? (
        <div className="treatment-note">
          This blocks incorrect claim submission, not patient treatment.
        </div>
      ) : null}

      <div className="result-grid">
        <ResultMetric label="Rule Decision" tone={decisionTone} value={prettyLabel(result.rule_decision)} />
        <ResultMetric label="Risk Level" tone={riskTone} value={result.risk_level || "Not available"} />
        <ResultMetric label="Submission Allowed" value={result.submission_allowed ? "Yes" : "No"} />
        <ResultMetric label="Compliance Score" value={`${result.compliance_score}%`} />
        <ResultMetric label="Conflict Probability" value={formatPercent(result.ml_conflict_probability)} />
        <ResultMetric label="Final Risk Score" value={formatPercent(result.final_risk_score)} />
        <ResultMetric label="Suggested Action" value={result.suggested_action} />
        <ResultMetric label="STP Pathway" value={pathway} />
      </div>

      {/* <div className="compliance-card">
        <div className="compliance-header">
          <strong>Compliance Score: {result.compliance_score}%</strong>
          <span>STP Pathway: {pathway}</span>
        </div>
        <div className="progress-track">
          <div
            className={`progress-fill ${getComplianceTone(complianceScore)}`}
            style={{ width: `${Math.max(0, Math.min(complianceScore, 100))}%` }}
          />
        </div>
      </div> */}

      <div className="detail-grid">
        <div className="detail-card">
          <h3>Reasons</h3>
          <ol>
            {(result.reasons || []).length > 0
              ? result.reasons.map((reason) => <li key={reason}>{reason}</li>)
              : <li>No reasons returned.</li>}
          </ol>
        </div>
        <div className="detail-card">
          <h3>Rule Hits</h3>
          <div className="chip-wrap">
            {(result.rule_hits || []).length > 0
              ? result.rule_hits.map((hit) => <span key={hit}>{hit}</span>)
              : <span>No rule hits returned.</span>}
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [activePage, setActivePage] = useState(PAGE_KEYS.claimEntry);
  const [validationId, setValidationId] = useState("VAL-001");
  const [form, setForm] = useState(buildDefaultForm());
  const [health, setHealth] = useState({
    checking: true,
    connected: false,
    modelLoaded: false,
    supportedCount: 0,
  });
  const [livePreviewResult, setLivePreviewResult] = useState(null);
  const [submittedResult, setSubmittedResult] = useState(null);
  const [livePreviewError, setLivePreviewError] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [livePreviewChecking, setLivePreviewChecking] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [diagnosisResetNote, setDiagnosisResetNote] = useState("");
  const [resultMode, setResultMode] = useState("");

  const previewRequestRef = useRef(0);
  const availableDiagnoses = getDiagnosesForCategory(
    form.careCategory,
    form.patient.gender,
  );
  const selectedDiagnosis = findDiagnosisByIcd(form.icdCode);

  async function checkHealth() {
    setHealth((current) => ({ ...current, checking: true }));
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) {
        throw new Error("Health check failed.");
      }
      const data = await response.json();
      setHealth({
        checking: false,
        connected: true,
        modelLoaded: Boolean(data.model_loaded),
        supportedCount: Array.isArray(data.supported_conditions)
          ? data.supported_conditions.length
          : 0,
      });
    } catch (error) {
      console.error("Health check error:", error);
      setHealth({
        checking: false,
        connected: false,
        modelLoaded: false,
        supportedCount: 0,
      });
    }
  }

  useEffect(() => {
    checkHealth();
  }, []);

  function resetResults() {
    setLivePreviewResult(null);
    setSubmittedResult(null);
    setLivePreviewError("");
    setSubmitError("");
    setResultMode("");
  }

  function updatePatient(field, value) {
    setForm((current) => {
      const isBasicGenderChange = field === "gender" && current.careCategory === "basic";
      const filteredServices = isBasicGenderChange
        ? filterBasicCodesByGender(current.services, value)
        : current.services;
      const filteredMedicines = isBasicGenderChange
        ? filterBasicCodesByGender(current.medicines, value)
        : current.medicines;
      const nextForm = {
        ...current,
        patient: {
          ...current.patient,
          [field]: value,
        },
        services: filteredServices,
        medicines: filteredMedicines,
      };

      if (isBasicGenderChange) {
        const currentDiagnosis = findDiagnosisByIcd(current.icdCode);
        if (
          currentDiagnosis &&
          currentDiagnosis.genderScope !== "all" &&
          currentDiagnosis.genderScope !== value
        ) {
          nextForm.icdCode = "";
          nextForm.condition_code = "";
          nextForm.clinical_conditions = {};
          setDiagnosisResetNote(
            "Diagnosis reset — not applicable for selected gender.",
          );
        } else {
          setDiagnosisResetNote("");
        }
      }

      return nextForm;
    });
    resetResults();
  }

  function changeCareCategory(nextCategory) {
    const nextDiagnoses = getDiagnosesForCategory(nextCategory, form.patient.gender);
    const nextDiagnosis = nextDiagnoses[0] || null;
    setForm((current) => ({
      ...current,
      careCategory: nextCategory,
      icdCode: nextDiagnosis ? nextDiagnosis.icd : "",
      condition_code: nextDiagnosis ? nextDiagnosis.condition : "",
      patient: {
        ...current.patient,
        care_category: nextCategory,
      },
      clinical_conditions: buildEmptyClinicalFlags(nextDiagnosis),
      services: [],
      medicines: [],
      claimed_amount: 0,
    }));
    setDiagnosisResetNote("");
    resetResults();
  }

  function changeDiagnosis(icdCode) {
    const diagnosis = findDiagnosisByIcd(icdCode);
    setForm((current) => ({
      ...current,
      icdCode,
      condition_code: diagnosis ? diagnosis.condition : "",
      patient: {
        ...current.patient,
        care_category: diagnosis ? diagnosis.careCategory : current.patient.care_category,
      },
      clinical_conditions: buildEmptyClinicalFlags(diagnosis),
      services: [],
      medicines: [],
      claimed_amount: 0,
    }));
    setDiagnosisResetNote("");
    resetResults();
  }

  function toggleClinicalFlag(flag) {
    setForm((current) => ({
      ...current,
      clinical_conditions: {
        ...current.clinical_conditions,
        [flag]: !current.clinical_conditions[flag],
      },
    }));
    setSubmitError("");
  }

  function toggleClaimItem(code) {
    setForm((current) => {
      const isMedicine = GROUP_ITEM_CATEGORY[code] === "medicine";
      const targetField = isMedicine ? "medicines" : "services";
      const source = current[targetField];
      const nextValues = source.includes(code)
        ? source.filter((value) => value !== code)
        : [...source, code];
      return {
        ...current,
        [targetField]: nextValues,
      };
    });
    setSubmitError("");
  }

  function applyDemoScenario(demo) {
    const diagnosis = findDiagnosisByIcd(demo.icdCode);
    setValidationId(demo.validationId);
    setForm({
      careCategory: demo.careCategory,
      icdCode: demo.icdCode,
      condition_code: demo.value.condition_code,
      patient: {
        ...demo.value.patient,
        care_category: demo.careCategory,
      },
      clinical_conditions: {
        ...buildEmptyClinicalFlags(diagnosis),
        ...demo.value.clinical_conditions,
      },
      services: [...demo.value.services],
      medicines: [...demo.value.medicines],
      claimed_amount: 0,
    });
    setDiagnosisResetNote("");
    resetResults();
    setActivePage(PAGE_KEYS.claimEntry);
  }

  function buildPayload(validationMode) {
    return {
      condition_code: form.condition_code,
      icd_code: form.icdCode,
      validation_mode: validationMode,
      patient: {
        gender: form.patient.gender,
        age_group: form.patient.age_group,
        care_type: form.patient.care_type,
        care_category: form.careCategory,
      },
      clinical_conditions: form.clinical_conditions,
      services: form.services,
      medicines: form.medicines,
      claimed_amount: 0,
    };
  }

  useEffect(() => {
    if (!form.icdCode || !form.condition_code) {
      setLivePreviewChecking(false);
      setLivePreviewResult(null);
      setLivePreviewError("");
      return undefined;
    }

    const requestId = previewRequestRef.current + 1;
    previewRequestRef.current = requestId;

    const timer = setTimeout(async () => {
      setLivePreviewChecking(true);
      setLivePreviewError("");
      try {
        const response = await fetch(`${API_BASE_URL}/validate-claim`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(buildPayload("live_preview")),
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || "Live preview failed.");
        }
        if (previewRequestRef.current !== requestId) {
          return;
        }
        setLivePreviewResult(data);
        setResultMode("live_preview");
        setHealth((current) => ({ ...current, checking: false, connected: true }));
      } catch (error) {
        console.error("Live preview error:", error);
        if (previewRequestRef.current !== requestId) {
          return;
        }
        setLivePreviewResult(null);
        setLivePreviewError("Live preview unavailable. Check backend connectivity.");
        setHealth((current) => ({
          ...current,
          checking: false,
          connected: false,
          modelLoaded: false,
        }));
      } finally {
        if (previewRequestRef.current === requestId) {
          setLivePreviewChecking(false);
        }
      }
    }, 700);

    return () => clearTimeout(timer);
  }, [form]);

  async function submitClaim(event) {
    event.preventDefault();
    if (!form.icdCode || !form.condition_code) {
      setSubmitError("Select an ICD diagnosis before submitting the claim.");
      return;
    }

    setSubmitLoading(true);
    setSubmitError("");
    try {
      const response = await fetch(`${API_BASE_URL}/validate-claim`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildPayload("submitted_validation")),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Validation failed.");
      }
      setSubmittedResult(data);
      setResultMode("submitted_validation");
      setHealth((current) => ({ ...current, checking: false, connected: true }));
    } catch (error) {
      console.error("Submit validation error:", error);
      setSubmitError("Claim validation failed. Please check backend server.");
      setHealth((current) => ({
        ...current,
        checking: false,
        connected: false,
        modelLoaded: false,
      }));
    } finally {
      setSubmitLoading(false);
    }
  }

  function renderHomePage() {
    return (
      <section className="content-stack">
        <section className="panel">
          <div className="panel-header">
            <h2>Welcome to ClaimGuard</h2>
          </div>
          <div className="panel-body">
            <p className="body-copy">
              ClaimGuard validates openIMIS-style claims against Nepal STP 2078 pathways before reimbursement.
              Use the claim entry module to check emergency and basic care claims in one place.
            </p>
            <div className="inline-actions">
              <button className="primary-button" onClick={() => setActivePage(PAGE_KEYS.claimEntry)} type="button">
                Go to Claim Entry
              </button>
            </div>
          </div>
        </section>
      </section>
    );
  }

  function renderRecommendedPanel() {
    if (!selectedDiagnosis) {
      return (
        <section className="workflow-section recommendation-section">
          <SectionHeading
            number="4"
            title="STP Recommendation"
            subtitle="Recommended STP Services / Items"
          />
          <p className="helper-copy">Select a diagnosis to load the recommended STP guidance.</p>
        </section>
      );
    }

    const recommended = selectedDiagnosis.recommended;
    return (
      <section className="workflow-section recommendation-section">
        <SectionHeading
          number="4"
          title="STP Recommendation"
          subtitle="Recommended STP Services / Items"
        />
        <div className="recommendation-panel">
          <div className="recommendation-block">
            <span>Expected</span>
            <ul>
              {recommended.expected.map((item) => (
                <li key={item}>{prettyLabel(item)}</li>
              ))}
            </ul>
          </div>
          <div className="recommendation-block">
            <span>Common</span>
            <ul>
              {(recommended.common.length > 0 ? recommended.common : ["No extra common items listed."]).map((item) => (
                <li key={item}>{prettyLabel(item)}</li>
              ))}
            </ul>
          </div>
          <div className="recommendation-block">
            <span>Conditional</span>
            <ul>
              {(recommended.conditional.length > 0 ? recommended.conditional : ["No conditional items listed."]).map((item) => (
                <li key={item}>{prettyLabel(item)}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>
    );
  }

  function renderClaimEntryPage() {
    const visibleResult =
      resultMode === "submitted_validation"
        ? submittedResult || livePreviewResult
        : livePreviewResult || submittedResult;

    return (
      <section className="content-stack">
        <div className="page-heading">
          <h1>Emergency Claim Entry — ClaimGuard Compliance Module</h1>
          <p>Follow the guided workflow to validate a claim against the selected Nepal STP 2078 pathway.</p>
        </div>

        <form className="panel" onSubmit={submitClaim}>
          <div className="panel-header">
            <h2>Guided Claim Entry</h2>
            <span className="header-tag">ICD → STP → Evidence → Claim → Result</span>
          </div>

          <div className="panel-body workflow-stack">
            <section className="workflow-section care-category-section">
              <SectionHeading
                number="1"
                title="Care Category"
                helper="Choose the care stream first. It controls the available diagnoses and claim items."
              />
              <div className="care-category-toggle" role="group" aria-label="Care Category">
                {CARE_CATEGORY_OPTIONS.map((item) => (
                  <label
                    className={`care-category-option ${form.careCategory === item.key ? "selected" : ""}`}
                    key={item.key}
                  >
                    <input
                      checked={form.careCategory === item.key}
                      name="care-category"
                      onChange={() => changeCareCategory(item.key)}
                      type="radio"
                    />
                    <span>{item.label}</span>
                  </label>
                ))}
              </div>
            </section>

            <section className="workflow-section">
              <SectionHeading
                number="2"
                title="Insuree Details"
                helper="Confirm the patient and facility details used for pathway validation."
              />
              <div className="field-grid">
                <Field label="Validation ID">
                  <input onChange={(event) => setValidationId(event.target.value)} value={validationId} />
                </Field>
                <Field label="Health Facility">
                  <input readOnly value="Dhulikhel Hospital" />
                </Field>
                <Field label="Insuree Gender">
                  <select onChange={(event) => updatePatient("gender", event.target.value)} value={form.patient.gender}>
                    <option value="male">male</option>
                    <option value="female">female</option>
                  </select>
                </Field>
                <Field label="Age Category">
                  <select onChange={(event) => updatePatient("age_group", event.target.value)} value={form.patient.age_group}>
                    <option value="adult">adult</option>
                    <option value="minor">minor</option>
                  </select>
                </Field>
                <Field label="Care Type">
                  <select onChange={(event) => updatePatient("care_type", event.target.value)} value={form.patient.care_type}>
                    <option value="outpatient">outpatient</option>
                    <option value="inpatient">inpatient</option>
                  </select>
                </Field>
              </div>
            </section>

            <section className="workflow-section">
              <SectionHeading
                number="3"
                title="ICD / Diagnosis"
                helper="Select the diagnosis that determines the applicable STP pathway."
              />
              <div className="diagnosis-layout">
                <Field label="ICD-10 / Diagnosis">
                  <select onChange={(event) => changeDiagnosis(event.target.value)} value={form.icdCode}>
                    {availableDiagnoses.length === 0 ? (
                      <option value="">No diagnosis available</option>
                    ) : (
                      <>
                        <option value="">Select diagnosis</option>
                        {availableDiagnoses.map((item) => (
                          <option key={item.icd} value={item.icd}>
                            {item.label}
                          </option>
                        ))}
                      </>
                    )}
                  </select>
                </Field>
                <div className="pathway-card full-width">
                  <span>Selected STP Pathway</span>
                  <strong>{selectedDiagnosis ? selectedDiagnosis.pathway : "Select a diagnosis to load the pathway."}</strong>
                </div>
              </div>
              {diagnosisResetNote ? <div className="inline-note">{diagnosisResetNote}</div> : null}
            </section>

            {renderRecommendedPanel()}

            <section className="workflow-section">
              <SectionHeading
                number="5"
                title="Clinical Findings / STP Evidence"
                helper="Select recorded clinical findings that justify the claimed services and medicines."
              />
              {selectedDiagnosis ? (
                <CheckboxGrid
                  items={selectedDiagnosis.evidenceFlags}
                  onToggle={toggleClinicalFlag}
                  selected={form.clinical_conditions}
                />
              ) : (
                <p className="helper-copy">Choose a diagnosis to display condition-specific findings.</p>
              )}
            </section>

            <section className="workflow-section">
              <SectionHeading
                number="6"
                title="Claimed Services / Medicines"
                helper="Choose only the services, investigations, medicines, or procedures recorded for this claim."
              />
              <div className="group-stack">
                {(form.careCategory === "emergency" ? GROUPS.emergencyServices : GROUPS.basicCare).map((group) => (
                  <details className="group-details" key={`${form.careCategory}-${group.title}`}>
                    <summary>{group.title}</summary>
                    <CheckboxGrid
                      items={filterGroupItemsByGender(group.items, form.careCategory, form.patient.gender)}
                      onToggle={toggleClaimItem}
                      selected={[...form.services, ...form.medicines]}
                    />
                  </details>
                ))}
              </div>
            </section>

            <section className="workflow-section demo-block">
              <SectionHeading
                number="7"
                title="Demo Scenarios"
                helper="Load one of five prepared cases for a quick hackathon demonstration."
              />
              <div className="demo-actions">
                {DEMO_SCENARIOS.map((demo) => (
                  <button className="secondary-button" key={demo.label} onClick={() => applyDemoScenario(demo)} type="button">
                    {demo.label}
                  </button>
                ))}
              </div>
            </section>

            <section className="workflow-section submit-section">
              <SectionHeading
                number="8"
                title="Submit + Result"
                helper="Run the rule engine and conflict model. The adjudication result appears directly below."
              />
              {submitError ? <div className="error-box">{submitError}</div> : null}
              {livePreviewChecking ? (
                <div className="helper-copy live-status">Checking the current claim against the STP pathway...</div>
              ) : null}
              {livePreviewError ? <div className="error-box compact">{livePreviewError}</div> : null}

              <div className="submit-row">
                <button className="primary-button submit-button" disabled={submitLoading} type="submit">
                  {submitLoading ? "Submitting..." : "Submit Claim for STP Validation"}
                </button>
              </div>
            </section>
          </div>
        </form>

        <section className="panel">
          <div className="panel-header">
            <div className="result-panel-title">
              <div>
                <h2>ClaimGuard Adjudication Result</h2>
                <p>Compliance result for the selected ICD-to-STP pathway.</p>
              </div>
            </div>
          </div>
          <div className="panel-body result-stack">
            <ValidationCard
              result={visibleResult}
              emptyText="No validation result yet. Select a demo or submit a claim to validate."
            />
          </div>
        </section>
      </section>
    );
  }

  function renderClaimReviewPage() {
    return (
      <section className="content-stack">
        <div className="page-heading">
          <h1>Claim Review Queue</h1>
          <p>Compact review queue examples for the openIMIS-style prototype.</p>
        </div>
        <section className="panel">
          <div className="panel-body">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Validation ID</th>
                    <th>ICD</th>
                    <th>Health Facility</th>
                    <th>Decision</th>
                    <th>Risk</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {CLAIM_REVIEW_ROWS.map((row) => (
                    <tr key={row[0]}>
                      <td>{row[0]}</td>
                      <td>{row[1]}</td>
                      <td>{row[2]}</td>
                      <td><span className={`table-badge ${getDecisionTone(row[3])}`}>{prettyLabel(row[3])}</span></td>
                      <td><span className={`table-badge ${getRiskTone(row[4])}`}>{row[4]}</span></td>
                      <td>{row[5]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </section>
    );
  }

  function renderFlaggedClaimsPage() {
    return (
      <section className="content-stack">
        <div className="page-heading">
          <h1>Flagged Claims</h1>
          <p>Examples of claims likely to be escalated before reimbursement.</p>
        </div>
        <section className="panel">
          <div className="panel-body">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>ICD</th>
                    <th>Reason</th>
                    <th>Risk</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {FLAGGED_ROWS.map((row) => (
                    <tr key={`${row[0]}-${row[1]}`}>
                      <td>{row[0]}</td>
                      <td>{row[1]}</td>
                      <td>{row[2]}</td>
                      <td><span className={`table-badge ${getRiskTone(row[3])}`}>{row[3]}</span></td>
                      <td>{row[4]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </section>
    );
  }

  function renderAboutPage() {
    return (
      <section className="content-stack">
        <div className="page-heading">
          <h1>About ClaimGuard</h1>
          <p>Scope and positioning of the current prototype.</p>
        </div>
        <section className="panel">
          <div className="panel-body">
            <p className="body-copy">
              ClaimGuard is a pre-adjudication validation prototype for openIMIS-style claim workflows.
              It checks structured claim entries against Nepal STP 2078 care pathways before reimbursement.
            </p>
            <p className="body-copy">
              The interface supports both emergency and basic care conditions in one lightweight workflow.
              Future integration can map this API to openIMIS FHIR Claim resources without changing the demo flow.
            </p>
          </div>
        </section>
      </section>
    );
  }

  function renderActivePage() {
    if (activePage === PAGE_KEYS.home) {
      return renderHomePage();
    }
    if (activePage === PAGE_KEYS.claimReview) {
      return renderClaimReviewPage();
    }
    if (activePage === PAGE_KEYS.flaggedClaims) {
      return renderFlaggedClaimsPage();
    }
    if (activePage === PAGE_KEYS.about) {
      return renderAboutPage();
    }
    return renderClaimEntryPage();
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <strong>ClaimGuard</strong>
        </div>
      </header>

      {!health.connected && !health.checking ? (
        <div className="backend-banner">
          <span>Backend not connected. Start Flask API with python app.py</span>
          <button className="ghost-button" onClick={checkHealth} type="button">
            Retry
          </button>
        </div>
      ) : null}

      <div className="app-layout">
        <aside className="sidebar">
          <nav className="sidebar-nav">
            {[
              { key: PAGE_KEYS.home, label: "Home" },
              { key: PAGE_KEYS.claimEntry, label: "Claim Entry" },
              { key: PAGE_KEYS.claimReview, label: "Claim Review" },
              { key: PAGE_KEYS.flaggedClaims, label: "Flagged Claims" },
              { key: PAGE_KEYS.about, label: "About" },
            ].map((item) => (
              <button
                className={activePage === item.key ? "active" : ""}
                key={item.key}
                onClick={() => setActivePage(item.key)}
                type="button"
              >
                {item.label}
              </button>
            ))}
          </nav>
        </aside>

        <main className="main-area">{renderActivePage()}</main>
      </div>
    </div>
  );
}

export default App;
