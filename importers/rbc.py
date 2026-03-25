import pandas as pd
from core.importer import Importer
from utils.date_utils import parse_datetime
from services.account_service import get_account_id_cached


class RBCImporter(Importer):

    ACCOUNT_CODE_MAP = {
        "Chequing": "RBCCHEK",
        "Savings": "RBCSAV",
        "Visa": "RBCVISA"
    }

    def __init__(self, type_map):
        self.type_map = type_map

    def parse(self, file_path: str):
        columns = [
            "account_type",
            "account_number",
            "transaction_date",
            "cheque_number",
            "description_1",
            "description_2",
            "cad",
            "usd",
            "extra"
        ]
        df = pd.read_csv(file_path, names=columns, header=0, engine="python")

        transactions = []

        for _, row in df.iterrows():
            try:
                account_type = row["account_type"].strip()
                account_code = self.ACCOUNT_CODE_MAP.get(account_type)

                if not account_code:
                    print(f"Unknown account type: {account_type}")
                    continue

                date_str = row["transaction_date"]

                datetime = parse_datetime(date_str, "12:00 PM")
                amount = self._parse_amount(row)
                description = self._build_description(row)
                type_code = self._map_type(description, amount, account_type)

                transactions.append({
                    "accountId": get_account_id_cached(account_code),
                    "datetime": datetime,
                    "amount": amount,
                    "description": description,
                    "type": type_code
                })

            except Exception as e:
                print(f"Error processing row: {e}")
                continue

        return transactions

    def _parse_amount(self, row):
        cad = row.get("cad")
        usd = row.get("usd")

        if pd.notna(cad):
            return float(cad)

        if pd.notna(usd):
            return float(usd)

        return 0.0

    def _build_description(self, row):
        d1 = str(row.get("description_1") or "").strip()
        d2 = str(row.get("description_2") or "").strip()

        description = f"{d1} {d2}".strip()

        # Clean extra spaces
        return " ".join(description.split())

    def _map_type(self, description: str, amount: float, account_type: str):
        desc = description.upper()

        # 🔹 Interest
        if "INTEREST" in desc:
            return self.type_map.get("INTEREST")

        # 🔹 Payments (credit card)
        if "PAYMENT" in desc and account_type == "Visa":
            return self.type_map.get("PAYMENT")

        # 🔹 Transfers / E-Transfers
        if "TRANSFER" in desc or "TRF" in desc:
            return self.type_map.get("PAYMENT")

        # 🔹 Default rules
        if amount < 0:
            return self.type_map.get("PURCHASE")

        return self.type_map.get("PAYMENT")
