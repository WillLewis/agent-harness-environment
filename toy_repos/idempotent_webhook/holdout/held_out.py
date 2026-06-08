import asyncio
from core.types import WebhookEvent, ConflictError
from core.ledger import Ledger
from core.storage import Storage
from core.payment_service import PaymentService

def _ev(eid="e1", inv="inv1", amt=100, ph="h1"):
    return WebhookEvent(eid, inv, amt, ph)

# 1. CONCURRENT duplicates -> exactly one entry (check-then-act fails here).
def test_concurrent_same_event_one_entry():
    svc = PaymentService(Ledger(), Storage())
    async def run():
        return await asyncio.gather(svc.handle_webhook(_ev()),
                                    svc.handle_webhook(_ev()))
    r1, r2 = asyncio.run(run())
    assert len(svc.ledger.entries) == 1
    assert r1["entry_id"] == r2["entry_id"]   # both return the original result

# 2. Partial failure then retry completes exactly once.
def test_retry_after_partial_failure():
    class FlakyLedger(Ledger):
        def __init__(self):
            super().__init__(); self.calls = 0
        async def create_entry(self, event):
            self.calls += 1
            await asyncio.sleep(0)
            if self.calls == 1:
                raise RuntimeError("transient")
            return await super().create_entry(event)
    svc = PaymentService(FlakyLedger(), Storage())
    async def run():
        try:
            await svc.handle_webhook(_ev())
        except RuntimeError:
            pass
        return await svc.handle_webhook(_ev())   # retry
    res = asyncio.run(run())
    assert len(svc.ledger.entries) == 1
    assert res["status"] == "ok"

# 3. Same event_id, conflicting payload -> rejected, not silently accepted.
def test_conflicting_payload_rejected():
    svc = PaymentService(Ledger(), Storage())
    async def run():
        await svc.handle_webhook(_ev(ph="h1"))
        await svc.handle_webhook(_ev(ph="DIFFERENT"))
    try:
        asyncio.run(run())
        assert False, "expected ConflictError"
    except ConflictError:
        pass

# 4. Different invoices are independent (both succeed concurrently).
def test_different_invoices_independent():
    svc = PaymentService(Ledger(), Storage())
    async def run():
        return await asyncio.gather(
            svc.handle_webhook(_ev(eid="a", inv="inv1")),
            svc.handle_webhook(_ev(eid="b", inv="inv2")))
    asyncio.run(run())
    assert len(svc.ledger.entries) == 2
