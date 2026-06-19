"""Train emergency claim conflict-detection models."""

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
]


def build_preprocessor(categorical_columns, numeric_columns):
    """Create preprocessing for raw categorical and numeric claim fields."""
    categorical_pipeline = Pipeline(
        steps=[
            (
                "missing_values",
                SimpleImputer(strategy="constant", fill_value="unknown"),
            ),
            (
                "one_hot",
                OneHotEncoder(handle_unknown="ignore"),
            ),
        ]
    )

    numeric_pipeline = Pipeline(
        steps=[
            (
                "missing_values",
                SimpleImputer(strategy="constant", fill_value=0),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                categorical_pipeline,
                categorical_columns,
            ),
            (
                "numeric",
                numeric_pipeline,
                numeric_columns,
            ),
        ],
        remainder="drop",
    )


def build_model_pipeline(model, categorical_columns, numeric_columns):
    """Combine preprocessing and a classifier in one reusable pipeline."""
    return Pipeline(
        steps=[
            (
                "preprocessing",
                build_preprocessor(
                    categorical_columns,
                    numeric_columns,
                ),
            ),
            ("classifier", model),
        ]
    )


def evaluate_model(name, pipeline, x_test, y_test):
    """Print the requested binary classification metrics."""
    predictions = pipeline.predict(x_test)

    print(f"\n{name} evaluation")
    print("-" * 60)
    print(f"Accuracy:  {accuracy_score(y_test, predictions):.4f}")
    print(
        "Precision: "
        f"{precision_score(y_test, predictions, zero_division=0):.4f}"
    )
    print(
        f"Recall:    {recall_score(y_test, predictions, zero_division=0):.4f}"
    )
    print(
        f"F1 score:  {f1_score(y_test, predictions, zero_division=0):.4f}"
    )
    print("Confusion matrix:")
    print(confusion_matrix(y_test, predictions))
    print("Classification report:")
    print(classification_report(y_test, predictions, zero_division=0))


def main():
    """Load data, train both models, and save the final pipeline."""
    project_directory = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(
        project_directory,
        "data",
        "training_data.csv",
    )
    models_directory = os.path.join(project_directory, "models")
    model_path = os.path.join(models_directory, "conflict_model.pkl")
    feature_columns_path = os.path.join(
        models_directory,
        "feature_columns.json",
    )

    data = pd.read_csv(dataset_path)
    print(f"Dataset shape: {data.shape}")
    print(
        "Label distribution: "
        f"{data[TARGET_COLUMN].value_counts().sort_index().to_dict()}"
    )
    if "decision" in data.columns:
        print(
            "Decision distribution: "
            f"{data['decision'].value_counts().to_dict()}"
        )

    columns_to_drop = [
        column
        for column in LEAKAGE_COLUMNS
        if column in data.columns
    ]
    features = data.drop(columns=columns_to_drop)
    target = data[TARGET_COLUMN]

    categorical_columns = [
        column
        for column in CATEGORICAL_CANDIDATES
        if column in features.columns
    ]
    numeric_columns = [
        column
        for column in features.columns
        if column not in categorical_columns
    ]

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=42,
        stratify=target,
    )

    decision_tree_pipeline = build_model_pipeline(
        DecisionTreeClassifier(
            max_depth=8,
            random_state=42,
        ),
        categorical_columns,
        numeric_columns,
    )
    decision_tree_pipeline.fit(x_train, y_train)
    evaluate_model(
        "Decision Tree",
        decision_tree_pipeline,
        x_test,
        y_test,
    )

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
    evaluate_model(
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
    }
    with open(
        feature_columns_path,
        "w",
        encoding="utf-8",
    ) as json_file:
        json.dump(feature_information, json_file, indent=2)

    sample = x_test.iloc[[0]]
    sample_prediction = int(random_forest_pipeline.predict(sample)[0])
    sample_probability = float(
        random_forest_pipeline.predict_proba(sample)[0][1]
    )

    print("\nSaved outputs")
    print("-" * 60)
    print(f"Saved model path: {model_path}")
    print(f"Saved feature columns path: {feature_columns_path}")
    print(
        "Sample prediction: "
        f"conflict_label={sample_prediction}, "
        f"conflict_probability={sample_probability:.4f}"
    )
    print(
        "High accuracy is expected because this is synthetic rule-labeled data. "
        "This result verifies the ML pipeline, not real-world clinical performance."
    )


if __name__ == "__main__":
    main()
