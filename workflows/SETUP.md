# n8n Workflow Setup Guide

## Option A: Run Python Pipeline (Recommended for Zero-Cost)

The Python pipeline (`scripts/main.py`) is the primary automation layer and fully reproduces the workflow.

```bash
# 1. Install dependencies
pip install streamlit

# 2. Set your API key (optional — enables LLM extraction)
export ANTHROPIC_API_KEY=your_key_here

# 3. Run the batch pipeline
cd clara-ai-assignment
python scripts/main.py

# 4. Launch the dashboard
streamlit run dashboard.py
```

---

## Option B: n8n Workflow Import

### Prerequisites
- Docker installed
- Node.js 18+

### Setup
```bash
# Start n8n locally
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Open browser: http://localhost:5678
```

### Import Workflow
1. Open n8n at `http://localhost:5678`
2. Click "New Workflow" → "Import from JSON"
3. Upload `workflows/clara_pipeline.json`
4. Configure credentials:
   - Add `ANTHROPIC_API_KEY` in Settings → Credentials
   - Set `TRANSCRIPTS_DEMO` env variable to your transcript folder path

### Environment Variables
```
ANTHROPIC_API_KEY=sk-ant-xxxx     # Required for LLM extraction
TRANSCRIPTS_DEMO=./transcripts/demo
TRANSCRIPTS_ONBOARDING=./transcripts/onboarding
OUTPUT_BASE=./outputs/accounts
```

### Run the Workflow
1. Drop a `*_demo.txt` file into `transcripts/demo/`
2. The workflow triggers automatically
3. Outputs appear in `outputs/accounts/<account_id>/v1/`
4. Drop a `*_onboarding.txt` file to trigger v2 generation

---

## Pipeline Architecture

```
transcripts/demo/*.txt
        │
        ▼
   [main.py / n8n]
        │
        ├── extractor.py  ──── Claude API (LLM) ────► memo.json (v1)
        │                       └── rule-based fallback
        │
        ├── prompt_generator.py ────────────────────► agent_spec.json (v1)
        │
        ├── validator.py ───────────────────────────► validation.json
        │
        ├── task_tracker.py ────────────────────────► task_log.json
        │
transcripts/onboarding/*.txt
        │
        ▼
        ├── extractor.py  ──── Claude API ──────────► extracted onboarding
        │
        ├── merger.py (deep merge) ─────────────────► memo.json (v2)
        │
        ├── versioning.py (diff) ───────────────────► changes.json + changes.md
        │
        └── prompt_generator.py ────────────────────► agent_spec.json (v2)
```

---

## Output Structure

```
outputs/
├── accounts/
│   └── account_001/
│       ├── v1/
│       │   ├── memo.json              # Extracted config from demo
│       │   ├── agent_spec.json        # Retell-ready agent config
│       │   ├── validation.json        # Validation results
│       │   ├── completeness.json      # % fields filled
│       │   └── transcript_hash.txt    # Idempotency hash
│       └── v2/
│           └── ... (same files, updated from onboarding)
├── task_log.json                      # Task tracker items
└── reports/
    ├── batch_summary.md
    └── batch_results.json

changelog/
├── account_001_changes.json
├── account_001_changes.md
└── ...
```
