from src.interfaces.observer import Observer

class HistoryTxObserver(Observer):
    def __init__(self, frame):
        self.frame = frame

    def update(self, subject):
        subject.update_txs()