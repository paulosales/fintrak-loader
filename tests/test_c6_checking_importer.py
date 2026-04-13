import io
import pytest
import pandas as pd
from unittest.mock import patch, mock_open
from importers.c6_checking import C6CheckingImporter


SAMPLE_CSV_HEADER = """\
EXTRATO DE CONTA CORRENTE C6 BANK

Agência: 1 / Conta: 289279313
Extrato gerado em 12/04/2026 - as 20:48:41

Extrato de 12/04/2025 a 12/04/2026

Data Lançamento,Data Contábil,Título,Descrição,Entrada(R$),Saída(R$),Saldo do Dia(R$)
28/04/2025,28/04/2025,RESGATE DE CDB,,3000.77,0.00,3548.90
30/04/2025,30/04/2025,Pix recebido c6 de ODENISIO SOARES DA SILVA,Pix recebido c6 de ODENISIO SOARES DA SILVA,500.00,0.00,4048.90
01/05/2025,02/05/2025,Pix enviado para BANCO SANTANDER (BRASIL) S.A.,TRANSF ENVIADA PIX,0.00,2618.54,1539.01
02/05/2025,02/05/2025,UNIMED FORTALEZA SOCIEDADE COOP,UNIMED FORTALEZA SOCIEDADE COOP,0.00,411.35,1539.01
"""


class TestC6CheckingImporter:

    @pytest.fixture
    def type_map(self):
        return {
            "PAYMENT": 1,
            "PURCHASE": 2,
        }

    @pytest.fixture
    def importer(self, type_map):
        return C6CheckingImporter(type_map)

    # ------------------------------------------------------------------
    # _find_header_line
    # ------------------------------------------------------------------

    def test_find_header_line(self, importer, tmp_path):
        f = tmp_path / "c6.csv"
        f.write_text(SAMPLE_CSV_HEADER, encoding="utf-8")
        assert importer._find_header_line(str(f)) == 7

    def test_find_header_line_raises_when_missing(self, importer, tmp_path):
        f = tmp_path / "bad.csv"
        f.write_text("some,other,content\n1,2,3\n", encoding="utf-8")
        with pytest.raises(ValueError, match="Could not find header row"):
            importer._find_header_line(str(f))

    # ------------------------------------------------------------------
    # _parse_brl
    # ------------------------------------------------------------------

    def test_parse_brl_simple(self, importer):
        assert importer._parse_brl("2618.54") == 2618.54

    def test_parse_brl_nan(self, importer):
        assert importer._parse_brl(float("nan")) == 0.0

    def test_parse_brl_empty(self, importer):
        assert importer._parse_brl("") == 0.0

    def test_parse_brl_comma_decimal(self, importer):
        assert importer._parse_brl("1.234,56") == pytest.approx(1234.56)

    # ------------------------------------------------------------------
    # _build_description
    # ------------------------------------------------------------------

    def test_build_description_different(self, importer):
        result = importer._build_description("Pix enviado para BANCO SANTANDER", "TRANSF ENVIADA PIX")
        assert result == "Pix enviado para BANCO SANTANDER - TRANSF ENVIADA PIX"

    def test_build_description_same(self, importer):
        desc = "Pix recebido c6 de ODENISIO SOARES DA SILVA"
        assert importer._build_description(desc, desc) == desc

    def test_build_description_empty_description(self, importer):
        assert importer._build_description("RESGATE DE CDB", "") == "RESGATE DE CDB"

    # ------------------------------------------------------------------
    # _map_type
    # ------------------------------------------------------------------

    def test_map_type_income_pix(self, importer):
        assert importer._map_type("PIX RECEBIDO C6 DE SOMEONE", 500.0) == 1  # PAYMENT

    def test_map_type_income_resgate(self, importer):
        assert importer._map_type("RESGATE DE CDB", 3000.77) == 1  # PAYMENT

    def test_map_type_expense_transf(self, importer):
        assert importer._map_type("Pix enviado para BANCO - TRANSF ENVIADA PIX", -2618.54) == 2  # PURCHASE

    def test_map_type_expense_pgto_cartao(self, importer):
        assert importer._map_type("PGTO FAT CARTAO C6 - Fatura de cartão", -326.68) == 2  # PURCHASE

    def test_map_type_expense_saque(self, importer):
        assert importer._map_type("SAQUE BANCO 24H - TERMINAL TECBAN", -100.0) == 2  # PURCHASE

    def test_map_type_fallback_positive(self, importer):
        assert importer._map_type("UNKNOWN TRANSACTION", 50.0) == 1  # PAYMENT

    def test_map_type_fallback_negative(self, importer):
        assert importer._map_type("UNKNOWN TRANSACTION", -50.0) == 2  # PURCHASE

    # ------------------------------------------------------------------
    # parse (integration over real file content)
    # ------------------------------------------------------------------

    @patch("importers.c6_checking.get_account_id_cached")
    def test_parse_returns_correct_count(self, mock_account, importer, tmp_path):
        mock_account.return_value = 42
        f = tmp_path / "c6.csv"
        f.write_text(SAMPLE_CSV_HEADER, encoding="utf-8")

        transactions = importer.parse(str(f))

        # 4 data rows: RESGATE, Pix recebido, Pix enviado, UNIMED
        assert len(transactions) == 4

    @patch("importers.c6_checking.get_account_id_cached")
    def test_parse_credit_row(self, mock_account, importer, tmp_path):
        mock_account.return_value = 42
        f = tmp_path / "c6.csv"
        f.write_text(SAMPLE_CSV_HEADER, encoding="utf-8")

        transactions = importer.parse(str(f))

        resgate = transactions[0]
        assert resgate["accountId"] == 42
        assert resgate["amount"] == pytest.approx(3000.77)
        assert resgate["datetime"] == "2025-04-28 12:00:00"
        assert resgate["type"] == 1  # PAYMENT

    @patch("importers.c6_checking.get_account_id_cached")
    def test_parse_debit_row(self, mock_account, importer, tmp_path):
        mock_account.return_value = 42
        f = tmp_path / "c6.csv"
        f.write_text(SAMPLE_CSV_HEADER, encoding="utf-8")

        transactions = importer.parse(str(f))

        pix_sent = transactions[2]
        assert pix_sent["amount"] == pytest.approx(-2618.54)
        assert pix_sent["type"] == 2  # PURCHASE

    @patch("importers.c6_checking.get_account_id_cached")
    def test_parse_account_id(self, mock_account, importer, tmp_path):
        mock_account.return_value = 99
        f = tmp_path / "c6.csv"
        f.write_text(SAMPLE_CSV_HEADER, encoding="utf-8")

        transactions = importer.parse(str(f))

        mock_account.assert_called_with("C6CHECK")
        assert all(t["accountId"] == 99 for t in transactions)
