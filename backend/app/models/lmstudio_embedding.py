from typing import List
import requests
from llama_index.core.embeddings import BaseEmbedding

class LMStudioEmbedding(BaseEmbedding):
    def __init__(self, base_url: str, model_name: str, api_key: str = "lm-studio"):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.api_key = api_key

    def _embed(self, texts: List[str]) -> List[List[float]]:
        resp = requests.post(
            f"{self.base_url}/embeddings",
            json={"input": texts, "model": self.model_name},
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        # assuming standard OpenAI-style response
        return [item["embedding"] for item in data["data"]]

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts)
