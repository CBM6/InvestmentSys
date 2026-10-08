# Phase 7.c Risk-Intent Baseline Evaluation

## Purpose

This document records two Phase 7.c evidence stages for the offline multi-label
risk-intent classifier:

1. the original 24-case pipeline-validation run; and
2. the one authorized run against the frozen 120-case dataset and 30-case
   holdout.

The 24-case stage verifies that the project can load and validate the dataset,
train the approved baseline, predict fixed test cases, calculate the approved
metrics, derive the `general_research` fallback, and expose failed predictions
for review.

The frozen-120 stage evaluates the unchanged baseline once on a larger
leakage-controlled holdout. It provides honest baseline evidence for this fixed
dataset, but it does not establish generalization or production readiness.

## 24-Case Pipeline-Validation Setup

- Run date: 2026-07-24
- Dataset: `data/risk_intent_cases.csv`
- Total cases: 24
- Training cases: 18
- Test cases: 6
- Languages: English and Chinese
- Input: question text only
- Trained labels:
  - `valuation_risk`
  - `business_risk`
  - `portfolio_fit`
  - `catalyst_research`
  - `safety_sensitive_advice`
- Derived fallback: `general_research`
- Text features: character n-gram TF-IDF, range 2-5
- Classifier: One-vs-Rest Logistic Regression

## 24-Case Run Command

```bash
.venv/bin/python -m ml.risk_intent_classifier
```

The command completed successfully with exit code `0`.

## 24-Case Verified Metrics

| Metric | Result |
| --- | ---: |
| Micro F1 | 0.615 |
| Macro F1 | 0.567 |
| Exact-match accuracy | 0.333 |

### Per-Label Results

| Label | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| `valuation_risk` | 0.000 | 0.000 | 0.000 |
| `business_risk` | 0.500 | 1.000 | 0.667 |
| `portfolio_fit` | 1.000 | 1.000 | 1.000 |
| `catalyst_research` | 0.500 | 0.500 | 0.500 |
| `safety_sensitive_advice` | 0.500 | 1.000 | 0.667 |

These values are recorded as pipeline output only. They must not be presented
as evidence that the classifier performs well.

## Failure-Case Summary

The fixed test run produced four failed cases:

| Case | Expected | Predicted | Error Type |
| --- | --- | --- | --- |
| `RI-019` | `valuation_risk` | `business_risk` | Missed valuation label and added business label |
| `RI-020` | `business_risk` | `business_risk`, `safety_sensitive_advice` | Extra safety label |
| `RI-021` | `portfolio_fit` | `portfolio_fit`, `catalyst_research` | Extra catalyst label |
| `RI-022` | `catalyst_research` | `general_research` | Missed catalyst label; all-zero fallback derived |

`RI-023` and `RI-024` were exact matches and therefore did not appear in the
failure output.

## Failure Analysis

### RI-019: Valuation Language Was Not Recognized

Question:

> How sensitive is the company's estimated fair value to changes in the
> discount rate?

The expected label is `valuation_risk`, but the model predicted
`business_risk`.

The expected label is not meaningfully ambiguous. Fair value and discount-rate
sensitivity are valuation concepts. However, the small training set expresses
valuation mainly through words such as "overvalued," "valuation," and
"multiples." It does not contain the phrases "discount rate" or "estimated fair
value."

Character n-grams can recognize repeated character patterns, but they do not
understand that unseen phrases may be financial synonyms for valuation
concepts. With only 18 training cases, there is not enough lexical coverage to
bridge that gap. This result is consistent with a character-feature limitation
combined with a tiny-sample effect. It does not justify changing the expected
label.

### RI-020: Business Risk Received an Extra Safety Label

Question:

> 供应商依赖和出口限制可能怎样影响公司的长期经营？

The expected `business_risk` label was found, but the model also predicted
`safety_sensitive_advice`.

The question asks for analysis of operating risk and does not request a buy,
sell, short, all-in, or guaranteed-return instruction. The safety prediction is
therefore a false positive rather than a labeling ambiguity.

