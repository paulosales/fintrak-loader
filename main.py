import sys
import os
from services.transaction_service import insert_transactions, get_transaction_by_id
from importers.pcfinancial import PCFinancialImporter
from importers.mbna import MBNACardImporter
from importers.rbc import RBCImporter
from importers.receipt_ocr import ReceiptOCRImporter
from importers.bb import BBImporter
from importers.nu import NUImporter
from importers.cibic_checking import CIBICCheckingImporter
from importers.cibic_savings import CIBICSavingsImporter
from utils.logger import get_logger
from services.transaction_type_service import load_transaction_types
from core.fingerprint import generate
from typing import Dict, Any

logger = get_logger("app")
from importers.receipt_ocr import ReceiptOCRImporter
from services.sub_transaction_service import insert_sub_transactions

IMPORTERS = {
    "pcfinancial": PCFinancialImporter,
    "mbna": MBNACardImporter,
    "receipt": ReceiptOCRImporter,
    "rbc": RBCImporter,
    "bb": BBImporter,
    "nu": NUImporter,
    "cibic-checking": CIBICCheckingImporter,
    "cibic-savings": CIBICSavingsImporter
}

def main():
    if len(sys.argv) < 2:
        logger.info("Usage:")
        logger.info("Import transactions: python main.py <importer> <file>")
        logger.info("Import receipts: python main.py receipt <image> <transaction_id>")
        logger.info("Calculate fingerprint: python main.py fingerprint <transaction_id>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "fingerprint":
        if len(sys.argv) < 3:
            logger.error("transaction_id is required for fingerprint calculation")
            sys.exit(1)

        try:
            transaction_id = int(sys.argv[2])
        except ValueError:
            logger.error("transaction_id must be a valid integer")
            sys.exit(1)

        transaction = get_transaction_by_id(transaction_id)
        if not transaction:
            logger.error(f"Transaction with id {transaction_id} not found")
            sys.exit(1)

        # Type assertion for Pylance
        transaction_dict: Dict[str, Any] = transaction

        # Calculate fingerprint
        fingerprint_data = {
            'datetime': str(transaction_dict['datetime']),
            'amount': str(transaction_dict['amount']),
            'description': transaction_dict['description']
        }
        fingerprint = generate(fingerprint_data)

        print(fingerprint)
        return

    # Handle import commands
    if len(sys.argv) < 3:
        logger.info("Usage:")
        logger.info("Transactions: python main.py pcfinancial|mbna|rbc|bb|nu|cibic-checking|cibic-savings <file>")
        logger.info("Receipts: python main.py receipt <image> <transaction_id>")
        sys.exit(1)

    importer_name = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        sys.exit(1)

    if importer_name == "receipt":
        if len(sys.argv) < 4:
            logger.error("transaction_id is required for receipt import")
            sys.exit(1)

        transaction_id = int(sys.argv[3])

        # importer = ReceiptOCRImporter()
        # sub_transactions = importer.parse(file_path)
        # print(sub_transactions)

        sub_transactions = []
 
        insert_sub_transactions(transaction_id, sub_transactions)
        logger.info(f"Inserted {len(sub_transactions)} sub-transactions")

    else:
        importer_class = IMPORTERS.get(importer_name)

        if not importer_class:
            logger.error(f"Unknown importer: {importer_name}")
            sys.exit(1)

        type_map = load_transaction_types()

        importer = importer_class(type_map)
        transactions = importer.parse(file_path)

        if transactions:
            insert_transactions(transactions)
            logger.info(f"Imported {len(transactions)} transactions")
        else:
            logger.info("No transactions found to import")

if __name__ == "__main__":
    main()