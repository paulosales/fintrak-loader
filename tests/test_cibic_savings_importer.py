import pytest
import pandas as pd
from unittest.mock import patch
from importers.cibic_savings import CIBICSavingsImporter


class TestCIBICSavingsImporter:

    @pytest.fixture
    def type_map(self):
        return {
            'PURCHASE': 1,
            'PAYMENT': 2,
        }

    @patch('importers.cibic_savings.get_account_id_cached')
    def test_parse_cibic_savings(self, mock_get_account_id, type_map):
        mock_get_account_id.return_value = 101

        csv_data = pd.DataFrame({
            'date': ['2026-03-31', '2026-03-31', '2026-03-31'],
            'description': [
                'Branch Transaction BONUS INTEREST',
                'Branch Transaction INTEREST',
                'Internet Banking INTERNET TRANSFER 000000135390'
            ],
            'empty': ['', '', ''],
            'amount': [0.12, 0.02, 1260.00]
        })

        importer = CIBICSavingsImporter(type_map)

        with patch('pandas.read_csv', return_value=csv_data):
            transactions = importer.parse('dummy.csv')

        assert len(transactions) == 3

        assert transactions[0]['accountId'] == 101
        assert transactions[0]['datetime'] == '2026-03-31 00:00:00'
        assert transactions[0]['amount'] == 0.12
        assert transactions[0]['description'] == 'Branch Transaction BONUS INTEREST'
        assert transactions[0]['type'] == 2  # INTEREST -> PAYMENT

        assert transactions[1]['amount'] == 0.02
        assert transactions[1]['type'] == 2  # INTEREST -> PAYMENT

        assert transactions[2]['amount'] == 1260.0
        assert transactions[2]['type'] == 2  # INTERNET TRANSFER -> PAYMENT

    @patch('importers.cibic_savings.get_account_id_cached')
    def test_parse_cibic_savings_transfers_out(self, mock_get_account_id, type_map):
        mock_get_account_id.return_value = 101

        csv_data = pd.DataFrame({
            'date': ['2026-03-31', '2026-03-27'],
            'description': [
                'Electronic Funds Transfer PAY BOMIMED INC CPT',
                'Internet Banking E-TRANSFER 011538802496 PAULO SANTOS'
            ],
            'empty': ['', ''],
            'amount': [1247.92, 160.00]
        })

        importer = CIBICSavingsImporter(type_map)

        with patch('pandas.read_csv', return_value=csv_data):
            transactions = importer.parse('dummy.csv')

        assert len(transactions) == 2

        assert transactions[0]['amount'] == 1247.92
        assert transactions[0]['type'] == 1  # ELECTRONIC FUNDS TRANSFER -> PURCHASE

        assert transactions[1]['amount'] == 160.0
        assert transactions[1]['type'] == 2  # E-TRANSFER -> PAYMENT

    @patch('importers.cibic_savings.get_account_id_cached')
    def test_parse_cibic_savings_empty(self, mock_get_account_id, type_map):
        mock_get_account_id.return_value = 101
        csv_data = pd.DataFrame(columns=['date', 'description', 'empty', 'amount'])

        importer = CIBICSavingsImporter(type_map)

        with patch('pandas.read_csv', return_value=csv_data):
            transactions = importer.parse('dummy.csv')

        assert transactions == []