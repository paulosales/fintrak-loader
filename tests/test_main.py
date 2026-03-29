import pytest
import sys
from unittest.mock import patch, MagicMock

mock_receipt_ocr = MagicMock()
sys.modules['importers.receipt_ocr'] = mock_receipt_ocr

from main import main


class TestMainCLI:
    """Test cases for the main CLI functionality."""

    @patch('main.logger')
    def test_main_no_args_shows_help(self, mock_logger, capsys):
        """Test that running main with no args shows help."""
        with patch('sys.argv', ['main.py']):
            with pytest.raises(SystemExit) as excinfo:
                main()

            assert excinfo.value.code == 1

            # Check that logger.info was called with usage information
            mock_logger.info.assert_called()
            calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("Usage:" in call for call in calls)
            assert any("fingerprint" in call for call in calls)
            assert any("receipt" in call for call in calls)
            assert any("<importer>" in call for call in calls)

    @patch('main.logger')
    def test_main_fingerprint_command_missing_id(self, mock_logger, capsys):
        """Test fingerprint command with missing transaction ID."""
        with patch('sys.argv', ['main.py', 'fingerprint']):
            with pytest.raises(SystemExit) as excinfo:
                main()

            assert excinfo.value.code == 1

            mock_logger.error.assert_called_with("transaction_id is required for fingerprint calculation")

    @patch('main.logger')
    def test_main_fingerprint_command_invalid_id(self, mock_logger, capsys):
        """Test fingerprint command with invalid transaction ID."""
        with patch('sys.argv', ['main.py', 'fingerprint', 'abc']):
            with pytest.raises(SystemExit) as excinfo:
                main()

            assert excinfo.value.code == 1

            mock_logger.error.assert_called_with("transaction_id must be a valid integer")

    @patch('main.get_transaction_by_id')
    @patch('main.logger')
    def test_main_fingerprint_command_transaction_not_found(self, mock_logger, mock_get_transaction, capsys):
        """Test fingerprint command when transaction is not found."""
        mock_get_transaction.return_value = None

        with patch('sys.argv', ['main.py', 'fingerprint', '123']):
            with pytest.raises(SystemExit) as excinfo:
                main()

            assert excinfo.value.code == 1

            mock_logger.error.assert_called_with("Transaction with id 123 not found")

    @patch('main.get_transaction_by_id')
    @patch('main.generate')
    def test_main_fingerprint_command_success(self, mock_generate, mock_get_transaction, sample_transaction, capsys):
        """Test successful fingerprint command execution."""
        mock_get_transaction.return_value = sample_transaction
        mock_generate.return_value = 'test_fingerprint_hash'

        with patch('sys.argv', ['main.py', 'fingerprint', '1']):
            main()

        captured = capsys.readouterr()
        assert 'test_fingerprint_hash' in captured.out

        # Verify the transaction data was passed correctly to generate
        mock_generate.assert_called_once()
        call_args = mock_generate.call_args[0][0]

        assert call_args['datetime'] == str(sample_transaction['datetime'])
        assert call_args['amount'] == str(sample_transaction['amount'])
        assert call_args['description'] == sample_transaction['description']

    @patch('main.logger')
    def test_main_unknown_command(self, mock_logger, capsys):
        """Test unknown command handling."""
        with patch('sys.argv', ['main.py', 'unknown_command']):
            with pytest.raises(SystemExit) as excinfo:
                main()

            assert excinfo.value.code == 1

            # Check that logger.info was called with usage information
            mock_logger.info.assert_called()
            calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("Usage:" in call for call in calls)

    @patch('main.logger')
    def test_main_import_command_missing_file(self, mock_logger, capsys):
        """Test import command with missing file argument."""
        with patch('sys.argv', ['main.py', 'pcfinancial']):
            with pytest.raises(SystemExit) as excinfo:
                main()

            assert excinfo.value.code == 1

            # Check that logger.info was called with usage information
            mock_logger.info.assert_called()
            calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("Usage:" in call for call in calls)

    @patch('os.path.exists')
    @patch('main.logger')
    def test_main_import_command_file_not_found(self, mock_logger, mock_exists, capsys):
        """Test import command when file doesn't exist."""
        mock_exists.return_value = False

        with patch('sys.argv', ['main.py', 'pcfinancial', 'nonexistent.csv']):
            with pytest.raises(SystemExit) as excinfo:
                main()

            assert excinfo.value.code == 1

            mock_logger.error.assert_called_with("File not found: nonexistent.csv")

    @patch('os.path.exists')
    @patch('main.logger')
    def test_main_receipt_command_missing_transaction_id(self, mock_logger, mock_exists, capsys):
        """Test receipt command with missing transaction ID."""
        mock_exists.return_value = True  # Pretend the file exists

        with patch('sys.argv', ['main.py', 'receipt', 'image.jpg']):
            with pytest.raises(SystemExit) as excinfo:
                main()

            assert excinfo.value.code == 1

            mock_logger.error.assert_called_with("transaction_id is required for receipt import")