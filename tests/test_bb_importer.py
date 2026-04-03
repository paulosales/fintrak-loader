import pytest
import pandas as pd
from unittest.mock import patch
from importers.bb import BBImporter


class TestBBImporter:

    @pytest.fixture
    def type_map(self):
        return {
            'PURCHASE': 1,
            'PAYMENT': 2,
            'INTEREST': 3
        }

    @patch('importers.bb.get_account_id_cached')
    def test_parse_bb_csv(self, mock_get_account_id, type_map):
        mock_get_account_id.return_value = 99

        csv_data = pd.DataFrame({
            'Data': ['27/11/2025', '04/12/2025', '00/00/0000', '09/12/2025'],
            'Lançamento': ['Saldo Anterior', 'Pix - Enviado', 'Saldo do dia', 'Pix - Enviado'],
            'Detalhes': ['', '04/12 22:17 Sabrina Sousa Duarte', '', '09/12 11:47 DOM'],
            'N° documento': ['', '120401', '', '120901'],
            'Valor': ['686,02', '-50,00', '636,02', '-50,00'],
            'Tipo Lançamento': ['', 'Saída', '', 'Saída']
        })

        importer = BBImporter(type_map)

        with patch('pandas.read_csv', return_value=csv_data):
            transactions = importer.parse('dummy.csv')

        assert len(transactions) == 3

        assert transactions[0]['accountId'] == 99
        assert transactions[0]['datetime'] == '2025-11-27 12:00:00'
        assert transactions[0]['amount'] == 686.02
        assert transactions[0]['description'] == 'Saldo Anterior'
        assert transactions[0]['type'] == 2  # default PAYMENT for non-type row

        assert transactions[1]['amount'] == -50.0
        assert transactions[1]['description'] == 'Pix - Enviado 04/12 22:17 Sabrina Sousa Duarte'
        assert transactions[1]['type'] == 1  # SAÍDA -> PURCHASE

        assert transactions[2]['amount'] == -50.0
        assert transactions[2]['description'] == 'Pix - Enviado 09/12 11:47 DOM'
        assert transactions[2]['type'] == 1

    @patch('importers.bb.get_account_id_cached')
    def test_parse_bb_empty(self, mock_get_account_id, type_map):
        mock_get_account_id.return_value = 99
        csv_data = pd.DataFrame(columns=['Data', 'Lançamento', 'Detalhes', 'N° documento', 'Valor', 'Tipo Lançamento'])

        importer = BBImporter(type_map)

        with patch('pandas.read_csv', return_value=csv_data):
            transactions = importer.parse('dummy.csv')

        assert transactions == []
