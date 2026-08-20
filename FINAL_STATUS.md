# CarePulse Twin — Final Status

## Verified against the included official eICU-CRD Demo v2.0 data

The included trained checkpoint is `ml/artifacts/carepulse_lstm.pt`.

Held-out test metrics from the included run:

- ROC-AUC: 0.8438
- PR-AUC: 0.6518
- F1: 0.6027
- Precision: 0.6028
- Recall: 0.6026
- Test windows: 14,640
- Positive test windows: 2,944

These are research-prototype metrics on the eICU demo, not clinical validation.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d
uvicorn backend.main:app --reload --port 8000
```

In another terminal:

```bash
python -m http.server 3000 --directory frontend
```

Open `http://localhost:3000`.

Replay an included eICU demo patient after infrastructure is running:

```bash
python -m replay.list_patients --eicu-dir data/eicu --n 10
python -m replay.replay --eicu-dir data/eicu --patient-id <ID> --api http://localhost:8000 --speed 60
```

## Important

The complete Kafka/PostgreSQL/Redis/WebSocket deployment has not been executed in the packaging environment because Docker services were unavailable there. The project contains the integration code and benchmark script, but do not claim an end-to-end latency number until it is measured on the deployed stack.
