"""Flask API for the ClaimGuard Emergency Validator."""

import json
import os

import joblib
import pandas as pd
from flask import Flask, jsonify, request

from rule_engine import SERVICE_CATALOG, validate_claim


app = Flask(__name__)

SUPPORTED_CONDITIONS = ["DROWNING", "SNAKE_BITE", "FALL_INJURY"]
PROJECT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(
    PROJECT_DIRECTORY,
    "models",
    "conflict_model.pkl",
)
FEATURE_METADATA_PATH = os.path.join(
    PROJECT_DIRECTORY,
    "models",
    "feature_columns.json",
)


def _load_model_files():
    """Load the trained pipeline and its raw feature-column metadata."""
    try:
        with open(
            FEATURE_METADATA_PATH,
            "r",
            encoding="utf-8",
        ) as metadata_file:
            metadata = json.load(metadata_file)

        model = joblib.load(MODEL_PATH)
        feature_columns = metadata.get("all_feature_columns", [])
        if not feature_columns:
            return None, None
        return model, metadata
    except (FileNotFoundError, OSError, ValueError, KeyError):
        return None, None


MODEL, FEATURE_METADATA = _load_model_files()


def _normalize_text(value):
    """Normalize a code or field name to lowercase snake_case."""
    if value is None:
        return ""
    return "_".join(str(value).strip().lower().split())


def _as_dictionary(value):
    """Return a dictionary or a safe empty default."""
    return value if isinstance(value, dict) else {}


def _as_list(value):
    """Return a list or a safe empty default."""
    return value if isinstance(value, list) else []


def _to_flag(value):
    """Convert common boolean-like values to numeric ML flags."""
    if isinstance(value, str):
        return int(value.strip().lower() in {"true", "1", "yes", "y"})
    return int(bool(value))


def _safe_number(value, default=0):
    """Convert a value to a number without breaking feature construction."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _build_feature_row(
    condition_code,
    patient,
    clinical_conditions,
    services,
    medicines,
    claimed_amount,
    rule_result,
):
    """Build one raw model row using the saved training feature schema."""
    feature_columns = FEATURE_METADATA["all_feature_columns"]
    feature_row = {column: 0 for column in feature_columns}

    normalized_patient = rule_result.get("patient", {})
    normalized_services = [_normalize_text(item) for item in services]
    normalized_medicines = [_normalize_text(item) for item in medicines]
    all_items = set(normalized_services + normalized_medicines)

    basic_values = {
        "condition_code": _normalize_text(condition_code).upper(),
        "gender": normalized_patient.get(
            "gender",
            _normalize_text(patient.get("gender")),
        ),
        "age_group": normalized_patient.get(
            "age_group",
            _normalize_text(patient.get("age_group")),
        ),
        "care_type": normalized_patient.get("care_type", "outpatient"),
        "claimed_amount": _safe_number(claimed_amount),
        "expected_total": rule_result.get("expected_total", 0),
        "amount_ratio": rule_result.get("amount_ratio") or 0,
        "service_count": len(normalized_services),
        "medicine_count": len(normalized_medicines),
    }
    for column, value in basic_values.items():
        if column in feature_row:
            feature_row[column] = value

    for flag, value in clinical_conditions.items():
        normalized_flag = _normalize_text(flag)
        if normalized_flag in feature_row:
            feature_row[normalized_flag] = _to_flag(value)

    for item in all_items:
        item_column = "has_" + item
        if item_column in feature_row:
            feature_row[item_column] = 1

    openimis_checks = rule_result.get("openimis_checks", {})
    check_mapping = {
        "has_gender_mismatch": "gender_mismatch",
        "has_age_mismatch": "age_mismatch",
        "has_care_type_mismatch": "care_type_mismatch",
        "has_max_amount_violation": "max_amount_violation",
    }
    for feature_name, check_name in check_mapping.items():
        if feature_name in feature_row:
            feature_row[feature_name] = _to_flag(
                openimis_checks.get(check_name, False)
            )

    high_cost_count = int(openimis_checks.get("high_cost_count", 0))
    if "high_cost_count" in feature_row:
        feature_row["high_cost_count"] = high_cost_count
    if "has_multiple_high_cost_items" in feature_row:
        feature_row["has_multiple_high_cost_items"] = int(
            high_cost_count >= 2
        )

    for item in all_items:
        metadata = SERVICE_CATALOG.get(item)
        if metadata is None:
            continue

        care_type = metadata.get("care_type")
        category = metadata.get("category")

        if (
            care_type == "inpatient"
            and "has_inpatient_only_service" in feature_row
        ):
            feature_row["has_inpatient_only_service"] = 1
        if (
            care_type == "outpatient"
            and "has_outpatient_service" in feature_row
        ):
            feature_row["has_outpatient_service"] = 1

        category_features = {
            "emergency_care": "has_emergency_service",
            "investigation": "has_investigation",
            "procedure": "has_procedure",
            "medicine": "has_medicine",
            "referral": "has_referral",
        }
        category_feature = category_features.get(category)
        if category_feature in feature_row:
            feature_row[category_feature] = 1

    return feature_row


def _predict_conflict(feature_row):
    """Return the saved model's class prediction and conflict probability."""
    if MODEL is None or FEATURE_METADATA is None:
        return None, None

    feature_columns = FEATURE_METADATA["all_feature_columns"]
    feature_frame = pd.DataFrame(
        [feature_row],
        columns=feature_columns,
    )
    prediction = int(MODEL.predict(feature_frame)[0])
    probabilities = MODEL.predict_proba(feature_frame)[0]
    class_labels = list(MODEL.classes_)
    conflict_probability = float(probabilities[class_labels.index(1)])
    return prediction, conflict_probability


