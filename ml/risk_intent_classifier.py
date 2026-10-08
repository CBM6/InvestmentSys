import csv
import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_recall_fscore_support,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data"/"risk_intent_cases.csv"

#These are 5 labels that the classifier will train
LABEL_COLUMN = [
     "valuation_risk",
     "business_risk",
     "portfolio_fit",
     "catalyst_research",
     "safety_sensitive_advice"
 ]

 #The CSV header needs to match this scheme
CSV_COLUMNS = [
     "id",
     "question",
     "language",
     "split",
]+LABEL_COLUMN

VALID_LANG = {"en","zh"}
VALID_SPLIT = {"train", "test"}
VALID_LABEL_VALUES = {"0", "1"}

def load_data():
    """Read the data file, validate it, and return cleaned rows"""

    cases = []

    with DATA_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != CSV_COLUMNS:
            raise ValueError(f"Invalid CSV columns. \n"
                             f"Expected {CSV_COLUMNS}\n "
                             f"Found {reader.fieldnames}")

        for row_number, raw_case in enumerate(reader,start = 2):
            # DictReader uses NONE when a row has missing or extra columns.
            if None in raw_case or any(raw_case.get(column) is None for column in CSV_COLUMNS):
                raise ValueError(f"Row {row_number} does not have exactly"
                                 f"{len(CSV_COLUMNS)} columns")
            cleaned_case = {}
            for column in CSV_COLUMNS:
                cleaned_case[column] = raw_case[column].strip()
            cases.append(cleaned_case)
    validate_cases(cases)
    return cases

def validate_cases(cases):

    if not cases:
        raise ValueError("The dataset is empty.")

    seen_ids = set()
    seen_questions = set()

    for row_number, case in enumerate(cases,start = 2):
        case_id = case["id"]
        question = case["question"]

        if not re.fullmatch(r"RI-\d{3}", case_id):
            raise ValueError(
                f"Row {row_number} has an invalid ID: {case_id}"
            )

        if case_id in seen_ids:
            raise ValueError(f"Duplicate ID found: {case_id}")
        seen_ids.add(case_id)

        if not question:
            raise ValueError(f"Row {row_number} has an empty question.")
        normalized_question = " ".join(question.lower().split())

        if normalized_question in seen_questions:
            raise ValueError(
                f"Duplicate question found in row {row_number}."
            )
        seen_questions.add(normalized_question)

        if case["language"] not in VALID_LANG:
            raise ValueError(
                f"{case_id} has an invalid language: {case['language']}"
            )

        if case["split"] not in VALID_SPLIT:
            raise ValueError(
                f"{case_id} has an invalid split: {case['split']}"
            )

        for label in LABEL_COLUMN:
            if case[label] not in VALID_LABEL_VALUES:
                raise ValueError(
                    f"{case_id} has an invalid value for {label}: "
                    f"{case[label]}"
                )

def get_active_labels(values):
    """Return active labels or the derived general-research fallback."""

    active_labels = [label for label, value in zip(LABEL_COLUMN, values) if value == 1]

    return active_labels or ["general_research"]

def main():
    """Load the dataset, train the classifier, and run test predictions."""

    cases = load_data()
    train_cases = [case for case in cases if case["split"] == "train"]
    test_cases = [case for case in cases if case["split"] == "test"]

    if not train_cases or not test_cases:
        raise ValueError("Training and test data are both required.")

    x_train = [case["question"] for case in train_cases]
    x_test = [case["question"] for case in test_cases]

    y_train = []
    for case in train_cases:
        casetemp = []
        for label in LABEL_COLUMN:
            casetemp.append(int(case[label]))
        y_train.append(casetemp)

    y_test = []
    for case in test_cases:
        casetemp = []
        for label in LABEL_COLUMN:
            casetemp.append(int(case[label]))
        y_test.append(casetemp)

    model = Pipeline([("tfidf", TfidfVectorizer(analyzer = "char",ngram_range=(2,5))),("classifier",OneVsRestClassifier(LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)))])

    model.fit(x_train,y_train)

    y_pred = model.predict(x_test)

    # Measure performance across all label decisions.
    micro_f1 = f1_score(y_test, y_pred, average="micro",zero_division=0)
    macro_f1 = f1_score(y_test, y_pred, average="macro",zero_division=0)

    #exact match requires all five labels for a case to be correct
    exact_match = accuracy_score(y_test,y_pred)
    #Calculate seperate scores for each trained label
    precision, recall, per_label_f1, _= precision_recall_fscore_support(y_test,y_pred,average=None, zero_division=0)

    print(f"Micro F1: {micro_f1:.3f}")
    print(f"Macro F1: {macro_f1:.3f}")
    print(f"Exact-match accuracy: {exact_match:.3f}")

    for index, label in enumerate(LABEL_COLUMN):
        print(
            f"{label}: "
            f"precision={precision[index]:.3f}, "
            f"recall={recall[index]:.3f}, "
            f"f1={per_label_f1[index]:.3f}"
        )
    #collect incorrect predictions for manual review
    failure_cases = []
    for case, expected, predicted in zip(test_cases,y_test,y_pred):
        predicted_values = predicted.tolist()

        if expected != predicted_values:
            failure_cases.append({
                "id": case["id"],
                "question": case["question"],
                "expected": get_active_labels(expected),
                "predicted": get_active_labels(predicted_values),
            })

    print(f"\nFailure cases: {len(failure_cases)}")

    for failure in failure_cases:
        print(f"\n{failure['id']}: {failure['question']}")
        print(f"Expected: {', '.join(failure['expected'])}")
        print(f"Predicted: {', '.join(failure['predicted'])}")


if __name__ == "__main__":
    main()





