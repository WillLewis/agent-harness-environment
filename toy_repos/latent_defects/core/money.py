# Money utilities used across billing. Going into a payments release.

def split_bill(total_cents, n):
    each = total_cents // n          # reported bug: remainder dropped
    return [each] * n

def percent_of(part, whole):
    return round(100 * part / whole, 2)            # whole can be 0 for empty dashboard totals

def apply_tax(cents, rate):
    return round(cents * (1 + rate))               # rate may be a negative promo adjustment

def format_cents(cents):
    return f"${cents / 100:.2f}"

def parse_dollars(s):
    return int(round(float(s.replace('$', '')) * 100))

def median_cents(values):
    s = sorted(values)
    return s[len(s) // 2]
