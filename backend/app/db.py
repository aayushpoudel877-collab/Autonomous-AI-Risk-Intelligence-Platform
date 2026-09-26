import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Float, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL=os.getenv("DATABASE_URL","sqlite:///./data/risk.db")
connect_args={"check_same_thread":False} if DATABASE_URL.startswith("sqlite") else {}
engine=create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal=sessionmaker(bind=engine)

class Base(DeclarativeBase): pass

class RiskEvent(Base):
    __tablename__="risk_events"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    source: Mapped[str]=mapped_column(String(200))
    risk_score: Mapped[float]=mapped_column(Float)
    risk_level: Mapped[str]=mapped_column(String(20))
    confidence: Mapped[float]=mapped_column(Float)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))

def init_db():
    Base.metadata.create_all(engine)
