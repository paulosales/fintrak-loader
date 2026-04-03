import pytest
from unittest.mock import patch, MagicMock
from services.transaction_service import insert_transactions, get_transaction_by_id


class TestTransactionService:
    """Test cases for transaction service functions."""

    @patch('services.transaction_service.get_connection')
    def test_insert_transactions_success(self, mock_get_connection, mock_db_connection):
        """Test successful insertion of transactions."""
        mock_conn, mock_cursor = mock_db_connection
        mock_get_connection.return_value = mock_conn

        transactions = [
            {
                'accountId': 1,
                'type': 1,
                'datetime': '2023-01-01 10:00:00',
                'amount': 100.50,
                'description': 'Test transaction 1'
            },
            {
                'accountId': 1,
                'type': 1,
                'datetime': '2023-01-02 11:00:00',
                'amount': 200.75,
                'description': 'Test transaction 2'
            }
        ]

        insert_transactions(transactions)

        # Verify cursor.execute was called
        assert mock_cursor.execute.call_count == 1
        # Verify commit was called
        mock_conn.commit.assert_called_once()

        # Check the SQL query structure
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        assert 'INSERT IGNORE INTO transactions' in query
        assert 'VALUES' in query

    @patch('services.transaction_service.get_connection')
    def test_insert_transactions_empty_list(self, mock_get_connection, mock_db_connection):
        """Test insertion with empty transaction list."""
        mock_conn, mock_cursor = mock_db_connection
        mock_get_connection.return_value = mock_conn

        insert_transactions([])

        # With empty list, no database operations should occur
        mock_cursor.execute.assert_not_called()
        mock_conn.commit.assert_not_called()

    @patch('services.transaction_service.get_connection')
    def test_get_transaction_by_id_found(self, mock_get_connection, mock_db_connection, sample_transaction):
        """Test successful retrieval of transaction by ID."""
        mock_conn, mock_cursor = mock_db_connection
        mock_get_connection.return_value = mock_conn
        mock_cursor.fetchone.return_value = sample_transaction

        result = get_transaction_by_id(1)

        assert result == sample_transaction
        mock_cursor.execute.assert_called_once()

        # Check the query
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert 'SELECT' in query
        assert 'FROM transactions' in query
        assert 'WHERE id = %s' in query
        assert params == (1,)

    @patch('services.transaction_service.get_connection')
    def test_get_transaction_by_id_not_found(self, mock_get_connection, mock_db_connection):
        """Test retrieval when transaction is not found."""
        mock_conn, mock_cursor = mock_db_connection
        mock_get_connection.return_value = mock_conn
        mock_cursor.fetchone.return_value = None

        result = get_transaction_by_id(999)

        assert result is None
        mock_cursor.execute.assert_called_once()

    @patch('services.transaction_service.get_connection')
    def test_get_transaction_by_id_database_error(self, mock_get_connection, mock_db_connection):
        """Test handling of database errors."""
        mock_conn, mock_cursor = mock_db_connection
        mock_get_connection.return_value = mock_conn
        mock_cursor.fetchone.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            get_transaction_by_id(1)

    @patch('services.transaction_service.get_connection')
    def test_insert_transactions_database_error(self, mock_get_connection, mock_db_connection):
        """Test handling of database errors during insertion."""
        mock_conn, mock_cursor = mock_db_connection
        mock_get_connection.return_value = mock_conn
        mock_cursor.execute.side_effect = Exception("Database error")

        transactions = [{
            'accountId': 1,
            'type': 1,
            'datetime': '2023-01-01 10:00:00',
            'amount': 100.50,
            'description': 'Test transaction'
        }]

        with pytest.raises(Exception, match="Database error"):
            insert_transactions(transactions)

        # Commit should not be called on error
        mock_conn.commit.assert_not_called()