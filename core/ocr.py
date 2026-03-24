import pytesseract
from PIL import Image
import re

AMOUNT_REGEX = re.compile(r'[-+]?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})')

NOISE_KEYWORDS = [
    "total", "subtotal", "tax", "gst", "pst",
    "points", "redeem", "balance", "visit",
    "survey", "call", "www", "up to"
]

def is_valid_description(desc: str) -> bool:
    # Must be at least 5 chars
    if len(desc) < 5:
        return False

    # Reject weird OCR garbage (symbols)
    if re.search(r'[^\w\s]', desc):  # only letters/numbers/spaces allowed
        return False

    # Must contain at least one letter
    if not re.search(r'[A-Za-z]', desc):
        return False

    # Reject if too many numbers (likely not a product)
    if len(re.findall(r'\d', desc)) > 3:
        return False

    return True


def extract_transactions_from_receipt(image_path: str):
    img = Image.open(image_path)
    img = img.convert("L")

    text = pytesseract.image_to_string(img)

    print(text)

    lines = text.splitlines()

    transactions = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Skip known noise
        if any(keyword in line.lower() for keyword in NOISE_KEYWORDS):
            continue

        matches = AMOUNT_REGEX.findall(line)
        if not matches:
            continue

        amount_str = matches[-1].replace(",", ".")
        try:
            amount = float(amount_str)
        except ValueError:
            continue

        last_match = list(AMOUNT_REGEX.finditer(line))[-1]
        description = line[:last_match.start()].strip()

        # Clean trailing numbers
        description = re.sub(r'\s*\d+[.,]?\d*\s*$', '', description).strip()

        # 🚨 Strong validation here
        if not is_valid_description(description):
            continue

        transactions.append({
            "description": description,
            "amount": amount,
            "product_code": ""
        })

    return transactions