import zipfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests
from esma_data_processor.downloader import (
    DownloadError,
    ESMADataDownloader,
)


class TestESMADataDownloader:
    """Test suite for ESMADataDownloader class."""

    def test_init_creates_output_directory(self, temp_dir):
        """Test that __init__ creates output directory."""
        output_dir = temp_dir / "downloads"
        downloader = ESMADataDownloader(str(output_dir))

        assert output_dir.exists()

    @patch("esma_data_processor.downloader.requests.get")
    def test_fetch_xml_success(self, mock_get, temp_dir):
        """Test successful XML fetch."""
        downloader = ESMADataDownloader(str(temp_dir))

        # Mock successful response
        mock_response = Mock()
        mock_response.text = "<xml>test</xml>"
        mock_get.return_value = mock_response

        result = downloader.fetch_xml("http://test.com")

        assert result == "<xml>test</xml>"
        mock_get.assert_called_once()

    @patch("esma_data_processor.downloader.requests.get")
    def test_fetch_xml_failure(self, mock_get, temp_dir):
        """Test fetch_xml handles HTTP errors."""
        downloader = ESMADataDownloader(str(temp_dir))

        # Mock failed response with RequestException
        mock_get.side_effect = requests.RequestException("Connection error")

        with pytest.raises(DownloadError):
            downloader.fetch_xml("http://test.com")

    def test_extract_dltins_url_success(self, temp_dir, sample_xml):
        """Test successful extraction of DLTINS URL."""
        downloader = ESMADataDownloader(str(temp_dir))

        result = downloader.extract_dltins_url(sample_xml)

        assert result == "https://example.com/download2.zip"

    def test_extract_dltins_url_invalid_xml(self, temp_dir):
        """Test extract_dltins_url with invalid XML."""
        downloader = ESMADataDownloader(str(temp_dir))

        with pytest.raises(DownloadError):
            downloader.extract_dltins_url("<invalid>xml")

    @patch("esma_data_processor.downloader.requests.get")
    def test_download_zip_success(self, mock_get, temp_dir):
        """Test successful zip download."""
        downloader = ESMADataDownloader(str(temp_dir))

        # Mock response with file content
        mock_response = Mock()
        mock_response.iter_content = Mock(return_value=[b"test data"])
        mock_get.return_value = mock_response

        output_path = temp_dir / "test.zip"
        downloader.download_zip("http://test.com", str(output_path))

        assert output_path.exists()

    def test_extract_zip_success(self, temp_dir, sample_dltins_xml):
        """Test successful zip extraction."""
        downloader = ESMADataDownloader(str(temp_dir))

        # Create test zip file
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("data.xml", sample_dltins_xml)

        # Extract
        extract_dir = temp_dir / "extract"
        result = downloader.extract_zip(str(zip_path), str(extract_dir))

        assert Path(result).exists()
        assert Path(result).name == "data.xml"

    def test_extract_zip_invalid_zip(self, temp_dir):
        """Test extract_zip with invalid zip file."""
        downloader = ESMADataDownloader(str(temp_dir))

        # Create invalid zip file
        invalid_zip = temp_dir / "invalid.zip"
        invalid_zip.write_text("not a zip file")

        with pytest.raises(DownloadError):
            downloader.extract_zip(str(invalid_zip), str(temp_dir))
