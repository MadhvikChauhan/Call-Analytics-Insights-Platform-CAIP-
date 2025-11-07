
"""Utility script to find pending (unprocessed) calls and enqueue Celery tasks for them."""
import asyncio
from app.db import AsyncSessionLocal
from sqlalchemy import select
from app.models import CallRecord
from app.tasks import process_call_record as celery_process_call

async def main():
    """Query the database for pending calls and enqueue tasks for processing."""
    async with AsyncSessionLocal() as session:
        q = select(CallRecord).where(CallRecord.is_processed == False)
        res = await session.execute(q)
        pending = res.scalars().all()
        print(f"Found {len(pending)} pending calls")
        for p in pending:
            celery_process_call.delay(p.id)

if __name__ == '__main__':
    asyncio.run(main())
