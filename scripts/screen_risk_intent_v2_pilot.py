import argparse
import html
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, deque
from datetime import datetime, timezone
from html.parser import HTMLParser

from prepare_risk_intent_v2_pilot import (
    BIZFIN_ROOT,
    MSE_MIN_DATE,
    MSE_REQUIRED_LICENSE,
    MSE_ROOT,
    PILOT_ROOT,
    load_manifest,
    verify_bizfin,
    verify_money_stackexchange,
)

CANDIDATES_FILE = PILOT_ROOT / "candidates.jsonl"
TERMS_CHECKED_AT = "2026-08-07"
MAX_SCREENED_PER_LANGUAGE = 60

MSE_RESEARCH_TAGS = {
    "asset-allocation",
    "corporate-acquisition",
    "corporate-earnings",
    "diversification",
    "earnings-per-share",
    "portfolio",
    "price-earnings-ratio",
    "rebalancing",
    "stock-analysis",
    "stock-valuation",
    "value-investing",
}

VIEW_TARGETS = {
    "natural": 12,
    "challenge": 8,
}

DISCOVERY_TARGETS = {
    "natural": 7,
    "challenge": 5,
}

# Decision 60: freeze these rules before resuming screening. Match a complete
# personal-administration request, never a topic or a sentence inside a case.
# There are no free-text slots: unaccounted-for context stays with the human.
OUT_OF_SCOPE_REQUEST_PATTERNS = {
    "personal_tax": (
        r"how (?:do|can|should) (?:i|we) (?:file|prepare|amend|submit) "
        r"(?:(?:my|our|a|the) )?(?:(?:personal|individual|income) )?"
        r"(?:tax returns?|taxes)(?: (?:online|after moving|this year))?",
        r"how much (?:(?:income|capital gains?|withholding|gift) )?tax(?:es)? "
        r"(?:do|will|would|should|must) (?:i|we) (?:owe|pay)"
        r"(?: on (?:gains from )?(?:my|our) "
        r"(?:etfs?|stocks?|shares?|funds?|bonds?))?",
        r"how (?:can|do|should) (?:i|we) "
        r"(?:calculate|reduce|avoid|minimi[sz]e) (?:(?:my|our) )?"
        r"(?:(?:income|capital gains?|withholding|gift) )?tax(?:es)?"
        r"(?: in (?:(?:my|our|a) )?(?:rrsp|tfsa|ira|roth ira|401k|401\(k\)))?",
        r"(?:what|which) (?:(?:income|capital gains?|withholding|gift) )?"
        r"tax(?:es)? (?:do|will|must) (?:i|we) (?:owe|pay)",
        r"what (?:(?:withholding|income|capital gains?) )?tax(?:es)? "
        r"(?:applies|apply) to (?:(?:my|our|a) )?"
        r"(?:rrsp|tfsa|ira|roth ira|401k|401\(k\))",
        r"what is the tax treatment of (?:(?:my|our) )?"
        r"(?:etfs?|stocks?|shares?|funds?|bonds?) in (?:(?:my|our|a) )?"
        r"(?:rrsp|tfsa|ira|roth ira|401k|401\(k\))",
        r"(?:我|我们)(?:应该|该|需要)?(?:如何|怎么|怎样)"
        r"(?:报税|申报个税|申请退税)",
        r"(?:我|我们)(?:卖出|出售|赎回)(?:股票|股份|etf|基金|债券)后"
        r"(?:要|需要|应该)?(?:交|缴)多少(?:资本利得|预扣|个人所得)?税",
        r"(?:我的|我们的)(?:rrsp|tfsa|ira|退休)账户(?:如何|怎么|怎样)"
        r"(?:减少|计算|避免)(?:预扣税|个人所得税|资本利得税)",
    ),
    "mortgage_or_home_finance": (
        r"(?:which|what) mortgage lender should (?:i|we) use"
        r"(?: for (?:(?:my|our|a) )?(?:home loan|mortgage))?",
        r"how (?:can|do|should) (?:i|we) "
        r"(?:apply for|qualify for|refinance|repay|pay off|pay down) "
        r"(?:(?:my|our|a) )?(?:mortgage|home loan|home equity loan|heloc)",
        r"should (?:i|we) (?:refinance|repay|pay off) "
        r"(?:my|our) (?:mortgage|home loan)",
        r"how (?:can|do|should) (?:i|we) (?:pay for|finance) "
        r"(?:my|our|my parents') (?:home|house) renovation",
        r"(?:我|我们)?(?:应该|该|需要)?(?:如何|怎么|怎样)"
        r"(?:申请|办理|偿还|提前还清)(?:房贷|按揭|住房贷款|装修贷款)",
    ),
    "personal_insurance": (
        r"(?:which|what) (?:life|health|car|auto|home|travel|disability) "
        r"insurance policy should (?:i|we) (?:choose|buy)",
        r"(?:can you |please )?recommend (?:a |an )?"
        r"(?:life|health|car|auto|home|travel|disability) insurance policy",
        r"(?:我|我们)(?:应该|该|需要)?(?:选择|买|购买)哪种"
        r"(?:寿险|医疗保险|车险|房屋保险|旅行保险)",
        r"请?推荐(?:一款|一个)?(?:寿险|医疗保险|车险|房屋保险|旅行保险)",
    ),
    "household_budget_or_debt": (
        r"how (?:can|do|should) (?:i|we) (?:make|create|build|manage|plan) "
        r"(?:a|my|our) (?:household budget|monthly budget)",
        r"how (?:can|do|should) (?:i|we) "
        r"(?:pay off|repay|pay down|consolidate) (?:my|our) "
        r"(?:credit card debt|student loans?|personal loans?)",
        r"(?:我|我们)?(?:应该|该|需要)?(?:如何|怎么|怎样)"
        r"(?:安排|制定|管理|规划)(?:家庭预算|生活费|应急金)",
        r"(?:我|我们)?(?:应该|该|需要)?(?:如何|怎么|怎样)"
        r"(?:偿还|还清|还掉)(?:信用卡欠款|助学贷款|个人贷款)",
    ),
    "retirement_account_administration": (
        r"how (?:can|do|should) (?:i|we) "
        r"(?:open|close|transfer|roll over|withdraw from|contribute to) "
        r"(?:my|our) (?:rrsp|tfsa|ira|roth ira|401k|401\(k\)|retirement account)"
        r"(?: to (?:another|a new) (?:provider|bank|broker))?",
        r"what is (?:my|our|the) "
        r"(?:rrsp|tfsa|ira|roth ira|401k|401\(k\)) contribution limit",
        r"(?:我|我们)?(?:应该|该|需要)?(?:如何|怎么|怎样)"
        r"(?:转移|关闭|开立)(?:我的|我们的)?"
        r"(?:退休账户|养老金账户|rrsp|tfsa|ira)",
        r"(?:我的|我们的)?(?:rrsp|tfsa|ira)(?:供款|缴款)上限是多少",
    ),
    "broker_or_software": (
        r"(?:which|what) broker has (?:the )?lowest fees for "
        r"(?:buying|selling) (?:stocks|shares|etfs|bonds)",
        r"(?:which|what) (?:broker|trading platform) should (?:i|we) use",
        r"(?:can you |please )?recommend (?:a |an |some )?"
        r"(?:brokers?|trading platforms?|charting software|"
        r"stock screeners?|investment apps?)",
        r"what is the best (?:charting software|stock screener|investment app)",
        r"请?推荐哪家券商(?:购买|买卖)(?:股票|基金|债券)",
        r"哪(?:个|种)(?:交易平台|炒股软件|选股软件|看盘软件)(?:比较)?好用",
    ),
}


