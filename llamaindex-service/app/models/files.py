from pathlib import Path
from abc import ABC, abstractmethod
from typing import Optional
from app.core.document_mapper import DocumentMapper

class File(ABC):
    def __init__(self, company_id: str, project_id: str, document_category: str, document_type: str):
        self.company_id = company_id
        self.project_id = project_id
        self.document_category = DocumentMapper.get_document_type_for_name(name=document_category)
        self.document_type = document_type
        
    @property
    @abstractmethod
    def file_id(self) -> str:
        pass
    
    @property
    def project(self) -> str:
        return self.project_id
            
    @property
    def bucket(self) -> str:
        return self.company_id

class LocalFile(File):
        def __init__(self, company_id: str, project_id: str, document_category: str, local_path: str, document_type: Optional[str] = "raw", forced_file_name: Optional[str] = None):
            File.__init__(self, company_id, project_id, document_category, document_type)
            self.local_path = local_path
            self.forced_file_name = forced_file_name
            
        @property
        def file_name(self) -> str:
            if self.forced_file_name:
                return self.forced_file_name
            return Path(self.local_path).name
        
        @property
        def remote_file_path(self) -> str:
            return f"{self.project_id}/{self.document_category}/{self.document_type}/{self.file_name}"
            
        @property
        def file_id(self) -> str:
            return f"{self.company_id}/{self.project_id}/{self.document_category}/{self.document_type}/{self.file_name}"
                            
class KBFile(LocalFile):
    def __init__(self, company_id: str, project_id: str, document_category: str, document_type: str, local_path: str, metadata: dict = {}):
        LocalFile.__init__(self, company_id=company_id, project_id=project_id, document_category=document_category, document_type=document_type, local_path=local_path)
        self.metadata = metadata
        self.__set_metadata()
        
    def __set_metadata(self):
        self.metadata["company_id"] = self.company_id
        self.metadata["project_id"] = self.project_id
        self.metadata["document_category"] = self.document_category
        self.metadata["document_type"] = self.document_type
        self.metadata["file_name"] = self.file_name        
        self.metadata["file_id"] = self.file_id
        
    @staticmethod
    def fromLocalFile(file: LocalFile):
        return KBFile(
            company_id=file.company_id,
            project_id=file.project_id,
            document_category=file.document_category,
            document_type=file.document_type,
            local_path=file.local_path,
        )
    

class FSFile(File):
        def __init__(self, company_id: str, project_id: str, document_category: str, document_type: Optional[str] = None, file_name: Optional[str] = None):
            File.__init__(self, company_id, project_id, document_category, document_type)
            self.file_name = file_name
                         
        @property
        def remote_file_path(self) -> str:
            path = f"{self.project}/{self.document_category}"
            if self.document_type:
                path += f"/{self.document_type}"
            if self.file_name:
                path += f"/{self.file_name}"
            return path
        
        @property
        def file_id(self) -> str:
            return self.company_id + "/" + self.remote_file_path
        
