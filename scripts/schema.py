def field(value="", confidence="demo_assumed"):
    return {"value": value, "confidence": confidence}


def empty_account_memo(account_id):
    return {
        "account_id": account_id,
        "company_name": field(),
        "business_hours": {
            "days": field(),
            "start": field(),
            "end": field(),
            "timezone": field()
        },
        "office_address": field(),
        "phone_number": field(),
        "services_supported": field([]),
        "emergency_definition": field([]),
        "emergency_routing_rules": field(),
        "non_emergency_routing_rules": field(),
        "call_transfer_rules": {
            "primary_number": field(),
            "secondary_number": field(),
            "timeout_seconds": field(),
            "retries": field(),
            "failure_message": field()
        },
        "integration_constraints": field([]),
        "after_hours_flow_summary": field(),
        "office_hours_flow_summary": field(),
        "questions_or_unknowns": [],
        "notes": field()
    }
