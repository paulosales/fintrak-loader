from core.fingerprint import generate
from config.db import get_connection
from typing import Optional, Dict, Any, cast

def insert_transactions(transactions):
    connection = get_connection()
    cursor = connection.cursor()

    values = []
    for t in transactions:
        fingerprint = generate(t)

        values.append((
            t["accountId"],
            t["type"],
            t["datetime"],
            t["amount"],
            t["description"],
            None,
            fingerprint
        ))

    placeholders = ', '.join(['(%s,%s,%s,%s,%s,%s,%s)'] * len(values))
    flattened = [item for sublist in values for item in sublist]

    query = f"""
    INSERT IGNORE INTO transactions
    (account_id, transaction_type_id, datetime, amount, description, note, fingerprint)
    VALUES {placeholders}
    """


    cursor.execute(query, flattened)
    connection.commit()

def get_transaction_by_id(transaction_id: int) -> Optional[Dict[str, Any]]:
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT id, account_id, transaction_type_id, datetime, amount, description, note, fingerprint
    FROM transactions
    WHERE id = %s
    """

    cursor.execute(query, (transaction_id,))
    result = cursor.fetchone()
    cursor.close()

    return cast(Optional[Dict[str, Any]], result)