import sys
import os
from config.db import get_connection
from services.transaction_service import insert_transactions
from importers.pcfinancial import PCFinancialImporter
from importers.mbna import MBNACardImporter
from importers.receipt_ocr import ReceiptOCRImporter
from utils.logger import get_logger
from services.transaction_type_service import load_transaction_types
from services.account_service import get_account_id_by_code

logger = get_logger("app")
from importers.receipt_ocr import ReceiptOCRImporter
from services.sub_transaction_service import insert_sub_transactions

IMPORTERS = {
    "pcfinancial": PCFinancialImporter,
    "mbna": MBNACardImporter,
    "receipt": ReceiptOCRImporter
}

ACCOUNT_CODES = {
    "pcfinancial": "PCFINANCIAL",
    "mbna": "MBNA"
}

def main():
    if len(sys.argv) < 3:
        logger.info("Usage:")
        logger.info("Transactions: python main.py pcfinancial <file>")
        logger.info("Receipts: python main.py receipt <image> <transaction_id>")
        sys.exit(1)

    importer_name = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        sys.exit(1)

    connection = get_connection()

    if importer_name == "receipt":
        if len(sys.argv) < 4:
            logger.error("transaction_id is required for receipt import")
            sys.exit(1)

        transaction_id = int(sys.argv[3])

        importer = ReceiptOCRImporter()
        sub_transactions = importer.parse(file_path)

        print(sub_transactions)

        # insert_sub_transactions(connection, transaction_id, sub_transactions)

        # logger.info(f"Inserted {len(sub_transactions)} sub-transactions")

    else:
        importer_class = IMPORTERS.get(importer_name)

        if not importer_class:
            logger.error(f"Unknown importer: {importer_name}")
            sys.exit(1)

        type_map = load_transaction_types(connection)

        importer = importer_class(type_map)
        transactions = importer.parse(file_path)

        account_id = get_account_id_by_code(connection, ACCOUNT_CODES.get(importer_name, ""))

        insert_transactions(connection, transactions, account_id)

        logger.info(f"Imported {len(transactions)} transactions")

if __name__ == "__main__":
    main()