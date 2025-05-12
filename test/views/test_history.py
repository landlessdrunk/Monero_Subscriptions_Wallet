import unittest
import time
from dataclasses import asdict
from gui import App
from test.utils.rpc_server_helper import RPCServerContextManager
from src.clients.rpc import RPCClient
from test.factories.transaction import TransactionFactory

def mocked_transfers():
    transactions = {}
    for transaction in TransactionFactory.create_batch(5):
        trans_dict = asdict(transaction)
        del(trans_dict['direction'])
        if not transactions.get(transaction.direction):
            transactions[transaction.direction] = [trans_dict]
        else:
            transactions[transaction.direction].append(trans_dict)
    return transactions

class HistoryViewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.default_transfers = mocked_transfers()
        cls.context = RPCServerContextManager()
        cls.context.server_setup()
        with unittest.mock.patch('src.views.history.RPCClient.get_transfers', return_value=cls.default_transfers):
            with unittest.mock.patch('src.views.history.Wallet', return_value=cls.context.server_wallet()):
                with unittest.mock.patch('gui.rpc', return_value='False'):
                    with unittest.mock.patch('gui.cfg.subscriptions', return_value='[]'):
                        with unittest.mock.patch('src.views.history.Transaction.notes', return_value='Test'):
                            cls.app = App()
                            cls.app.update()
                            cls.context.server_ready()

    def setUp(self):
        with unittest.mock.patch('src.views.history.RPCClient.get_transfers', return_value=self.default_transfers):
            with unittest.mock.patch('src.views.history.Transaction.notes', return_value='Test'):
                self.app.switch_view('history')
                self.app.update()


    #The view will update the history as soon as the RPC Server starts
    #so when we switch to the view, the history should already be in the view.
    def test_transaction_observer(self):
        self.assertEqual(len(self.app.views['history'].transactions_frame.transaction_frames), 5)

    #There should be an update to the transactions list every 5 seconds if there's a diff detected.
    def test_transaction_updates(self):
        new_transfers = mocked_transfers()
        for direction, transfers in self.default_transfers.items():
            for trnfr in transfers:
                if not new_transfers.get(direction):
                    new_transfers[direction] = [trnfr]
                else:
                    new_transfers[direction].append(trnfr)
        with unittest.mock.patch('src.views.history.RPCClient.get_transfers', return_value=new_transfers):
            with unittest.mock.patch('src.views.history.Transaction.notes', return_value='Test'):
                time.sleep(5)
                self.app.update()
                self.assertEqual(len(self.app.views['history'].transactions_frame.transaction_frames), 10)


    @classmethod
    def tearDownClass(cls):
        cls.context.server_teardown()
        cls.app.destroy()
        cls.app._app = None
        RPCClient._instance = None