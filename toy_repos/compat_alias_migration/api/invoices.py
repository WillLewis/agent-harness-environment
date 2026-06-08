from core.refs import parse_customer_ref

def create_invoice(payload):
    customer = parse_customer_ref(payload["customer_id"])
    return {"invoice_id": "inv_1", "customer_id": customer.value}
