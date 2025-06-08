import unittest
import clipman
from gui import App
from test.utils.rpc_server_helper import RPCServerContextManager
from test.utils.config import config_mock
from src.clients.rpc import RPCClient

class ReceiveViewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with unittest.mock.patch('gui.rpc', return_value='False'):
            cls.app = App()
            cls.app.update()
            cls.context = RPCServerContextManager()
            cls.context.server_setup()
            cls.context.server_ready()

    def setUp(self):
        self.app.switch_view('main')
        self.app.update()

    def test_buttons(self):
        with config_mock():
            with unittest.mock.patch('webbrowser.open', return_value=None) as browser_mock:
                self.app.current_view.receive_button._canvas.event_generate('<Button-1>')
                self.app.update()
                self.assertEqual(self.app.current_view, self.app.views['receive'])
                #Test browser opening buttons
                self.app.current_view.buy_monero._canvas.event_generate('<Button-1>')
                self.app.update()
                self.assertEqual(browser_mock.call_count, 1)
                self.app.current_view.earn_monero._canvas.event_generate('<Button-1>')
                self.app.update()
                self.assertEqual(browser_mock.call_count, 2)
                self.app.current_view.sell_for_monero._canvas.event_generate('<Button-1>')
                self.app.update()
                self.assertEqual(browser_mock.call_count, 3)
                self.app.current_view.swap_for_monero._canvas.event_generate('<Button-1>')
                self.app.update()
                self.assertEqual(browser_mock.call_count, 4)
                #Test wallet address copy
                clipman.init()
                clipman.copy('something else')
                self.assertEqual(clipman.paste(), 'something else')
                self.app.current_view.copy_wallet_button._canvas.event_generate('<Button-1>')
                self.app.update()
                self.assertEqual(clipman.paste(), '54NGcidS2BnhEMDdZEBdPdKQQRfh1QXHra7HQzXCwrwgWfxkCmSXfWi5tQ8qc2nFTPVNBsfc7cRwWL59xYiN8S5jMX6g9Tq')
                self.assertEqual(self.app.current_view, self.app.views['main'])


    @classmethod
    def tearDownClass(cls):
        cls.context.server_teardown()
        cls.app.shutdown_steps()
        cls.app._app = None
        RPCClient._instance = None