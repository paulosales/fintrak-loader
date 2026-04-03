import pandas as pd
from core.importer import Importer
from utils.date_utils import parse_date_iso
from services.account_service import get_account_id_cached


class NUImporter(Importer):

    ACCOUNT_CODE = "NU"

    def __init__(self, type_map):
        self.type_map = type_map

    def parse(self, file_path: str):
        df = pd.read_csv(file_path)

        transactions = []

        for _, row in df.iterrows():
            try:
                date = str(row["date"]).strip()
                if not date:
                    continue

                amount = self._parse_amount(row["amount"])
                description = str(row.get("title") or "").strip()

                transactions.append({
                    "accountId": get_account_id_cached(self.ACCOUNT_CODE),
                    "datetime": parse_date_iso(date),
                    "amount": amount,
                    "description": description,
                    "type": self._choose_type(amount)
                })

            except Exception as e:
                print(f"Error processing row: {e}")
                continue

        return transactions

    def _parse_amount(self, amount):
        if pd.isna(amount):
            return 0.0

        val = float(amount)
        # NU credit card CSV is positive for expenses, negative for payments.
        # Normalize to the same convention as PCFinancial/RBC (debit negative, credit positive).
        return -val

    def _choose_type(self, amount):
        # Convention: negative = PURCHASE, positive = PAYMENT
        if amount < 0:
            return self.type_map.get("PURCHASE")
        return self.type_map.get("PAYMENT")