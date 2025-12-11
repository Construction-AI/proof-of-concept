from functools import lru_cache
from app.core.config import get_settings, Settings
from minio import Minio
from typing import Optional
from pathlib import Path
from app.core.logger import get_logger
from pydantic import BaseModel
import io
from minio.helpers import ObjectWriteResult
from minio.error import S3Error
import tempfile
import shutil

from app.models.files import LocalFile, FSFile


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

    ########
    # CRUD #
    ########
    def create_file(self, local_file: LocalFile) -> str:
        if not self.client.bucket_exists(bucket_name=local_file.bucket):
            self.logger.warning(f"Bucket not found: {local_file.bucket}. Creating...")
            self.client.make_bucket(bucket_name=local_file.bucket)
        
        if self.check_object_exists(local_file=local_file):
            raise Exception(f"Cannot create object. '{local_file.remote_file_path}' already exists. Did you mean to use upsert?")

        result: ObjectWriteResult = None
        result = self.client.fput_object(
            bucket_name=local_file.bucket,
            object_name=local_file.remote_file_path,
            file_path=local_file.local_path
        )
            
        self.logger.info(f"{local_file.local_path} successfully uploaded as object {local_file.remote_file_path}")
        return result.object_name
    
    def read_file(self, target_file: FSFile) -> str:
        result = None
        try:
            assert target_file.file_name, "No file name specified."
            if not self.check_object_exists(remote_file=target_file):
                raise f"Object {target_file.remote_file_path} was not found."
            response = self.client.get_object(bucket_name=target_file.bucket, object_name=target_file.remote_file_path)
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                shutil.copyfileobj(io.BytesIO(response.data), tmp_file)
                tmp_file_path = tmp_file.name
            self.logger.info(f"File downloaded to temporary location: {tmp_file_path}")
            result = tmp_file_path
        finally:
            response.close()
            response.release_conn()
        return result

    def upsert_file(self, old_file: LocalFile, new_file: LocalFile):
        self.logger.info(f"Upserting file {new_file.remote_file_path}...")
        self.delete_file(target_file=old_file)
        file_url = self.create_file(local_file=new_file)
        self.logger.info(f"Upsert of file {new_file.remote_file_path} successful.")
        return file_url
    
    def __delete_directory(self, target_file: FSFile):
        objects_to_delete = self.client.list_objects(target_file.bucket, prefix=self.__construct_delete_path(target_file=target_file), recursive=True)
        for obj in objects_to_delete:
            self.client.remove_object(target_file.bucket, object_name=obj.object_name)

    def delete_file(self, target_file: FSFile):
        try:
            self.__delete_directory(target_file=target_file)
            self.logger.info(f"The files under {self.__construct_delete_path(target_file=target_file)} have been removed.")
        except Exception as e:
            self.logger.error(f"Failed to remove object {target_file.remote_file_path}: {str(e)}")
            raise e
        
    def __construct_delete_path(self, target_file: FSFile) -> str:
        path = f"{target_file.project}/{target_file.document_category}"
        if target_file.document_type:
            path += f"/{target_file.document_type}"
        if target_file.file_name:
            path += f"/{target_file.file_name}"
        return path
        
    def check_object_exists(self, local_file: Optional[LocalFile] = None, remote_file: Optional[LocalFile] = None) -> bool:
        try:
            assert local_file or remote_file, "Either local or remote file has to be provided"
            if local_file:
                bucket = local_file.bucket
                remote_file_path = local_file.remote_file_path
            else:
                bucket = remote_file.bucket
                remote_file_path = remote_file.remote_file_path
                
            current = self.client.get_object(bucket_name=bucket, object_name=remote_file_path)
            return current.url is not None
        except Exception as e:
            if isinstance(e, S3Error) and e.code == 'NoSuchKey':
                return False
            raise e



@lru_cache()
def get_file_storage_wrapper() -> FileStorageWrapper:
    settings = get_settings()
    file_manager = FileStorageWrapper(
        url=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY
    )
    return file_manager