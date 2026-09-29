import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, HttpUrl

class FetchRequest(BaseModel):
    url: HttpUrl

class DocumentResponse(BaseModel):
    id: uuid.UUID
    url: str
    canonical_url: str | None
    content_hash: str
    title: str | None
    description: str | None
    text: str
    word_count: int
    analysis: dict | None
    analyzer: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DocumentListItem(BaseModel):
    id: uuid.UUID
    url: str
    title: str | None
    word_count: int
    analyzer: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class FetchResponse(BaseModel):
    document: DocumentResponse
    duplicate: bool

class AnalysisResponse(BaseModel):
    document_id: uuid.UUID
    analyzer: str
    analysis: dict
