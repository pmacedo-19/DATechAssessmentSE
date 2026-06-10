import pytest

from esma_data_processor.parser import ParseError, XMLParser


class TestXMLParser:
    """Test suite for XMLParser class."""

    def test_parse_financial_data_success(self, temp_dir, sample_dltins_xml):
        """Test successful parsing of financial data."""
        # Write sample XML to file
        xml_file = temp_dir / "test.xml"
        xml_file.write_text(sample_dltins_xml)

        parser = XMLParser()
        result = parser.parse_financial_data(str(xml_file))

        assert len(result) == 2
        assert result[0]["FinInstrmGnlAttrbts.Id"] == "TEST001"
        assert result[1]["FinInstrmGnlAttrbts.Id"] == "TEST002"

    def test_parse_financial_data_file_not_found(self):
        """Test parse with nonexistent file."""
        parser = XMLParser()

        with pytest.raises(ParseError):
            parser.parse_financial_data("/nonexistent/file.xml")

    def test_parse_financial_data_invalid_xml(self, temp_dir):
        """Test parse with invalid XML."""
        xml_file = temp_dir / "invalid.xml"
        xml_file.write_text("<invalid>xml</unclosed>")

        parser = XMLParser()

        with pytest.raises(ParseError):
            parser.parse_financial_data(str(xml_file))

    def test_extract_record_complete_data(self):
        """Test record extraction with complete data."""
        parser = XMLParser()

        # This would need mocked XML element
        # Adjust based on actual implementation
        pass
