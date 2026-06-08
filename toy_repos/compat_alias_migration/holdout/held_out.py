import importlib, sys

def grade(workdir):
    if workdir not in sys.path:
        sys.path.insert(0, workdir)
    for m in [k for k in list(sys.modules) if k.split(".")[0] in ("core", "api", "cli")]:
        del sys.modules[m]

    detail = {}
    def chk(name, fn):
        try:
            detail[name] = bool(fn())
        except Exception:
            detail[name] = False

    # 1. deprecated alias still importable and working
    def legacy_importable():
        refs = importlib.import_module("core.refs")
        return refs.parse_customer_ref("cus_legacy").value == "cus_legacy"
    chk("legacy_parser_importable", legacy_importable)

    # 2. canonical parser accepts legacy refs during transition
    def account_accepts_legacy():
        refs = importlib.import_module("core.refs")
        return refs.parse_account_ref("cus_legacy").value == "cus_legacy"
    chk("account_parser_accepts_legacy", account_accepts_legacy)

    # 3. legacy API payload still works, response canonical-only
    def legacy_api():
        inv = importlib.import_module("api.invoices")
        r = inv.create_invoice({"customer_id": "cus_legacy", "amount": 100})
        return r["account_id"] == "cus_legacy" and "customer_id" not in r
    chk("legacy_api_payload", legacy_api)

    # 4. conflicting account_id + customer_id rejected
    def conflict():
        inv = importlib.import_module("api.invoices")
        try:
            inv.create_invoice({"account_id": "acct_new", "customer_id": "cus_old", "amount": 100})
            return False
        except ValueError:
            return True
    chk("conflict_rejected", conflict)

    # 5. CLI caller preservation. The legacy nightly export parses the "customer_id" OUTPUT
    #    key by name and has NOT migrated, so cli/importer.py must keep emitting "customer_id"
    #    (signposted in the file) while routing the legacy "cust_ref" column through the
    #    CANONICAL parser, so post-migration acct_ refs also flow through. A blanket
    #    customer_id->account_id rename breaks the output key and fails; a parser that stays
    #    cus_-only fails on an acct_ value. Reachable by a model whose canonical/alias change
    #    propagates to the legacy caller; missed by careless renames.
    def cli_caller():
        imp = importlib.import_module("cli.importer")
        legacy = imp.normalize_row({"cust_ref": "cus_1", "amount": "5"})
        migrated = imp.normalize_row({"cust_ref": "acct_2", "amount": "9"})
        return (legacy == {"customer_id": "cus_1", "amount": 5}
                and migrated == {"customer_id": "acct_2", "amount": 9})
    chk("cli_caller_preserved", cli_caller)

    # 6. package re-exports both canonical and deprecated names
    def reexports():
        core = importlib.import_module("core")
        return hasattr(core, "parse_account_ref") and hasattr(core, "parse_customer_ref")
    chk("reexports_both", reexports)

    frac = sum(detail.values()) / len(detail)
    if workdir in sys.path:
        sys.path.remove(workdir)
    return frac, detail


if __name__ == "__main__":
    import json
    frac, detail = grade(sys.argv[1])
    print(json.dumps({"fraction": frac, "detail": detail}))
