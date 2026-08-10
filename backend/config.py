import os
from dataclasses import dataclass
@dataclass(frozen=True)
class Settings:
    postgres_dsn: str = (f"postgresql+psycopg://{os.getenv('POSTGRES_USER','carepulse')}:"
        f"{os.getenv('POSTGRES_PASSWORD','carepulse')}@{os.getenv('POSTGRES_HOST','localhost')}:"
        f"{os.getenv('POSTGRES_PORT','5432')}/{os.getenv('POSTGRES_DB','carepulse')}")
    redis_url: str = os.getenv('REDIS_URL','redis://localhost:6379/0')
    kafka_bootstrap: str = os.getenv('KAFKA_BOOTSTRAP_SERVERS','localhost:9092')
    kafka_topic: str = os.getenv('KAFKA_TOPIC','vitals')
    model_path: str = os.getenv('MODEL_PATH','ml/artifacts/carepulse_lstm.pt')
    auth_disabled: bool = os.getenv('AUTH_DISABLED','true').lower() == 'true'
    jwt_secret: str = os.getenv('JWT_SECRET','dev-secret')
    jwt_algorithm: str = os.getenv('JWT_ALGORITHM','HS256')
settings = Settings()
