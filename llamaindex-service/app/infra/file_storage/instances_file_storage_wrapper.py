from functools import lru_cache
from app.core.settings import get_settings, Settings
from minio import Minio
from typing import Optional
from app.core.logger import get_logger

import io
from minio.helpers import ObjectWriteResult
from minio.error import S3Error
import tempfile
import shutil
from typing import Tuple

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
    def upload_file(self, local_file: LocalFile) -> str:
        """
        Uploads a local file to the specified bucket in the object storage.
        If the target bucket does not exist, it will be created. If an object with the same
        remote file path already exists in the bucket, an exception is raised to prevent overwriting.
        Args:
            local_file (LocalFile): The local file to be uploaded, including bucket, local path, and remote file path.
        Returns:
            str: The path to the file in S3 (object name).
        Raises:
            Exception: If the object already exists in the bucket.
        # This method returns the path to the file in S3.
        """
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
    
    def read_file(self, target_file: FSFile) -> Tuple[FSFile, Optional[str]]:
        result = None
        try:
            if not target_file.file_name:
                self.logger.info("No file name specified, fetching by type...")
                target_file = self.__fetch_document_from_directory(target_file=target_file)
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
        return target_file, result

    def upsert_file(self, target_file: LocalFile):
        self.logger.info(f"Upserting file {target_file.remote_file_path}...")
        self.delete_file(target_file=target_file)
        file_url = self.upload_file(local_file=target_file)
        self.logger.info(f"Upsert of file {target_file.remote_file_path} successful.")
        return file_url
    
    def delete_file(self, target_file: FSFile):
        try:
            self.__delete_directory(target_file=target_file)
            self.logger.info(f"The files under {self.__construct_file_path(target_file=target_file)} have been removed.")
        except Exception as e:
            self.logger.error(f"Failed to remove object {target_file.remote_file_path}: {str(e)}")
            raise e
        
    def __fetch_document_from_directory(self, target_file: FSFile) -> FSFile:
        path = self.__construct_file_path(target_file=target_file)
        objects_from_dir = self.client.list_objects(target_file.bucket, prefix=path, recursive=True)
        
        from pathlib import Path
        
        # TODO: Figure this out, why can't I just access the [0] element
        for obj in objects_from_dir:
            target_file.file_name = Path(obj.object_name).name
            return target_file
        raise ValueError(f"No objects for {path}")
        
    def __delete_directory(self, target_file: FSFile):
        objects_to_delete = self.client.list_objects(target_file.bucket, prefix=self.__construct_file_path(target_file=target_file), recursive=True)
        for obj in objects_to_delete:
            self.client.remove_object(target_file.bucket, object_name=obj.object_name)
        
    def __construct_file_path(self, target_file: FSFile) -> str:
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