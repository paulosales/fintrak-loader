import pandas as pd
from core.importer import Importer as BaseImporter
from utils.date_utils import parse_datetime

TYPE_MAP = {
    "PURCHASE": 1,
    "PAYMENT": 2,
    "REFUND": 3,
    "INTEREST": 4
}

class PCFinancialImporter(BaseImporter):

    def parse(self, file_path: str) -> list:
        df = pd.read_csv(file_path)

        transactions = []

        for _, row in df.iterrows():
            transactions.append({
                "datetime": parse_datetime(row["Date"], row["Time"]),
                "amount": float(row["Amount"]),
                "description": row["Description"],
                "type": TYPE_MAP.get(row["Type"], 1)
            })

        return transactions