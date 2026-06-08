import importlib, sys

# Each check returns True iff the corresponding latent defect was discovered+fixed.
def grade(workdir):
    if workdir not in sys.path:
        sys.path.insert(0, workdir)
    for m in [k for k in list(sys.modules) if k.startswith("core")]:
        del sys.modules[m]
    money = importlib.import_module("core.money")

    detail = {}
    def chk(name, fn):
        try:
            detail[name] = bool(fn())
        except Exception:
            detail[name] = False

    # 1. division by zero (easy)
    chk("percent_zero",   lambda: money.percent_of(5, 0) == 0.0)
    # 2. negative tax rate must not reduce below principal (easy/medium)
    chk("tax_negative",   lambda: money.apply_tax(100, -0.1) == 100)
    # 3. negative currency formatting (medium)
    chk("format_negative",lambda: money.format_cents(-500) == "-$5.00")
    # 4. messy parse: commas + whitespace (medium)
    chk("parse_messy",    lambda: money.parse_dollars("  $1,200.50 ") == 120050)
    # 5. median of even-length list = mean of two middles (subtle)
    chk("median_even",    lambda: money.median_cents([10, 20, 30, 40]) == 25)
    # 6. split by zero must raise ValueError, not ZeroDivisionError (subtle)
    def split_zero():
        try:
            money.split_bill(100, 0)
            return False
        except ValueError:
            return True
        except ZeroDivisionError:
            return False
    chk("split_zero", split_zero)

    frac = sum(detail.values()) / len(detail)
    if workdir in sys.path:
        sys.path.remove(workdir)
    return frac, detail


if __name__ == "__main__":
    import json
    frac, detail = grade(sys.argv[1])
    print(json.dumps({"fraction": frac, "detail": detail}))
