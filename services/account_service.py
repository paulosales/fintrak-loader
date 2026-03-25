from config.db import get_connection
from typing import Dict, Any, cast

_account_cache = {}

def get_account_id_cached(code: str):

    connection = get_connection()
    
    if code in _account_cache:
        return _account_cache[code]

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id FROM accounts WHERE code = %s", (code,))
    result = cast(Dict[str, Any], cursor.fetchone())
    cursor.close()

    if not result:
        raise ValueError(f"Account not found: {code}")
    
    account_id = result["id"] 

    _account_cache[code] = account_id
    return account_id
