import json
import re
import os
import urllib.request
from schema import empty_account_memo

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


def call_claude(prompt, system):
    if not ANTHROPIC_API_KEY:
        return None
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 2000,
        "system": system,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["content"][0]["text"]
    except Exception as e:
        print("   [WARN] Claude API failed: " + str(e))
        return None


def llm_extract(transcript, account_id):
    system = (
        "You are a precise data extraction assistant for Clara Answers, an AI voice agent platform. "
        "Extract structured information from call transcripts exactly as stated. "
        "Do not invent or assume details. Return ONLY valid JSON. No markdown, no explanation."
    )
    prompt = (
        "Extract all business configuration details from this transcript for account " + account_id + ".\n\n"
        "Return a JSON object with these exact fields (use empty string or empty list if not found):\n"
        "{\n"
        '  "company_name": "",\n'
        '  "business_hours_days": "",\n'
        '  "business_hours_start": "",\n'
        '  "business_hours_end": "",\n'
        '  "business_hours_timezone": "",\n'
        '  "office_address": "",\n'
        '  "phone_number": "",\n'
        '  "services_supported": [],\n'
        '  "emergency_definition": [],\n'
        '  "emergency_routing_primary": "",\n'
        '  "emergency_routing_secondary": "",\n'
        '  "emergency_transfer_timeout_seconds": "",\n'
        '  "emergency_fallback_message": "",\n'
        '  "non_emergency_routing": "",\n'
        '  "integration_constraints": [],\n'
        '  "after_hours_flow_summary": "",\n'
        '  "office_hours_flow_summary": "",\n'
        '  "questions_or_unknowns": [],\n'
        '  "notes": ""\n'
        "}\n\n"
        "Rules:\n"
        "- Only extract what is explicitly stated\n"
        "- emergency_definition: list each trigger separately\n"
        "- integration_constraints: list each constraint separately\n"
        "- questions_or_unknowns: anything vague or unresolved\n"
        "- after_hours_flow_summary: 1-2 sentence summary of after-hours handling\n"
        "- office_hours_flow_summary: 1-2 sentence summary of office-hours handling\n"
        "- non_emergency_routing: what to do with non-emergency after-hours calls\n\n"
        "TRANSCRIPT:\n" + transcript
    )
    raw = call_claude(prompt, system)
    if not raw:
        return None
    try:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = re.sub(r"```[a-z]*\n?", "", clean).strip("`").strip()
        return json.loads(clean)
    except Exception as e:
        print("   [WARN] LLM parse failed: " + str(e))
        return None


def apply_llm_result(memo, extracted):
    def setf(keys, value, conf="extracted"):
        obj = memo
        for k in keys[:-1]:
            obj = obj[k]
        last = keys[-1]
        if value and value not in ["", [], {}, None]:
            obj[last]["value"] = value
            obj[last]["confidence"] = conf

    setf(["company_name"], extracted.get("company_name"))
    setf(["business_hours", "days"], extracted.get("business_hours_days"))
    setf(["business_hours", "start"], extracted.get("business_hours_start"))
    setf(["business_hours", "end"], extracted.get("business_hours_end"))
    setf(["business_hours", "timezone"], extracted.get("business_hours_timezone"))
    setf(["office_address"], extracted.get("office_address"))
    setf(["phone_number"], extracted.get("phone_number"))
    setf(["services_supported"], extracted.get("services_supported", []))
    setf(["emergency_definition"], extracted.get("emergency_definition", []))
    setf(["emergency_routing_rules"], extracted.get("emergency_routing_primary"))
    setf(["non_emergency_routing_rules"], extracted.get("non_emergency_routing"))
    setf(["call_transfer_rules", "primary_number"], extracted.get("emergency_routing_primary"))
    setf(["call_transfer_rules", "secondary_number"], extracted.get("emergency_routing_secondary"))
    setf(["call_transfer_rules", "timeout_seconds"], str(extracted.get("emergency_transfer_timeout_seconds") or ""))
    setf(["call_transfer_rules", "failure_message"], extracted.get("emergency_fallback_message"))
    setf(["integration_constraints"], extracted.get("integration_constraints", []))
    setf(["after_hours_flow_summary"], extracted.get("after_hours_flow_summary"))
    setf(["office_hours_flow_summary"], extracted.get("office_hours_flow_summary"))
    setf(["notes"], extracted.get("notes") or "Extracted via LLM")

    unknowns = extracted.get("questions_or_unknowns", [])
    if isinstance(unknowns, list):
        memo["questions_or_unknowns"].extend(unknowns)
    return memo


