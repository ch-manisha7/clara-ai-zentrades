def validate_memo(memo, stage="v1"):
    errors = []
    warnings = []

    def empty(f):
        if isinstance(f, dict):
            v = f.get("value")
            return not v or v in ["", [], {}, None]
        return not f

    if empty(memo.get("company_name")):
        warnings.append("Company name missing")
    bh = memo.get("business_hours", {})
    if empty(bh.get("start")) or empty(bh.get("end")):
        warnings.append("Business hours (start/end) not fully specified")
    if empty(bh.get("timezone")):
        warnings.append("Timezone not specified")
    if empty(memo.get("emergency_definition")):
        warnings.append("Emergency definition missing")
    if empty(memo.get("call_transfer_rules", {}).get("primary_number")):
        warnings.append("No primary transfer number defined")

    if stage == "v2":
        ct = memo.get("call_transfer_rules", {})
        if empty(ct.get("timeout_seconds")):
            errors.append("Transfer timeout not confirmed during onboarding")
        if empty(ct.get("failure_message")):
            warnings.append("Transfer failure message not defined")
        if empty(memo.get("phone_number")):
            errors.append("Main phone number not confirmed during onboarding")
        if empty(memo.get("non_emergency_routing_rules")):
            warnings.append("Non-emergency routing not defined")

        def walk(obj, path=""):
            for k, v in obj.items():
                if isinstance(v, dict) and "confidence" in v:
                    if v["confidence"] == "demo_assumed" and v.get("value"):
                        warnings.append("Field '" + path + k + "' still at demo_assumed confidence")
                elif isinstance(v, dict):
                    walk(v, path + k + ".")
        walk(memo)

    return {"errors": errors, "warnings": warnings, "is_valid": len(errors) == 0}


def calculate_completeness(memo):
    total = 0
    filled = 0

    def walk(obj):
        nonlocal total, filled
        for k, v in obj.items():
            if k in ("account_id", "questions_or_unknowns"):
                continue
            if isinstance(v, dict) and "value" in v:
                total += 1
                val = v.get("value")
                if val and val not in ["", [], {}, None]:
                    filled += 1
            elif isinstance(v, dict):
                walk(v)
    walk(memo)
    return round((filled / total) * 100, 1) if total else 0.0
