import asyncio
from core.types import WebhookEvent
from core.ledger import Ledger
from core.storage import Storage
from core.payment_service import PaymentService

def _svc():
    return PaymentService(Ledger(), Storage())

def _ev(eid="e1", inv="inv1", amt=100, ph="h1"):
    return WebhookEvent(eid, inv, amt, ph)

def test_first_creates_one():
    svc = _svc()
    asyncio.run(svc.handle_webhook(_ev()))
    assert len(svc.ledger.entries) == 1

def test_sequential_duplicate_no_second_entry():
    svc = _svc()
    async def run():
        await svc.handle_webhook(_ev())
        await svc.handle_webhook(_ev())   # same event_id, delivered again
    asyncio.run(run())
    assert len(svc.ledger.entries) == 1

def test_different_ids_create_separate_entries():
    svc = _svc()
    async def run():
        await svc.handle_webhook(_ev(eid="a"))
        await svc.handle_webhook(_ev(eid="b"))
    asyncio.run(run())
    assert len(svc.ledger.entries) == 2
