from functools import lru_cache
from app.core.config import get_settings, Settings
from minio import Minio
from typing import Optional
from pathlib import Path
from app.core.logger import get_logger
from pydantic import BaseModel

class FileUploadRequest(BaseModel):
    file_path: str
    bucket_name: str

class FileManager():
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
        self.logger = get_logger("FileManager")
        
    def upload_file(self, bucket_name: str, source_file: str, destination_file: Optional[str]):
        if not destination_file:
            destination_file = Path(source_file).name
        
        if not self.client.bucket_exists(bucket_name=bucket_name):
            self.logger.warning(f"Bucket not found: {bucket_name}. Creating...")
            self.client.make_bucket(bucket_name=bucket_name)

        self.client.fput_object(
            bucket_name=bucket_name,
            object_name=destination_file,
            file_path=source_file
        )
        self.logger.info(f"{source_file} successfully uploaded as object {destination_file} to bucket {bucket_name}")


@lru_cache()
def get_file_manager() -> FileManager:
    settings = get_settings()
    file_manager = FileManager(
        url=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY
    )
    return file_manager