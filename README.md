# Clinical Decision Making and Pattern Recognition

Agentic claim audit system for healthcare payment integrity. Combines LangGraph orchestration with classification, provider clustering, and spend anomaly detection across Treatment, Payment, and Operations (TPO).

## Overview

TPO Pattern Intelligence Copilot runs medical claims through a deterministic LangGraph pipeline. Each claim is extracted, validated against billing policy, scored for payment risk, compared to provider billing patterns, and checked for spend anomalies. A confidence router either auto-resolves the claim or escalates it to a human auditor with a structured evidence payload.

Built for prepay review workflows where explainability, audit trails, and human-in-the-loop controls matter as much as automation speed.

## Architecture

```mermaid
flowchart TB
    subgraph input [Input]
        Claim[ClaimCase]
        Note[ClinicalNote]
        Codes[CPT_and_ICD10]
    end

    subgraph graph [LangGraph Pipeline]
        Extractor[ExtractorNode]
        Policy[PolicyNode]
        Classifier[PaymentRiskClassifier]
        Cluster[ProviderPatternCluster]
        Anomaly[TimeSeriesAnomaly]
        Scorer[ConfidenceScorer]
        Finalize[FinalizeNode]
    end

    subgraph output [Output]
        Auto[AutoResolve]
        Human[HumanEscalation]
        TPO[TPORecommendations]
        Trace[ExecutionTrace]
    end

    Claim --> Extractor
    Note --> Extractor
    Codes --> Policy
    Extractor --> Policy
    Policy --> Classifier
    Classifier --> Cluster
    Cluster --> Anomaly
    Anomaly --> Scorer
    Scorer --> Finalize
    Finalize --> Auto
    Finalize --> Human
    Finalize --> TPO
    graph --> Trace
```

**Pipeline stages**

| Stage | What it does |
|-------|----------------|
| Extractor | Pulls structured facts from clinical documentation via LLM (regex fallback offline) |
| Policy | Validates billed CPT against documented time and complexity rules |
| Payment Risk | RandomForest classifier scores prepay integrity risk |
| Provider Patterns | KMeans clustering flags aberrant provider billing behavior |
| Spend Anomaly | Z-score detection on monthly member claim spend |
| Confidence Scorer | Fuses all signals into a routing confidence score |
| Finalize | Auto-resolve at ≥90% confidence, or emit escalation JSON for analysts |

## Quick Start

```bash
git clone https://github.com/prashantsonibps/Clinical-Decision-making-and-Pattern-Recognition.git
cd Clinical-Decision-making-and-Pattern-Recognition

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add OPENAI_API_KEY to .env

python poc/data/generate_synthetic_data.py
python poc/models/train_models.py
streamlit run poc/app.py
```

Models train automatically on first launch if missing. Sample data ships with the repo.

## Sample Cases

| Case | Scenario | Result |
|------|----------|--------|
| CASE-001 | E/M upcoding — CPT 99215 with 15 min documented | Escalated |
| CASE-002 | Home health billing burst + spend spike | Escalated |
| CASE-003 | Same-day high E/M + home visit pairing | Escalated |
| CASE-004 | Properly documented moderate visit | Auto-resolved |

## Project Layout

```
poc/
├── app.py                  # Streamlit UI
├── config.py
├── agent/
│   ├── graph.py            # LangGraph state machine
│   ├── nodes.py            # Pipeline nodes
│   ├── state.py            # Graph state schema
│   └── tools.py            # Extraction, policy, scoring
├── analytics/
│   ├── classifier.py       # Payment risk model
│   ├── clustering.py       # Provider pattern clusters
│   └── anomaly.py          # Spend anomaly detection
├── data/                   # Synthetic claims + sample cases
└── models/                 # Trained model artifacts
```

## Data

All claim data is synthetic. No PHI is used. Record structures follow standard professional claim fields (member, provider, CPT, ICD-10, allowed amount, service date).

## Stack

- LangGraph — stateful agent pipeline with auditable execution traces
- OpenAI — clinical fact extraction
- scikit-learn — classification and clustering
- Streamlit — interactive audit dashboard
- Plotly — risk gauges and spend charts

## License

MIT
