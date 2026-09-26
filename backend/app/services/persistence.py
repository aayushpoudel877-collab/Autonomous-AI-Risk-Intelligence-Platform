from backend.app.db import RiskEvent, SessionLocal

def save_risk_event(result):
    with SessionLocal() as session:
        event=RiskEvent(source=result.source,risk_score=result.risk_score,risk_level=result.risk_level,confidence=result.confidence)
        session.add(event); session.commit(); session.refresh(event)
        return event

def recent_events(limit:int=20):
    with SessionLocal() as session:
        return session.query(RiskEvent).order_by(RiskEvent.id.desc()).limit(limit).all()
