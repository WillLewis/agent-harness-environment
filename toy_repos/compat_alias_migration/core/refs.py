import re
from dataclasses import dataclass

_CUSTOMER_RE = re.compile(r"^cus_[a-zA-Z0-9]+$")

@dataclass(frozen=True)
class CustomerRef:
    value: str

def parse_customer_ref(ref):
    if not _CUSTOMER_RE.match(ref):
        raise ValueError(f"invalid customer ref: {ref}")
    return CustomerRef(value=ref)
