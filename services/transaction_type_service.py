def load_transaction_types(connection):
    cursor = connection.cursor()

    cursor.execute("SELECT id, code FROM transaction_types")

    result = {}
    for (id, code) in cursor.fetchall():
        result[code] = id

    cursor.close()
    return result