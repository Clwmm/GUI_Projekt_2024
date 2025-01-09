def individual_serial(item) -> dict:
    return {
        "user_id": item["user_id"],
        "currency": item["currency"],
        "amount": item["amount"],
        "transaction_type": item["transaction_type"],
        "timestamp": item["timestamp"],
    }

def list_serial(items) -> list:
    return[individual_serial(item) for item in items]