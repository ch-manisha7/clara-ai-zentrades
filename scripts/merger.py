def deep_merge(old, new, path=""):
    merged = {}
    changes = {}
    all_keys = set(list(old.keys()) + list(new.keys()))
    for key in all_keys:
        if key == "account_id":
            merged[key] = old.get(key, new.get(key))
            continue
        current_path = (path + "." + key) if path else key
        old_value = old.get(key)
        new_value = new.get(key)
        if new_value is None:
            merged[key] = old_value
            continue
        if old_value is None:
            merged[key] = new_value
            continue
        if isinstance(new_value, dict) and "value" in new_value:
            nv = new_value.get("value")
            ov = old_value.get("value") if isinstance(old_value, dict) else old_value
            if nv in ["", [], {}, None]:
                merged[key] = old_value
                continue
            if isinstance(nv, list) and isinstance(ov, list):
                combined = ov + [item for item in nv if item not in ov]
                merged[key] = {"value": combined, "confidence": "confirmed"}
                if set(map(str, nv)) != set(map(str, ov)):
                    changes[current_path] = {
                        "old": ov, "new": combined,
                        "confidence_change": str(old_value.get("confidence", "")) + " -> confirmed",
                        "reason": "onboarding update"
                    }
                else:
                    merged[key] = old_value
            elif ov != nv:
                merged[key] = {"value": nv, "confidence": "confirmed"}
                changes[current_path] = {
                    "old": ov, "new": nv,
                    "confidence_change": str(old_value.get("confidence", "")) + " -> confirmed",
                    "reason": "onboarding update"
                }
            else:
                merged[key] = {"value": nv, "confidence": "confirmed"}
        elif isinstance(new_value, dict) and isinstance(old_value, dict):
            nested_merged, nested_changes = deep_merge(old_value, new_value, current_path)
            merged[key] = nested_merged
            changes.update(nested_changes)
        elif key == "questions_or_unknowns":
            if isinstance(new_value, list) and isinstance(old_value, list):
                merged[key] = old_value + [x for x in new_value if x not in old_value]
            else:
                merged[key] = old_value
        else:
            merged[key] = new_value if new_value else old_value
    return merged, changes


def merge_memos(old_memo, new_memo):
    return deep_merge(old_memo, new_memo)
