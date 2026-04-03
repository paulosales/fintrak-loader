import pytest
import pandas as pd
from unittest.mock import patch
from importers.cibic_checking import CIBICCheckingImporter


class TestCIBICCheckingImporter:

    @pytest.fixture
    def type_map(self):
        return {
            'PURCHASE': 1,
            'PAYMENT': 2,
        }

    @patch('importers.cibic_checking.get_account_id_cached')
    def test_parse_cibic_checking(self, mock_get_account_id, type_map):
        mock_get_account_id.return_value = 100

        csv_data = pd.DataFrame({
            'date': ['2026-04-02', '2026-03-31', '2026-03-27'],
            'description': [
                'Point of Sale - Visa Debit VISA DEBIT RETAIL PURCHASE Wise 609200454561',
                'Branch Transaction SERVICE CHARGE REWARDS',
                'Automated Banking Machine ATM WITHDRAWAL SOUTHWOOD MALL 2A0J'
            ],
            'amount': [150.00, 16.95, 160.00],
            'extra': ['', '', '']
        })

        importer = CIBICCheckingImporter(type_map)

        with patch('pandas.read_csv', return_value=csv_data):
            transactions = importer.parse('dummy.csv')

        assert len(transactions) == 3

        assert transactions[0]['accountId'] == 100
        assert transactions[0]['datetime'] == '2026-04-02 00:00:00'
        assert transactions[0]['amount'] == 150.0
        assert transactions[0]['description'] == 'Point of Sale - Visa Debit VISA DEBIT RETAIL PURCHASE Wise 609200454561'
        assert transactions[0]['type'] == 1  # PURCHASE

        assert transactions[1]['amount'] == 16.95
        assert transactions[1]['type'] == 1  # SERVICE CHARGE -> PURCHASE

        assert transactions[2]['amount'] == 160.0
        assert transactions[2]['type'] == 1  # ATM WITHDRAWAL -> PURCHASE

    @patch('importers.cibic_checking.get_account_id_cached')
    def test_parse_cibic_checking_transfers(self, mock_get_account_id, type_map):
        mock_get_account_id.return_value = 100

        csv_data = pd.DataFrame({
            'date': ['2026-03-31', '2026-03-31'],
            'description': [
                'Internet Banking E-TRANSFER 105883526651 Paulo Rogério',
                'Internet Banking INTERNET TRANSFER 000000135390'
            ],
            'amount': [1000.00, 1260.00],
            'extra': ['', '']
        })

        importer = CIBICCheckingImporter(type_map)

        with patch('pandas.read_csv', return_value=csv_data):
            transactions = importer.parse('dummy.csv')

        assert len(transactions) == 2

        assert transactions[0]['amount'] == 1000.0
        assert transactions[0]['type'] == 2  # E-TRANSFER -> PAYMENT

        assert transactions[1]['amount'] == 1260.0
        assert transactions[1]['type'] == 2  # INTERNET TRANSFER -> PAYMENT

    @patch('importers.cibic_checking.get_account_id_cached')
    def test_parse_cibic_checking_empty(self, mock_get_account_id, type_map):
        mock_get_account_id.return_value = 100
        csv_data = pd.DataFrame(columns=['date', 'description', 'amount', 'extra'])

        importer = CIBICCheckingImporter(type_map)

        with patch('pandas.read_csv', return_value=csv_data):
            transactions = importer.parse('dummy.csv')

        assert transactions == []