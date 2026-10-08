# Risk Intent Labeling Guide

## Guide Version

- `label_guide_version`: `2.0.0-pilot.1`
- Status: frozen initial candidate for the Phase 7.e V2 Data Pilot discovery review.
- This version applies to V2 pilot eligibility and labeling. It does not alter
  the frozen V1 questions, labels, splits, hash, or evaluation evidence.

## Classification Contract

- Input is the current question text.
- Assign the five trained binary labels independently:
  `valuation_risk`, `business_risk`, `portfolio_fit`,
  `catalyst_research`, and `safety_sensitive_advice`.
- Derive `general_research` only when the candidate is eligible and all five
  trained labels are `0`. It is not a trained or stored sixth label.
- The labels support routing and analysis assistance. In particular,
  `safety_sensitive_advice` never authorizes the App to choose or prescribe a
  trade and must never be the App's only safety control.

## Candidate Eligibility

Accept a candidate only when both conditions below pass:

1. It is an in-scope investment-research question concerning research,
   explanation, evidence, risk, events, valuation, or portfolio analysis for a
   security, issuer, sector, market event, or investment exposure.
2. Its current text is self-contained enough to decide all five labels. It does
   not need to name a ticker or contain enough facts to answer the question.

Reject the candidate when:

- it is primarily about personal tax filing, insurance, retirement-account
  administration, budgeting or debt, broker/software recommendations, or
  unrelated personal finance;
- a material requested output is out of scope and cannot be separated without
  rewriting the question;
- an unresolved reference or prior-turn dependency could change any label.

Incidental out-of-scope background alone does not require rejection. Source
context may establish that a question belongs to the investment domain, but it
cannot supply missing label intent. Do not concatenate turns, rewrite the
question, or infer missing context. Eligibility is a review decision, not a new
label or core-dataset column.

## Global Semantic Rule

A thematic label is positive only when answering the question as asked requires
that analysis or requires verification or interpretation of an explicit
condition. A condition supplied only as an assumed premise or incidental
background does not create another label.

Do not label from keywords alone or infer hidden intent. Evaluate every label
independently. Multiple labels may be `1` when the requested analyses genuinely
co-occur; no label suppresses another valid label.

## Operational Label Rules

### `valuation_risk`

Set to `1` for intrinsic or fair value, valuation multiples, market-implied
assumptions, margin of safety, or overvaluation/undervaluation analysis.

A direction or price forecast and a neutral technical-indicator explanation are
not valuation by default. An event-specific forecast or interpretation may be
`catalyst_research`; a requested investment action adds
`safety_sensitive_advice`.

### `business_risk`

Set to `1` when the requested analysis concerns durable effects on operations,
revenue, margins, cash, debt, regulation, governance, execution, or competitive
position.

Do not infer business risk merely because an event sounds negative.

### `portfolio_fit`

Set to `1` when the requested analysis materially concerns concentration,
diversification, correlation, exposure, risk-profile compatibility, current
holdings, cash, or portfolio fit.

A descriptive exposure calculation or fit analysis is portfolio only. A
personalized prescription for an exact allocation, position size, or trade adds
`safety_sensitive_advice`. Merely mentioning an existing position is not
enough.

### `catalyst_research`

Set to `1` when the requested analysis requires event- or sentiment-specific
discovery, verification, chronology, monitoring, or interpretation.

Mere event mention or background is not enough. Apply both
`catalyst_research` and `business_risk` when the question explicitly asks how a
specific event could create a durable business effect.

### `safety_sensitive_advice`

Set to `1` only when the requested output asks the assistant to choose,
recommend, prescribe, or guarantee an investment action or outcome, including:

- whether or when to buy, sell, short, or hold;
- an entry or exit price;
- a prescriptive position or allocation size;
- a guaranteed investment outcome.

Neutral mention, calculation, or analysis of price, date, timing, shares,
exposure, or a forecast is not safety by itself. Safety may co-occur with any
thematic label that is materially requested. The label marks the need for safe
handling; it never authorizes giving the requested action.

## Review Procedure

1. Apply the eligibility gate.
2. Evaluate each trained label independently under the semantic rule.
3. For an eligible all-zero result, derive `general_research`.
4. A Train/Validation reviewer may recommend `revise` or `reject`; a second
   review is not required merely because one reviewer sees ambiguity.
5. When submitted reviews disagree, use the approved adjudication process.
6. Reject any unresolved candidate. It never enters an accepted core CSV.

## Bilingual Consistency

Apply every rule by meaning and identically in English and Chinese. Keywords do
not determine labels. True translations or materially equivalent questions
must receive the same labels and remain in one
`scenario_equivalence_group_id`.

## Examples

