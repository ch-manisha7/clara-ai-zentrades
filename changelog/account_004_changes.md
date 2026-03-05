# Change Log -- Cascade Sprinkler Systems
**Account ID:** `account_004`
**Generated:** 2026-03-05 05:46:09
**Version:** v1 -> v2 (Post-Onboarding Update)

---

## Summary: 7 field(s) updated

### `phone_number`
- **Before (v1):** ``
- **After  (v2):** `206-555-0178`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update

### `services_supported`
- **Before (v1):** `['Fire Sprinkler', 'Fire Alarm', 'Inspection']`
- **After  (v2):** `['Fire Sprinkler', 'Fire Alarm', 'Inspection', 'Monitoring', 'Fire Extinguisher']`
- **Confidence:** keyword_detected -> confirmed
- **Reason:** onboarding update

### `emergency_definition`
- **Before (v1):** `[]`
- **After  (v2):** `['Fire alarm triggered and cannot be silenced', 'Visible smoke reported']`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update

### `after_hours_flow_summary`
- **Before (v1):** `Greet caller and identify purpose. If emergency: collect name, phone, address immediately then attempt transfer with 45s timeout. If transfer fails: apologize and confirm callback within 15 minutes. If non-emergency: collect details and confirm next-business-day follow-up.`
- **After  (v2):** `Greet caller and identify purpose. If emergency: collect name, phone, address immediately then attempt transfer to 206-555-0178 with 30s timeout. If transfer fails: apologize and confirm callback within 15 minutes. If non-emergency: collect details and confirm next-business-day follow-up.`
- **Confidence:** generated -> confirmed
- **Reason:** onboarding update

### `call_transfer_rules.secondary_number`
- **Before (v1):** ``
- **After  (v2):** `206-555-0341`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update

### `call_transfer_rules.primary_number`
- **Before (v1):** ``
- **After  (v2):** `206-555-0178`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update

### `call_transfer_rules.timeout_seconds`
- **Before (v1):** ``
- **After  (v2):** `30`
- **Confidence:** demo_assumed -> confirmed
- **Reason:** onboarding update
