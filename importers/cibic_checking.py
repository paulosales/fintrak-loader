import pandas as pd
from core.importer import Importer
from utils.date_utils import parse_date_iso
from services.account_service import get_account_id_cached


class CIBICCheckingImporter(Importer):

    ACCOUNT_CODE = "CIBICCHK"

    def __init__(self, type_map):
        self.type_map = type_map

    def parse(self, file_path: str):
        # CSV has no header, columns: date, description, amount, empty
        df = pd.read_csv(file_path, header=None, names=['date', 'description', 'amount', 'extra'])

        transactions = []

        for _, row in df.iterrows():
            try:
                date_str = str(row['date']).strip()
                if not date_str or pd.isna(date_str):
                    continue

                amount = self._parse_amount(row['amount'])
                description = str(row['description']).strip()
                type_code = self._map_type(description, amount)

                transactions.append({
                    "accountId": get_account_id_cached(self.ACCOUNT_CODE),
                    "datetime": parse_date_iso(date_str),
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
        return float(amount_str)

    def _map_type(self, description, amount):
        desc = description.upper()

        # Debits (expenses)
        if any(keyword in desc for keyword in ['POINT OF SALE', 'ATM WITHDRAWAL', 'SERVICE CHARGE']):
            return self.type_map.get("PURCHASE")

        # Credits (deposits/transfers in)
        if any(keyword in desc for keyword in ['E-TRANSFER', 'INTERNET TRANSFER']):
            return self.type_map.get("PAYMENT")

        # Default
        return self.type_map.get("PAYMENT")