def get_mse_non_admission_reason(raw_tags):
    # Match the entire attribute so unknown or malformed metadata cannot
    # accidentally qualify a question for the strict English queue.
    if not isinstance(raw_tags, str) or not re.fullmatch(
        r"(?:<[^<>\s]+>)+", raw_tags
    ):
        return "missing_or_malformed_tags"

    tags = set(re.findall(r"<([^<>\s]+)>", raw_tags))

    if not tags.issubset(MSE_RESEARCH_TAGS):
        return "outside_research_tags"

    return None


def get_prescreen_skip_reason(question):
    # Decision 60's full-request rules remain in use for Chinese only.
    text = " ".join(question.casefold().split())

    if text.endswith(("?", "？", ".", "。", "!", "！")):
        text = text[:-1].rstrip()

    # Full matching leaves every extra clause/background sentence unfiltered.
    for reason, patterns in OUT_OF_SCOPE_REQUEST_PATTERNS.items():
        for pattern in patterns:
            if re.fullmatch(pattern, text):
                return reason

    return None


def print_prescreen_summary(language, scanned_count, skipped_counts):
    skipped_total = sum(skipped_counts.values())

    if language == "en":
        print(
            f"EN metadata pre-screen this run: scanned {scanned_count}, "
            f"admitted {scanned_count - skipped_total}, "
            f"not admitted {skipped_total}."
        )
        print("Metadata admission is not human selection or verified relevance.")
    else:
        print(
            f"{language.upper()} pre-screen this run: "
            f"scanned {scanned_count}, rule-skipped {skipped_total}."
        )

    for reason, count in sorted(skipped_counts.items()):
        print(f"  {reason}: {count}")

    print("Unshown skips may be scanned again on resume; do not sum runs.")


class PlainTextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        if data.strip():
            self.parts.append(data)

    def get_text(self):
        return normalize_text(" ".join(self.parts))


def normalize_text(text):
    printable_text = "".join(
        character
        for character in text
        if character.isprintable() or character in "\n\t"
    )

    cleaned_lines = []

    for line in printable_text.splitlines():
        cleaned_line = " ".join(line.split())

        if cleaned_line:
            cleaned_lines.append(cleaned_line)

    return "\n".join(cleaned_lines)


def html_to_text(value):
    parser = PlainTextParser()
    parser.feed(value)
    parser.close()
    return parser.get_text()


def utc_now():
    current_time = datetime.now(timezone.utc)
    return current_time.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_candidate_records():
    records = []

    with CANDIDATES_FILE.open(mode="r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid candidate JSON on line {line_number}"
                ) from error

            if not isinstance(record, dict):
                raise ValueError(
                    f"Candidate line {line_number} is not a JSON object"
                )

            records.append(record)

    return records


def append_candidate_record(record):
    with CANDIDATES_FILE.open(mode="a", encoding="utf-8") as file:
        json.dump(record, file, ensure_ascii=False)
        file.write("\n")


def iter_mse_candidates():
    manifest = load_manifest(MSE_ROOT)

    posts_record = None

    for record in manifest["permitted_local_inputs"]:
        if record["path"].endswith("/Posts.xml"):
            posts_record = record
            break

    if posts_record is None:
        raise ValueError("Posts.xml is missing from permitted inputs")

    posts_path = MSE_ROOT / posts_record["path"]

    for _, element in ET.iterparse(posts_path, events=("end",)):
        candidate = None

        if element.tag == "row":
            fields = element.attrib

            correct_type = fields.get("PostTypeId") == "1"
            correct_date = (
                fields.get("CreationDate", "")[:10] >= MSE_MIN_DATE
            )
            correct_license = (
                fields.get("ContentLicense") == MSE_REQUIRED_LICENSE
            )

            if correct_type and correct_date and correct_license:
                title = normalize_text(
                    html.unescape(fields.get("Title", ""))
                )
                body = html_to_text(fields.get("Body", ""))

                if title and body:
                    source_item_id = fields.get("Id", "")
                    question = f"{title}\n\n{body}"

                    candidate = {
                        "question": question,
                        "source_tags": fields.get("Tags", ""),
                        "source_id": manifest["source_id"],
                        "source_revision": posts_record["sha256"],
                        "source_file": posts_record["path"],
                        "source_item_id": source_item_id,
                        "license_basis": fields["ContentLicense"],
                        "attribution": (
                            "https://money.stackexchange.com/questions/"
                            f"{source_item_id}"
                        ),
                        "transformation": "html_to_plain_text",
                    }

        element.clear()

        if candidate is not None:
            yield candidate


