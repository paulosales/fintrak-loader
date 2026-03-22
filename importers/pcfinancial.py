import pandas as pd
from core.importer import Importer as BaseImporter
from utils.date_utils import parse_datetime

class PCFinancialImporter(BaseImporter):

    def __init__(self, transaction_type_map):
        self.transaction_type_map = transaction_type_map

    def parse(self, file_path: str) -> list:
        df = pd.read_csv(file_path)

        transactions = []

        for _, row in df.iterrows():
            transaction_type_code = row["Type"].strip().upper()
            transactions.append({
                "datetime": parse_datetime(row["Date"], row["Time"]),
                "amount": float(row["Amount"]),
                "description": row["Description"],
                "type": self.transaction_type_map.get(transaction_type_code, self.transaction_type_map.get("PURCHASE"))
            })

        return transactions