import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from importers.pcfinancial import PCFinancialImporter


class TestPCFinancialImporter:
    """Test cases for PCFinancial importer."""

    @pytest.fixture
    def sample_csv_data(self):
        """Sample CSV data for testing."""
        return pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02'],
            'Time': ['10:00:00', '11:30:00'],
            'Amount': [100.50, -50.25],
            'Description': ['Purchase at Store', 'ATM Withdrawal'],
            'Type': ['PURCHASE', 'WITHDRAWAL']
        })

    @pytest.fixture
    def transaction_type_map(self):
        """Sample transaction type mapping."""
        return {
            'PURCHASE': 1,
            'WITHDRAWAL': 2,
            'DEPOSIT': 3
        }

    @patch('importers.pcfinancial.get_account_id_cached')
    @patch('importers.pcfinancial.parse_datetime')
    def test_parse_success(self, mock_parse_datetime, mock_get_account_id,
                          sample_csv_data, transaction_type_map):
        """Test successful parsing of PCFinancial CSV."""
        # Setup mocks
        mock_get_account_id.return_value = 1
        mock_parse_datetime.side_effect = [
            '2023-01-01 10:00:00',
            '2023-01-02 11:30:00'
        ]

        # Create importer
        importer = PCFinancialImporter(transaction_type_map)

        # Mock pandas read_csv
        with patch('pandas.read_csv', return_value=sample_csv_data):
            transactions = importer.parse('dummy.csv')

        # Verify results
        assert len(transactions) == 2

        # Check first transaction
        assert transactions[0]['accountId'] == 1
        assert transactions[0]['datetime'] == '2023-01-01 10:00:00'
        assert transactions[0]['amount'] == 100.50
        assert transactions[0]['description'] == 'Purchase at Store'
        assert transactions[0]['type'] == 1  # PURCHASE type

        # Check second transaction
        assert transactions[1]['accountId'] == 1
        assert transactions[1]['datetime'] == '2023-01-02 11:30:00'
        assert transactions[1]['amount'] == -50.25
        assert transactions[1]['description'] == 'ATM Withdrawal'
        assert transactions[1]['type'] == 2  # WITHDRAWAL type

    @patch('importers.pcfinancial.get_account_id_cached')
    @patch('importers.pcfinancial.parse_datetime')
    def test_parse_unknown_transaction_type(self, mock_parse_datetime, mock_get_account_id,
                                           transaction_type_map):
        """Test parsing with unknown transaction type falls back to PURCHASE."""
        # Setup mocks
        mock_get_account_id.return_value = 1
        mock_parse_datetime.return_value = '2023-01-01 10:00:00'

        # Create data with unknown type
        csv_data = pd.DataFrame({
            'Date': ['2023-01-01'],
            'Time': ['10:00:00'],
            'Amount': [75.00],
            'Description': ['Unknown transaction'],
            'Type': ['UNKNOWN']  # This type is not in the map
        })

        importer = PCFinancialImporter(transaction_type_map)

        with patch('pandas.read_csv', return_value=csv_data):
            transactions = importer.parse('dummy.csv')

        assert len(transactions) == 1
        assert transactions[0]['type'] == 1  # Should fall back to PURCHASE (1)

    @patch('importers.pcfinancial.get_account_id_cached')
    @patch('importers.pcfinancial.parse_datetime')
    def test_parse_empty_csv(self, mock_parse_datetime, mock_get_account_id, transaction_type_map):
        """Test parsing empty CSV file."""
        # Setup mocks
        mock_get_account_id.return_value = 1

        # Empty dataframe
        csv_data = pd.DataFrame(columns=['Date', 'Time', 'Amount', 'Description', 'Type'])

        importer = PCFinancialImporter(transaction_type_map)

        with patch('pandas.read_csv', return_value=csv_data):
            transactions = importer.parse('dummy.csv')

        assert len(transactions) == 0

    def test_init(self, transaction_type_map):
        """Test importer initialization."""
        importer = PCFinancialImporter(transaction_type_map)
        assert importer.transaction_type_map == transaction_type_map