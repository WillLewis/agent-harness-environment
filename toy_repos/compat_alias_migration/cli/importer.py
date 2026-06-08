from core.refs import parse_customer_ref

# NOTE: the nightly export consumer parses the "customer_id" output key BY NAME and has not
# migrated yet, so this importer must keep emitting "customer_id" for one release. The legacy
# CSV column is "cust_ref".
def normalize_row(row):
    return {"customer_id": parse_customer_ref(row["cust_ref"]).value,
            "amount": int(row["amount"])}