def iter_bizfin_file(file_record, manifest):
    file_path = BIZFIN_ROOT / file_record["path"]

    with file_path.open(mode="r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON in {file_path}, line {line_number}"
                ) from error

            messages = record.get("messages")

            if not isinstance(messages, list) or len(messages) != 1:
                continue

            message = messages[0]

            if (
                not isinstance(message, dict)
                or message.get("role") != "user"
            ):
                continue

            content_parts = message.get("content")

            if not isinstance(content_parts, list):
                continue

            text_parts = []

            for content_part in content_parts:
                if not isinstance(content_part, dict):
                    continue

                if content_part.get("type") != "text":
                    continue

                text = content_part.get("text")

                if isinstance(text, str) and text.strip():
                    text_parts.append(normalize_text(text))

            question = "\n".join(text_parts).strip()

            if not question:
                continue

            source_item_id = f"{file_record['path']}:{line_number}"

            yield {
                "question": question,
                "source_id": manifest["source_id"],
                "source_revision": manifest["revision"],
                "source_file": file_record["path"],
                "source_item_id": source_item_id,
                "license_basis": manifest["license_interpretation"],
                "attribution": (
                    "https://huggingface.co/datasets/"
                    f"{manifest['repository']}/tree/"
                    f"{manifest['revision']}/{file_record['path']}"
                ),
                "transformation": "structured_text_extraction",
            }


def iter_bizfin_candidates():
    manifest = load_manifest(BIZFIN_ROOT)

    jsonl_records = [
        record
        for record in manifest["files"]
        if record["path"].endswith(".jsonl")
    ]
    jsonl_records.sort(key=lambda record: record["path"])

    streams = deque(
        iter_bizfin_file(record, manifest)
        for record in jsonl_records
    )

    # Round-robin traversal avoids taking every Chinese candidate
    # from only the first task file.
    while streams:
        stream = streams.popleft()

        try:
            candidate = next(stream)
        except StopIteration:
            continue

        streams.append(stream)
        yield candidate


def ask_choice(prompt, valid_choices):
    while True:
        choice = input(prompt).strip().lower()

        if choice in valid_choices:
            return choice

        print(f"Choose one of: {', '.join(valid_choices)}")


def ask_required(prompt):
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("This value cannot be empty.")


def get_language_stats(records, language):
    language_records = [
        record
        for record in records
        if record.get("language") == language
    ]
    selected_records = [
        record
        for record in language_records
        if record.get("selection_status") == "selected"
    ]

    return {
        "screened": len(language_records),
        "selected": len(selected_records),
        "natural": sum(
            record.get("evaluation_view") == "natural"
            for record in selected_records
        ),
        "challenge": sum(
            record.get("evaluation_view") == "challenge"
            for record in selected_records
        ),
    }


def choose_stage(records, language, evaluation_view):
    discovery_count = sum(
        record.get("language") == language
        and record.get("selection_status") == "selected"
        and record.get("stage") == "discovery"
        and record.get("evaluation_view") == evaluation_view
        for record in records
    )

    if discovery_count < DISCOVERY_TARGETS[evaluation_view]:
        return "discovery"

    return "confirmation"


def print_progress(records, language):
    stats = get_language_stats(records, language)

    print(
        f"{language.upper()} progress: "
        f"screened {stats['screened']}/{MAX_SCREENED_PER_LANGUAGE}, "
        f"selected {stats['selected']}/20, "
        f"natural {stats['natural']}/12, "
        f"challenge {stats['challenge']}/8"
    )


