from datetime import datetime


def generate_markdown_changelog(account_id, changes, company_name=""):
    title = company_name or account_id
    lines = [
        "# Change Log -- " + title,
        "**Account ID:** `" + account_id + "`",
        "**Generated:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "**Version:** v1 -> v2 (Post-Onboarding Update)",
        "", "---", ""
    ]
    if not changes:
        lines.append("## No Changes Detected")
        lines.append("The onboarding data matched all existing demo-derived assumptions.")
    else:
        lines.append("## Summary: " + str(len(changes)) + " field(s) updated")
        lines.append("")
        for field, change in changes.items():
            lines.append("### `" + field + "`")
            lines.append("- **Before (v1):** `" + str(change.get("old", "--")) + "`")
            lines.append("- **After  (v2):** `" + str(change.get("new", "--")) + "`")
            if change.get("confidence_change"):
                lines.append("- **Confidence:** " + change["confidence_change"])
            lines.append("- **Reason:** " + change.get("reason", "onboarding update"))
            lines.append("")
    return "\n".join(lines)


def generate_batch_summary_report(results):
    total    = len(results)
    success  = sum(1 for r in results if r.get("status") == "success")
    failed   = sum(1 for r in results if r.get("status") == "failed")
    warnings = sum(1 for r in results if r.get("warnings"))

    lines = [
        "# Clara AI Zentrades -- Batch Processing Report",
        "**Run Date:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "",
        "## Summary",
        "| Metric | Count |",
        "|--------|-------|",
        "| Total Accounts | " + str(total) + " |",
        "| v1 + v2 Completed | " + str(success) + " |",
        "| Failed | " + str(failed) + " |",
        "| Has Warnings | " + str(warnings) + " |",
        "", "## Account Details", ""
    ]
    for r in results:
        icon = "[OK]" if r.get("status") == "success" else "[FAIL]" if r.get("status") == "failed" else "[WARN]"
        lines.append("### " + icon + " " + r.get("account_id", "") + " -- " + r.get("company_name", "Unknown"))
        lines.append("- **v1 Completeness:** " + str(r.get("v1_score", 0)) + "%")
        lines.append("- **v2 Completeness:** " + str(r.get("v2_score", 0)) + "%")
        lines.append("- **Changes (v1->v2):** " + str(r.get("change_count", 0)) + " fields")
        if r.get("warnings"):
            lines.append("- **Warnings:** " + str(len(r["warnings"])))
        if r.get("errors"):
            lines.append("- **Errors:** " + ", ".join(r["errors"]))
        lines.append("")
    return "\n".join(lines)
