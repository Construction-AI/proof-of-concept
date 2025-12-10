from pathlib import Path
from abc import ABC, abstractmethod

class File(ABC):
    def __init__(self, company_id: str, project_id: str, document_category: str, document_type: str):
        self.company_id = company_id
        self.project_id = project_id
        self.document_category = document_category
        self.document_type = document_type
        
    @property
    @abstractmethod
    def file_id(self) -> str:
        pass

class LocalFile(File):
        def __init__(self, company_id: str, project_id: str, document_category: str, document_type: str, local_path: str):
            File.__init__(company_id, project_id, document_category, document_type)
            self.local_path = local_path
            
        @property
        def file_name(self) -> str:
            return Path(self.local_path).name
            
        @property
        def file_id(self) -> str:
            return f"{self.company_id}/{self.project_id}/{self.document_category}/{self.document_type}/{self.file_name}"
                            
class KBFile(LocalFile):
    def __init__(self, company_id: str, project_id: str, document_category: str, document_type: str, local_path: str, metadata: dict = {}):
        LocalFile.__init__(self, company_id, project_id, document_category, document_type, local_path)
        self.metadata = metadata
        self.__set_metadata()
        
    def __set_metadata(self):
        self.metadata["company_id"] = self.company_id
        self.metadata["project_id"] = self.project_id
        self.metadata["document_category"] = self.document_category
        self.metadata["document_type"] = self.document_type
        self.metadata["file_name"] = self.file_name        
        self.metadata["file_id"] = self.file_id        
    

class FSFile(File):
        def __init__(self, company_id: str, project_id: str, document_category: str, document_type: str, remote_file_path: str):
            File.__init__(company_id, project_id, document_category, document_type)
            self.remote_file_path = remote_file_path
             
        @property
        def file_name(self) -> str:
            return Path(self.remote_file_path).name
            
        @property
        def bucket(self) -> str:
            return self.company_id
        
        @property
        def project(self) -> str:
            return self.project_id
            
        @property
        def remote_file_path(self) -> str:
            return f"{self.bucket}/{self.project}/{self.document_category}/{self.document_type}/{self.file_name}"
        
        @property
        def file_id(self) -> str:
            return self.company_id + "/" + self.remote_file_path
        
