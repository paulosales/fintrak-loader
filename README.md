# Fintrack Data Loader

## Usage

### Import Transactions
Importing PC Financial transaction files:
```bash
python main.py pcfinancial report.csv
```

Importing MBNA transaction files:
```bash
python main.py mbna report.csv
```

Importing RBC transaction files:
```bash
python main.py rbc report.csv
```

### Import Receipts
Import receipt images with OCR:
```bash
python main.py receipt image.jpg <transaction_id>
```

### Calculate Transaction Fingerprint
Calculate and display the fingerprint for a transaction (without persisting to database):
```bash
python main.py fingerprint <transaction_id>
```

Example:
```bash
python main.py fingerprint 123
# Output: d5a44a049ac7a65abf8e0b8c7be96d30
```