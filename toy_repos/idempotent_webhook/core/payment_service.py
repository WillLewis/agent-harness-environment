class PaymentService:
    def __init__(self, ledger, storage):
        self.ledger = ledger
        self.storage = storage

    async def handle_webhook(self, event):
        # BUG: not idempotent — creates a ledger entry on every delivery.
        entry = await self.ledger.create_entry(event)
        return {"status": "ok", "entry_id": entry.id, "payload_hash": event.payload_hash}
