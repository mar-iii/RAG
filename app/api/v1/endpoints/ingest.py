from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.security import require_api_key
from app.schemas.pydantic_models import IngestResponse
from app.services.document_ingestion import SUPPORTED_EXTENSIONS, prepare_document, split_text
from app.services.llm_service import llm_service
from app.services.vector_store import vector_store

router = APIRouter(
    prefix="/ingest",
    tags=["ingestion"],
    dependencies=[Depends(require_api_key)],
)

@router.post("/", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)) -> IngestResponse:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Supported file types: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    try:
        document = prepare_document(file.filename, await file.read())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    chunks = split_text(document.text)
    embeddings = llm_service.embed(chunks)
    vector_store.add_documents(
        texts=chunks,
        metadatas=[
            {"source": document.filename, "file_type": document.file_type}
            for _ in chunks
        ],
        ids=[str(uuid4()) for _ in chunks],
        embeddings=embeddings,
    )
    return IngestResponse(
        message=f"Indexed {file.filename}",
        chunks_indexed=len(chunks),
    )