def screen_language(language):
    records = load_candidate_records()
    stats = get_language_stats(records, language)

    if stats["selected"] == 20:
        print(f"{language.upper()} pilot cases are already sealed.")
        return

    if stats["screened"] >= MAX_SCREENED_PER_LANGUAGE:
        raise RuntimeError(
            f"{language.upper()} reached the 60-candidate screening cap"
        )

    screened_source_items = {
        (record.get("source_id"), record.get("source_item_id"))
        for record in records
    }

    if language == "en":
        candidate_iterator = iter_mse_candidates()
    else:
        candidate_iterator = iter_bizfin_candidates()

    scanned_count = 0
    skipped_counts = Counter()
    source_exhausted = False

    for candidate in candidate_iterator:
        source_key = (
            candidate["source_id"],
            candidate["source_item_id"],
        )

        if source_key in screened_source_items:
            continue

        stats = get_language_stats(records, language)

        if stats["selected"] == 20:
            break

        if stats["screened"] >= MAX_SCREENED_PER_LANGUAGE:
            break

        scanned_count += 1

        if language == "en":
            skip_reason = get_mse_non_admission_reason(
                candidate.get("source_tags")
            )
        else:
            skip_reason = get_prescreen_skip_reason(candidate["question"])

        if skip_reason is not None:
            skipped_counts[skip_reason] += 1
            continue

        command = ask_choice(
            "\nPress Enter to inspect the next candidate, or q to stop: ",
            {"", "q"},
        )

        if command == "q":
            break

        print("\n" + "=" * 72)
        print(f"Source: {candidate['source_id']}")
        print(f"Item: {candidate['source_item_id']}")
        print("-" * 72)
        print(candidate["question"])
        print("=" * 72)

        screening_sequence = stats["screened"] + 1
        candidate_id = (
            f"RI2-C-{language.upper()}-{screening_sequence:03d}"
        )

        while True:
            outcome = ask_choice(
                "Decision: reject [r], select natural [n], "
                "or select challenge [c]: ",
                {"r", "n", "c"},
            )

            if outcome == "r":
                selection_status = "rejected"
                evaluation_view = None
                break

            if outcome == "n":
                evaluation_view = "natural"
            else:
                evaluation_view = "challenge"

            if stats[evaluation_view] < VIEW_TARGETS[evaluation_view]:
                selection_status = "selected"
                break

            print(
                f"The {evaluation_view} quota is already full. "
                "Reject this candidate unless it genuinely belongs "
                "to the other view."
            )

        stored_question = candidate["question"]
        transformation = candidate["transformation"]

        # Rejected candidates are recorded but never sealed as pilot cases.
        privacy_action = "not_applicable_rejected_unsealed"

        if selection_status == "selected":
            replacement_text = input(
                "Enter a privacy-safe replacement, or press Enter "
                "only if no redaction is needed: "
            ).strip()

            if replacement_text:
                stored_question = replacement_text
                transformation += "; manual_edit"
                privacy_action = ask_required(
                    "Privacy action (describe what was removed): "
                )
            else:
                privacy_action = "none"

        record = {
            "candidate_id": candidate_id,
            "screening_sequence": screening_sequence,
            "question": stored_question,
            "language": language,
            "source_id": candidate["source_id"],
            "source_revision": candidate["source_revision"],
            "source_file": candidate["source_file"],
            "source_item_id": candidate["source_item_id"],
            "license_basis": candidate["license_basis"],
            "terms_checked_at": TERMS_CHECKED_AT,
            "attribution": candidate["attribution"],
            "transformation": transformation,
            "privacy_action": privacy_action,
            "scenario_equivalence_group_id": None,
            "selection_status": selection_status,
            "rejection_reason": None,
            "case_id": None,
            "stage": None,
            "evaluation_view": evaluation_view,
            "sealed_at_utc": None,
        }

        if selection_status == "rejected":
            record["rejection_reason"] = ask_required(
                "Rejection reason: "
            )
        else:
            case_number = stats["selected"] + 1
            case_id = f"RI2-P-{language.upper()}-{case_number:02d}"
            stage = choose_stage(records, language, evaluation_view)

            default_group_id = f"scenario-{case_id.lower()}"
            group_id = input(
                "Scenario-equivalence group ID "
                f"[{default_group_id}]: "
            ).strip()

            record["case_id"] = case_id
            record["stage"] = stage
            record["scenario_equivalence_group_id"] = (
                group_id or default_group_id
            )
            record["sealed_at_utc"] = utc_now()

        append_candidate_record(record)
        records.append(record)
        screened_source_items.add(source_key)
        print_progress(records, language)
    else:
        source_exhausted = True

    stats = get_language_stats(records, language)

    if stats["selected"] == 20:
        print(f"{language.upper()} selection is complete and sealed.")
    elif stats["screened"] >= MAX_SCREENED_PER_LANGUAGE:
        print(
            f"STOP: {language.upper()} reached the screening cap "
            "without satisfying the fixed composition."
        )
    elif language == "en" and source_exhausted:
        print(
            "STOP: No unseen EN candidates remain under the frozen "
            "metadata policy, but the fixed composition is incomplete. "
            "Review source/policy feasibility before continuing."
        )
    else:
        print(f"{language.upper()} screening paused.")

    print_progress(records, language)
    print_prescreen_summary(language, scanned_count, skipped_counts)


def main():
    parser = argparse.ArgumentParser(
        description="Privately screen Risk-Intent V2 pilot candidates."
    )
    parser.add_argument(
        "--language",
        required=True,
        choices=("en", "zh"),
    )
    args = parser.parse_args()

    verify_money_stackexchange()
    verify_bizfin()
    screen_language(args.language)


if __name__ == "__main__":
    main()
