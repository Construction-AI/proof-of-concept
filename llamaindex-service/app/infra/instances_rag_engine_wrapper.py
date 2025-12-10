from functools import lru_cache

from app.infra.instances_file_storage_wrapper import get_file_storage_wrapper
from app.infra.instances_llamaindex import get_llamaindex_contexts

from llama_index.core.schema import Document
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.readers.file import PyMuPDFReader
from llama_index.core import VectorStoreIndex, StorageContext

from pydantic import BaseModel
from pathlib import Path

from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor

from app.infra.instances_qdrant import get_qdrant_aclient

SENTENCE_WINDOW_PARSER = SentenceWindowNodeParser.from_defaults(window_size=3)
WINDOW_POST = MetadataReplacementPostProcessor(target_metadata_key="window")

class RagEngineWrapper:
    def __init__(self):
        self.file_storage_wrapper = get_file_storage_wrapper()
        self.llamaindex_contexts = get_llamaindex_contexts()
        self.llamaindex_storage_context: StorageContext = self.llamaindex_contexts["ctx"]
        
    class ProjectEngine:
        def __init__(self, company_id: str, project_id: str):
            self.company_id = company_id
            self.project_id = project_id
            self.index = None
            self.nodes = None
            self.retriever = None
            self.query_engine = None
            
        ############
        #  Files   #
        ############
        class File:
            def __init__(self, company_id: str, project_id: str, document_category: str, local_path: str, document_type: str = "raw"):
                self.company_id = company_id
                self.project_id = project_id
                self.document_category = document_category
                self.document_type = document_type
                self.local_path = local_path
                
            @property
            def file_name(self) -> str:
                return Path(self.local_path).name
            
        def load_documents(self, local_file: File) -> list[Document]:
            reader = SimpleDirectoryReader(
                input_files=[local_file.local_path],
                filename_as_id=False,
                file_extractor={".pdf": PyMuPDFReader()}
            )
            
            docs = reader.load_data()
            for d in docs:
                d.metadata.setdefault("page_label", d.metadata.get("source", None))
                d.metadata.setdefault("file_name", local_file.file_name)
                d.metadata.setdefault("company_id", local_file.company_id)
                d.metadata.setdefault("project_id", local_file.project_id)
                d.metadata.setdefault("document_category", local_file.document_category)
                d.metadata.setdefault("document_type", local_file.document_type)
            return docs
        
        def index_documents(self, documents: list[Document]):
            index = VectorStoreIndex.from_documents(
                documents=documents,
                storage_context=self.llamaindex_storage_context
            )
            index.storage_context.persist()

        # async def build_project_index(self, local_file: File):
        #     documents = self.load_documents(local_file=local_file)
        #     if not documents:
        #         raise ValueError(f"No documents provided.")
            
        #     nodes = SENTENCE_WINDOW_PARSER.get_nodes_from_documents(documents=documents)
        #     qdrant_aclient = get_qdrant_aclient()
            
        #     try:
        #         await qdrant_aclient.delete_collection()
        
    
    
    
    ############
    # Requests #
    ############
    class RequestLoadDocument(BaseModel):
        local_path: str
        company_id: str
        project_id: str
        document_category: str
        document_type: str
        
        
        
@lru_cache()
def get_rag_engine_wrapper():
    return RagEngineWrapper()