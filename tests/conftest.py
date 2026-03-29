import pytest
import sys
import os
from unittest.mock import Mock, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(autouse=True)
def mock_ocr_dependencies(monkeypatch):
    """Mock OCR-related dependencies for all tests."""
    # Mock pytesseract
    pytesseract_mock = MagicMock()
    monkeypatch.setitem(sys.modules, 'pytesseract', pytesseract_mock)

    # Mock PIL
    pil_mock = MagicMock()
    monkeypatch.setitem(sys.modules, 'PIL', pil_mock)

    # Mock core.ocr
    ocr_mock = MagicMock()
    monkeypatch.setitem(sys.modules, 'core.ocr', ocr_mock)

    # Mock importers.receipt_ocr
    receipt_ocr_mock = MagicMock()
    monkeypatch.setitem(sys.modules, 'importers.receipt_ocr', receipt_ocr_mock)


@pytest.fixture
def mock_db_connection():
    """Mock database connection for testing."""
    connection = Mock()
    cursor = Mock()
    connection.cursor.return_value = cursor
    return connection, cursor


@pytest.fixture
def sample_transaction():
    """Sample transaction data for testing."""
    return {
        'id': 1,
        'account_id': 1,
        'transaction_type_id': 1,
        'datetime': '2023-01-01 10:00:00',
        'amount': 100.50,
        'description': 'Test transaction',
        'note': None,
        'fingerprint': 'd5a44a049ac7a65abf8e0b8c7be96d30'
    }


@pytest.fixture
def sample_transaction_for_fingerprint():
    """Sample transaction data for fingerprint generation."""
    return {
        'datetime': '2023-01-01 10:00:00',
        'amount': '100.50',
        'description': 'Test transaction'
    }