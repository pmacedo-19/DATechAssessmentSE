import logging
import zipfile
from pathlib import Path

import requests
from lxml import etree

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Custom exception for download-related errors."""

    pass


class ESMADataDownloader:
    """Downloads and extracts ESMA financial instrument data.

    This class handles downloading XML files from ESMA registers,
    locating the DLTINS zip file, and extracting XML content.
    """

    def __init__(self, output_dir: str = "./downloads") -> None:
        """Initialize downloader with output directory.

        Args:
            output_dir: Directory to store downloaded files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def fetch_xml(self, url: str) -> str:
        """Fetch XML content from ESMA API endpoint.

        Args:
            url: ESMA API endpoint URL

        Returns:
            XML content as string

        Raises:
            DownloadError: If download fails
        """
        try:
            self.logger.info(f"Fetching XML from {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise DownloadError(f"Failed to fetch XML: {e}")

    def extract_dltins_url(self, xml: str) -> str:
        """Extract DLTINS zip download URL from XML.

        Args:
            xml: XML content as string

        Returns:
            Download URL for DLTINS zip file

        Raises:
            DownloadError: If DLTINS URL not found
        """
        try:
            self.logger.info("Parsing XML for DLTINS download link")
            root = etree.fromstring(xml.encode())
            # Find all doc elements
            docs = root.xpath('//doc')
            self.logger.info(f"Found {len(docs)} doc elements in XML")

            dltins_urls = []
  
            # Extract DLTINS URLs from docs
            for doc in docs:
                file_type = None
                download_link = None

                # Find file_type and download_link in str elements
                for str_elem in doc.findall('str'):
                    name_attr = str_elem.get('name')

                    if name_attr == 'file_type' and str_elem.text == 'DLTINS':
                        file_type = str_elem.text
                    elif name_attr == 'download_link':
                        download_link = str_elem.text

                # If this is a DLTINS file, save the URL
                if file_type == 'DLTINS' and download_link:
                    dltins_urls.append(download_link)
                    self.logger.info(f"Found DLTINS URL: {download_link}")

            if len(dltins_urls) == 0:
                raise DownloadError("No DLTINS files found in XML")

            # Use 2nd if available, otherwise use 1st
            file_index = min(1, len(dltins_urls) - 1)
            selected_url = dltins_urls[file_index]
            self.logger.info(f"Using DLTINS file {file_index + 1} of {len(dltins_urls)}")
            return selected_url
        except etree.XMLSyntaxError as e:
            raise DownloadError(f"Invalid XML: {e}")

    def download_zip(self, url: str, output_path: str) -> None:
        """Download zip file from URL with retry logic.

        Args:
            url: Download URL
            output_path: Path to save zip file

        Raises:
            DownloadError: If download fails after retries
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.logger.info(
                    f"Downloading zip (attempt {attempt + 1}/{max_retries})"
                )
                response = requests.get(url, timeout=60, stream=True)
                response.raise_for_status()

                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                self.logger.info(f"Successfully downloaded to {output_path}")
                return
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise DownloadError(
                        f"Failed to download after {max_retries} attempts: {e}"
                    )
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying...")

    def extract_zip(self, zip_path: str, output_dir: str) -> str:
        """Extract XML file from zip.

        Args:
            zip_path: Path to zip file
            output_dir: Directory to extract files

        Returns:
            Path to extracted XML file

        Raises:
            DownloadError: If extraction fails
        """
        try:
            self.logger.info(f"Extracting zip from {zip_path}")
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(output_path)

            # Find XML file
            xml_files = list(output_path.glob("*.xml"))
            if not xml_files:
                raise DownloadError("No XML files found in zip")

            xml_file = xml_files[0]
            self.logger.info(f"Extracted XML to {xml_file}")
            return str(xml_file)
        except (zipfile.BadZipFile, FileNotFoundError) as e:
            raise DownloadError(f"Failed to extract zip: {e}")