One likely contributor is the training composition. `RI-016` combines
`business_risk` and `safety_sensitive_advice` and contains a similar Chinese
pattern about how an external risk may affect the company. In a very small
character-based dataset, shared wording can become associated with both labels,
even when the direct trading-advice portion is absent from the test question.

This is a multi-label decision error amplified by limited and correlated
training examples. The current run does not isolate the exact feature weights,
so this explanation remains a supported hypothesis rather than a proven causal
attribution.

### RI-021: Portfolio Fit Received an Extra Catalyst Label

Question:

> Would a non-dividend growth stock fit a portfolio designed to produce stable
> income?

The expected `portfolio_fit` label was found, but the model also predicted
`catalyst_research`.

The question is about portfolio objective and suitability. It does not ask
about an event, product launch, earnings release, news item, or sentiment
signal, so the catalyst prediction is a false positive.

The training set contains `RI-017`, which combines `portfolio_fit` and
`catalyst_research` in a question that also uses the words "stock" and
"portfolio." With few examples, the independent catalyst classifier may learn
an overly broad association from those shared character sequences. This is
another likely interaction between tiny-sample effects, character features, and
co-occurring labels.

The perfect `portfolio_fit` score in this run is based on only one positive
test case. It proves that this case's portfolio label was recognized, not that
the portfolio classifier generalizes reliably.

### RI-022: A Catalyst Was Reduced to General Research

Question:

> 并购获批或大客户合同落地可能如何改变未来几个季度的预期？

The expected label is `catalyst_research`. The model predicted no trained
labels, so the program correctly derived `general_research`.

The fallback logic worked as designed, but the underlying prediction was
incorrect. An acquisition approval or major customer contract is a potential
catalyst. The Chinese catalyst examples in the training set focus mostly on
earnings, guidance, and related wording. The test question introduces different
catalyst vocabulary that the character n-gram baseline did not connect to the
same intent.

This is primarily a catalyst false negative consistent with missing lexical
coverage and the small bilingual sample. It also demonstrates an important
boundary: correct fallback logic cannot repair an incorrect all-zero prediction.

## Cross-Case Findings

### Data Ambiguity

No automatic relabeling is justified by these four failures:

- `RI-019` is a valuation question.
- `RI-020` is a business-risk question without a direct trading request.
- `RI-021` is a portfolio-fit question without a catalyst request.
- `RI-022` is a catalyst question.

Some investment questions can legitimately be multi-label, but the observed
extra and missing labels are better explained by model and data limitations
than by clearly incorrect ground truth.

### Tiny-Sample Effects

The model trained on only 18 cases and was tested on only 6. Each test label has
one positive example except `catalyst_research`, which has two. A single
prediction can therefore change a per-label score substantially.

The bilingual design further divides the already small lexical evidence between
English and Chinese. These results are too unstable for model comparison,
generalization claims, or product decisions.

### Character-Feature Limitations

Character n-grams provide a simple tokenizer-free baseline for English and
Chinese, but they learn surface character patterns rather than financial
meaning. They do not inherently know that:

- "discount rate" is related to valuation;
- a customer contract may be a catalyst;
- portfolio wording does not automatically imply a catalyst;
- operating-risk wording does not automatically request trading advice.

English and Chinese can pass through the same pipeline, but the model does not
automatically learn semantic equivalence across the two writing systems.

### Multi-Label Decision Errors

One-vs-Rest trains five independent binary classifiers. Each label can be
predicted without considering whether another label has already been selected.
That design supports genuine multi-label questions, but it also permits:

- extra labels, as seen in `RI-020` and `RI-021`;
- missing labels, as seen in `RI-019` and `RI-022`;
- an all-zero result that triggers `general_research`.

This run used the approved default decision behavior. It did not tune
thresholds or add label-dependency rules.

## Metric Interpretation

- Micro F1 `0.615` summarizes positive-label decisions across the complete
  test matrix, but it comes from only six questions.
- Macro F1 `0.567` gives each trained label equal weight and is reduced by the
  complete miss on `valuation_risk`.
- Exact-match accuracy `0.333` means only two of six questions had all five
  label decisions correct.
