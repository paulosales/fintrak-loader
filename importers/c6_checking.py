import pandas as pd
from core.importer import Importer
from utils.date_utils import parse_datetime_br
from services.account_service import get_account_id_cached


class C6CheckingImporter(Importer):
    """
    Importer for C6 Bank Conta Corrente CSV export.

    Expected header row (after 8 lines of bank metadata):
        Data Lançamento,Data Contábil,Título,Descrição,Entrada(R$),Saída(R$),Saldo do Dia(R$)

    Amount convention:
        - Entrada (credit/income) > 0  → positive amount
        - Saída   (debit/expense) > 0  → negative amount
    """

    ACCOUNT_CODE = "C6CHECK"
    HEADER_ROW = "Data Lançamento"

    def __init__(self, type_map):
        self.type_map = type_map

    def parse(self, file_path: str):
        header_line = self._find_header_line(file_path)

        df = pd.read_csv(
            file_path,
            skiprows=header_line,
            encoding="utf-8",
        )

        # Normalise column names (strip whitespace)
        df.columns = [c.strip() for c in df.columns]

        transactions = []

        for _, row in df.iterrows():
            try:
                date_str = str(row["Data Lançamento"]).strip()
                if not date_str or pd.isna(row["Data Lançamento"]):
                    continue

                credit = self._parse_brl(row["Entrada(R$)"])
                debit = self._parse_brl(row["Saída(R$)"])

                # Skip rows where both amounts are zero (e.g. footer lines)
                if credit == 0.0 and debit == 0.0:
                    continue

                amount = credit - debit  # positive = income, negative = expense
                title = str(row.get("Título", "") or "").strip()
                description = str(row.get("Descrição", "") or "").strip()
                full_description = self._build_description(title, description)
                type_code = self._map_type(full_description, amount)

                transactions.append({
                    "accountId": get_account_id_cached(self.ACCOUNT_CODE),
                    "datetime": parse_datetime_br(date_str),
                    "amount": amount,
                    "description": full_description,
                    "type": type_code,
                })

            except Exception as e:
                print(f"[C6Checking] Error processing row: {e} — row: {dict(row)}")
                continue

        return transactions

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _find_header_line(self, file_path: str) -> int:
        """Return the 0-based line index of the CSV header row."""
        with open(file_path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if line.startswith(self.HEADER_ROW):
                    return i
        raise ValueError(f"Could not find header row starting with '{self.HEADER_ROW}' in {file_path}")

    def _parse_brl(self, value) -> float:
        """Parse a decimal string to float.

        Handles two formats:
        - Standard dot-decimal (e.g. '2618.54') — used by C6 CSV exports
        - Brazilian comma-decimal with dot thousands (e.g. '2.618,54')
        """
        if pd.isna(value):
            return 0.0
        s = str(value).strip()
        if not s:
            return 0.0
        # Brazilian format: has comma as decimal separator
        if "," in s:
            s = s.replace(".", "").replace(",", ".")
        # Standard dot-decimal format: parse directly
        try:
            return float(s)
        except ValueError:
            return 0.0

    def _build_description(self, title: str, description: str) -> str:
        """Combine Título + Descrição into a single meaningful description."""
        if description and description != title:
            return f"{title} - {description}".strip(" -")
        return title or description

    def _map_type(self, description: str, amount: float) -> str:
        desc = description.upper()

        # Transfers sent (debits)
        if any(k in desc for k in ["TRANSF ENVIADA", "PIX ENVIADO", "PGTO FAT CARTAO", "SAQUE"]):
            return self.type_map.get("PURCHASE")

        # Transfers received (credits)
        if any(k in desc for k in ["PIX RECEBIDO", "TRANSF RECEBIDA", "PIX RECEBIDO C6",
                                    "DEVOL RECEBIDA", "EST PGO BOLETO"]):
            return self.type_map.get("PAYMENT")

        # CDB redemptions are income
        if "RESGATE DE CDB" in desc:
            return self.type_map.get("PAYMENT")

        # Fall back to sign
        if amount >= 0:
            return self.type_map.get("PAYMENT")
        return self.type_map.get("PURCHASE")
