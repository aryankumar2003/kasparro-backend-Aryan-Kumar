from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    
    import schemas.database_models
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