- `What fair value does this DCF imply?` -> `valuation_risk` only.
- `What limit price should I use to buy tomorrow?` ->
  `safety_sensitive_advice` only.
- `Should I buy before earnings?` -> `catalyst_research` plus
  `safety_sensitive_advice`.
- `Explain RSI.` -> eligible all-zero derived `general_research`.
- `When was the investigation announced?` -> `catalyst_research` only.
- `How could the investigation affect its license and margins?` ->
  `catalyst_research` plus `business_risk`.
- `How dependent is it on one supplier?` -> `business_risk` only.
- `If I invest $1,000, what would my portfolio weight be?` ->
  `portfolio_fit` only.
- `How much should I allocate?` -> `portfolio_fit` plus
  `safety_sensitive_advice`.
- `Should I sell half to reduce concentration?` -> `portfolio_fit` plus
  `safety_sensitive_advice`.
- `What about the second one?` and `Does that change your answer?` -> reject
  when prior context is required.
- `Should I sell it now?` -> accept as `safety_sensitive_advice` only when the
  investment domain is independently established and the text itself is enough
  to determine safety. Source context may establish the domain only; it cannot
  create another label.

## Frozen V1 Dataset Conventions

- language: `en` or `zh`
- split: `train` or `test`
- trained-label values: `0` or `1`
- a question may have more than one trained label set to `1`
- similar questions and translated versions stay in the same split to prevent
  leakage

## Step 1F Expansion Protocol

### Immutable Baseline

- Preserve `RI-001` through `RI-024` unchanged during Step 1F.
- A genuine correction to an accepted question, label, or split requires a separate documented review. Model output alone is not a reason to relabel or move a case.

### Batch Plan

Add 96 cases in eight human-reviewed batches of 12:

| Batch | IDs | EN Train | EN Test | ZH Train | ZH Test |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | `RI-025`-`RI-036` | 5 | 1 | 5 | 1 |
| 2 | `RI-037`-`RI-048` | 4 | 2 | 4 | 2 |
| 3 | `RI-049`-`RI-060` | 5 | 1 | 5 | 1 |
| 4 | `RI-061`-`RI-072` | 4 | 2 | 4 | 2 |
| 5 | `RI-073`-`RI-084` | 5 | 1 | 5 | 1 |
| 6 | `RI-085`-`RI-096` | 4 | 2 | 4 | 2 |
| 7 | `RI-097`-`RI-108` | 5 | 1 | 5 | 1 |
| 8 | `RI-109`-`RI-120` | 4 | 2 | 4 | 2 |

Each batch contains exactly six English and six Chinese questions. The completed 120-case dataset contains 90 train and 30 test cases, with 45 English and 45 Chinese train cases and 15 English and 15 Chinese test cases.

### Expansion Progress

- Batch 1 (`RI-025`-`RI-036`): Accepted. It contains 5 EN train, 1 EN test, 5 ZH train, and 1 ZH test case; its composition is 6 single-label, 5 multi-label, and 1 all-zero hard negative.
- Batch 2 (`RI-037`-`RI-048`): Accepted. It contains 4 EN train, 2 EN test, 4 ZH train, and 2 ZH test cases; its composition is 4 single-label, 6 multi-label, and 2 all-zero hard negatives.
- Batch 3 (`RI-049`-`RI-060`): Accepted. It contains 5 EN train, 1 EN test, 5 ZH train, and 1 ZH test case; its composition is 4 single-label, 5 multi-label, and 3 all-zero hard negatives.
- Batch 4 (`RI-061`-`RI-072`): Accepted. It contains 4 EN train, 2 EN test, 4 ZH train, and 2 ZH test cases; its composition is 5 single-label, 5 multi-label, and 2 all-zero hard negatives.
- Batch 4 provenance: the user explicitly authorized the complete batch; the programming thread authored and inserted the rows, and the planning thread independently reviewed every question and label. The user did not review each row before insertion.
- Batch 5 (`RI-073`-`RI-084`): Accepted. It contains 5 EN train, 1 EN test, 5 ZH train, and 1 ZH test case; its composition is 5 single-label, 5 multi-label, and 2 all-zero hard negatives.
- Batch 5 provenance: the user explicitly authorized the complete batch; the programming thread authored and inserted the rows, and the planning thread independently reviewed every question and label. The user did not review each row before insertion.
- Batch 6 (`RI-085`-`RI-096`): Accepted. It contains 4 EN train, 2 EN test, 4 ZH train, and 2 ZH test cases; its composition is 4 single-label, 6 multi-label, and 2 all-zero hard negatives.
- Batch 6 provenance: the user explicitly authorized the complete batch; the programming thread authored and inserted the rows, and the planning thread independently reviewed every question and label. The user did not review each row before insertion.
- Batch 7 (`RI-097`-`RI-108`): Accepted. It contains 5 EN train, 1 EN test, 5 ZH train, and 1 ZH test case; its composition is 5 single-label, 5 multi-label, and 2 all-zero hard negatives.
- Batch 7 provenance: the user explicitly authorized the complete batch; the programming thread authored and inserted the rows, and the planning thread independently reviewed every question and label. The user did not review each row before insertion.
- Batch 8 (`RI-109`-`RI-120`): Accepted. It contains 4 EN train, 2 EN test, 4 ZH train, and 2 ZH test cases; its composition is 4 single-label, 6 multi-label, and 2 all-zero hard negatives.
- Batch 8 provenance: the user explicitly authorized the complete batch; the programming thread authored and inserted the rows, and the planning thread independently reviewed every question and label. The user did not review each row before insertion.
- Final dataset: 120 cases, with 90 train and 30 test; train contains 45 English / 45 Chinese and test contains 15 English / 15 Chinese.
- The classifier was not run during Batch 1 through Batch 8 acceptance, so the holdout remained unexamined by model output throughout expansion.

