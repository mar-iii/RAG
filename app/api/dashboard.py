from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.services.document_ingestion import (
    SUPPORTED_EXTENSIONS,
    prepare_document,
    split_text,
)
from app.schemas.pydantic_models import IngestResponse, QueryRequest, QueryResponse, SourceDocument
from app.services.llm_service import llm_service
from app.services.vector_store import vector_store

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.post("/ingest/", response_model=IngestResponse)
async def dashboard_ingest(file: UploadFile = File(...)) -> IngestResponse:
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


@router.post("/query/", response_model=QueryResponse)
def dashboard_query(payload: QueryRequest) -> QueryResponse:
    query_embedding = llm_service.embed([payload.question])[0]
    retrieved_docs = vector_store.similarity_search(query_embedding, payload.top_k)
    context = "\n\n".join(document["content"] for document in retrieved_docs)
    answer = llm_service.answer(payload.question, context)
    return QueryResponse(
        answer=answer,
        source_documents=[SourceDocument(**document) for document in retrieved_docs],
    )
