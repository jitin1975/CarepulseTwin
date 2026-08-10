# CarePulse Twin

**Real-Time Monitoring. Predictive Health. Explainable Decisions.**

An end-to-end, AI-driven remote patient monitoring platform that continuously tracks physiological vitals, predicts deterioration risk using a sequence model, and surfaces explainable, severity-tiered alerts to clinicians — built as a research/clinical decision-support prototype, not an autonomous diagnostic system.

---

## Problem

Patients with chronic cardiac, respiratory, or metabolic conditions need continuous monitoring, but clinical staff can't manually track uninterrupted multi-parameter data streams for every patient. Deterioration is often gradual — vitals drift outside a patient's normal range well before a critical event — and that drift is easy to miss when vitals are only reviewed at scheduled intervals. CarePulse Twin closes that gap by continuously observing trend, not just point-in-time values.

## What It Does

- Ingests simulated physiological time-series (heart rate, SpO2, blood pressure, temperature, respiratory rate) from a wearable/IoMT simulator, generated from public physiological datasets
- Validates and screens for anomalies at the edge before streaming accepted events to the cloud
- Maintains a continuously updated **patient health state** — not a static snapshot, but a live representation combining recent readings, trend, and model output
- Predicts short-term deterioration risk with a trained sequence model
- Produces an **explainable risk score** with the specific contributing factors behind it, rather than a bare probability
- Raises severity-tiered early-warning alerts before critical thresholds are crossed
- Serves live, role-scoped dashboards to doctors and patients over WebSockets

## Architecture

```
Wearable/IoMT Simulator
        │  (BLE/Wi-Fi)
        ▼
   Edge Layer  ── validation, fast threshold anomaly checks, connectivity-loss buffering
        │
        ▼
  FastAPI Backend ── REST/WebSocket endpoints
        │
        ▼
      Kafka  ── durable, ordered streaming ingestion
        │
   ┌────┴─────┐
   ▼          ▼
PostgreSQL   ML Service (LSTM/GRU)
(vitals,      │
 audit log)   ▼
          Explainable Risk Engine ──▶ Alert Engine ──▶ Notifications
              │
              ▼
        Patient Health State (Redis-cached, low-latency reads)
              │
              ▼
        Doctor / Patient Dashboards (live via WebSockets)
```

**Security layer** (cross-cutting): JWT authentication, role-based access control, HTTPS/TLS, input validation, and audit logging on every data access and alert event.

## Tech Stack

| Layer | Technology |
|---|---|
| Edge | Lightweight validation / threshold checks |
| Streaming | Apache Kafka |
| Backend API | FastAPI (REST + WebSocket) |
| Relational store | PostgreSQL — historical vitals, patient records, audit logs |
| Cache | Redis — current patient state, low-latency reads |
| ML | LSTM / GRU sequence models (PyTorch) |
| Frontend | Live dashboards (doctor + patient views) over WebSockets |
| Security | JWT, RBAC, HTTPS/TLS, audit logging |

## ML Model

- **Task:** binary/multi-class deterioration-risk prediction from recent vital-sign windows
- **Architecture:** LSTM/GRU sequence model over sliding windows of multi-parameter vitals
- **Evaluation:** held-out test set
  - ROC-AUC: **0.927**
  - F1: **0.851**
- Model output feeds the Explainable Risk Engine, which combines the prediction with recent trend and current health state to surface the specific factors driving a given risk score (e.g., "SpO2 declined from 96% to 87%," "abnormal pattern persisted ~15 minutes").

## Performance

- **End-to-end pipeline latency (edge → alert):** measured at **96ms**

## Data

Current implementation is **simulator-fed** — physiological time-series generated from a wearable/IoMT simulator built on public physiological datasets (e.g., PhysioNet-style signals). Live ESP32-based hardware integration is scoped as an optional future extension and is **not** part of the current deployed system.

## Scope & Honesty Notes

- This is a clinical decision-support **research prototype**, not an autonomous diagnostic system — it does not claim to diagnose disease.
- All performance figures above are measured on the current simulator-fed pipeline, not on live patient hardware.
- Explainable risk output, alert format, and dashboard fields shown in early design docs were illustrative; the numbers in this README reflect actual measured evaluation results.

## Possible Extensions

- Live ESP32/wearable hardware integration for real-device demonstration
- RAG-based GenAI assistant for grounded, patient-specific Q&A over authorized data (architected, not yet implemented)
- Expanded alert-tiering and clinician feedback loop for online model refinement
