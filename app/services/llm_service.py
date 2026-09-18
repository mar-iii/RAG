from google import genai

from app.config import settings


class LLMService:
    def __init__(self) -> None:
        self._client: genai.Client | None = None

    @property
    def client(self) -> genai.Client:
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY must be configured before using embeddings or Q&A"
            )
        if self._client is None:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.models.embed_content(
            model=settings.gemini_embedding_model,
            contents=texts,
        )
        return [embedding.values for embedding in response.embeddings]

    def answer(self, question: str, context: str) -> str:
        prompt = (
            "You are an enterprise AI assistant. Answer using only the provided "
            "context. If the context does not contain the answer, say you do not "
            "know.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}"
        )
        response = self.client.models.generate_content(
            model=settings.gemini_chat_model,
            contents=prompt,
        )
        return response.text or "I do not know."


llm_service = LLMService()
