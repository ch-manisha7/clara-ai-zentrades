# Change Log -- Patriot Fire
**Account ID:** `account_001`
**Generated:** 2026-03-05 05:46:09
**Version:** v1 -> v2 (Post-Onboarding Update)

---

## Summary: 7 field(s) updated

### `phone_number`
- **Before (v1):** ``
- **After  (v2):** `704-555-0183`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update

### `emergency_definition`
- **Before (v1):** `['Active sprinkler water discharge', 'Fire alarm triggered and cannot be silenced']`
- **After  (v2):** `['Active sprinkler water discharge', 'Fire alarm triggered and cannot be silenced', 'Visible smoke reported']`
- **Confidence:** keyword_detected -> confirmed
- **Reason:** onboarding update

### `after_hours_flow_summary`
- **Before (v1):** `Greet caller and identify purpose. If emergency: collect name, phone, address immediately then attempt transfer with 45s timeout. If transfer fails: apologize and confirm callback within 15 minutes. If non-emergency: collect details and confirm next-business-day follow-up.`
- **After  (v2):** `Greet caller and identify purpose. If emergency: collect name, phone, address immediately then attempt transfer to 704-555-0183 with 45s timeout. If transfer fails: apologize and confirm callback within 15 minutes. If non-emergency: collect details and confirm next-business-day follow-up.`
- **Confidence:** generated -> confirmed
- **Reason:** onboarding update

### `call_transfer_rules.secondary_number`
- **Before (v1):** ``
- **After  (v2):** `704-555-0217`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update

### `call_transfer_rules.primary_number`
- **Before (v1):** ``
- **After  (v2):** `704-555-0183`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update

### `call_transfer_rules.timeout_seconds`
- **Before (v1):** ``
- **After  (v2):** `45`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update

### `company_name`
- **Before (v1):** `Patriot Fire Protection`
- **After  (v2):** `Patriot Fire`
- **Confidence:** extracted -> confirmed
- **Reason:** onboarding update