- `valuation_risk` scoring `0.000` means the sole valuation-positive test case
  was missed. It does not prove that the classifier can never recognize
  valuation questions.
- `portfolio_fit` scoring `1.000` is based on one positive test case and must
  not be described as perfect general performance.

## Limitations

- The dataset has only 24 hand-labeled cases.
- The test set contains only 6 cases.
- Most labels have only one positive test example.
- The run uses one fixed split and no cross-validation.
- No external or independently collected evaluation set is used.
- No threshold tuning, probability calibration, feature comparison, or model
  comparison was performed.
- The classifier is not integrated into the App.
- The classifier is not a stock predictor or trading-signal model.

## Pipeline Verdict

The Phase 7.c pipeline validation passed:

- the fixed CSV was loaded and validated;
- train and test cases were separated;
- the offline classifier trained successfully;
- predictions used the fixed test set;
- all approved metrics were calculated;
- `general_research` was derived only from an all-zero label result;
- failed predictions were exposed with expected and predicted labels.

The run proves that the offline evaluation pipeline executes end to end. It
does not prove that the classifier is accurate, useful in production, or able
to generalize.

The approved next data milestone was at least 120 leakage-controlled bilingual
cases before reviewing classifier performance. No data, labels, features,
thresholds, or model parameters were changed during Step 1E.

## Frozen-120 Holdout Evaluation

### Setup And Provenance

- Run date: 2026-07-24
- Dataset: `data/risk_intent_cases.csv`
- Frozen CSV SHA-256:
  `f7cff30cb80aca1b738d6bd28202efd28cfc3530bd663c84906eae63822caadc`
- Total cases: 120
- Training cases: 90
- Test cases: 30
- Training-language split: 45 English / 45 Chinese
- Test-language split: 15 English / 15 Chinese
- Input, features, classifier, labels, and fallback: unchanged from the
  approved Phase 7.c contract
- Execution count: one authorized frozen-120 run

The user executed the run in PyCharm. The Programmer thread read and captured
the terminal output and rechecked the frozen CSV hash after execution. The
Planner thread then independently rechecked the hash and recomputed the
reported metrics from the frozen expected labels and captured predictions. The
Planner did not rerun the classifier.

No question, label, language, split, feature, threshold, model parameter, App
behavior, OpenAI flow, report flow, or retrieval behavior changed before or
after this evaluation.

### Run Command

```text
/Users/chenboma/Documents/InvestmentSys/.venv/bin/python /Users/chenboma/Documents/InvestmentSys/ml/risk_intent_classifier.py
```

The command completed successfully with exit code `0`.

### Verified Metrics

| Metric | Result |
| --- | ---: |
| Micro F1 | 0.476 |
| Macro F1 | 0.478 |
| Exact-match accuracy | 0.233 |
| Exact matches | 7 / 30 |
| Failure cases | 23 / 30 |

### Per-Label Results

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `valuation_risk` | 4 | 0 | 5 | 1.000 | 0.444 | 0.615 |
| `business_risk` | 2 | 0 | 13 | 1.000 | 0.133 | 0.235 |
| `portfolio_fit` | 5 | 0 | 9 | 1.000 | 0.357 | 0.526 |
| `catalyst_research` | 2 | 0 | 13 | 1.000 | 0.133 | 0.235 |
| `safety_sensitive_advice` | 7 | 1 | 3 | 0.875 | 0.700 | 0.778 |

The exact-match cases were `RI-020`, `RI-021`, `RI-023`, `RI-024`, `RI-041`,
`RI-047`, and `RI-054`.

### Failure-Case Summary

