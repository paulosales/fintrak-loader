def get_account_id_by_code(connection, code: str) -> int:
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM accounts WHERE code = %s",
        (code,)
    )

    result = cursor.fetchone()
    cursor.close()

    if not result:
        raise ValueError(f"Account not found for code: {code}")

    return result[0]