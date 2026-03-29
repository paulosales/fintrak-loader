# Tests

This directory contains unit tests for the Fintrack Data Loader application.

## Running Tests

Install test dependencies:
```bash
pip install -r requirements.txt
```

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=. --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_fingerprint.py
```

Run tests in verbose mode:
```bash
pytest -v
```

## Test Structure

- `conftest.py` - Shared fixtures and configuration
- `test_fingerprint.py` - Tests for fingerprint generation
- `test_transaction_service.py` - Tests for database operations
- `test_main.py` - Tests for CLI functionality
- `test_pcfinancial_importer.py` - Tests for PCFinancial importer
- `test_logger.py` - Tests for logging utility

## Test Coverage

The tests cover:
- Core business logic (fingerprint generation)
- Database operations (with mocking)
- CLI argument parsing and command execution
- Data import functionality
- Utility functions

## Mocking Strategy

Database operations are mocked to avoid requiring a real database connection during testing. External dependencies like pandas and file I/O are also mocked where appropriate.