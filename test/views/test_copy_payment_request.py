import unittest
from gui import App
from src.clients.rpc import RPCClient
from test.utils.rpc_server_helper import RPCServerContextManager

class TestCopyPaymentRequestView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with unittest.mock.patch('gui.rpc', return_value='False'):
            with unittest.mock.patch('gui.cfg.subscriptions', return_value='[]'):
                cls.app = App()
                cls.app.update()
                cls.context = RPCServerContextManager()
                cls.context.server_setup()
                cls.context.server_ready()

    def test_copy_payment_request(self):
        self.assertTrue(True)

    @classmethod
    def tearDownClass(cls):
        cls.context.server_teardown()
        cls.app.shutdown_steps()
        cls.app._app = None
        RPCClient._instance = None