from dataclasses import dataclass

@dataclass(frozen=True)
class WebhookEvent:
    event_id: str
    invoice_id: str
    amount: int
    payload_hash: str

class ConflictError(Exception):
    pass
