# Change Log -- Sentinel Alarm Services
**Account ID:** `account_005`
**Generated:** 2026-03-05 05:46:09
**Version:** v1 -> v2 (Post-Onboarding Update)

---

## Summary: 6 field(s) updated

### `phone_number`
- **Before (v1):** `404-555-0147`
- **After  (v2):** `404-555-0229`
- **Confidence:** extracted -> confirmed
- **Reason:** onboarding update

### `emergency_definition`
- **Before (v1):** `['Electrical panel failure']`
- **After  (v2):** `['Electrical panel failure', 'Active fire']`
- **Confidence:** keyword_detected -> confirmed
- **Reason:** onboarding update

### `after_hours_flow_summary`
- **Before (v1):** `Greet caller and identify purpose. If emergency: collect name, phone, address immediately then attempt transfer with 45s timeout. If transfer fails: apologize and confirm callback within 15 minutes. If non-emergency: collect details and confirm next-business-day follow-up.`
- **After  (v2):** `Greet caller and identify purpose. If emergency: collect name, phone, address immediately then attempt transfer to 404-555-0318 with 45s timeout. If transfer fails: apologize and confirm callback within 15 minutes. If non-emergency: collect details and confirm next-business-day follow-up.`
- **Confidence:** generated -> confirmed
- **Reason:** onboarding update

### `call_transfer_rules.secondary_number`
- **Before (v1):** ``
- **After  (v2):** `404-555-0147`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update

### `call_transfer_rules.primary_number`
- **Before (v1):** ``
- **After  (v2):** `404-555-0318`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update

### `call_transfer_rules.timeout_seconds`
- **Before (v1):** ``
- **After  (v2):** `45`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update
