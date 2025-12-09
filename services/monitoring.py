from dataclasses import dataclass, field

@dataclass
class Metrics:
    ingested_count: int = 0
    error_count: int = 0
    sources_active: int = 0
    last_run_status: str = "Not started"
    last_run_time: str = None

metrics = Metrics()

def increment_ingested():
    metrics.ingested_count += 1

def increment_error():
    metrics.error_count += 1

def set_last_run_status(status: str):
    metrics.last_run_status = status
    from datetime import datetime
    metrics.last_run_time = datetime.utcnow().isoformat()

def get_metrics():
    return metrics
