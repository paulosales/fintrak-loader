import pandas as pd
from core.importer import Importer
from utils.date_utils import parse_datetime_br
from services.account_service import get_account_id_cached


class BBImporter(Importer):

    ACCOUNT_CODE = "BBCC"

    def __init__(self, type_map):
        self.type_map = type_map

    def parse(self, file_path: str):
        columns = [
            "Data",
            "Lançamento",
            "Detalhes",
            "N° documento",
            "Valor",
            "Tipo Lançamento"
        ]
        df = pd.read_csv(file_path, names=columns, header=0, engine="python", encoding='iso-8859-1')

        transactions = []

        for _, row in df.iterrows():
            try:
                date_str = row["Data"].strip()
                if date_str == "00/00/0000":
                    continue  # Skip summary rows

                datetime = parse_datetime_br(date_str)
                amount = self._parse_amount(row["Valor"])
                description = self._build_description(row)
                type_code = self._map_type(row["Tipo Lançamento"], amount)

                transactions.append({
                    "accountId": get_account_id_cached(self.ACCOUNT_CODE),
                    "datetime": datetime,
                    "amount": amount,
                    "description": description,
                    "type": type_code
                })

            except Exception as e:
                print(f"Error processing row: {e}")
                continue

        return transactions

    def _parse_amount(self, amount_str):
        if pd.isna(amount_str):
            return 0.0
        # Remove thousand separators (dots) and replace comma with dot for decimal
        amount_str = amount_str.replace('.', '').replace(',', '.')
        return float(amount_str)

    def _build_description(self, row):
        lancamento = str(row.get("Lançamento") or "").strip()
        detalhes = str(row.get("Detalhes") or "").strip()

        description = f"{lancamento} {detalhes}".strip()

        # Clean extra spaces
        return " ".join(description.split())

    def _map_type(self, tipo_lancamento, amount):
        tipo = str(tipo_lancamento).strip().upper()

        if tipo == "SAÍDA":
            return self.type_map.get("PURCHASE")  # Assuming debit is purchase
        elif tipo == "ENTRADA":
            return self.type_map.get("PAYMENT")  # Assuming credit is payment
        else:
            # For others, like saldo, but we skip them anyway
            return self.type_map.get("PAYMENT")