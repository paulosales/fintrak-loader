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

## Testing

### Prerequisites
Make sure you have the testing dependencies installed:
```bash
pip install -r requirements.txt
```

### Running Unit Tests
The project includes a comprehensive unit test suite to ensure code quality and functionality.

#### Run All Tests
To run the complete test suite:
```bash
python -m pytest tests/ -v --tb=short
```

#### Run Specific Test Files
To run tests for a specific module:
```bash
# Test fingerprint functionality
python -m pytest tests/test_fingerprint.py -v

# Test transaction service
python -m pytest tests/test_transaction_service.py -v

# Test CLI functionality
python -m pytest tests/test_main.py -v

# Test logger utilities
python -m pytest tests/test_logger.py -v

# Test PC Financial importer
python -m pytest tests/test_pcfinancial_importer.py -v
```

### Test Coverage
The test suite covers:
- **Fingerprint generation** - Transaction fingerprint calculation logic
- **Database operations** - Transaction service CRUD operations with error handling
- **CLI functionality** - Command-line argument parsing and execution
- **Logging utilities** - Logger configuration and usage
- **Data importers** - PC Financial transaction file parsing

All tests use mocked dependencies to avoid requiring actual database connections or external libraries during testing.