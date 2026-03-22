from core.fingerprint import generate

def insert_transactions(connection, transactions):
    cursor = connection.cursor()

    values = []
    for t in transactions:
        fingerprint = generate(t)

        values.append((
            1,
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