| Case | Expected | Predicted |
| --- | --- | --- |
| `RI-019` | `valuation_risk` | `general_research` |
| `RI-022` | `catalyst_research` | `general_research` |
| `RI-030` | `business_risk`, `portfolio_fit`, `safety_sensitive_advice` | `general_research` |
| `RI-036` | `valuation_risk`, `portfolio_fit`, `safety_sensitive_advice` | `valuation_risk` |
| `RI-042` | `valuation_risk`, `business_risk`, `catalyst_research` | `general_research` |
| `RI-048` | `business_risk`, `portfolio_fit`, `catalyst_research`, `safety_sensitive_advice` | `safety_sensitive_advice` |
| `RI-060` | `valuation_risk`, `business_risk`, `portfolio_fit`, `catalyst_research` | `valuation_risk` |
| `RI-065` | `valuation_risk`, `business_risk`, `portfolio_fit` | `general_research` |
| `RI-066` | `business_risk`, `catalyst_research`, `safety_sensitive_advice` | `catalyst_research`, `safety_sensitive_advice` |
| `RI-071` | `valuation_risk` | `general_research` |
| `RI-072` | `safety_sensitive_advice` | `general_research` |
| `RI-078` | `valuation_risk`, `business_risk`, `catalyst_research` | `general_research` |
| `RI-084` | `valuation_risk`, `business_risk`, `safety_sensitive_advice` | `valuation_risk`, `safety_sensitive_advice` |
| `RI-089` | `portfolio_fit`, `catalyst_research` | `portfolio_fit` |
| `RI-090` | `valuation_risk`, `business_risk`, `catalyst_research` | `valuation_risk` |
| `RI-095` | `portfolio_fit`, `catalyst_research` | `portfolio_fit` |
| `RI-096` | `business_risk`, `portfolio_fit`, `safety_sensitive_advice` | `safety_sensitive_advice` |
| `RI-102` | `business_risk`, `portfolio_fit`, `catalyst_research` | `portfolio_fit`, `safety_sensitive_advice` |
| `RI-108` | `business_risk`, `portfolio_fit`, `catalyst_research`, `safety_sensitive_advice` | `safety_sensitive_advice` |
| `RI-113` | `business_risk`, `catalyst_research` | `business_risk` |
| `RI-114` | `portfolio_fit`, `safety_sensitive_advice` | `safety_sensitive_advice` |
| `RI-119` | `business_risk`, `portfolio_fit`, `catalyst_research` | `portfolio_fit` |
| `RI-120` | `portfolio_fit`, `catalyst_research` | `general_research` |

### Review Findings

The pipeline remained operational, but baseline quality on the frozen holdout
is weak.

- High precision with low recall shows a conservative classifier that usually
  avoids false-positive labels but misses many true labels.
- `business_risk` and `catalyst_research` each recall only 2 of 15 positive
  test labels.
- Nine failed cases collapsed to an all-zero prediction and therefore derived
  `general_research`; correct fallback mechanics cannot repair missed intent
  labels.
- Exact-match accuracy by expected label count was 4/4 for all-zero hard
  negatives, 2/6 for single-label cases, and 1/20 for multi-label cases.
- The baseline therefore handles explicit negative/fallback cases better than
  realistic multi-intent questions.
- `safety_sensitive_advice` is the strongest label, but three safety-positive
  cases were missed and `RI-102` received one false-positive safety label.
  This is not reliable enough for safety enforcement or App integration.

The result does not justify changing the frozen labels. The dominant pattern is
underprediction by the approved baseline, especially on multi-label questions,
not evidence that the holdout contract is wrong.

### Limitations

- This is one fixed 30-case holdout, not repeated cross-validation or an
  external benchmark.
- The dataset is deliberately coverage-balanced and does not estimate
  real-world intent prevalence.
- Character n-grams model surface form rather than financial semantics.
- The experiment did not inspect probabilities, feature weights, calibration,
  or alternative thresholds.
- No tuning or model comparison was allowed after holdout inspection.

### Frozen-120 Verdict

The frozen-120 experiment is complete and reproducible enough to support a
narrow conclusion:

```text
The approved traditional-ML baseline runs end to end, but its frozen-holdout
recall and multi-label exact-match performance are too weak for App integration.
```

This is a useful negative result. It demonstrates dataset design, holdout
control, offline model training, multi-label evaluation, and honest failure
analysis without overstating model capability.

Phase 7.c is complete after this Review/Document checkpoint. Completion does
not authorize another classifier run, tuning, relabeling, dataset changes, App
integration, Phase 7.d, or Phase 8 implementation.