def _risk_level(rule_decision, final_risk_score):
    """Set risk level while keeping the rule decision authoritative."""
    if rule_decision == "REJECT_ENTRY":
        return "CRITICAL"

    if rule_decision == "REVIEW_REQUIRED":
        if final_risk_score >= 0.85:
            return "CRITICAL"
        return "HIGH"

    if rule_decision == "WARNING":
        if final_risk_score >= 0.85:
            return "CRITICAL"
        if final_risk_score >= 0.60:
            return "HIGH"
        return "MEDIUM"

    if final_risk_score < 0.30:
        return "LOW"
    if final_risk_score < 0.60:
        return "MEDIUM"
    if final_risk_score < 0.85:
        return "HIGH"
    return "CRITICAL"


@app.after_request
def add_cors_headers(response):
    """Add simple CORS headers to every API response."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.get("/")
def index():
    """Describe the API and its available endpoints."""
    return jsonify(
        {
            "service": "ClaimGuard Emergency Validator API",
            "status": "running",
            "message": (
                "Use /health for API status and /validate-claim "
                "for claim validation."
            ),
            "endpoints": {
                "health": "/health",
                "validate_claim": "/validate-claim",
            },
            "frontend_note": (
                "Run the React frontend separately on "
                "http://localhost:5173"
            ),
        }
    )


@app.get("/health")
def health():
    """Report API and model availability."""
    return jsonify(
        {
            "status": "ok",
            "service": "ClaimGuard Emergency Validator API",
            "model_loaded": MODEL is not None and FEATURE_METADATA is not None,
            "supported_conditions": SUPPORTED_CONDITIONS,
        }
    )


@app.route("/validate-claim", methods=["POST", "OPTIONS"])
def validate_claim_endpoint():
    """Validate a claim with the rule engine and optional ML pipeline."""
    if request.method == "OPTIONS":
        return "", 204

    request_data = request.get_json(silent=True)
    if not isinstance(request_data, dict):
        return jsonify({"error": "Request body must contain valid JSON."}), 400

    try:
        condition_code = request_data.get("condition_code", "")
        patient = _as_dictionary(request_data.get("patient", {}))
        clinical_conditions = _as_dictionary(
            request_data.get("clinical_conditions", {})
        )
        services = _as_list(request_data.get("services", []))
        medicines = _as_list(request_data.get("medicines", []))
        claimed_amount = request_data.get("claimed_amount", 0)

        rule_result = validate_claim(
            condition_code,
            patient,
            clinical_conditions,
            services,
            medicines,
            claimed_amount,
        )

        ml_prediction = None
        ml_probability = None
        if MODEL is not None and FEATURE_METADATA is not None:
            feature_row = _build_feature_row(
                condition_code,
                patient,
                clinical_conditions,
                services,
                medicines,
                claimed_amount,
                rule_result,
            )
            ml_prediction, ml_probability = _predict_conflict(feature_row)

        rule_risk = 1 - float(rule_result["legitimacy_score"])
        if ml_probability is None:
            final_risk_score = rule_risk
        else:
            final_risk_score = (
                0.70 * rule_risk
                + 0.30 * ml_probability
            )
        final_risk_score = round(final_risk_score, 2)

        return jsonify(
            {
                "condition_code": rule_result["condition_code"],
                "patient": rule_result["patient"],
                "rule_decision": rule_result["decision"],
                "submission_allowed": rule_result["submission_allowed"],
                "compliance_score": rule_result["compliance_score"],
                "legitimacy_score": rule_result["legitimacy_score"],
                "model_loaded": (
                    MODEL is not None and FEATURE_METADATA is not None
                ),
                "ml_conflict_prediction": ml_prediction,
                "ml_conflict_probability": (
                    round(ml_probability, 4)
                    if ml_probability is not None
                    else None
                ),
                "final_risk_score": final_risk_score,
                "risk_level": _risk_level(
                    rule_result["decision"],
                    final_risk_score,
                ),
                "expected_total": rule_result["expected_total"],
                "amount_ratio": rule_result["amount_ratio"],
                "openimis_checks": rule_result["openimis_checks"],
                "rule_hits": rule_result["rule_hits"],
                "reasons": rule_result["reasons"],
                "suggested_action": rule_result["suggested_action"],
            }
        )
    except Exception as error:
        return jsonify({"error": str(error)}), 500


# Example health check:
# curl http://127.0.0.1:5000/health
#
# Example valid drowning claim:
# curl -X POST http://127.0.0.1:5000/validate-claim -H "Content-Type: application/json" -d "{\"condition_code\":\"DROWNING\",\"patient\":{\"gender\":\"male\",\"age_group\":\"adult\",\"care_type\":\"outpatient\"},\"clinical_conditions\":{\"not_breathing\":true,\"hypothermia\":true},\"services\":[\"emergency_assessment\",\"airway_clearance\",\"oxygen_support\",\"cpr\",\"warming_blanket\",\"referral\",\"avpu_assessment\"],\"medicines\":[],\"claimed_amount\":5600}"
#
# Example snake bite ASV misuse:
# curl -X POST http://127.0.0.1:5000/validate-claim -H "Content-Type: application/json" -d "{\"condition_code\":\"SNAKE_BITE\",\"patient\":{\"gender\":\"male\",\"age_group\":\"adult\",\"care_type\":\"outpatient\"},\"clinical_conditions\":{},\"services\":[\"emergency_assessment\",\"limb_immobilization\",\"observation\"],\"medicines\":[\"anti_snake_venom\"],\"claimed_amount\":18000}"
#
# Example unsupported high-cost fall injury claim:
# curl -X POST http://127.0.0.1:5000/validate-claim -H "Content-Type: application/json" -d "{\"condition_code\":\"FALL_INJURY\",\"patient\":{\"gender\":\"female\",\"age_group\":\"adult\",\"care_type\":\"outpatient\"},\"clinical_conditions\":{},\"services\":[\"emergency_assessment\",\"mri\",\"surgery\",\"icu_stay\"],\"medicines\":[\"morphine\"],\"claimed_amount\":45000}"
#
# Example unrelated normal delivery claim:
# curl -X POST http://127.0.0.1:5000/validate-claim -H "Content-Type: application/json" -d "{\"condition_code\":\"SNAKE_BITE\",\"patient\":{\"gender\":\"female\",\"age_group\":\"adult\",\"care_type\":\"outpatient\"},\"clinical_conditions\":{},\"services\":[\"normal_delivery\"],\"medicines\":[],\"claimed_amount\":7000}"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
