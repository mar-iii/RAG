from pathlib import Path
from typing import Any

import chromadb

from app.config import settings


class VectorStoreService:
    def __init__(self) -> None:
        Path(settings.chroma_persist_directory).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name
        )

    def add_documents(
        self, texts: list[str], metadatas: list[dict[str, str]], ids: list[str],
        embeddings: list[list[float]],
    ) -> None:
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings,
        )

    def similarity_search(
        self, query_embedding: list[float], k: int
    ) -> list[dict[str, str]]:
        results: dict[str, Any] = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
        )
        documents = results.get("documents") or [[]]
        metadatas = results.get("metadatas") or [[]]
        return [
            {"content": content, "source": metadata.get("source", "unknown")}
            for content, metadata in zip(documents[0], metadatas[0])
        ]


vector_store = VectorStoreService()
