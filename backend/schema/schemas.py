def individual_serial(item) -> dict:
    return {
        "transaction_id": item["transaction_id"],
        "currency_from": item["currency_from"],
        "currency_to": item["currency_to"],
        "amount_from": item["amount_from"],
        "amount_to": item["amount_to"],
        "timestamp": item["timestamp"],
    }

def list_serial(items) -> list:
    return[individual_serial(item) for item in items]