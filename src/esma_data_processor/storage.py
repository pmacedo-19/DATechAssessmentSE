import logging
from abc import ABC, abstractmethod
from pathlib import Path

try:
    import boto3
except ImportError:
    boto3 = None

try:
    import fsspec
except ImportError:
    fsspec = None

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Custom exception for storage-related errors."""

    pass


class CloudStorage(ABC):
    """Abstract base class for cloud storage backends.

    Defines interface for uploading files to cloud storage.
    """

    def __init__(self) -> None:
        """Initialize cloud storage."""
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def upload(self, local_path: str, remote_path: str) -> None:
        """Upload file to cloud storage.

        Args:
            local_path: Path to local file
            remote_path: Cloud path (e.g., s3://bucket/path or az://container/path)

        Raises:
            StorageError: If upload fails
        """
        pass


class S3Storage(CloudStorage):
    """AWS S3 storage backend.

    Uploads files to Amazon S3 using boto3.
    """

    def __init__(self, region: str = "us-east-1") -> None:
        """Initialize S3 storage.

        Args:
            region: AWS region
        """
        super().__init__()
        if boto3 is None:
            raise StorageError("boto3 not installed")
        self.client = boto3.client("s3", region_name=region)

    def upload(self, local_path: str, remote_path: str) -> None:
        """Upload file to S3.

        Args:
            local_path: Path to local file
            remote_path: S3 path (s3://bucket/key)

        Raises:
            StorageError: If upload fails
        """
        try:
            self.logger.info(f"Uploading {local_path} to {remote_path}")

            # Parse S3 path
            if not remote_path.startswith("s3://"):
                raise StorageError("Invalid S3 path format")

            parts = remote_path[5:].split("/", 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else Path(local_path).name

            # Upload file
            self.client.upload_file(local_path, bucket, key)
            self.logger.info(f"Successfully uploaded to s3://{bucket}/{key}")

        except Exception as e:
            raise StorageError(f"S3 upload failed: {e}")


class AzureStorage(CloudStorage):
    """Microsoft Azure Blob Storage backend.

    Uploads files to Azure using fsspec.
    """

    def __init__(self) -> None:
        """Initialize Azure storage."""
        super().__init__()
        if fsspec is None:
            raise StorageError("fsspec[az] not installed")
        self.fs = fsspec.filesystem("az")

    def upload(self, local_path: str, remote_path: str) -> None:
        """Upload file to Azure Blob Storage.

        Args:
            local_path: Path to local file
            remote_path: Azure path (az://container/path)

        Raises:
            StorageError: If upload fails
        """
        try:
            self.logger.info(f"Uploading {local_path} to {remote_path}")

            # Use fsspec to upload
            with open(local_path, "rb") as f:
                self.fs.pipe(remote_path, f.read())

            self.logger.info(f"Successfully uploaded to {remote_path}")

        except Exception as e:
            raise StorageError(f"Azure upload failed: {e}")


class StorageFactory:
    """Factory for creating cloud storage instances.

    Determines storage backend based on remote path.
    """

    @staticmethod
    def create(remote_path: str) -> CloudStorage:
        """Create appropriate storage instance.

        Args:
            remote_path: Cloud path (s3:// or az://)

        Returns:
            CloudStorage instance

        Raises:
            StorageError: If backend not supported
        """
        if remote_path.startswith("s3://"):
            return S3Storage()
        elif remote_path.startswith("az://"):
            return AzureStorage()
        else:
            raise StorageError(f"Unsupported storage backend: {remote_path}")
