import logging
import os
import sys

from dotenv import load_dotenv
from esma_data_processor.downloader import DownloadError, ESMADataDownloader
from esma_data_processor.parser import ParseError, XMLParser
from esma_data_processor.storage import StorageError, StorageFactory
from esma_data_processor.transformer import DataTransformer, TransformError

# Load environment variables
load_dotenv()


def setup_logging() -> None:
    """Configure logging for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO")

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("esma_processor.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def main() -> None:
    """Run ESMA data processing pipeline.

    Raises:
        Exception: If any pipeline step fails
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting ESMA data processing pipeline")

        # Configuration
        api_url = "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select?q=*&fq=publication_date:%5B2021-01-17T00:00:00Z+TO+2021-01-19T23:59:59Z%5D&wt=xml&indent=true&start=0&rows=100"
        output_csv = os.getenv("OUTPUT_PATH", "./output/instruments.csv")
        storage_path = os.getenv("STORAGE_PATH", "s3://my-bucket/instruments.csv")

        # Step 1: Download
        logger.info("Step 1: Downloading ESMA data")
        downloader = ESMADataDownloader()
        xml_content = downloader.fetch_xml(api_url)
        dltins_url = downloader.extract_dltins_url(xml_content)
        zip_path = "./temp_download.zip"
        downloader.download_zip(dltins_url, zip_path)
        xml_path = downloader.extract_zip(zip_path, "./temp_extract")

        # Step 2: Parse
        logger.info("Step 2: Parsing XML data")
        parser = XMLParser()
        data = parser.parse_financial_data(xml_path)

        # Step 3: Transform
        logger.info("Step 3: Transforming data")
        transformer = DataTransformer()
        transformer.to_csv(data, output_csv)

        # Read CSV and add computed columns
        import pandas as pd

        df = pd.read_csv(output_csv)
        df = transformer.add_a_count_column(df)
        df = transformer.add_contains_a_column(df)
        df.to_csv(output_csv, index=False)

        # Step 4: Upload
        logger.info("Step 4: Uploading to cloud storage")
        storage = StorageFactory.create(storage_path)
        storage.upload(output_csv, storage_path)

        logger.info("Pipeline completed successfully")

    except (DownloadError, ParseError, TransformError, StorageError) as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    main()
