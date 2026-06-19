# ClaimGuard Emergency Validator

ClaimGuard is a backend prototype for openIMIS-style emergency claim
validation. It supports three diagnoses:

- `DROWNING`
- `SNAKE_BITE`
- `FALL_INJURY`

The rule engine provides explainable claim-entry decisions. The machine
learning pipeline predicts the probability that a claim contains a conflict
requiring review or correction.

## Project files

```text
rule_engine.py
generate_training_data.py
train_model.py
README.md
STATUS_CHECK.md
data/
  training_data.csv
models/
  conflict_model.pkl
  feature_columns.json
```

## Run the backend workflow

Install the required Python packages:

```bash
pip install pandas scikit-learn joblib
```

Generate the synthetic dataset:

```bash
python generate_training_data.py
```

Train and save the models:

```bash
python train_model.py
```

Run the four built-in rule-engine checks:

```bash
python rule_engine.py
```

## Dataset

The generator creates exactly 12,000 synthetic rows:

- 4,000 rows for each diagnosis
- 2,000 non-conflict and 2,000 conflict rows per diagnosis
- 6,000 non-conflict and 6,000 conflict rows overall

Labels come only from `validate_claim()` in `rule_engine.py`.

## Important limitation

The model is trained on synthetic STP-derived rule-labeled data, not
real-world openIMIS claims. High evaluation accuracy verifies the backend ML
pipeline and must not be interpreted as real-world fraud or clinical
performance.
