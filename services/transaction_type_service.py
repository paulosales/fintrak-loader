from config.db import get_connection

def load_transaction_types():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, code FROM transaction_types")

    result = {}
    for (id, code) in cursor.fetchall():
        result[code] = id

    cursor.close()
    return result