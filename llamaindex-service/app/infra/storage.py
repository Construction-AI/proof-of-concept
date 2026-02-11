from minio import Minio
from app.core.config import settings
from fastapi import UploadFile
from datetime import datetime, timedelta

class StorageClient:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        self.bucket = "construction-docs"
        self.working = True
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(bucket_name=self.bucket):
                self.client.make_bucket(bucket_name=self.bucket)
        except Exception as e:
            print(f"Failed to create default bucket: {str(e)}")
            self.working = False
            
    def upload_file(self, file_obj: UploadFile, object_name: str, content_type: str, project_id: str):
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=file_obj.file,
            length=file_obj.size,
            content_type=content_type
        )
    
    def get_download_url(self, storage_key: str, expiration=3600):
        return self.client.get_presigned_url(
            method="GET",
            bucket_name=self.bucket,
            object_name=storage_key,
            expires=timedelta(seconds=expiration)
        )
        
storage_client = StorageClient()
