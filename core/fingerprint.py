import hashlib

def generate(transaction):
    raw = f"{transaction['datetime']}|{transaction['amount']}|{transaction['description']}"
    return hashlib.md5(raw.encode()).hexdigest()
