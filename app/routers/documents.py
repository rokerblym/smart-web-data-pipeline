import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.hashing import content_hash
from app.core.security import UnsafeURLError
from app.database import get_db
from app.models import Document
from app.schemas.documents import (
    AnalysisResponse,
    DocumentListItem,
    DocumentResponse,
    FetchRequest,
    FetchResponse,
)
from app.services.analyzer import analyze_text
from app.services.fetcher import FetchError, fetch_html
from app.services.parser import parse_html

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/fetch", response_model=FetchResponse, status_code=status.HTTP_201_CREATED)
async def fetch_document(request: FetchRequest, db: AsyncSession = Depends(get_db)):
    url = str(request.url)

    try:
        html = await fetch_html(url)
    except (UnsafeURLError, FetchError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not fetch URL: {exc}") from exc

    parsed = parse_html(html, url)
    if not parsed.text:
        raise HTTPException(status_code=422, detail="No readable text was extracted")

    digest = content_hash(parsed.text)

    existing = (
        await db.execute(select(Document).where(Document.content_hash == digest))
    ).scalar_one_or_none()

    if existing:
        return FetchResponse(document=existing, duplicate=True)

    document = Document(
        url=url,
        canonical_url=parsed.canonical_url,
        content_hash=digest,
        title=parsed.title,
        description=parsed.description,
        text=parsed.text,
        word_count=parsed.word_count,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    return FetchResponse(document=document, duplicate=False)

@router.get("", response_model=list[DocumentListItem])
async def list_documents(
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).order_by(desc(Document.created_at)).limit(limit)
    )
    return list(result.scalars().all())

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    document = (
        await db.execute(select(Document).where(Document.id == document_id))
    ).scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document

@router.post("/{document_id}/analyze", response_model=AnalysisResponse)
async def analyze_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    document = (
        await db.execute(select(Document).where(Document.id == document_id))
    ).scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    analyzer, analysis = await analyze_text(document.text, document.title)
    document.analysis = analysis
    document.analyzer = analyzer
    await db.commit()
    await db.refresh(document)

    return AnalysisResponse(
        document_id=document.id,
        analyzer=analyzer,
        analysis=analysis,
    )
