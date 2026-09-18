from fastapi import APIRouter, Depends

from app.core.security import require_api_key
from app.schemas.pydantic_models import QueryRequest, QueryResponse, SourceDocument
from app.services.llm_service import llm_service
from app.services.vector_store import vector_store

router = APIRouter(
    prefix="/query",
    tags=["query"],
    dependencies=[Depends(require_api_key)],
)


@router.post("/", response_model=QueryResponse)
def query_documents(payload: QueryRequest) -> QueryResponse:
    query_embedding = llm_service.embed([payload.question])[0]
    retrieved_docs = vector_store.similarity_search(query_embedding, payload.top_k)
    context = "\n\n".join(document["content"] for document in retrieved_docs)
    answer = llm_service.answer(payload.question, context)
    sources = [SourceDocument(**document) for document in retrieved_docs]
    return QueryResponse(answer=answer, source_documents=sources)
