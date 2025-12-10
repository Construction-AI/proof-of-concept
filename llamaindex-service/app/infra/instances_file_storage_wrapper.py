from functools import lru_cache
from app.core.config import get_settings, Settings
from minio import Minio
from typing import Optional
from pathlib import Path
from app.core.logger import get_logger
from pydantic import BaseModel
import io
from minio.helpers import ObjectWriteResult

class FileUploadRequest(BaseModel):
    local_file_path: str
    company_id: str
    project_id: str
    document_category: str

class FileDeleteRequest(BaseModel):
    bucket_name: str
    target_file: str

class FileStorageWrapper():
    def __init__(self, url: str, access_key: str, secret_key: str):
        self.url = url
        self.access_key = access_key
        self.secret_key = secret_key
        self.client = Minio(
            endpoint=self.url,
            access_key=self.access_key,
            secret_key=secret_key,
            secure=False
        )
        self.logger = get_logger(self.__class__.__name__)

    class File():
        def __init__(self, company_id: str, project_id: str, document_category: str, local_path: Optional[str] = None, data_as_bytes: Optional[bytes] = None, document_type: str = "raw"):
            """
            Initializes the file entity with identifiers for company, project, document category, and document type.

            Args:
                company_id (str): Unique identifier for the company.
                project_id (str): Unique identifier for the project.
                document_category (str): Category of the document.
                document_type (str): Type of the document.
            """
            self.company_id = company_id
            self.project_id = project_id
            self.document_category = document_category
            self.document_type = document_type

            assert not (local_path and data_as_bytes), "Cannot use local_path and data_as_bytes simultaneously."
            self.local_path = local_path
            self.data_as_bytes = data_as_bytes
            self.file_name = Path(local_path).name if local_path else None

        @property
        def bucket_name(self) -> str:
            return self.company_id
        
        @property
        def project(self) -> str:
            return self.project_id
                
        @property
        def remote_file_path(self) -> str:
            return f"{self.project_id}/{self.document_category}/{self.document_type}/{self.file_name}"
        
        @property
        def is_file(self) -> bool:
            return not self.data_as_bytes
        

    ########
    # CRUD #
    ########
    def create_file(self, target_file: File) -> str:
        if not self.client.bucket_exists(bucket_name=target_file.bucket_name):
            self.logger.warning(f"Bucket not found: {target_file.bucket_name}. Creating...")
            self.client.make_bucket(bucket_name=target_file.bucket_name)
        
        result: ObjectWriteResult = None
        if target_file.is_file:
            result = self.client.fput_object(
                bucket_name=target_file.bucket_name,
                object_name=target_file.remote_file_path,
                file_path=target_file.local_path
            )
        else:
            data_as_stream = io.BytesIO(target_file.data_as_bytes)
            result = self.client.put_object(
                bucket_name=target_file.bucket_name,
                object_name=target_file.remote_file_path,
                data=data_as_stream,
                length=len(target_file.data_as_bytes)
            )

        self.logger.info(f"{target_file.local_path} successfully uploaded as object {target_file.remote_file_path}")
        return result.object_name
    
    def read_file(self, target_file: File) -> str:
        try:
            response = self.client.get_object(bucket_name=target_file.bucket_name, object_name=target_file.remote_file_path)
            print(response)
        finally:
            response.close()
            response.release_conn()
        return "ok"

    def update_file(self, old_file: File, source_file: str, new_file: File):
        self.delete_file(target_file=old_file)
        self.create_file(source_file=source_file, destination_file=new_file)


    def delete_file(self, target_file: File):
        try:
            self.client.remove_object(target_file.bucket_name, target_file.remote_file_path)
            self.logger.info(f"The file {target_file.remote_file_path} has been removed.")
        except Exception as e:
            self.logger.error(f"Failed to remove object {target_file.remote_file_path}: {str(e)}")
            raise e


@lru_cache()
def get_file_manager() -> FileStorageWrapper:
    settings = get_settings()
    file_manager = FileStorageWrapper(
        url=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY
    )
    return file_manager