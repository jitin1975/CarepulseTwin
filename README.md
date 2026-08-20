# CarePulse Twin — eICU-CRD Demo, End-to-End Prototype

**Real-Time Monitoring. Predictive Health. Explainable Decisions.**

CarePulse Twin is a research/clinical-decision-support prototype using the
official **eICU Collaborative Research Database Demo v2.0** supplied by the
user. The website is an original premium product UI; the backend replays
historical eICU observations as a live stream.

## What was actually run on the supplied dataset

The supplied archive was inspected and contains 33 files, including:
`patient.csv.gz`, `vitalPeriodic.csv.gz`, and `vitalAperiodic.csv.gz`.
The demo contains 2,520 patient-unit rows and 1,634,960 periodic-vital rows;
126 patient-unit rows have `unitdischargestatus = Expired`.

The final ML target was changed from mortality to a more direct deterioration
signal:

> Given the previous 24 hourly observations, predict whether a qualifying
> physiological abnormality occurs during the **following 6 hours**.

A qualifying abnormality is one of:
- SpO2 < 88%
- heart rate > 130 bpm
- respiratory rate > 30/min
- systolic BP < 90 mmHg

The label is strictly future-looking relative to the prediction time. It is a
research label, not a diagnosis.

### Actual held-out test result from the supplied demo

- ROC-AUC: **0.8442**
- PR-AUC: **0.6567**
- F1: **0.6062**
- Precision: **0.5688**
- Recall: **0.6488**
- Test windows: **14,691**
- Positive test windows: **2,956**
- Validation-selected threshold: **0.4138**

These are the results of the included trained checkpoint in
`ml/artifacts/carepulse_lstm_eicu_demo.pt`.

## ML pipeline

```text
eICU vitalPeriodic + vitalAperiodic
             |
             v
      Hourly aggregation
             |
      Missing-value handling
             |
      24-hour sequences
             |
      Patient-level split
             |
             v
       PyTorch LSTM
             |
      deterioration risk
             |
      severity + explanation
```

Model:
- 24 time steps
- 6 features: HR, SpO2, systolic BP, diastolic BP, temperature, respiratory rate
- 1-layer LSTM, hidden size 48
- small dense prediction head
- balanced training subset to address class imbalance
- threshold selected on validation data

## Real-time architecture

```text
Historical eICU patient
        |
        v
Replay service
        |
        v
Edge validation
        |
        v
FastAPI
        |
        v
Kafka
        |
        v
Inference consumer
   |          |
   v          v
Postgres     LSTM
   |          |
   |          v
   |      Risk + explanation
   |          |
   +------> Alert engine
              |
              v
             Redis
              |
              v
          WebSocket
              |
              v
       CarePulse website
```

## Website

The frontend is a complete original CarePulse UI with:
- premium responsive layout
- animated hero
- live patient monitor
- risk visualization
- vital cards
- explainability panel
- architecture visualization
- model metrics
- alert cards
- research-scope section
- responsive navigation
- demo modal
- simulated values when the backend is offline
- WebSocket integration when the backend is online

Run it:

```bash
python -m http.server 3000 --directory frontend
```

Open `http://localhost:3000`.

To point the UI at a patient replay, use for example:
`http://localhost:3000/?patient=141765`.

## Run the real ML model immediately

The supplied demo has already been processed and the trained checkpoint is
included. You can inspect the saved metrics at:

```text
ml/artifacts/metrics.json
```

For a fresh training run, extract the supplied eICU demo so that the three
required files are available as CSVs:

```text
data/eicu/
  patient.csv
  vitalPeriodic.csv
  vitalAperiodic.csv
```

Then:

```bash
python -m data.prepare --eicu-dir data/eicu --out data/processed
python -m ml.train \
  --data data/processed/sequences.npz \
  --out ml/artifacts/carepulse_lstm.pt \
  --epochs 6
```

## Run infrastructure

Create `.env` from `.env.example`, then:

```bash
docker compose up -d
```

Start API:

```bash
uvicorn backend.main:app --reload --port 8000
```

Check:

```text
http://localhost:8000/health
```

## Replay a real eICU patient

After extracting the demo CSV files:

```bash
python -m replay.list_patients --eicu-dir data/eicu --n 10
```

Then:

```bash
python -m replay.replay \
  --eicu-dir data/eicu \
  --patient-id 141765 \
  --api http://localhost:8000 \
  --speed 120
```

The replay converts historical observations into timestamped events and sends
them through the same ingestion endpoint used by the streaming system.

## End-to-end latency

Do not claim a 96 ms latency unless it is measured on the running deployment.
The benchmark script is:

```bash
python scripts/benchmark_e2e.py
```

It is intended to measure the actual deployed ingestion-to-state path.

## Security

The backend includes:
- JWT bearer authentication scaffold
- role checks for doctor/patient endpoints
- input validation
- PostgreSQL audit logging
- HTTPS/TLS deployment as an infrastructure responsibility

`AUTH_DISABLED=true` is provided only for local demonstration.
Set it to `false` and use a real secret before any non-local deployment.

## Clinical / research scope

This is **not an autonomous diagnostic system** and does not prescribe
therapy. eICU is ICU data, not a wearable population. The real-time behavior
is demonstrated by replaying historical data. External validation is required
before any clinical use.

## Reproducibility note

The full eICU-CRD is credentialed-access data. This repository contains the
trained artifact and processed demo data generated from the supplied official
eICU demo archive, not the restricted full dataset.
