"""
Clara AI Zentrades -- Main Pipeline Orchestrator
Runs Pipeline A (demo -> v1) and Pipeline B (onboarding -> v2) for all accounts.

Usage:
    python scripts/main.py

Optional - set API key for LLM extraction (much better accuracy):
    Windows: set ANTHROPIC_API_KEY=sk-ant-xxxxx
    Mac/Linux: export ANTHROPIC_API_KEY=sk-ant-xxxxx
"""
import os
import sys
import json
import hashlib
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from extractor import extract_from_transcript
from prompt_generator import generate_agent_spec
from merger import merge_memos
from validator import validate_memo, calculate_completeness
from versioning import generate_diff
from reporting import generate_markdown_changelog, generate_batch_summary_report
from task_tracker import create_task, update_task_status

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPTS_DEMO = os.path.join(PROJECT_ROOT, "transcripts", "demo")
TRANSCRIPTS_ONBOARDING = os.path.join(PROJECT_ROOT, "transcripts", "onboarding")
OUTPUT_BASE = os.path.join(PROJECT_ROOT, "outputs", "accounts")
CHANGELOG_PATH = os.path.join(PROJECT_ROOT, "changelog")
REPORTS_PATH = os.path.join(PROJECT_ROOT, "outputs", "reports")


def log(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_transcript(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def update_history(history_path, new_hash, source):
    history = []
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    history.append({
        "version": len(history) + 1,
        "timestamp": datetime.now().isoformat(),
        "hash": new_hash,
        "source": source
    })
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)


def get_company(memo):
    cn = memo.get("company_name", {})
    if isinstance(cn, dict):
        return cn.get("value") or "Unknown"
    return str(cn) or "Unknown"


# ── Pipeline A: Demo -> v1 ────────────────────────────────────────────────────

def run_pipeline_a(account_id, demo_transcript):
    v1_path = os.path.join(OUTPUT_BASE, account_id, "v1")
    hash_file = os.path.join(v1_path, "transcript_hash.txt")
    history_file = os.path.join(v1_path, "transcript_history.json")
    demo_hash = sha256(demo_transcript)

    if os.path.exists(hash_file):
        with open(hash_file, "r", encoding="utf-8") as f:
            if f.read().strip() == demo_hash:
                log("   [CACHED] Demo unchanged -- loading v1")
                return (
                    load_json(os.path.join(v1_path, "memo.json")),
                    load_json(os.path.join(v1_path, "agent_spec.json")),
                    load_json(os.path.join(v1_path, "validation.json")),
                    load_json(os.path.join(v1_path, "completeness.json"))["score_percent"],
                    True
                )

    os.makedirs(v1_path, exist_ok=True)
    memo_v1 = extract_from_transcript(demo_transcript, account_id)
    agent_v1 = generate_agent_spec(memo_v1, version="v1")
    validation_v1 = validate_memo(memo_v1, stage="v1")
    score_v1 = calculate_completeness(memo_v1)

    save_json(os.path.join(v1_path, "memo.json"), memo_v1)
    save_json(os.path.join(v1_path, "agent_spec.json"), agent_v1)
    save_json(os.path.join(v1_path, "validation.json"), validation_v1)
    save_json(os.path.join(v1_path, "completeness.json"), {"score_percent": score_v1})

    with open(hash_file, "w", encoding="utf-8") as f:
        f.write(demo_hash)
    update_history(history_file, demo_hash, "demo_call")

    return memo_v1, agent_v1, validation_v1, score_v1, False


# ── Pipeline B: Onboarding -> v2 ──────────────────────────────────────────────

def run_pipeline_b(account_id, onboarding_transcript, memo_v1):
    v2_path = os.path.join(OUTPUT_BASE, account_id, "v2")
    v1_path = os.path.join(OUTPUT_BASE, account_id, "v1")
    hash_file = os.path.join(v2_path, "transcript_hash.txt")
    history_file = os.path.join(v2_path, "transcript_history.json")
    ob_hash = sha256(onboarding_transcript)

    if os.path.exists(hash_file):
        with open(hash_file, "r", encoding="utf-8") as f:
            if f.read().strip() == ob_hash:
                log("   [CACHED] Onboarding unchanged -- loading v2")
                cl_path = os.path.join(CHANGELOG_PATH, account_id + "_changes.json")
                changelog = load_json(cl_path) if os.path.exists(cl_path) else {}
                return (
                    load_json(os.path.join(v2_path, "memo.json")),
                    load_json(os.path.join(v2_path, "agent_spec.json")),
                    changelog,
                    load_json(os.path.join(v2_path, "validation.json")),
                    load_json(os.path.join(v2_path, "completeness.json"))["score_percent"],
                    True
                )

    os.makedirs(v2_path, exist_ok=True)
    ob_extracted = extract_from_transcript(onboarding_transcript, account_id)
    memo_v2, _ = merge_memos(memo_v1, ob_extracted)
    diff = generate_diff(load_json(os.path.join(v1_path, "memo.json")), memo_v2)
    agent_v2 = generate_agent_spec(memo_v2, version="v2")
    validation_v2 = validate_memo(memo_v2, stage="v2")
    score_v2 = calculate_completeness(memo_v2)

    save_json(os.path.join(v2_path, "memo.json"), memo_v2)
    save_json(os.path.join(v2_path, "agent_spec.json"), agent_v2)
    save_json(os.path.join(v2_path, "validation.json"), validation_v2)
    save_json(os.path.join(v2_path, "completeness.json"), {"score_percent": score_v2})

    os.makedirs(CHANGELOG_PATH, exist_ok=True)
    save_json(os.path.join(CHANGELOG_PATH, account_id + "_changes.json"), diff)
    with open(os.path.join(CHANGELOG_PATH, account_id + "_changes.md"), "w", encoding="utf-8") as f:
        f.write(generate_markdown_changelog(account_id, diff, get_company(memo_v2)))

    with open(hash_file, "w", encoding="utf-8") as f:
        f.write(ob_hash)
    update_history(history_file, ob_hash, "onboarding_call")

    return memo_v2, agent_v2, diff, validation_v2, score_v2, False


# ── Account processor ─────────────────────────────────────────────────────────

def process_account(account_id):
    result = {
        "account_id": account_id,
        "company_name": "Unknown",
        "status": "failed",
        "has_v2": False,
        "v1_score": 0,
        "v2_score": 0,
        "warnings": [],
        "errors": [],
        "change_count": 0
    }

    demo_file = os.path.join(TRANSCRIPTS_DEMO, account_id + "_demo.txt")
    ob_file = os.path.join(TRANSCRIPTS_ONBOARDING, account_id + "_onboarding.txt")

    if not os.path.exists(demo_file):
        log("   [ERROR] Demo transcript not found: " + demo_file)
        result["errors"] = ["Demo transcript missing"]
        return result

    log("\n" + "=" * 52)
    log("  Processing " + account_id)
    log("=" * 52)

    try:
        demo_transcript = read_transcript(demo_file)
        memo_v1, _, val_v1, score_v1, cached_v1 = run_pipeline_a(account_id, demo_transcript)
        company = get_company(memo_v1)

        result["company_name"] = company
        result["v1_score"] = score_v1
        result["warnings"] = val_v1["warnings"]
        result["errors"] = val_v1["errors"]

        if not cached_v1:
            log("   [OK] v1 created -- " + company)
        log("   [SCORE] v1: " + str(score_v1) + "%")

        create_task(account_id, company, "v1_generated", "complete",
                    "v1 completeness: " + str(score_v1) + "%. Warnings: " + str(len(val_v1["warnings"])))

        if val_v1["errors"]:
            log("   [ERROR] v1 errors: " + str(val_v1["errors"]))
            create_task(account_id, company, "needs_review", "open",
                        "v1 errors: " + "; ".join(val_v1["errors"]))
            result["status"] = "v1_only_errors"
            return result

        if os.path.exists(ob_file):
            ob_transcript = read_transcript(ob_file)
            memo_v2, _, changes, val_v2, score_v2, cached_v2 = run_pipeline_b(
                account_id, ob_transcript, memo_v1)

            if not cached_v2:
                log("   [OK] v2 created -- " + str(len(changes)) + " fields updated")
            log("   [SCORE] v2: " + str(score_v2) + "% | Changes: " + str(len(changes)))

            result["has_v2"] = True
            result["v2_score"] = score_v2
            result["change_count"] = len(changes)
            result["warnings"] = val_v2["warnings"]
            result["errors"] = val_v2["errors"]
            result["status"] = "success"

            update_task_status(account_id, "v1_generated", "v2_complete")
            create_task(account_id, company, "v2_updated", "complete",
                        "v2: " + str(score_v2) + "%. " + str(len(changes)) + " fields updated.")

            if val_v2["errors"]:
                log("   [ERROR] v2 errors: " + str(val_v2["errors"]))
                create_task(account_id, company, "needs_review", "open",
                            "v2 errors: " + "; ".join(val_v2["errors"]))
            if val_v2["warnings"]:
                log("   [WARN] " + str(len(val_v2["warnings"])) + " warning(s)")
        else:
            log("   [WARN] No onboarding transcript -- v2 skipped")
            create_task(account_id, company, "onboarding_pending", "open",
                        "Awaiting onboarding call")
            result["status"] = "v1_only"

    except Exception as e:
        log("   [ERROR] " + account_id + ": " + str(e))
        result["errors"] = [str(e)]
        result["status"] = "failed"
        import traceback
        traceback.print_exc()

    return result


# ── Batch runner ───────────────────────────────────────────────────────────────

def run_batch():
    log("\n" + "=" * 60)
    log("  CLARA AI ZENTRADES -- PIPELINE BATCH RUN")
    log("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log("=" * 60)

    if not os.path.exists(TRANSCRIPTS_DEMO):
        log("[ERROR] Demo folder not found: " + TRANSCRIPTS_DEMO)
        return

    demo_files = [f for f in os.listdir(TRANSCRIPTS_DEMO) if f.endswith("_demo.txt")]
    if not demo_files:
        log("[ERROR] No demo transcript files found.")
        return

    log("\n  Found " + str(len(demo_files)) + " account(s)\n")
    batch_results = []

    for file in sorted(demo_files):
        account_id = file.replace("_demo.txt", "")
        result = process_account(account_id)
        batch_results.append(result)

    os.makedirs(REPORTS_PATH, exist_ok=True)
    with open(os.path.join(REPORTS_PATH, "batch_summary.md"), "w", encoding="utf-8") as f:
        f.write(generate_batch_summary_report(batch_results))
    save_json(os.path.join(REPORTS_PATH, "batch_results.json"), batch_results)

    total = len(batch_results)
    successful = sum(1 for r in batch_results if r["status"] == "success")
    v1_only = sum(1 for r in batch_results if r["status"] in ("v1_only", "v1_only_errors"))
    failed = sum(1 for r in batch_results if r["status"] == "failed")

    log("\n" + "=" * 60)
    log("  BATCH SUMMARY")
    log("=" * 60)
    log("  Total Accounts  : " + str(total))
    log("  v1+v2 Complete  : " + str(successful))
    log("  v1 Only         : " + str(v1_only))
    log("  Failed          : " + str(failed))
    log("\n  Reports saved to: " + REPORTS_PATH)
    log("=" * 60 + "\n")


if __name__ == "__main__":
    run_batch()
