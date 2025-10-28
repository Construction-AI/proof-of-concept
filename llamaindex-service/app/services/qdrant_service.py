import os
import time
from qdrant_client import QdrantClient

def wait_for_qdrant(max_retries=30, retry_delay=2):
    """Wait for Qdrant to become available."""
    for i in range(max_retries):
        try:
            client = QdrantClient(
                host=os.getenv("QDRANT_HOST", "qdrant"),
                port=int(os.getenv("QDRANT_PORT", 6333)),
                timeout=10
            )
            client.get_collections()
            print("✅ Connected to Qdrant")
            return True
        except Exception as e:
            print(f"Waiting for Qdrant... ({i + 1}/{max_retries}): {e}")
            time.sleep(retry_delay)

    return False