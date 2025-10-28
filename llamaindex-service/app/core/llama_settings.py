import os
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

# Configure LLM
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
if LLM_PROVIDER.lower() == "ollama":
    from llama_index.llms.ollama import Ollama
    Settings.llm = Ollama(model=os.getenv("OLLAMA_MODEL", "llama3"))
elif LLM_PROVIDER.lower() == "openai":
    from llama_index.llms.openai import OpenAI
    Settings.llm = OpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
else:
    Settings.llm = None

embed_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
Settings.embed_model = HuggingFaceEmbedding(embed_model)