from unittest.mock import Mock, patch

import pytest

from esma_data_processor.storage import (
    AzureStorage,
    S3Storage,
    StorageError,
    StorageFactory,
)


class TestS3Storage:
    """Test suite for S3Storage class."""

    @patch("esma_data_processor.storage.boto3")
    def test_init_success(self, mock_boto3):
        """Test S3Storage initialization."""
        storage = S3Storage()

        mock_boto3.client.assert_called_once_with("s3", region_name="us-east-1")

    @patch("esma_data_processor.storage.boto3")
    def test_upload_success(self, mock_boto3, temp_dir):
        """Test successful S3 upload."""
        mock_client = Mock()
        mock_boto3.client.return_value = mock_client

        storage = S3Storage()

        # Create test file
        test_file = temp_dir / "test.csv"
        test_file.write_text("test,data")

        storage.upload(str(test_file), "s3://my-bucket/test.csv")

        mock_client.upload_file.assert_called_once()

    @patch("esma_data_processor.storage.boto3")
    def test_upload_invalid_path(self, mock_boto3, temp_dir):
        """Test upload with invalid S3 path."""
        mock_client = Mock()
        mock_boto3.client.return_value = mock_client

        storage = S3Storage()

        test_file = temp_dir / "test.csv"
        test_file.write_text("test,data")

        with pytest.raises(StorageError):
            storage.upload(str(test_file), "invalid://path")


class TestAzureStorage:
    """Test suite for AzureStorage class."""

    @patch("esma_data_processor.storage.fsspec.filesystem")
    def test_init_success(self, mock_fs):
        """Test AzureStorage initialization."""
        storage = AzureStorage()

        mock_fs.assert_called_once_with("az")

    @patch("esma_data_processor.storage.fsspec.filesystem")
    def test_upload_success(self, mock_fs, temp_dir):
        """Test successful Azure upload."""
        mock_filesystem = Mock()
        mock_fs.return_value = mock_filesystem

        storage = AzureStorage()

        # Create test file
        test_file = temp_dir / "test.csv"
        test_file.write_text("test,data")

        storage.upload(str(test_file), "az://container/test.csv")

        mock_filesystem.pipe.assert_called_once()


class TestStorageFactory:
    """Test suite for StorageFactory class."""

    def test_create_s3(self):
        """Test factory creates S3 storage."""
        storage = StorageFactory.create("s3://bucket/path")

        assert isinstance(storage, S3Storage)

    def test_create_azure(self):
        """Test factory creates Azure storage."""
        storage = StorageFactory.create("az://container/path")

        assert isinstance(storage, AzureStorage)

    def test_create_unsupported_backend(self):
        """Test factory with unsupported backend."""
        with pytest.raises(StorageError):
            StorageFactory.create("ftp://server/path")
