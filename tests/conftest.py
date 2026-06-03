import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide temporary directory for test files.

    Yields:
        Path to temporary directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_xml() -> str:
    """Provide sample ESMA XML response.

    Returns:
        Sample XML content as string
    """
    return """<?xml version="1.0"?>
    <response>
        <result numFound="2">
            <file file_type="DLTINS">
                <url>https://example.com/download1.zip</url>
            </file>
            <file file_type="DLTINS">
                <url>https://example.com/download2.zip</url>
            </file>
        </result>
    </response>
    """


@pytest.fixture
def sample_dltins_xml() -> str:
    """Provide sample DLTINS XML content.

    Returns:
        Sample DLTINS XML as string
    """
    return """<?xml version="1.0"?>
    <FinInstrmRptgSts>
        <FinInstrm>
            <FinInstrmGnlAttrbts>
                <Id>TEST001</Id>
                <FullNm>Test Financial Instrument A</FullNm>
                <ClssfctnTp>EQUITY</ClssfctnTp>
                <CmmdtyDerivInd>N</CmmdtyDerivInd>
                <NtnlCcy>USD</NtnlCcy>
            </FinInstrmGnlAttrbts>
            <Issr>TEST_ISSUER_1</Issr>
        </FinInstrm>
        <FinInstrm>
            <FinInstrmGnlAttrbts>
                <Id>TEST002</Id>
                <FullNm>Another Test Value</FullNm>
                <ClssfctnTp>BOND</ClssfctnTp>
                <CmmdtyDerivInd>N</CmmdtyDerivInd>
                <NtnlCcy>EUR</NtnlCcy>
            </FinInstrmGnlAttrbts>
            <Issr>TEST_ISSUER_2</Issr>
        </FinInstrm>
    </FinInstrmRptgSts>
    """


@pytest.fixture
def sample_data() -> list:
    """Provide sample parsed financial instrument data.

    Returns:
        List of dictionaries with instrument data
    """
    return [
        {
            "FinInstrmGnlAttrbts.Id": "TEST001",
            "FinInstrmGnlAttrbts.FullNm": "Test Financial Instrument A",
            "FinInstrmGnlAttrbts.ClssfctnTp": "EQUITY",
            "FinInstrmGnlAttrbts.CmmdtyDerivInd": "N",
            "FinInstrmGnlAttrbts.NtnlCcy": "USD",
            "Issr": "TEST_ISSUER_1",
        },
        {
            "FinInstrmGnlAttrbts.Id": "TEST002",
            "FinInstrmGnlAttrbts.FullNm": "Another Test Value",
            "FinInstrmGnlAttrbts.ClssfctnTp": "BOND",
            "FinInstrmGnlAttrbts.CmmdtyDerivInd": "N",
            "FinInstrmGnlAttrbts.NtnlCcy": "EUR",
            "Issr": "TEST_ISSUER_2",
        },
    ]


@pytest.fixture
def env_setup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up environment variables for testing.

    Args:
        monkeypatch: pytest fixture for modifying environment
    """
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("OUTPUT_PATH", "./test_output")
    monkeypatch.setenv("AWS_S3_BUCKET", "test-bucket")
