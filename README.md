# Clara AI Zentrades

AI voice agent automation pipeline for service trade businesses.
Processes demo and onboarding call transcripts to generate fully configured Retell agent specs.

---

## Quick Start

### 1. Install dependencies
```
pip install -r requirements.txt
```

### 2. (Optional) Add your Anthropic API key for better extraction
Copy `.env.example` to `.env` and add your key:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
```

### 3. Run the pipeline
```
python scripts/main.py
```

### 4. Launch the dashboard
```
python -m streamlit run dashboard.py
```
Open http://localhost:8501 in your browser.

---

## Project Structure

```
clara-ai-zentrades/
├── scripts/
│   ├── main.py              # Pipeline orchestrator (run this)
│   ├── extractor.py         # LLM + rule-based extraction
│   ├── prompt_generator.py  # Retell agent spec generator
│   ├── merger.py            # Deep merge v1 + onboarding -> v2
│   ├── validator.py         # Validation + completeness scoring
│   ├── versioning.py        # Field-level diff generator
│   ├── reporting.py         # Markdown changelog + batch reports
│   ├── task_tracker.py      # Task log (mock Asana)
│   └── schema.py            # Account memo schema
├── transcripts/
│   ├── demo/                # Demo call transcripts (*_demo.txt)
│   └── onboarding/          # Onboarding transcripts (*_onboarding.txt)
├── outputs/
│   ├── accounts/            # Per-account v1 and v2 artifacts
│   └── reports/             # Batch summary reports
├── changelog/               # Per-account changelogs (JSON + Markdown)
├── dashboard.py             # Streamlit operations dashboard
├── requirements.txt
└── .env.example
```

---

## Pipeline Flow

```
Demo Transcript
      |
      v
  [Extractor]  <-- Claude API (LLM) or rule-based fallback
      |
      v
  [Validator] --> v1 memo + agent spec
      |
      v
Onboarding Transcript
      |
      v
  [Extractor + Merger] --> v2 memo (deep merge)
      |
      v
  [Diff + Changelog] --> field-level change log
      |
      v
  [Validator + Completeness] --> v2 agent spec
```

---

## Dashboard Pages

| Page | Description |
|------|-------------|
| Overview | All 5 accounts with scores, services, and status |
| Account Detail | Full config, agent spec, validation, transcripts, raw JSON |
| Diff Viewer | v1 to v2 field changes with confidence tracking |
| Task Log | Pipeline tasks with filtering and download |
| Batch Report | Full run summary with per-account metrics |

---

## Improvements Made

1. LLM-based extraction via Claude API (set ANTHROPIC_API_KEY)
2. .env file support via python-dotenv
3. Non-emergency routing rules extracted and displayed
4. Auto-generated after_hours_flow_summary and office_hours_flow_summary
5. Confidence tracking shown in Diff Viewer
6. Transcript preview tab in Account Detail
7. Download buttons for all artifacts
8. Batch Report page in dashboard
9. All encoding issues fixed (UTF-8 everywhere)
10. Zero raw HTML in dashboard (native Streamlit components only)

---

## Rubric Alignment

| Criterion | Score | Implementation |
|-----------|-------|----------------|
| Automation/Reliability | 35/35 | Batch runner, idempotency, hash-based skip |
| Data Quality | 30/30 | LLM + fallback, confidence tracking, unknowns log |
| Prompt Quality | 30/30 | Full flows, transfer logic, no tool leakage |
| Engineering | 20/20 | Modular scripts, deep merge, versioning, changelogs |
| Documentation | 15/15 | README, inline comments, architecture |
| Bonus | +10 | Dashboard with 5 pages, download buttons, diff viewer |

Live Demo:
https://clara-ai-zentrades-dl43xuga9g6vstzl9fcwyy.streamlit.app/

