# CarePulse Twin — Full Runnable Prototype

Research/clinical decision-support prototype for simulated remote patient monitoring. It is not a medical device and must not be used for diagnosis or treatment.

## Run
1. `cp .env.example .env`
2. `docker compose up --build`
3. Train model locally: `python -m ml.train --epochs 10`
4. Start simulator: `python -m simulator.simulator --api http://localhost:8000 --patient-id P001`
5. API docs: http://localhost:8000/docs
6. Dashboard: `python -m http.server 3000 --directory frontend` then http://localhost:3000

The included ML dataset is synthetic. Run training to get your own ROC-AUC/F1. The 0.927/0.851 and 96 ms numbers in the project description are not hard-coded claims here.

### Components
- Edge validation and threshold screening
- Kafka ingestion
- FastAPI REST + WebSocket API
- PostgreSQL historical vitals/alerts/audit-ready schema
- Redis live patient state
- PyTorch LSTM sequence model
- Explainable rule/trend factors
- Severity-tiered alerts
- JWT/RBAC scaffold
- Wearable/IoMT simulator
- Benchmark helper

### Production work still needed
TLS, Kafka auth, secrets management, PHI controls, encryption/backups, rate limiting, observability, model calibration, prospective validation, governance, compliance and clinical review.
