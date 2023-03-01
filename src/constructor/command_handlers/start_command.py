
def handler(data):
    first_name = data["message"]["chat"]["first_name"]
    return f"Hello {first_name}"
