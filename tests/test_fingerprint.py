import pytest
from core.fingerprint import generate


class TestFingerprint:
    """Test cases for fingerprint generation."""

    def test_generate_fingerprint_basic(self, sample_transaction_for_fingerprint):
        """Test basic fingerprint generation."""
        fingerprint = generate(sample_transaction_for_fingerprint)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 32  # MD5 hash length
        assert fingerprint == 'd5a44a049ac7a65abf8e0b8c7be96d30'

    def test_generate_fingerprint_different_data(self):
        """Test that different data produces different fingerprints."""
        transaction1 = {
            'datetime': '2023-01-01 10:00:00',
            'amount': '100.00',
            'description': 'Transaction 1'
        }
        transaction2 = {
            'datetime': '2023-01-01 10:00:00',
            'amount': '100.00',
            'description': 'Transaction 2'
        }

        fingerprint1 = generate(transaction1)
        fingerprint2 = generate(transaction2)

        assert fingerprint1 != fingerprint2
        assert isinstance(fingerprint1, str)
        assert isinstance(fingerprint2, str)

    def test_generate_fingerprint_same_data_same_result(self):
        """Test that same data produces same fingerprint."""
        transaction = {
            'datetime': '2023-01-01 10:00:00',
            'amount': '100.00',
            'description': 'Same transaction'
        }

        fingerprint1 = generate(transaction)
        fingerprint2 = generate(transaction)

        assert fingerprint1 == fingerprint2

    def test_generate_fingerprint_numeric_amount(self):
        """Test fingerprint generation with numeric amount."""
        transaction = {
            'datetime': '2023-01-01 10:00:00',
            'amount': 100.50,  # numeric instead of string
            'description': 'Test transaction'
        }

        fingerprint = generate(transaction)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 32

    def test_generate_fingerprint_empty_description(self):
        """Test fingerprint generation with empty description."""
        transaction = {
            'datetime': '2023-01-01 10:00:00',
            'amount': '100.00',
            'description': ''
        }

        fingerprint = generate(transaction)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 32

    def test_generate_fingerprint_special_characters(self):
        """Test fingerprint generation with special characters."""
        transaction = {
            'datetime': '2023-01-01 10:00:00',
            'amount': '100.00',
            'description': 'Special chars: @#$%^&*()'
        }

        fingerprint = generate(transaction)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 32

    def test_generate_fingerprint_missing_keys(self):
        """Test that missing keys raise appropriate errors."""
        incomplete_transaction = {
            'datetime': '2023-01-01 10:00:00',
            'amount': '100.00'
            # missing description
        }

        with pytest.raises(KeyError):
            generate(incomplete_transaction)