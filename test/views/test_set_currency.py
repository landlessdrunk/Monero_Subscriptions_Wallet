import unittest
from src.clients.rpc import RPCClient
from gui import App
from test.utils.rpc_server_helper import RPCServerContextManager
from test.utils.config import config_mock
from config import default_currency, secondary_currency
from src.exchange import Exchange

class SetCurrencyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with unittest.mock.patch('gui.rpc', return_value='False'):
            with unittest.mock.patch('gui.cfg.subscriptions', return_value='[]'):
                cls.app = App()
                cls.app.update()
                cls.context = RPCServerContextManager()
                cls.context.server_setup()
                cls.context.server_ready()

    def setUp(self):
        self.app.switch_view('main')
        self.app.update()

    def test_set_currencies(self):
        with config_mock():
            self.app.current_view.settings_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['settings'])
            self.app.current_view.set_currency_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['set_currency'])
            self.assertEqual(self.app.current_view.default_currency.get(), 'USD')
            self.assertEqual(self.app.current_view.secondary_currency.get(), 'XMR')
            self.assertEqual(default_currency(), 'USD')
            self.assertEqual(secondary_currency(), 'XMR')

            self.app.current_view.default_currency._dropdown_menu.invoke(Exchange.options().index('XMR'))
            self.app.current_view.secondary_currency._dropdown_menu.invoke(Exchange.options().index('USD'))
            self.assertEqual(default_currency(), 'XMR')
            self.assertEqual(secondary_currency(), 'USD')            
            self.app.update()

    @classmethod
    def tearDownClass(cls):
        cls.context.server_teardown()
        cls.app.shutdown_steps()
        cls.app._app = None
        RPCClient._instance = None