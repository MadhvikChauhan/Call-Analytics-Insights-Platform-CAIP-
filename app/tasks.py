
"""Celery tasks with robust logging and error handling."""
from .celery_app import celery
from time import sleep
import random, os, json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from .models import CallRecord, CallInsight, SentimentEnum
from .logger import get_logger

logger = get_logger(__name__)

def _sync_db_url(async_url: str) -> str:
    """Convert async DB URL to sync DB URL for Celery tasks.

    This helper makes a best-effort conversion for simple URLs like sqlite+aiosqlite:///
    and asyncpg-based URLs.
    """
    if async_url.startswith("sqlite+aiosqlite:"):
        return async_url.replace("+aiosqlite", "")
    return async_url.replace("+asyncpg", "")  # naive conversion for example

SYNC_DB_URL = _sync_db_url(settings.DATABASE_URL)
engine = create_engine(SYNC_DB_URL, connect_args={})
Session = sessionmaker(bind=engine)

@celery.task(bind=True)
def process_call_record(self, call_record_id: int):
    """Process a CallRecord by generating a simulated insight and updating the record.

    The function is defensive: it uses try/except to capture errors, logs appropriately,
    and rolls back transactions on failure.
    """
    session = Session()
    try:
        logger.info("Starting processing for CallRecord id=%s", call_record_id)
        cr = session.query(CallRecord).get(call_record_id)
        if not cr:
            logger.error("CallRecord id=%s not found", call_record_id)
            return {"error": "callrecord not found"}

        # Simulate processing time
        sleep(random.uniform(0.5, 2.0))

        # Create CallInsight
        insight = CallInsight(
            call_id=cr.id,
            transcription=f"Simulated transcription for {cr.call_id}",
            sentiment=random.choice(list(SentimentEnum)),
            keywords={"topics": ["support", "billing", "upgrade"]},
            summary="Simulated summary of the call.",
            created_at=datetime.utcnow()
        )
        session.add(insight)
        cr.is_processed = True
        session.add(cr)
        session.commit()
        logger.info("Successfully processed CallRecord id=%s", call_record_id)
        return {"ok": True, "call_id": cr.call_id}
    except Exception as exc:
        logger.exception("Error while processing CallRecord id=%s: %s", call_record_id, exc)
        try:
            session.rollback()
        except Exception:
            logger.exception("Failed to rollback session for CallRecord id=%s", call_record_id)
        raise
    finally:
        session.close()

@celery.task(bind=True)
def generate_company_report(self, company_id: int):
    """Aggregate processed calls for a company and write a JSON report file.

    All unexpected errors are logged with exception level and re-raised.
    """
    session = Session()
    try:
        logger.info("Generating report for company_id=%s", company_id)
        calls = session.query(CallRecord).filter(CallRecord.company_id == company_id, CallRecord.is_processed == True).all()
        total = len(calls)
        avg_duration = sum((c.duration or 0) for c in calls) / total if total else 0
        sentiments = {}
        for c in calls:
            ins = session.query(CallInsight).filter(CallInsight.call_id == c.id).one_or_none()
            s = (ins.sentiment.value if ins and ins.sentiment else 'Unknown')
            sentiments[s] = sentiments.get(s, 0) + 1
        report = {
            "company_id": company_id,
            "total_calls": total,
            "avg_duration": avg_duration,
            "sentiment_distribution": sentiments,
            "generated_at": datetime.utcnow().isoformat()
        }
        reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports', str(company_id))
        os.makedirs(reports_dir, exist_ok=True)
        path = os.path.join(reports_dir, f"report-{int(datetime.utcnow().timestamp())}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        logger.info("Report written to %s", path)
        return {"ok": True, "path": path}
    except Exception as exc:
        logger.exception("Failed to generate report for company_id=%s: %s", company_id, exc)
        raise
    finally:
        session.close()
