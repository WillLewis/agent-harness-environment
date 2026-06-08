import asyncio
from dataclasses import dataclass

@dataclass
class Entry:
    id: int
    invoice_id: str
    amount: int

class Ledger:
    def __init__(self):
        self.entries = []

    async def create_entry(self, event):
        # Real handlers await I/O here; the yield exposes check-then-act races.
        await asyncio.sleep(0)
        entry = Entry(id=len(self.entries) + 1,
                      invoice_id=event.invoice_id, amount=event.amount)
        self.entries.append(entry)
        return entry
