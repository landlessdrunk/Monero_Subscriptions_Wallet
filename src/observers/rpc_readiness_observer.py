from src.interfaces.observer import Observer
from src.clients.rpc import RPCClient

class RPCReadinessObserver(Observer):
    def __init__(self, frame):
        self.frame = frame

    def update(self, subject):
        if subject.started:
            self.frame.transactions = RPCClient.get().get_transfers()
            self.frame.render_txs()
