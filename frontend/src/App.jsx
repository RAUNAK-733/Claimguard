import React, { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:5000";

const PAGE_KEYS = {
  home: "home",
  claimEntry: "claimEntry",
  claimReview: "claimReview",
  flaggedClaims: "flaggedClaims",
  about: "about",
};

const DIAGNOSES = [
  {
    condition: "DROWNING",
    icd: "T75.1",
    label: "T75.1 - Drowning / nonfatal submersion",
    pathway: "Nepal STP 2078 - Drowning Protocol",
  },
  {
    condition: "SNAKE_BITE",
    icd: "T63.0",
    label: "T63.0 - Toxic effect of snake venom",
    pathway: "Nepal STP 2078 - Snake Bite Protocol",
  },
  {
    condition: "FALL_INJURY",
    icd: "W00-W19",
    label: "W00-W19 - Fall injury event",
    pathway: "Nepal STP 2078 - Fall Injury Protocol",
  },
];

const CLINICAL_FLAGS = {
  DROWNING: [
    "not_breathing",
    "aspiration_risk",
    "hypovolemia_or_shock",
    "hypothermia",
    "associated_trauma",
    "neurological_concern",
  ],
  SNAKE_BITE: [
    "neurotoxicity",
    "coagulopathy_or_bleeding",
    "shock",
    "acute_kidney_injury",
    "respiratory_difficulty",
    "wound_infection",
  ],
  FALL_INJURY: [
    "fracture_suspected",
    "open_wound",
    "active_bleeding",
    "head_neck_trauma",
    "unconscious_or_low_gcs",
    "shock",
    "organ_injury_suspected",
    "neurological_concern",
  ],
};

const SERVICE_GROUPS = [
  {
    title: "Emergency",
    items: [
      "emergency_assessment",
      "airway_clearance",
      "oxygen_support",
      "cpr",
      "iv_fluids",
      "referral",
      "avpu_assessment",
    ],
  },
  {
    title: "Snake Bite Care",
    items: [
      "limb_immobilization",
      "airway_monitoring",
      "wound_cleaning",
      "observation",
    ],
  },
  {
    title: "Trauma Care",
    items: [
      "abcde_assessment",
      "pain_management",
      "xray",
      "splinting",
      "c_spine_protection",
      "bleeding_control",
    ],
  },
  {
    title: "High-cost",
    items: ["surgery", "icu_stay", "mri"],
  },
  {
    title: "Invalid / Fraud Demo",
    items: [
      "normal_delivery",
      "antenatal_care",
      "cosmetic_surgery",
      "tourniquet",
      "cut_wound",
      "suction_bite",
      "home_remedy",
    ],
  },
];

const MEDICINES = [
  "oxygen",
  "anti_snake_venom",
  "tetanus_toxoid",
  "paracetamol",
  "antibiotics",
  "morphine",
];

const NAV_ITEMS = [
  { key: PAGE_KEYS.home, label: "Home" },
  { key: PAGE_KEYS.claimEntry, label: "Claim Entry" },
  { key: PAGE_KEYS.claimReview, label: "Claim Review" },
  { key: PAGE_KEYS.flaggedClaims, label: "Flagged Claims" },
  { key: PAGE_KEYS.about, label: "About" },
];

const CLAIM_REVIEW_ROWS = [
  {
    id: "CLM-101",
    icd: "T63.0",
    facility: "Dhulikhel Hospital",
    decision: "REVIEW_REQUIRED",
    risk: "HIGH",
    status: "Medical Officer Review",
  },
  {
    id: "CLM-102",
    icd: "W00-W19",
    facility: "Dhulikhel Hospital",
    decision: "ACCEPT",
    risk: "LOW",
    status: "Ready for Adjudication",
  },
  {
    id: "CLM-103",
    icd: "T75.1",
    facility: "Dhulikhel Hospital",
    decision: "WARNING",
    risk: "MEDIUM",
    status: "Needs Justification",
  },
];

const FLAGGED_ROWS = [
  {
    date: "2026-06-18",
    icd: "T63.0",
    reason: "ASV without envenomation evidence",
    risk: "HIGH",
    action: "Assign to Medical Officer",
  },
  {
    date: "2026-06-17",
    icd: "W00-W19",
    reason: "ICU without severity evidence",
    risk: "HIGH",
    action: "Manual Review",
  },
  {
    date: "2026-06-17",
    icd: "T75.1",
    reason: "Surgery without trauma evidence",
    risk: "CRITICAL",
    action: "Block Entry",
  },
];

function buildEmptyClinicalFlags(conditionCode) {
  return Object.fromEntries(
    (CLINICAL_FLAGS[conditionCode] || []).map((flag) => [flag, false]),
  );
}

function buildDefaultForm(conditionCode = "SNAKE_BITE") {
  return {
    condition_code: conditionCode,
    patient: {
      gender: "male",
      age_group: "adult",
      care_type: "outpatient",
    },
    clinical_conditions: buildEmptyClinicalFlags(conditionCode),
    services: [],
    medicines: [],
    claimed_amount: "",
  };
}

const DEMO_SCENARIOS = [
  {
    label: "Normal Snakebite Claim",
    claimCode: "CLM-201",
    value: {
      condition_code: "SNAKE_BITE",
      patient: {
        gender: "male",
        age_group: "adult",
        care_type: "outpatient",
      },
      clinical_conditions: {
        neurotoxicity: true,
        coagulopathy_or_bleeding: false,
        shock: false,
        acute_kidney_injury: false,
        respiratory_difficulty: true,
        wound_infection: false,
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
    claimCode: "CLM-202",
    value: {
      condition_code: "DROWNING",
      patient: {
        gender: "male",
        age_group: "adult",
        care_type: "outpatient",
      },
      clinical_conditions: {
        not_breathing: false,
        aspiration_risk: true,
        hypovolemia_or_shock: false,
        hypothermia: false,
        associated_trauma: false,
        neurological_concern: false,
      },
      services: [
        "emergency_assessment",
        "cpr",
        "icu_stay",
        "mri",
        "surgery",
      ],
      medicines: ["oxygen"],
      claimed_amount: 50000,
    },
  },
  {
    label: "Suspicious Fall Injury",
    claimCode: "CLM-203",
    value: {
      condition_code: "FALL_INJURY",
      patient: {
        gender: "female",
        age_group: "adult",
        care_type: "outpatient",
      },
      clinical_conditions: {
        fracture_suspected: false,
        open_wound: false,
        active_bleeding: false,
        head_neck_trauma: false,
        unconscious_or_low_gcs: false,
        shock: false,
        organ_injury_suspected: false,
        neurological_concern: false,
      },
      services: ["emergency_assessment", "mri", "surgery", "icu_stay"],
      medicines: ["morphine"],
      claimed_amount: 45000,
    },
  },
];

function prettyLabel(value) {
  return String(value || "")
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(" ");
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
  }[value] || "review";
}

function getRiskTone(value) {
  return {
    LOW: "accept",
    MEDIUM: "warning",
    HIGH: "review",
    CRITICAL: "reject",
  }[value] || "review";
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

function Field({ label, children }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
    </label>
  );
}

function CheckboxGrid({ items, selected, onToggle }) {
  return (
    <div className="checkbox-grid">
      {items.map((item) => {
        const checked = Array.isArray(selected)
          ? selected.includes(item)
          : Boolean(selected[item]);

        return (
          <label className="checkbox-item" key={item}>
            <input
              checked={checked}
              onChange={() => onToggle(item)}
              type="checkbox"
            />
            <span>{prettyLabel(item)}</span>
          </label>
        );
      })}
    </div>
  );
}

function SummaryCard({ label, value }) {
  return (
    <div className="summary-card">
      <span>{label}</span>
      <strong>{value}</strong>
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

function App() {
  const [activePage, setActivePage] = useState(PAGE_KEYS.claimEntry);
  const [claimCode, setClaimCode] = useState("CLM-001");
  const [form, setForm] = useState(buildDefaultForm());
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [health, setHealth] = useState({
    checking: true,
    connected: false,
    modelLoaded: false,
  });

  const selectedDiagnosis =
    DIAGNOSES.find((item) => item.condition === form.condition_code) ||
    DIAGNOSES[0];
  const activeClinicalFlags = CLINICAL_FLAGS[form.condition_code] || [];

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
      });
    } catch (error) {
      console.error("Health check error:", error);
      setHealth({
        checking: false,
        connected: false,
        modelLoaded: false,
      });
    }
  }

  useEffect(() => {
    checkHealth();
  }, []);

  function updatePatient(field, value) {
    setForm((current) => ({
      ...current,
      patient: {
        ...current.patient,
        [field]: value,
      },
    }));
  }

  function changeDiagnosis(conditionCode) {
    setForm((current) => ({
      ...current,
      condition_code: conditionCode,
      clinical_conditions: buildEmptyClinicalFlags(conditionCode),
    }));
    setResult(null);
    setErrorMessage("");
  }

  function toggleClinicalFlag(flag) {
    setForm((current) => ({
      ...current,
      clinical_conditions: {
        ...current.clinical_conditions,
        [flag]: !current.clinical_conditions[flag],
      },
    }));
  }

  function toggleListItem(field, item) {
    setForm((current) => {
      const items = current[field];

      return {
        ...current,
        [field]: items.includes(item)
          ? items.filter((value) => value !== item)
          : [...items, item],
      };
    });
  }

  function applyDemoScenario(demo) {
    setClaimCode(demo.claimCode);
    setForm(JSON.parse(JSON.stringify(demo.value)));
    setResult(null);
    setErrorMessage("");
    setActivePage(PAGE_KEYS.claimEntry);
  }

  function resetForm() {
    setClaimCode("CLM-001");
    setForm(buildDefaultForm());
    setResult(null);
    setErrorMessage("");
  }

  async function submitClaim(event) {
    event.preventDefault();
    setLoading(true);
    setErrorMessage("");

    try {
      const response = await fetch(`${API_BASE_URL}/validate-claim`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          condition_code: form.condition_code,
          patient: form.patient,
          clinical_conditions: form.clinical_conditions,
          services: form.services,
          medicines: form.medicines,
          claimed_amount: Number(form.claimed_amount) || 0,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Validation failed.");
      }

      setResult(data);
      setHealth((current) => ({
        ...current,
        checking: false,
        connected: true,
      }));
    } catch (error) {
      console.error("Validation error:", error);
      setErrorMessage("Claim validation failed. Please check backend server.");
      setHealth({
        checking: false,
        connected: false,
        modelLoaded: false,
      });
    } finally {
      setLoading(false);
    }
  }

  function renderHomePage() {
    return (
      <section className="content-stack">
        <div className="page-heading">
          <h1>ClaimGuard Emergency Validator</h1>
          <p>Pre-adjudication validation layer for openIMIS-style emergency claims.</p>
        </div>

        <section className="panel">
          <div className="panel-header">
            <h2>Welcome</h2>
          </div>
          <div className="panel-body">
            <p className="body-copy">
              ClaimGuard checks emergency claims against Nepal STP-derived care
              pathways before adjudication. Use the claim entry page to validate
              structured demo claims against the backend API.
            </p>
            <div className="summary-grid">
              <SummaryCard label="Supported diagnoses" value="3" />
              <SummaryCard label="STP rule engine" value="Active" />
              <SummaryCard
                label="ML model"
                value={health.modelLoaded ? "Loaded" : "Offline"}
              />
            </div>
            <div className="inline-actions">
              <button
                className="primary-button"
                onClick={() => setActivePage(PAGE_KEYS.claimEntry)}
                type="button"
              >
                Go to Claim Entry
              </button>
            </div>
          </div>
        </section>
      </section>
    );
  }

  function renderClaimEntryPage() {
    const checks = result?.openimis_checks || {};
    const complianceScore = Number(result?.compliance_score || 0);
    const decisionTone = getDecisionTone(result?.rule_decision);
    const riskTone = getRiskTone(result?.risk_level);

    return (
      <section className="content-stack">
        <div className="page-heading">
          <h1>Emergency Claim Entry - ClaimGuard Compliance Module</h1>
          <p>STP-based validation with ML conflict scoring</p>
        </div>

        <form className="panel" onSubmit={submitClaim}>
          <div className="panel-header">
            <h2>Claim Information</h2>
            <span className="header-tag">{selectedDiagnosis.icd}</span>
          </div>

          <div className="panel-body section-stack">
            <section className="section-block">
              <h3>Insuree and Facility</h3>
              <div className="field-grid">
                <Field label="Claim Code">
                  <input
                    onChange={(event) => setClaimCode(event.target.value)}
                    value={claimCode}
                  />
                </Field>
                <Field label="Health Facility">
                  <input readOnly value="Dhulikhel Hospital" />
                </Field>
                <Field label="Insuree Gender">
                  <select
                    onChange={(event) =>
                      updatePatient("gender", event.target.value)
                    }
                    value={form.patient.gender}
                  >
                    <option value="male">male</option>
                    <option value="female">female</option>
                  </select>
                </Field>
                <Field label="Age Category">
                  <select
                    onChange={(event) =>
                      updatePatient("age_group", event.target.value)
                    }
                    value={form.patient.age_group}
                  >
                    <option value="adult">adult</option>
                    <option value="minor">minor</option>
                  </select>
                </Field>
                <Field label="Care Type">
                  <select
                    onChange={(event) =>
                      updatePatient("care_type", event.target.value)
                    }
                    value={form.patient.care_type}
                  >
                    <option value="outpatient">outpatient</option>
                    <option value="inpatient">inpatient</option>
                  </select>
                </Field>
                <Field label="Claimed Amount">
                  <input
                    min="0"
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        claimed_amount: event.target.value,
                      }))
                    }
                    step="0.01"
                    type="number"
                    value={form.claimed_amount}
                  />
                </Field>
              </div>
            </section>

            <section className="section-block">
              <h3>Diagnosis</h3>
              <div className="diagnosis-layout">
                <Field label="ICD-10 / Diagnosis">
                  <select
                    onChange={(event) => changeDiagnosis(event.target.value)}
                    value={form.condition_code}
                  >
                    {DIAGNOSES.map((item) => (
                      <option key={item.condition} value={item.condition}>
                        {item.label}
                      </option>
                    ))}
                  </select>
                </Field>
                <div className="pathway-card">
                  <span>Selected STP pathway</span>
                  <strong>{selectedDiagnosis.pathway}</strong>
                </div>
              </div>
            </section>

            <section className="section-block">
              <h3>Clinical Evidence</h3>
              <CheckboxGrid
                items={activeClinicalFlags}
                onToggle={toggleClinicalFlag}
                selected={form.clinical_conditions}
              />
            </section>

            <section className="section-block">
              <h3>Services and Medicines</h3>
              <div className="service-layout">
                <div className="service-column">
                  <div className="group-grid">
                    {SERVICE_GROUPS.map((group) => (
                      <div className="group-card" key={group.title}>
                        <h4>{group.title}</h4>
                        <CheckboxGrid
                          items={group.items}
                          onToggle={(item) => toggleListItem("services", item)}
                          selected={form.services}
                        />
                      </div>
                    ))}
                  </div>
                </div>
                <div className="medicine-column">
                  <div className="group-card">
                    <h4>Medicines / Items</h4>
                    <CheckboxGrid
                      items={MEDICINES}
                      onToggle={(item) => toggleListItem("medicines", item)}
                      selected={form.medicines}
                    />
                  </div>
                </div>
              </div>
            </section>

            <section className="section-block demo-block">
              <h3>Demo Scenarios</h3>
              <div className="demo-actions">
                {DEMO_SCENARIOS.map((demo) => (
                  <button
                    className="secondary-button"
                    key={demo.label}
                    onClick={() => applyDemoScenario(demo)}
                    type="button"
                  >
                    {demo.label}
                  </button>
                ))}
                <button
                  className="ghost-button"
                  onClick={resetForm}
                  type="button"
                >
                  Reset Form
                </button>
              </div>
            </section>

            {errorMessage ? <div className="error-box">{errorMessage}</div> : null}

            <div className="submit-row">
              <button className="primary-button submit-button" disabled={loading} type="submit">
                {loading ? "Validating..." : "Submit Claim for STP Validation"}
              </button>
            </div>
          </div>
        </form>

        <section className="panel">
          <div className="panel-header">
            <h2>ClaimGuard Adjudication Result</h2>
          </div>
          <div className="panel-body">
            {!result ? (
              <p className="empty-state">
                No claim submitted yet. Select a demo scenario or enter claim
                details.
              </p>
            ) : (
              <div className="result-stack">
                <div className={`decision-banner ${decisionTone}`}>
                  <strong>
                    {result.rule_decision === "REJECT_ENTRY"
                      ? "CLAIM REJECTED - Entry Blocked"
                      : prettyLabel(result.rule_decision)}
                  </strong>
                  <span>{result.suggested_action}</span>
                </div>

                <div className="result-grid">
                  <ResultMetric
                    label="Rule Decision"
                    tone={decisionTone}
                    value={prettyLabel(result.rule_decision)}
                  />
                  <ResultMetric
                    label="Risk Level"
                    tone={riskTone}
                    value={result.risk_level || "Not available"}
                  />
                  <ResultMetric
                    label="Submission Allowed"
                    value={result.submission_allowed ? "Yes" : "No"}
                  />
                  <ResultMetric
                    label="Compliance Score"
                    value={`${result.compliance_score}%`}
                  />
                  <ResultMetric
                    label="ML Conflict Probability"
                    value={formatPercent(result.ml_conflict_probability)}
                  />
                  <ResultMetric
                    label="Final Risk Score"
                    value={formatPercent(result.final_risk_score)}
                  />
                  <ResultMetric
                    label="Suggested Action"
                    value={result.suggested_action}
                  />
                </div>

                <div className="compliance-card">
                  <div className="compliance-header">
                    <strong>Compliance Score: {result.compliance_score}%</strong>
                    <span>STP Pathway: {selectedDiagnosis.pathway}</span>
                  </div>
                  <div className="progress-track">
                    <div
                      className={`progress-fill ${getComplianceTone(
                        complianceScore,
                      )}`}
                      style={{
                        width: `${Math.max(0, Math.min(complianceScore, 100))}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="detail-grid">
                  <div className="detail-card">
                    <h3>Reasons</h3>
                    <ol>
                      {(result.reasons || []).length > 0 ? (
                        result.reasons.map((reason) => <li key={reason}>{reason}</li>)
                      ) : (
                        <li>No rule reasons returned.</li>
                      )}
                    </ol>
                  </div>
                  <div className="detail-card">
                    <h3>Rule Hits</h3>
                    <div className="chip-wrap">
                      {(result.rule_hits || []).length > 0 ? (
                        result.rule_hits.map((hit) => <span key={hit}>{hit}</span>)
                      ) : (
                        <span>No rule hits returned</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="checks-card">
                  <h3>openIMIS Checks</h3>
                  <div className="checks-grid">
                    <span>
                      Gender Mismatch:
                      <strong>{checks.gender_mismatch ? " Flagged" : " Clear"}</strong>
                    </span>
                    <span>
                      Age Mismatch:
                      <strong>{checks.age_mismatch ? " Flagged" : " Clear"}</strong>
                    </span>
                    <span>
                      Care Type Mismatch:
                      <strong>{checks.care_type_mismatch ? " Flagged" : " Clear"}</strong>
                    </span>
                    <span>
                      Max Amount Violation:
                      <strong>
                        {checks.max_amount_violation ? " Flagged" : " Clear"}
                      </strong>
                    </span>
                    <span>
                      High Cost Count:
                      <strong>{` ${checks.high_cost_count ?? 0}`}</strong>
                    </span>
                    <span>
                      Unknown Item Count:
                      <strong>{` ${checks.unknown_item_count ?? 0}`}</strong>
                    </span>
                  </div>
                </div>

                <details className="json-block">
                  <summary>API Response JSON</summary>
                  <pre>{JSON.stringify(result, null, 2)}</pre>
                </details>
              </div>
            )}
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
          <p>Static review queue preview for the prototype user flow.</p>
        </div>

        <section className="panel">
          <div className="panel-body">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Claim ID</th>
                    <th>ICD</th>
                    <th>Health Facility</th>
                    <th>Decision</th>
                    <th>Risk</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {CLAIM_REVIEW_ROWS.map((row) => (
                    <tr key={row.id}>
                      <td>{row.id}</td>
                      <td>{row.icd}</td>
                      <td>{row.facility}</td>
                      <td>
                        <span className={`table-badge ${getDecisionTone(row.decision)}`}>
                          {prettyLabel(row.decision)}
                        </span>
                      </td>
                      <td>
                        <span className={`table-badge ${getRiskTone(row.risk)}`}>
                          {row.risk}
                        </span>
                      </td>
                      <td>{row.status}</td>
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
          <p>Static examples of claims that would be escalated for manual review.</p>
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
                    <tr key={`${row.date}-${row.icd}`}>
                      <td>{row.date}</td>
                      <td>{row.icd}</td>
                      <td>{row.reason}</td>
                      <td>
                        <span className={`table-badge ${getRiskTone(row.risk)}`}>
                          {row.risk}
                        </span>
                      </td>
                      <td>{row.action}</td>
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
          <p>Prototype background and integration scope.</p>
        </div>

        <section className="panel">
          <div className="panel-body">
            <p className="body-copy">
              ClaimGuard is a hackathon prototype designed as a pre-adjudication
              validation layer for openIMIS-style emergency claims. It combines
              Nepal STP-derived rule validation with a Random Forest conflict
              scoring model.
            </p>
            <p className="body-copy">
              Designed for openIMIS-style claims. Future integration can map this
              API to openIMIS FHIR Claim resources.
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
        <div className="title-block">Emergency Claim Entry</div>
        <div className="meta-block">
          <span>Health Facility: Dhulikhel Hospital | ClaimGuard v1.0</span>
          <span className={`status-badge ${health.connected ? "online" : "offline"}`}>
            API {health.connected ? "Connected" : "Disconnected"}
          </span>
          <span className={`status-badge ${health.modelLoaded ? "online" : "offline"}`}>
            Model {health.modelLoaded ? "Loaded" : "Offline"}
          </span>
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
            {NAV_ITEMS.map((item) => (
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
          <p className="sidebar-note">
            Designed for openIMIS-style claim entry and pre-adjudication review.
          </p>
        </aside>

        <main className="main-area">{renderActivePage()}</main>
      </div>
    </div>
  );
}

export default App;
