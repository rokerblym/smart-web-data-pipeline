from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Document

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("")
async def stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            func.count(Document.id),
            func.coalesce(func.sum(Document.word_count), 0),
            func.count(Document.analysis),
        )
    )
    documents, words, analyzed = result.one()

    return {
        "documents": documents,
        "total_words": words,
        "analyzed_documents": analyzed,
    }
