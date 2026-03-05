# Change Log -- Arctic Air HVAC Solutions
**Account ID:** `account_002`
**Generated:** 2026-03-05 05:46:09
**Version:** v1 -> v2 (Post-Onboarding Update)

---

## Summary: 7 field(s) updated

### `phone_number`
- **Before (v1):** ``
- **After  (v2):** `214-555-0094`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update

### `emergency_definition`
- **Before (v1):** `['No heat', 'No air conditioning', 'Refrigerant leak detected']`
- **After  (v2):** `['No heat', 'No air conditioning', 'Refrigerant leak detected', 'Carbon monoxide alarm triggered']`
- **Confidence:** keyword_detected -> confirmed
- **Reason:** onboarding update

### `after_hours_flow_summary`
- **Before (v1):** `Greet caller and identify purpose. If emergency: collect name, phone, address immediately then attempt transfer with 45s timeout. If transfer fails: apologize and confirm callback within 15 minutes. If non-emergency: collect details and confirm next-business-day follow-up.`
- **After  (v2):** `Greet caller and identify purpose. If emergency: collect name, phone, address immediately then attempt transfer to 214-555-0331 with 60s timeout. If transfer fails: apologize and confirm callback within 15 minutes. If non-emergency: collect details and confirm next-business-day follow-up.`
- **Confidence:** generated -> confirmed
- **Reason:** onboarding update

### `call_transfer_rules.secondary_number`
- **Before (v1):** ``
- **After  (v2):** `214-555-0448`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update

### `call_transfer_rules.primary_number`
- **Before (v1):** ``
- **After  (v2):** `214-555-0331`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update

### `call_transfer_rules.timeout_seconds`
- **Before (v1):** ``
- **After  (v2):** `60`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update

### `non_emergency_routing_rules`
- **Before (v1):** ``
- **After  (v2):** `Collect caller name, phone number, and description of request. Confirm team will follow up next business day.`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update
