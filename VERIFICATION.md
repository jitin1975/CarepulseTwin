# Verification Report — CarePulse Twin / eICU Demo

## Dataset

Supplied file: `eicu-collaborative-research-database-demo-2.0.zip`

Inspected archive contents and confirmed the presence of:
- patient.csv.gz
- vitalPeriodic.csv.gz
- vitalAperiodic.csv.gz

Observed in the supplied demo:
- 2,520 patient-unit rows in patient.csv.gz
- 1,634,960 rows in vitalPeriodic.csv.gz
- 2,375 unique patient-unit stays with periodic vitals
- 126 rows with `unitdischargestatus = Expired`

## Data preparation

The actual `data.prepare` script was run successfully against decompressed
copies of the supplied demo tables.

Output:
- train: 60,238 windows, positive rate 25.73%
- validation: 12,417 windows, positive rate 22.49%
- test: 14,691 windows, positive rate 20.12%

The script uses patient-level splits and requires 24 consecutive hourly
observations for a sequence.

## ML training

The actual `ml.train` script was run for 6 epochs against those prepared
sequences.

Final held-out test metrics:

- ROC-AUC: 0.84425
- PR-AUC: 0.65672
- F1: 0.60619
- Precision: 0.56880
- Recall: 0.64885
- Threshold: 0.41376
- Confusion matrix: [[10281, 1454], [1038, 1918]]

The trained checkpoint is included at:

`ml/artifacts/carepulse_lstm_eicu_demo.pt`

## Model loading / inference

Checkpoint loading was executed successfully and a forward pass over test
windows returned the expected binary-risk output shape.

## Python tests

```text
3 passed in 1.24s
```

## Syntax checks

Python compilation passed for the main data, ML, backend and replay modules.

## Infrastructure limitation

Docker is not installed in the current execution environment, so the live
PostgreSQL + Redis + Kafka deployment could not be started here. The service
configuration and integration code are included, but this report does NOT
claim that the live distributed pipeline was executed in this environment.

The actual end-to-end latency is therefore intentionally NOT claimed as 96 ms.
Use `scripts/benchmark_e2e.py` after starting the services to obtain a real
measurement.
