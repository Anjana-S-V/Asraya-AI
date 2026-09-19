import pandas as pd
import numpy as np

from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------

INPUT_PATH = Path(
    "data/kerala_ml_dataset.csv"
)

MODEL_OUTPUT = Path(
    "models"
)

TEST_START = pd.Timestamp("2020-01-01")


FEATURES = [
    "Rainfall_1d",
    "Rainfall_3d",
    "Rainfall_7d",
    "Rainfall_30d",
    "Rainfall_3d_max",
    "Rainfall_7d_max",
]

TARGET = "Flood_Tomorrow"


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

print("Loading ML dataset...")

df = pd.read_csv(INPUT_PATH)

df["Date"] = pd.to_datetime(df["Date"])

df = df.sort_values(
    "Date"
).reset_index(drop=True)


# --------------------------------------------------
# Time-based split
# --------------------------------------------------

train = df[
    df["Date"] < TEST_START
].copy()

test = df[
    df["Date"] >= TEST_START
].copy()


print("\n======================================")
print("DATA SPLIT")
print("======================================")

print(
    "Training period:",
    train["Date"].min(),
    "to",
    train["Date"].max()
)

print(
    "Testing period:",
    test["Date"].min(),
    "to",
    test["Date"].max()
)

print("\nTraining shape:", train.shape)
print("Testing shape:", test.shape)


# --------------------------------------------------
# Features and target
# --------------------------------------------------

X_train = train[FEATURES]
y_train = train[TARGET]

X_test = test[FEATURES]
y_test = test[TARGET]


print("\nTraining target distribution:")
print(y_train.value_counts())

print("\nTesting target distribution:")
print(y_test.value_counts())


# --------------------------------------------------
# Evaluation function
# --------------------------------------------------

def evaluate_model(name, model):

    print("\n")
    print("======================================")
    print(name)
    print("======================================")

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    # Standard threshold metrics
    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities
    )

    pr_auc = average_precision_score(
        y_test,
        probabilities
    )

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            digits=4,
            zero_division=0
        )
    )

    print("Confusion matrix:")
    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )

    print("\nMetrics:")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc_auc:.4f}")
    print(f"PR-AUC    : {pr_auc:.4f}")

    return model, probabilities


# --------------------------------------------------
# Model 1: Logistic Regression
# --------------------------------------------------

logistic_model = Pipeline(
    [
        (
            "scaler",
            StandardScaler()
        ),
        (
            "classifier",
            LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
                random_state=42
            )
        ),
    ]
)


logistic_model, logistic_probabilities = evaluate_model(
    "LOGISTIC REGRESSION",
    logistic_model
)


# --------------------------------------------------
# Model 2: Random Forest
# --------------------------------------------------

random_forest = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=5,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)


random_forest, rf_probabilities = evaluate_model(
    "RANDOM FOREST",
    random_forest
)


# --------------------------------------------------
# Random Forest feature importance
# --------------------------------------------------

importance = pd.DataFrame(
    {
        "Feature": FEATURES,
        "Importance": random_forest.feature_importances_,
    }
).sort_values(
    "Importance",
    ascending=False
)


print("\n======================================")
print("RANDOM FOREST FEATURE IMPORTANCE")
print("======================================")

print(importance.to_string(index=False))


# --------------------------------------------------
# Save feature importance
# --------------------------------------------------

MODEL_OUTPUT.mkdir(
    parents=True,
    exist_ok=True
)

importance.to_csv(
    MODEL_OUTPUT / "feature_importance.csv",
    index=False
)


# --------------------------------------------------
# Save test predictions
# --------------------------------------------------

results = test[
    [
        "Date",
        "District",
        TARGET,
    ]
].copy()

results["Logistic_Probability"] = (
    logistic_probabilities
)

results["RandomForest_Probability"] = (
    rf_probabilities
)

results.to_csv(
    MODEL_OUTPUT / "test_predictions.csv",
    index=False
)


# --------------------------------------------------
# Final message
# --------------------------------------------------

print("\n======================================")
print("MODEL TRAINING COMPLETED")
print("======================================")

print(
    "Saved feature importance to:",
    MODEL_OUTPUT / "feature_importance.csv"
)

print(
    "Saved predictions to:",
    MODEL_OUTPUT / "test_predictions.csv"
)