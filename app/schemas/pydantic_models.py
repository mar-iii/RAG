from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class SourceDocument(BaseModel):
    content: str
    source: str


class QueryResponse(BaseModel):
    answer: str
    source_documents: list[SourceDocument]


class IngestResponse(BaseModel):
    message: str
    chunks_indexed: int
