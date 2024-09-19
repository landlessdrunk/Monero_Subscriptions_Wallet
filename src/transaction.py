from dataclasses import dataclass, field
import time
from src.clients.rpc import RPCClient

@dataclass
class Transaction:
    address: str
    amount: int
    confirmations: int
    double_spend_seen: bool
    fee: int
    height: int
    locked: bool
    note: str
    payment_id: int
    timestamp: int
    txid: str
    type: str
    unlock_time: int
    direction: str
    subaddr_index: dict[str, int]
    subaddr_indices: list[dict[str, int]] = field(default_factory=list)
    suggested_confirmations_threshold: int = 0
    amounts: list[int] = field(default_factory=list)
    destinations: list[dict[str, str]] = field(default_factory=list)

    def time(self):
        return time.ctime(self.timestamp)

    def notes(self):
        return ' '.join(RPCClient().get().get_tx_notes([self.txid]))

    def amt(self):
        amt = 0
        if self.direction == 'in':
            amt = self.amount
        else:
            if self.destinations:
                amt = self.destinations[0]['amount']
        return amt