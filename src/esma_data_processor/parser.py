import logging
from typing import Any, Dict, List, Optional

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

    REQUIRED_FIELDS = ["Id", "FullNm", "ClssfctnTp", "CmmdyDerivInd", "NtnlCcy"]

    def __init__(self) -> None:
        """Initialize XML parser."""
        self.logger = logging.getLogger(__name__)

    def _strip_namespace(self, tag: str) -> str:
        """Strip namespace from XML tag.

        Args:
            tag: Full tag name with namespace

        Returns:
            Tag name without namespace
        """
        return tag.split("}")[-1] if "}" in tag else tag

    def _find_element_by_tag(self, parent: Any, tag_name: str) -> Optional[Any]:
        """Find first child element with given tag name (ignoring namespace).

        Args:
            parent: Parent element
            tag_name: Tag name to search for (without namespace)

        Returns:
            Element if found, None otherwise
        """
        for child in parent:
            if self._strip_namespace(child.tag) == tag_name:
                return child
        return None

    def _find_all_elements_by_tag(self, parent: Any, tag_name: str) -> List[Any]:
        """Find all direct child elements with given tag name (ignoring namespace).

        Args:
            parent: Parent element
            tag_name: Tag name to search for (without namespace)

        Returns:
            List of matching elements
        """
        results = []
        for child in parent:
            if self._strip_namespace(child.tag) == tag_name:
                results.append(child)
        return results

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

            # Navigate: BizData → Pyld → Document → FinInstrmRptgRefDataDltaRpt → FinInstrm
            pyld = self._find_element_by_tag(root, "Pyld")
            if not pyld:
                self.logger.warning("No Pyld element found in XML")
                return data

            document = self._find_element_by_tag(pyld, "Document")
            if not document:
                self.logger.warning("No Document element found in Pyld")
                return data

            rpt = self._find_element_by_tag(document, "FinInstrmRptgRefDataDltaRpt")
            if not rpt:
                self.logger.warning(
                    "No FinInstrmRptgRefDataDltaRpt element found in Document"
                )
                return data

            # Find all FinInstrm elements
            fin_instrms = self._find_all_elements_by_tag(rpt, "FinInstrm")
            self.logger.info(f"Found {len(fin_instrms)} FinInstrm elements")

            # Extract data from each instrument
            for fin_elem in fin_instrms:
                record = self._extract_record(fin_elem)
                if record:
                    data.append(record)

            self.logger.info(f"Parsed {len(data)} records")
            return data

        except etree.XMLSyntaxError as e:
            raise ParseError(f"Invalid XML syntax: {e}")
        except FileNotFoundError:
            raise ParseError(f"XML file not found: {xml_path}")
        except Exception as e:
            raise ParseError(f"Unexpected error parsing XML: {e}")

    def _extract_record(self, fin_elem: Any) -> Optional[Dict[str, str]]:
        """Extract single record from FinInstrm element.

        Args:
            fin_elem: FinInstrm XML element

        Returns:
            Dictionary with instrument data or None if validation fails
        """
        try:
            # Navigate: FinInstrm → ModfdRcrd → (FinInstrmGnlAttrbts + Issr)
            modfd = self._find_element_by_tag(fin_elem, "ModfdRcrd")
            if not modfd:
                return None

            gen_attrs = self._find_element_by_tag(modfd, "FinInstrmGnlAttrbts")
            if not gen_attrs:
                return None

            record = {}

            # Extract required fields from FinInstrmGnlAttrbts
            for field in ["Id", "FullNm", "ClssfctnTp", "CmmdtyDerivInd", "NtnlCcy"]:
                elem_node = self._find_element_by_tag(gen_attrs, field)
                value = elem_node.text if elem_node is not None else ""
                record[field] = value

            # Extract Issr from ModfdRcrd (sibling of FinInstrmGnlAttrbts)
            issr_elem = self._find_element_by_tag(modfd, "Issr")
            record["Issr"] = issr_elem.text if issr_elem is not None else ""

            # Validate required fields not empty
            # (allowing Issr to be optional for lenience)
            required_values = [
                record.get("Id"),
                record.get("FullNm"),
                record.get("ClssfctnTp"),
                record.get("NtnlCcy"),
            ]
            if not all(required_values):
                self.logger.debug(f"Record missing required fields: {record}")
                return None

            return record

        except Exception as e:
            self.logger.debug(f"Error extracting record: {e}")
            return None
