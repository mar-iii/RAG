from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import settings
from app.core.security import require_api_key
from app.schemas.pydantic_models import IngestResponse
from app.services.llm_service import llm_service
from app.services.vector_store import vector_store

router = APIRouter(
    prefix="/ingest",
    tags=["ingestion"],
    dependencies=[Depends(require_api_key)],
)


def split_text(text: str) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + settings.chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = end - settings.chunk_overlap
    return chunks


@router.post("/", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)) -> IngestResponse:
    if not file.filename or not file.filename.lower().endswith((".txt", ".md")):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only .txt and .md files are supported in Phase 1",
        )

    content = (await file.read()).decode("utf-8")
    chunks = split_text(content)
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded document is empty",
        )

    embeddings = llm_service.embed(chunks)
    vector_store.add_documents(
        texts=chunks,
        metadatas=[{"source": file.filename} for _ in chunks],
        ids=[str(uuid4()) for _ in chunks],
        embeddings=embeddings,
    )
    return IngestResponse(
        message=f"Indexed {file.filename}",
        chunks_indexed=len(chunks),
    )
