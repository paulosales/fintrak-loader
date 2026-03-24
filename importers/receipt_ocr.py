

from core.ocr import extract_transactions_from_receipt
from core.importer import Importer

class ReceiptOCRImporter(Importer):

    def parse(self, file_path: str):
        return extract_transactions_from_receipt(file_path)
