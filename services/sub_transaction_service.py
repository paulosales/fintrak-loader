from config.db import get_connection

def insert_sub_transactions(transaction_id, sub_transactions):
    connection = get_connection()
    cursor = connection.cursor()

    values = []

    for t in sub_transactions:
        values.append((
            transaction_id,
            '',
            t["amount"],
            t["description"],
            None
        ))

    if not values:
        return

    placeholders = ', '.join(['(%s,%s,%s,%s,%s)'] * len(values))
    flattened = [item for sublist in values for item in sublist]

    query = f"""
    INSERT INTO sub_transactions
    (transaction_id, product_code, amount, description, note)
    VALUES {placeholders}
    """

    cursor.execute(query, flattened)
    connection.commit()

    cursor.close()