"""Train claim conflict-detection models on synthetic emergency and basic-care data."""

import json
import os

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier


TARGET_COLUMN = "conflict_label"
LEAKAGE_COLUMNS = [
    TARGET_COLUMN,
    "decision",
    "compliance_score",
    "legitimacy_score",
    "suggested_action",
    "reasons",
    "rule_hits",
]
CATEGORICAL_CANDIDATES = [
    "condition_code",
    "gender",
    "age_group",
    "care_type",
    "care_category",
    "icd_code",
]


def build_preprocessor(categorical_columns, numeric_columns):
    """Create preprocessing for raw categorical and numeric claim fields."""
    categorical_pipeline = Pipeline(
        steps=[
            ("missing_values", SimpleImputer(strategy="constant", fill_value="unknown")),
            ("one_hot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    numeric_pipeline = Pipeline(
        steps=[
            ("missing_values", SimpleImputer(strategy="constant", fill_value=0)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("categorical", categorical_pipeline, categorical_columns),
            ("numeric", numeric_pipeline, numeric_columns),
        ],
        remainder="drop",
    )


def build_model_pipeline(model, categorical_columns, numeric_columns):
    """Combine preprocessing and a classifier in one reusable pipeline."""
    return Pipeline(
        steps=[
            ("preprocessing", build_preprocessor(categorical_columns, numeric_columns)),
            ("classifier", model),
        ]
    )


def evaluate_model(name, pipeline, x_test, y_test):
    """Return the requested evaluation metrics and print them."""
    predictions = pipeline.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, zero_division=0)
    recall = recall_score(y_test, predictions, zero_division=0)
    f1 = f1_score(y_test, predictions, zero_division=0)
    matrix = confusion_matrix(y_test, predictions)
    report = classification_report(y_test, predictions, zero_division=0)

    print(f"\n{name} evaluation")
    print("-" * 60)
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 score:  {f1:.4f}")
    print("Confusion matrix:")
    print(matrix)
    print("Classification report:")
    print(report)

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def main():
    """Load data, train both models, and save the final pipeline."""
    project_directory = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(project_directory, "data", "training_data.csv")
    models_directory = os.path.join(project_directory, "models")
    model_path = os.path.join(models_directory, "conflict_model.pkl")
    feature_columns_path = os.path.join(models_directory, "feature_columns.json")

    data = pd.read_csv(dataset_path)
    print(f"Dataset shape: {data.shape}")
    print(
        "Condition distribution: "
        f"{data['condition_code'].value_counts().sort_index().to_dict()}"
    )
    print(
        "Label distribution: "
        f"{data[TARGET_COLUMN].value_counts().sort_index().to_dict()}"
    )
    print(
        "Condition-wise label distribution: "
        f"{data.groupby('condition_code')[TARGET_COLUMN].value_counts().unstack(fill_value=0).to_dict(orient='index')}"
    )
    if "decision" in data.columns:
        print(f"Decision distribution: {data['decision'].value_counts().to_dict()}")

    columns_to_drop = [column for column in LEAKAGE_COLUMNS if column in data.columns]
    features = data.drop(columns=columns_to_drop)
    target = data[TARGET_COLUMN]

    categorical_columns = [
        column for column in CATEGORICAL_CANDIDATES if column in features.columns
    ]
    numeric_columns = [
        column for column in features.columns if column not in categorical_columns
    ]

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=42,
        stratify=target,
    )

    decision_tree_pipeline = build_model_pipeline(
        DecisionTreeClassifier(max_depth=8, random_state=42),
        categorical_columns,
        numeric_columns,
    )
    decision_tree_pipeline.fit(x_train, y_train)
    evaluate_model("Decision Tree", decision_tree_pipeline, x_test, y_test)

    random_forest_pipeline = build_model_pipeline(
        RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            random_state=42,
            class_weight="balanced",
        ),
        categorical_columns,
        numeric_columns,
    )
    random_forest_pipeline.fit(x_train, y_train)
    random_forest_metrics = evaluate_model(
        "Random Forest",
        random_forest_pipeline,
        x_test,
        y_test,
    )

    os.makedirs(models_directory, exist_ok=True)
    joblib.dump(random_forest_pipeline, model_path)

    feature_information = {
        "all_feature_columns": list(features.columns),
        "categorical_columns": categorical_columns,
        "numeric_columns": numeric_columns,
        "dropped_leakage_columns": columns_to_drop,
        "target_column": TARGET_COLUMN,
        "model_type": "RandomForestClassifier",
        "dataset_row_count": int(len(data)),
        "supported_condition_count": int(data["condition_code"].nunique()),
    }
    with open(feature_columns_path, "w", encoding="utf-8") as json_file:
        json.dump(feature_information, json_file, indent=2)

    print("\nSaved outputs")
    print("-" * 60)
    print(f"Saved model path: {model_path}")
    print(f"Saved feature columns path: {feature_columns_path}")

    if random_forest_metrics["accuracy"] >= 0.90:
        print(
            "High accuracy is expected because this is synthetic STP-derived rule-labeled data. "
            "This verifies the ML pipeline, not real-world clinical accuracy."
        )


if __name__ == "__main__":
    main()
