from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field, field_validator
class VitalReading(BaseModel):
    patient_id: str = Field(min_length=1,max_length=64)
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    heart_rate: float = Field(ge=20,le=250)
    spo2: float = Field(ge=50,le=100)
    systolic_bp: float = Field(ge=50,le=250)
    diastolic_bp: float = Field(ge=20,le=180)
    temperature: float = Field(ge=30,le=45)
    respiratory_rate: float = Field(ge=2,le=80)
    @field_validator('ts')
    @classmethod
    def normalize_ts(cls,v): return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
class IngestResponse(BaseModel):
    accepted: bool
    anomaly_flags: list[str]
    event_id: str
class HealthState(BaseModel):
    patient_id: str; ts: datetime; risk: float
    severity: Literal['LOW','MEDIUM','HIGH','CRITICAL']
    factors: list[str]; vitals: dict; model_available: bool
