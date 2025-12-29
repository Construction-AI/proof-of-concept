from functools import lru_cache
from app.core.settings import get_settings
from typing import Optional

from typing import Tuple

from app.models.files import LocalFile, FSFile
from app.api.services.file_storage_service import FileStorageService


class FileStorageWrapper:
    def __init__(self, url: str, access_key: str, secret_key: str):
        self.file_storage_service = FileStorageService(
            url=url,
            access_key=access_key,
            secret_key=secret_key
        )

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
        return self.file_storage_service.upload_file(local_file=local_file)
    
    def read_file(self, target_file: FSFile) -> Tuple[FSFile, Optional[str]]:
        """
        Reads a file from remote storage and saves it to a temporary local file.

        Args:
            target_file (FSFile): The file metadata object specifying the file to read.

        Returns:
            Tuple[FSFile, Optional[str]]: A tuple containing the (possibly updated) FSFile object and the path to the temporary local file, or None if the file could not be read.

        Raises:
            Exception: If the specified file does not exist in remote storage.

        Note:
            The temporary file is not deleted automatically. Caller is responsible for cleanup.
        """
        return self.file_storage_service.read_file(target_file=target_file)
    
    def read_file_from_url(self, bucket: str, file_url: str) -> str:
        return self.file_storage_service.read_file_from_url(bucket=bucket, file_url=file_url)

    def upsert_file(self, target_file: LocalFile):
        """
        Inserts or updates a file in the storage system.

        This method first deletes the existing file at the target location (if any),
        then uploads the provided local file to the storage, effectively performing
        an "upsert" (update or insert) operation.

        Args:
            target_file (LocalFile): The local file object containing information about
                the file to be uploaded, including its remote file path.

        Returns:
            str: The URL of the uploaded file in the storage system.

        Logs:
            - Information about the upsert operation's start and successful completion.
        """
        return self.file_storage_service.upsert_file(target_file=target_file)
    
    def delete_file(self, target_file: FSFile):
        """
        Deletes the specified file and its associated directory from the storage system.

        Args:
            target_file (FSFile): The file object representing the file to be deleted.

        Raises:
            Exception: If an error occurs during the deletion process, the exception is logged and re-raised.

        Side Effects:
            - Removes the directory associated with the target file.
            - Logs information about the deletion or any errors encountered.
        """
        self.delete_file(target_file=target_file)
                
@lru_cache()
def get_file_storage_wrapper() -> FileStorageWrapper:
    settings = get_settings()
    file_manager = FileStorageWrapper(
        url=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY
    )
    return file_manager