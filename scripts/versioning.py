def generate_diff(old, new, path=""):
    changes = {}
    all_keys = set(list(old.keys()) + list(new.keys()))
    for key in all_keys:
        if key in ("account_id", "questions_or_unknowns"):
            continue
        current_path = (path + "." + key) if path else key
        old_val = old.get(key)
        new_val = new.get(key)
        if old_val == new_val:
            continue
        if (isinstance(old_val, dict) and "value" in old_val
                and isinstance(new_val, dict) and "value" in new_val):
            if old_val.get("value") != new_val.get("value"):
                changes[current_path] = {
                    "old": old_val.get("value"),
                    "new": new_val.get("value"),
                    "confidence_change": str(old_val.get("confidence", "")) + " -> " + str(new_val.get("confidence", "")),
                    "reason": "onboarding update"
                }
        elif isinstance(old_val, dict) and isinstance(new_val, dict):
            nested = generate_diff(old_val, new_val, current_path)
            changes.update(nested)
        elif old_val != new_val:
            changes[current_path] = {"old": old_val, "new": new_val, "reason": "onboarding update"}
    return changes
