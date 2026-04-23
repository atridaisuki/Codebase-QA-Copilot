from sentence_transformers import SentenceTransformer

from app.config import get_settings


class EmbeddingService:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = SentenceTransformer(settings.embedding_model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        result: list[list[float]] = self.model.encode(texts, convert_to_numpy=True).tolist()
        return result

    def embed_query(self, text: str) -> list[float]:
        result: list[float] = self.model.encode(text, convert_to_numpy=True).tolist()
        return result
