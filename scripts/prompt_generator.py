from datetime import datetime


def _val(f):
    if isinstance(f, dict):
        return f.get("value", "") or ""
    return str(f) if f else ""


def _list(f):
    if isinstance(f, dict):
        v = f.get("value", [])
        return v if isinstance(v, list) else []
    return []


def generate_agent_spec(memo, version="v1"):
    company = _val(memo.get("company_name")) or "our company"
    bh = memo.get("business_hours", {})
    days = _val(bh.get("days")) or "Monday-Friday"
    start = _val(bh.get("start")) or "8am"
    end = _val(bh.get("end")) or "5pm"
    tz = _val(bh.get("timezone")) or "local time"
    phone = _val(memo.get("phone_number")) or "our main line"
    address = _val(memo.get("office_address")) or "our office"
    ct = memo.get("call_transfer_rules", {})
    primary = _val(ct.get("primary_number")) or phone
    secondary = _val(ct.get("secondary_number")) or ""
    timeout = _val(ct.get("timeout_seconds")) or "45"
    fail_msg = _val(ct.get("failure_message")) or (
        "I was unable to reach the " + company + " team directly. "
        "Your information has been logged and someone will contact you shortly. "
        "If this is a life-safety emergency, please call 911 immediately."
    )
    emergencies = _list(memo.get("emergency_definition"))
    em_text = "\n".join("  - " + e for e in emergencies) if emergencies else "  - Customer states urgent issue requiring immediate attention"
    services = _list(memo.get("services_supported"))
    services_text = ", ".join(services) if services else "general services"
    constraints = _list(memo.get("integration_constraints"))
    con_text = "\n".join("  - " + c for c in constraints) if constraints else "  - None specified"
    unknowns = memo.get("questions_or_unknowns", [])
    unk_text = "\n".join("  - " + u for u in unknowns) if unknowns else "  - None"
    non_em = _val(memo.get("non_emergency_routing_rules")) or "Collect name, phone, and description. Confirm next-business-day callback."
    after_summ = _val(memo.get("after_hours_flow_summary")) or ""
    office_summ = _val(memo.get("office_hours_flow_summary")) or ""

    secondary_line = ("Secondary: attempt transfer to " + secondary + " for " + timeout + " seconds") if secondary else ""

    system_prompt = (
        "You are Clara, a professional AI voice agent for " + company + ".\n"
        "You answer inbound calls with warmth and efficiency.\n\n"
        "COMPANY PROFILE\n"
        "===============\n"
        "Company : " + company + "\n"
        "Address : " + address + "\n"
        "Phone   : " + phone + "\n"
        "Services: " + services_text + "\n\n"
        "BUSINESS HOURS\n"
        "==============\n"
        "Days  : " + days + "\n"
        "Hours : " + start + " to " + end + " " + tz + "\n\n"
        + ("OFFICE HOURS FLOW\n=================\n" + office_summ + "\n\n" if office_summ else "")
        + ("AFTER HOURS FLOW\n================\n" + after_summ + "\n\n" if after_summ else "")
        +
        "DURING BUSINESS HOURS\n"
        "=====================\n\n"
        "STEP 1 - GREET:\n"
        '"Thank you for calling ' + company + '. This is Clara. How can I help you today?"\n\n'
        "STEP 2 - UNDERSTAND PURPOSE:\n"
        "Listen carefully. Is this an emergency? What service? New or existing customer?\n\n"
        "STEP 3 - COLLECT CALLER INFO:\n"
        "Always collect: Full name + Best callback phone number.\n"
        "If routing to dispatch, also collect: Property or site address.\n\n"
        "STEP 4 - ROUTE OR TRANSFER:\n"
        'Say: "Let me connect you with our team. One moment please."\n'
        "Transfer to: " + phone + "\n\n"
        "STEP 5 - IF TRANSFER FAILS (no answer within " + timeout + " seconds):\n"
        'Say: "' + fail_msg + '"\n'
        "Log: caller name, phone, reason, timestamp.\n\n"
        "STEP 6 - CLOSE:\n"
        '"Is there anything else I can help you with today?"\n'
        '"Thank you for calling ' + company + '. Have a great day. Goodbye."\n\n'
        "AFTER HOURS\n"
        "===========\n\n"
        "STEP 1 - GREET:\n"
        '"Thank you for calling ' + company + '. You have reached us outside our regular hours of ' + days + ' ' + start + ' to ' + end + ' ' + tz + '. This is Clara, our automated assistant."\n\n'
        "STEP 2 - ASK PURPOSE:\n"
        '"Can you briefly tell me the reason for your call?"\n\n'
        "STEP 3 - DETERMINE IF EMERGENCY:\n"
        "The following are EMERGENCIES requiring immediate dispatch:\n"
        + em_text + "\n\n"
        "If ANY apply or caller says it is an emergency -> EMERGENCY FLOW\n"
        "Otherwise -> NON-EMERGENCY FLOW\n\n"
        "-- EMERGENCY FLOW --\n\n"
        "STEP 4E - COLLECT CRITICAL INFO:\n"
        '"I understand this is urgent. I need a few quick details to reach our on-call team."\n'
        "Collect in order: (1) Full name  (2) Callback phone  (3) Site address  (4) Brief description\n\n"
        "STEP 5E - ATTEMPT TRANSFER:\n"
        '"I am connecting you with our on-call technician now. Please hold."\n'
        "Primary  : " + primary + " - wait " + timeout + " seconds\n"
        + (secondary_line + "\n" if secondary_line else "")
        +
        "\nSTEP 6E - IF ALL TRANSFERS FAIL:\n"
        'Say: "' + fail_msg + '"\n\n'
        "-- NON-EMERGENCY FLOW --\n\n"
        "STEP 4N - COLLECT DETAILS:\n"
        '"Let me take down your information and our team will follow up during business hours."\n'
        + non_em + "\n\n"
        "STEP 5N - CONFIRM AND CLOSE:\n"
        '"Someone from ' + company + ' will reach out on the next business day. Thank you. Goodbye."\n\n'
        "ABSOLUTE RULES\n"
        "==============\n"
        "- NEVER mention system tools, APIs, or internal software to the caller\n"
        "- NEVER discuss pricing or estimates - direct to sales team during business hours\n"
        "- NEVER invent information - if unsure, say our team will follow up\n"
        "- ONLY collect information needed for routing or dispatch\n"
        "- ALWAYS recommend calling 911 for any immediate life-safety situation\n\n"
        "INTEGRATION CONSTRAINTS\n"
        "=======================\n"
        + con_text + "\n\n"
        "PENDING CLARIFICATIONS\n"
        "======================\n"
        + unk_text + "\n"
    )

    return {
        "agent_name": company.replace(" ", "_").lower() + "_clara_agent",
        "voice_style": "Professional, calm, and empathetic",
        "language": "en-US",
        "system_prompt": system_prompt,
        "key_variables": {
            "company_name": company,
            "business_hours": {"days": days, "start": start, "end": end, "timezone": tz},
            "emergency_definitions": emergencies,
            "services_supported": services,
            "phone_number": phone,
            "office_address": address,
            "transfer_timeout_seconds": timeout
        },
        "call_transfer_protocol": {
            "primary_number": primary,
            "secondary_number": secondary,
            "timeout_seconds": timeout,
            "max_attempts": 2 if secondary else 1
        },
        "fallback_protocol": {
            "message": fail_msg,
            "log_required_fields": ["caller_name", "caller_phone", "call_reason", "timestamp"]
        },
        "integration_constraints": constraints,
        "pending_clarifications": unknowns,
        "version": version,
        "generated_at": datetime.now().isoformat()
    }
