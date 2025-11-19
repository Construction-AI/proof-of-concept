from llama_index.core import VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.schema import BaseNode

from typing import List

class ProjectEngine:
    def __init__(self, index: VectorStoreIndex, nodes: List[BaseNode] | None, retriever: QueryFusionRetriever, query_engine: RetrieverQueryEngine):
        self.index = index
        self.nodes = nodes
        self.retriever = retriever
        self.query_engine = query_engine