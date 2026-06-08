from core.types import ConflictError

# In-memory abstraction. try_reserve/release are SYNCHRONOUS (no await), so they
# are atomic under asyncio and can be used to claim an event_id BEFORE the first
# await. A correct solution uses them; a check-then-act solution that only uses
# get_result/save_result will race under asyncio.gather.
class Storage:
    def __init__(self):
        self._results = {}
        self._reservations = {}

    def get_result(self, event_id):
        return self._results.get(event_id)

    def save_result(self, event_id, result):
        self._results[event_id] = result

    def try_reserve(self, event_id, payload_hash):
        if event_id in self._reservations:
            if self._reservations[event_id] != payload_hash:
                raise ConflictError(event_id)
            return False
        self._reservations[event_id] = payload_hash
        return True

    def release(self, event_id):
        self._reservations.pop(event_id, None)
