# ClaimGuard Backend Status Check

## Files present

- `rule_engine.py`
- `generate_training_data.py`
- `train_model.py`
- `README.md`
- `STATUS_CHECK.md`
- `data/training_data.csv`
- `models/conflict_model.pkl`
- `models/feature_columns.json`

## Rule engine status

Status: **OK**

The four built-in checks completed with the required decisions:

1. Valid drowning pathway: `ACCEPT`
2. Snake bite anti-snake-venom misuse: `REVIEW_REQUIRED`
3. Fall injury with unsupported surgery, ICU, and MRI: `REVIEW_REQUIRED`
4. Snake bite with unrelated normal delivery: `REJECT_ENTRY`

## Dataset status

- Row count: **12,000**
- Column count: **76**
- Conflict labels: `{0: 6000, 1: 6000}`
- Decision distribution:
  - `ACCEPT`: 5,728
  - `WARNING`: 272
  - `REVIEW_REQUIRED`: 3,751
  - `REJECT_ENTRY`: 2,249
- Each diagnosis contains 2,000 non-conflict and 2,000 conflict rows.

## Model training status

Status: **OK**

- Decision Tree accuracy: **0.9800**
- Decision Tree F1 score: **0.9804**
- Random Forest accuracy: **0.9996**
- Random Forest F1 score: **0.9996**
- Saved model: `models/conflict_model.pkl`
- Saved feature metadata: `models/feature_columns.json`
- Final model: `RandomForestClassifier` pipeline with preprocessing
- Direct leakage columns were excluded from model features.

High accuracy is expected because this is synthetic rule-labeled data. This
result verifies the ML pipeline, not real-world clinical performance.

## Known limitation

The model is trained on synthetic STP-derived rule-labeled data, not
real-world openIMIS claims.

## Final readiness

- Backend rule engine: **OK**
- Dataset generation: **OK**
- Model training: **OK**
- Ready for Flask API: **YES**
