from core.refs import parse_account_ref
from api.invoices import create_invoice

def test_new_parser_accepts_account_ref():
    assert parse_account_ref("acct_123").value == "acct_123"

def test_create_invoice_accepts_account_id():
    res = create_invoice({"account_id": "acct_123", "amount": 100})
    assert res["account_id"] == "acct_123"
    assert "customer_id" not in res
