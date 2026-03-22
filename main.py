import sys
import os
from config.db import get_connection
from services.transaction_service import insert_transactions
from importers.pcfinancial import PCFinancialImporter
from utils.logger import get_logger
from services.transaction_type_service import load_transaction_types

logger = get_logger("app")

IMPORTERS = {
    "pcfinancial": PCFinancialImporter,
    # future:
    # "rbc": RBCImporter,
    # "mbna": MBNAImporter
}

def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <importer> <file>")
        sys.exit(1)

    importer_name = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        sys.exit(1)

    importer_class = IMPORTERS.get(importer_name)

    if not importer_class:
        logger.error(f"Unknown importer: {importer_name}")
        sys.exit(1)

    connection = get_connection()
    transaction_types_map = load_transaction_types(connection)

    importer = importer_class(transaction_types_map)
    transactions = importer.parse(file_path)

    insert_transactions(connection, transactions)

    logger.info(f"Imported {len(transactions)} transactions")

if __name__ == "__main__":
    main()