Current cumulative coverage:

| Target | Train EN | Train ZH | Test EN | Test ZH |
| --- | ---: | ---: | ---: | ---: |
| `valuation_risk` | 11 | 13 | 5 | 4 |
| `business_risk` | 13 | 15 | 8 | 7 |
| `portfolio_fit` | 11 | 12 | 6 | 8 |
| `catalyst_research` | 10 | 13 | 8 | 7 |
| `safety_sensitive_advice` | 11 | 9 | 4 | 6 |
| all-zero fallback | 7 | 7 | 2 | 2 |

All approved per-label, per-language, split, and all-zero coverage floors are met. Step 1F has reached the fixed 120-case evidence boundary.

### Final Dataset Freeze

- `RI-001` through `RI-120`, their questions, languages, splits, and five trained labels are frozen.
- Final split is 90 train / 30 test, with 45 English / 45 Chinese train and 15 English / 15 Chinese test cases.
- Frozen CSV SHA-256: `f7cff30cb80aca1b738d6bd28202efd28cfc3530bd663c84906eae63822caadc`.
- A genuine correction now requires separate user-approved unfreezing, documented justification, complete acceptance rechecks, and a new hash.
- Classifier output must never be used to revise the frozen test questions, labels, or splits.
- The user executed one authorized classifier run against the frozen 120-case dataset on 2026-07-24.
- The post-run hash remained unchanged, and `docs/RISK_INTENT_EVALUATION.md` records the reviewed result.
- Do not repeat the run, tune the baseline, relabel cases, or change the frozen dataset without a new explicit user decision.

### Batch Composition

Each 12-case batch must include at least:

- four single-label questions;
- three realistic multi-label questions;
- one all-zero `general_research` hard negative;
- varied financial wording, including wording not already present in the accepted dataset.

Use the remaining cases to close cumulative language, split, label, fallback, or wording-coverage gaps. Do not force an implausible label combination merely to satisfy a count.

### Final Coverage Floors

Before Step 1F can be marked complete:

- Each trained label must have at least 18 positive train cases and 6 positive test cases.
- For each trained label, train positives must include at least 9 English and 9 Chinese cases.
- For each trained label, test positives must include at least 3 English and 3 Chinese cases.
- The all-zero fallback must have at least 8 train cases, including at least 4 per language.
- The all-zero fallback must have at least 4 test cases, including at least 2 per language.

These are coverage floors for a controlled baseline dataset. They do not estimate real-world intent prevalence and do not by themselves establish statistical power or production quality.

### Batch Acceptance

Before accepting each batch:

- Review every label manually against this guide.
- Assign and review the fixed split before looking at classifier predictions.
- Validate the exact schema, sequential IDs, allowed values, and non-empty questions.
- Reject normalized exact duplicates.
- Review cross-split text similarity and manually check translations or substantially equivalent questions; equivalent questions must remain in the same split regardless of a string-similarity score.
- For reproducible same-language `SequenceMatcher` screening, pass the test question as the first sequence and the train question as the second. Treat the score as a manual-review flag, not an automatic rejection threshold.
- Update cumulative split, language, per-label positive, multi-label, and all-zero coverage counts.

Use data validation during batch construction. Do not use full-model test output to revise accepted test questions, labels, or splits. The one approved full-classifier run occurred only after all 120 cases and the final split were frozen.

### Authorization Boundary

Approval of this protocol did not authorize automatic question generation, automatic labeling, relabeling of accepted cases, model tuning, or CSV changes. Each completed implementation batch required explicit user authorization.

Completion of Step 1F did not authorize classifier execution. The user later authorized and executed one frozen-120 run. That authorization is exhausted and does not authorize a rerun, tuning, relabeling, or dataset changes.
