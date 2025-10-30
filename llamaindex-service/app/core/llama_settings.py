import os
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

# Configure LLM
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
if LLM_PROVIDER.lower() == "ollama":
    from llama_index.llms.ollama import Ollama
    from llama_index.embeddings.ollama import OllamaEmbedding
    ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
    ollama_embed_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    ollama_embedding = OllamaEmbedding(
        model_name=ollama_embed_model,
        base_url=ollama_url,
    )
    ollama_model=os.getenv("OLLAMA_MODEL", "llama3:8b")

    Settings.llm = Ollama(model=ollama_model, base_url=ollama_url)
    Settings.embed_model = ollama_embedding
elif LLM_PROVIDER.lower() == "openai":
    from llama_index.llms.openai import OpenAI
    Settings.llm = OpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    embed_model = os.getenv("EXT_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    Settings.embed_model = HuggingFaceEmbedding(embed_model)
else:
    Settings.llm = None
    Settings.embed_model = None