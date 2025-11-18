
"""Reports endpoints with logging and error handling."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from deps import get_company_by_api_key, get_db
from models import CallRecord, CallInsight
from tasks import generate_company_report as celery_generate_report
from collections import Counter
from logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/")
async def get_report(company=Depends(get_company_by_api_key), db: AsyncSession = Depends(get_db)):
    """Compute aggregated analytics for the authenticated company.

    This endpoint computes totals, average duration, sentiment distribution,
    and top keywords across processed calls. Exceptions are logged and internal
    errors return HTTP 500.
    """
    try:
        logger.debug("Computing report for company id=%s", getattr(company, 'id', None))
        q = select(CallRecord).where(CallRecord.company_id == company.id, CallRecord.is_processed == True)
        res = await db.execute(q)
        calls = res.scalars().all()
        total = len(calls)
        avg_duration = sum((c.duration or 0) for c in calls) / total if total else 0
        sentiments = Counter()
        keywords = Counter()
        for c in calls:
            q2 = select(CallInsight).where(CallInsight.call_id == c.id)
            r2 = await db.execute(q2)
            ins = r2.scalars().first()
            if ins:
                sentiments.update([ins.sentiment.value if ins.sentiment else 'Unknown'])
                if isinstance(ins.keywords, dict):
                    for _, vals in ins.keywords.items():
                        if isinstance(vals, list):
                            keywords.update(vals)
        top_keywords = [k for k,_ in keywords.most_common(5)]
        logger.info("Report computed for company id=%s: total=%s", company.id, total)
        return {
            "total_calls": total,
            "avg_duration": avg_duration,
            "sentiment_distribution": dict(sentiments),
            "top_keywords": top_keywords
        }
    except Exception as exc:
        logger.exception("Failed to compute report for company id=%s: %s", getattr(company, 'id', None), exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

@router.post("/")
async def regen_report(company=Depends(get_company_by_api_key)):
    """Trigger report regeneration via Celery for allowed companies."""
    try:
        logger.debug("Regenerate report requested for company id=%s", getattr(company, 'id', None))
        if not company.can_regen_reports:
            logger.warning("Company id=%s not allowed to regen reports", company.id)
            raise HTTPException(status_code=403, detail="company not allowed to regen reports")
        try:
            celery_generate_report.delay(company.id)
            logger.info("Queued report generation for company id=%s", company.id)
        except Exception as exc:
            logger.error("Failed to enqueue report generation for company id=%s: %s", company.id, exc)
        return {"ok": True, "message": "report regeneration started"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled error in regen_report: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
