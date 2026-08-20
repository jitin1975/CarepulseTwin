CREATE TABLE IF NOT EXISTS vitals(id BIGSERIAL PRIMARY KEY,patient_id TEXT,ts TIMESTAMPTZ,heart_rate FLOAT,spo2 FLOAT,systolic_bp FLOAT,diastolic_bp FLOAT,temperature FLOAT,respiratory_rate FLOAT,anomaly_flags JSONB,UNIQUE(patient_id,ts));
CREATE TABLE IF NOT EXISTS alerts(id BIGSERIAL PRIMARY KEY,patient_id TEXT,ts TIMESTAMPTZ,severity TEXT,risk FLOAT,factors JSONB,message TEXT);

CREATE TABLE IF NOT EXISTS audit_log (
 id BIGSERIAL PRIMARY KEY, actor VARCHAR(128), action VARCHAR(128) NOT NULL,
 patient_id VARCHAR(64), ts TIMESTAMPTZ NOT NULL DEFAULT NOW(), metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
