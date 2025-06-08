import unittest
from test.utils.rpc_server_helper import RPCServerContextManager
from test.utils.config import config_mock
from gui import App
from src.clients.rpc import RPCClient

class TestSubscriptionView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = RPCServerContextManager()
        cls.context.server_setup()
        with unittest.mock.patch('gui.rpc', return_value='False'):
            with unittest.mock.patch('src.views.history.RPCClient.get_transfers', return_value=[]):
                with config_mock():
                    cls.app = App()
                    cls.app.update()
                    cls.context.server_ready()

    def test_buttons(self):
        self.app.current_view.ok_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['main'])

    @classmethod
    def tearDownClass(cls):
        cls.context.server_teardown()
        cls.app.shutdown_steps()
        cls.app._app = None
        RPCClient._instance = None
