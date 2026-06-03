import logging
from typing import Any, Dict, List

from lxml import etree

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Custom exception for parsing errors."""

    pass


class XMLParser:
    """Parse DLTINS XML files and extract financial instrument data.

    This class reads XML files and extracts structured data
    about financial instruments.
    """

    REQUIRED_FIELDS = ["Id", "FullNm", "ClssfctnTp", "CmmdtyDerivInd", "NtnlCcy"]

    def __init__(self) -> None:
        """Initialize XML parser."""
        self.logger = logging.getLogger(__name__)

    def parse_financial_data(self, xml_path: str) -> List[Dict[str, str]]:
        """Parse DLTINS XML file and extract financial instrument data.

        Args:
            xml_path: Path to DLTINS XML file

        Returns:
            List of dictionaries containing financial instrument data

        Raises:
            ParseError: If parsing fails
        """
        try:
            self.logger.info(f"Parsing XML file: {xml_path}")

            with open(xml_path, "rb") as f:
                tree = etree.parse(f)

            root = tree.getroot()
            data = []

            # Find all financial instrument elements
            # Adjust XPath based on actual XML structure
            for elem in root.xpath("//FinInstrm"):
                record = self._extract_record(elem)
                if record:
                    data.append(record)

            self.logger.info(f"Parsed {len(data)} records")
            return data

        except etree.XMLSyntaxError as e:
            raise ParseError(f"Invalid XML syntax: {e}")
        except FileNotFoundError:
            raise ParseError(f"XML file not found: {xml_path}")

    def _extract_record(self, elem: Any) -> Dict[str, str]:
        """Extract single record from XML element.

        Args:
            elem: XML element

        Returns:
            Dictionary with instrument data or None if validation fails
        """
        try:
            # Navigate XML structure (adjust to actual structure)
            gen_attrs = elem.find(".//FinInstrmGnlAttrbts")
            if gen_attrs is None:
                return None

            record = {}

            # Extract fields
            for field in self.REQUIRED_FIELDS:
                elem_node = gen_attrs.find(field)
                record[f"FinInstrmGnlAttrbts.{field}"] = (
                    elem_node.text if elem_node is not None else ""
                )

            # Extract Issr
            issr_elem = elem.find(".//Issr")
            record["Issr"] = issr_elem.text if issr_elem is not None else ""

            # Validate required fields present
            if not all(record.values()):
                self.logger.warning(f"Record missing required fields: {record}")
                return None

            return record

        except Exception as e:
            self.logger.warning(f"Error extracting record: {e}")
            return None
