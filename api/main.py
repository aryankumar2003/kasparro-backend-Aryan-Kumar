from fastapi import FastAPI
from api.routes import router as api_router
from core.config import settings
from core.logging_config import setup_logging
from services.database import init_db
from prometheus_fastapi_instrumentator import Instrumentator

setup_logging()

app = FastAPI(title=settings.PROJECT_NAME)


Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
def on_startup():
    
    
    init_db()

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to the Data Ingestion API"}
