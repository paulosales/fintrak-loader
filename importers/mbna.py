import pandas as pd
from core.importer import Importer
from utils.date_utils import parse_datetime  # reuse your existing function

class MBNACardImporter(Importer):

    def __init__(self, transaction_type_map):
        self.transaction_type_map = transaction_type_map

    def parse(self, file_path: str):
        df = pd.read_csv(file_path)

        transactions = []

        for _, row in df.iterrows():
            try:
                date_str = row["Posted Date"]
                amount = float(row["Amount"])
                description = row["Payee"].strip()

                # MBNA does not have time → default to midnight
                datetime = parse_datetime(date_str, "12:00 PM")

                # Determine transaction type
                type_code = self._map_type(description, amount)

                transactions.append({
                    "datetime": datetime,
                    "amount": amount,
                    "description": description,
                    "type": type_code
                })

            except Exception as e:
                print(f"Error occurred while processing row: {e}")
                continue

        return transactions

    def _map_type(self, description: str, amount: float):
        desc = description.upper()

        if "PAYMENT" in desc:
            return self.transaction_type_map.get("PAYMENT")

        if "REFUND" in desc:
            return self.transaction_type_map.get("REFUND")

        if "INTEREST" in desc:
            return self.transaction_type_map.get("INTEREST")

        # Default rule
        if amount < 0:
            return self.transaction_type_map.get("PURCHASE")

        return self.transaction_type_map.get("PAYMENT")