def rule_based_extract(transcript, account_id):
    memo = empty_account_memo(account_id)
    text = transcript
    lower = text.lower()

    # Company name
    for pattern in [
        r"we(?:'re| are)\s+([A-Z][A-Za-z\s&]+?)(?:\.|,|\n)",
        r"([A-Z][A-Za-z\s&]{3,30}(?:HVAC|Fire|Electric|Alarm|Sprinkler|Air|Power|Services?|Solutions?|Systems?|Contractors?))",
    ]:
        m = re.search(pattern, text)
        if m:
            val = m.group(1).strip().rstrip(".,")
            if len(val) > 3:
                memo["company_name"]["value"] = val
                memo["company_name"]["confidence"] = "extracted"
                break

    # Business hours
    time_pat = r"(\d{1,2}(?::\d{2})?\s*(?:am|pm))\s+(?:to|-)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm))"
    m = re.search(time_pat, lower)
    if m:
        memo["business_hours"]["start"]["value"] = m.group(1).strip()
        memo["business_hours"]["end"]["value"] = m.group(2).strip()
        memo["business_hours"]["start"]["confidence"] = "extracted"
        memo["business_hours"]["end"]["confidence"] = "extracted"

    if re.search(r"monday\s+(?:through|to|-)\s+friday|mon\s*[-]\s*fri", lower):
        memo["business_hours"]["days"]["value"] = "Monday-Friday"
        memo["business_hours"]["days"]["confidence"] = "extracted"

    for key, val in {"eastern": "EST", "central": "CST", "mountain": "MST", "pacific": "PST",
                     " est": "EST", " cst": "CST", " mst": "MST", " pst": "PST"}.items():
        if key in lower:
            memo["business_hours"]["timezone"]["value"] = val
            memo["business_hours"]["timezone"]["confidence"] = "extracted"
            break

    # Address
    m = re.search(r"\d+\s+[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Way|Blvd|Drive|Dr)[^\n,]*", text)
    if m:
        memo["office_address"]["value"] = m.group().strip().rstrip(".,")
        memo["office_address"]["confidence"] = "extracted"

    # Phones
    phones = re.findall(r"\b(\d{3}[-.\s]\d{3}[-.\s]\d{4})\b", text)
    if phones:
        memo["phone_number"]["value"] = phones[0]
        memo["phone_number"]["confidence"] = "extracted"
        if len(phones) >= 2:
            memo["call_transfer_rules"]["primary_number"]["value"] = phones[1]
            memo["call_transfer_rules"]["primary_number"]["confidence"] = "extracted"
        if len(phones) >= 3:
            memo["call_transfer_rules"]["secondary_number"]["value"] = phones[2]
            memo["call_transfer_rules"]["secondary_number"]["confidence"] = "extracted"

    # Timeout
    tm = re.search(r"(\d+)\s*seconds?", lower)
    if tm:
        memo["call_transfer_rules"]["timeout_seconds"]["value"] = tm.group(1)
        memo["call_transfer_rules"]["timeout_seconds"]["confidence"] = "extracted"

    # Failure message
    for fp in [r'say\s+["""](.{20,200})["""]', r'tell.*caller[^.]{0,10}["""](.{20,200})["""]']:
        fm = re.search(fp, text, re.IGNORECASE)
        if fm:
            memo["call_transfer_rules"]["failure_message"]["value"] = fm.group(1).strip()
            memo["call_transfer_rules"]["failure_message"]["confidence"] = "extracted"
            break

    # Services
    service_map = {
        "hvac": "HVAC", "sprinkler": "Fire Sprinkler", "fire alarm": "Fire Alarm",
        "electrical": "Electrical", "inspection": "Inspection",
        "monitoring": "Monitoring", "extinguisher": "Fire Extinguisher",
        "maintenance": "Maintenance", "installation": "Installation", "repair": "Repair"
    }
    services = []
    for kw, label in service_map.items():
        if kw in lower and label not in services:
            services.append(label)
    if services:
        memo["services_supported"]["value"] = services
        memo["services_supported"]["confidence"] = "keyword_detected"

    # Emergency triggers
    em_kw = {
        r"sprinkler.*(?:flow|discharge|leak)": "Active sprinkler water discharge",
        r"fire alarm.*(?:trigger|activat|won.t reset|won.t silence)": "Fire alarm triggered and cannot be silenced",
        r"no heat": "No heat",
        r"no (?:ac|air conditioning)": "No air conditioning",
        r"power outage": "Power outage at commercial facility",
        r"live wire|exposed wire": "Live or exposed electrical wires",
        r"panel fail": "Electrical panel failure",
        r"carbon monoxide": "Carbon monoxide alarm triggered",
        r"refrigerant leak": "Refrigerant leak detected",
        r"visible smoke": "Visible smoke reported",
        r"active fire": "Active fire"
    }
    triggers = []
    for pattern, label in em_kw.items():
        if re.search(pattern, lower) and label not in triggers:
            triggers.append(label)
    if triggers:
        memo["emergency_definition"]["value"] = triggers
        memo["emergency_definition"]["confidence"] = "keyword_detected"
    else:
        memo["questions_or_unknowns"].append("Emergency definition not explicitly stated")

    # Integrations
    constraints = []
    if "servicetrade" in lower:
        constraints.append("Uses ServiceTrade for job management")
    if "servicetitan" in lower:
        constraints.append("Uses ServiceTitan for dispatch")
    if "never create" in lower and "sprinkler" in lower:
        constraints.append("Never auto-create sprinkler jobs - requires manual review")
    if "procore" in lower:
        constraints.append("Uses Procore for project management (not dispatch)")
    if constraints:
        memo["integration_constraints"]["value"] = constraints
        memo["integration_constraints"]["confidence"] = "keyword_detected"

    # Non-emergency routing
    if re.search(r"non.emergency|not.*emergency|routine|scheduling|billing", lower):
        memo["non_emergency_routing_rules"]["value"] = (
            "Collect caller name, phone number, and description of request. "
            "Confirm team will follow up next business day."
        )
        memo["non_emergency_routing_rules"]["confidence"] = "extracted"

    # Auto-generate flow summaries
    primary = memo["call_transfer_rules"]["primary_number"]["value"]
    timeout = memo["call_transfer_rules"]["timeout_seconds"]["value"] or "45"
    company = memo["company_name"]["value"] or "the company"
    start_t = memo["business_hours"]["start"]["value"] or "opening"
    end_t = memo["business_hours"]["end"]["value"] or "closing"
    tz_v = memo["business_hours"]["timezone"]["value"] or "local time"

    memo["after_hours_flow_summary"]["value"] = (
        "Greet caller and identify purpose. If emergency: collect name, phone, address immediately "
        "then attempt transfer" + (" to " + primary if primary else "") + " with " + timeout + "s timeout. "
        "If transfer fails: apologize and confirm callback within 15 minutes. "
        "If non-emergency: collect details and confirm next-business-day follow-up."
    )
    memo["after_hours_flow_summary"]["confidence"] = "generated"

    memo["office_hours_flow_summary"]["value"] = (
        "Greet caller. Ask purpose of call. Collect name and callback number. "
        "Route or transfer to appropriate team member. "
        "Business hours: " + start_t + " to " + end_t + " " + tz_v + "."
    )
    memo["office_hours_flow_summary"]["confidence"] = "generated"

    memo["notes"]["value"] = "Extracted via rule-based (set ANTHROPIC_API_KEY for LLM extraction)"
    return memo


def extract_from_transcript(transcript, account_id):
    memo = empty_account_memo(account_id)
    if ANTHROPIC_API_KEY:
        print("   [LLM] Using Claude API extraction...")
        extracted = llm_extract(transcript, account_id)
        if extracted:
            memo = apply_llm_result(memo, extracted)
            print("   [OK] LLM extraction successful")
            return memo
        else:
            print("   [WARN] LLM failed - falling back to rule-based")
    print("   [RULE] Using rule-based extraction...")
    return rule_based_extract(transcript, account_id)
