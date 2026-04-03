import pytest
import pandas as pd
from unittest.mock import patch
from importers.nu import NUImporter


class TestNUImporter:

    @pytest.fixture
    def transaction_type_map(self):
        return {
            'PURCHASE': 1,
            'PAYMENT': 2,
        }

    @patch('importers.nu.get_account_id_cached')
    def test_parse_nubank_rows(self, mock_get_account_id, transaction_type_map):
        mock_get_account_id.return_value = 42

        csv_data = pd.DataFrame({
            'date': ['2026-03-07', '2026-02-08'],
            'title': ['Uber Uber *Trip Help.U', 'Pagamento recebido'],
            'amount': [17.99, -111.97]
        })

        importer = NUImporter(transaction_type_map)

        with patch('pandas.read_csv', return_value=csv_data):
            transactions = importer.parse('dummy.csv')

        assert len(transactions) == 2

        assert transactions[0]['accountId'] == 42
        assert transactions[0]['datetime'] == '2026-03-07 00:00:00'
        assert transactions[0]['amount'] == -17.99
        assert transactions[0]['description'] == 'Uber Uber *Trip Help.U'
        assert transactions[0]['type'] == 1  # PURCHASE

        assert transactions[1]['amount'] == 111.97
        assert transactions[1]['type'] == 2  # PAYMENT

    @patch('importers.nu.get_account_id_cached')
    def test_parse_empty_csv(self, mock_get_account_id, transaction_type_map):
        mock_get_account_id.return_value = 42
        csv_data = pd.DataFrame(columns=['date', 'title','amount'])

        importer = NUImporter(transaction_type_map)

        with patch('pandas.read_csv', return_value=csv_data):
            transactions = importer.parse('dummy.csv')

        assert transactions == []
