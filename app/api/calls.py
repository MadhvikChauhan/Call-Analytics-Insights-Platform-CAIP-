
"""API endpoints for call ingestion and retrieval, with logging and defensive error handling."""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from deps import get_company_by_api_key, get_db
from models import CallRecord, CallInsight
from schemas import CallCreate, CallRead, InsightRead
from storage import save_upload_file
from tasks import process_call_record as celery_process_call
from datetime import datetime
from logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/", status_code=201)
async def create_call(call_meta: CallCreate = Depends(), file: UploadFile = File(...), company=Depends(get_company_by_api_key), db: AsyncSession = Depends(get_db)):
    """Register a new call record and enqueue background processing task.

    The endpoint saves the uploaded audio file, stores call metadata and triggers
    asynchronous processing via Celery. Errors during file save or DB operations
    are logged and a 500 response is returned.
    """
    try:
        logger.debug("Received create_call request for company id=%s, call_id=%s", getattr(company, 'id', None), call_meta.call_id)
        saved_path = save_upload_file(file, company.id, file.filename)
        cr = CallRecord(
            company_id=company.id,
            call_id=call_meta.call_id,
            caller=call_meta.caller,
            callee=call_meta.callee,
            start_time=call_meta.start_time,
            end_time=call_meta.end_time,
            duration=call_meta.duration,
            recording_file=saved_path,
            is_processed=False
        )
        db.add(cr)
        await db.commit()
        await db.refresh(cr)
        # Enqueue Celery task
        try:
            celery_process_call.delay(cr.id)
        except Exception as exc:
            logger.warning("Failed to enqueue Celery task for CallRecord id=%s: %s", cr.id, exc)
        logger.info("Created CallRecord id=%s for company id=%s", cr.id, company.id)
        return {"id": cr.id, "call_id": cr.call_id, "is_processed": cr.is_processed}
    except Exception as exc:
        logger.exception("Unhandled error in create_call: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

@router.get("/", response_model=List[CallRead])
async def list_calls(
    company=Depends(get_company_by_api_key),
    db: AsyncSession = Depends(get_db),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    duration_gt: Optional[int] = Query(None),
    duration_lt: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """List call records for the authenticated company with optional filters and pagination.

    Errors are logged and translated into HTTPException(500).
    """
    try:
        logger.debug("Listing calls for company id=%s", getattr(company, 'id', None))
        q = select(CallRecord).where(CallRecord.company_id == company.id)
        if from_date:
            try:
                d = datetime.fromisoformat(from_date)
                q = q.where(CallRecord.start_time >= d)
            except Exception as exc:
                logger.debug("Invalid from_date format: %s", exc)
                raise HTTPException(status_code=400, detail="from_date must be ISO format")
        if to_date:
            try:
                d = datetime.fromisoformat(to_date)
                q = q.where(CallRecord.start_time <= d)
            except Exception as exc:
                logger.debug("Invalid to_date format: %s", exc)
                raise HTTPException(status_code=400, detail="to_date must be ISO format")
        if duration_gt is not None:
            q = q.where(CallRecord.duration >= duration_gt)
        if duration_lt is not None:
            q = q.where(CallRecord.duration <= duration_lt)
        q = q.offset(offset).limit(limit)
        res = await db.execute(q)
        rows = res.scalars().all()
        logger.info("Returned %s call records for company id=%s", len(rows), company.id)
        return [CallRead.from_orm(r) for r in rows]
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled error in list_calls: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

@router.get("/{call_id}/insight", response_model=InsightRead)
async def get_insight(call_id: str, company=Depends(get_company_by_api_key), db: AsyncSession = Depends(get_db)):
    """Return processed insight for a call, or 404 if not ready."""
    try:
        logger.debug("Fetching insight for call_id=%s company_id=%s", call_id, getattr(company, 'id', None))
        q = select(CallRecord).where(CallRecord.company_id == company.id, CallRecord.call_id == call_id)
        res = await db.execute(q)
        cr = res.scalars().first()
        if not cr:
            logger.warning("Call not found: call_id=%s company_id=%s", call_id, company.id)
            raise HTTPException(status_code=404, detail="call not found")
        if not cr.is_processed:
            logger.info("Insight not ready for call_id=%s", call_id)
            raise HTTPException(status_code=404, detail="insight not ready")
        q2 = select(CallInsight).where(CallInsight.call_id == cr.id)
        r2 = await db.execute(q2)
        ins = r2.scalars().first()
        if not ins:
            logger.error("Insight missing for processed call id=%s", cr.id)
            raise HTTPException(status_code=404, detail="insight missing")
        logger.info("Returning insight for call_id=%s", call_id)
        return InsightRead.from_orm(ins)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled error in get_insight: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
