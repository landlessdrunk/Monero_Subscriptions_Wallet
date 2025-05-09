import unittest
from gui import App
from test.utils.rpc_server_helper import rpc_server_setup, rpc_server_teardown
from src.clients.rpc import RPCClient

class MainViewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('MainViewTest setUpClass')
        with unittest.mock.patch('gui.rpc', return_value='False'):
            with unittest.mock.patch('gui.cfg.subscriptions', return_value='[]'):
                cls.app = App()
                cls.app.update()
                cls.rpc_server = rpc_server_setup()
                cls.rpc_server.ready()

    def setUp(self):
        self.app.switch_view('main')
        self.app.update()

    def test_amount_switch(self):
        amount_text = self.app.current_view.amount.cget('text')
        self.assertIn('USD', amount_text)
        self.app.current_view.amount._canvas.event_generate('<Button-1>')
        self.app.update()
        amount_text = self.app.current_view.amount.cget('text')
        self.assertIn('XMR', amount_text)

    def test_receive_button(self):
        self.app.current_view.receive_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['recieve'])

    def test_pay_button(self):
        self.app.current_view.pay_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['pay'])

    def test_subscriptions_button(self):
        self.app.current_view.subscriptions_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['subscriptions'])

    def test_settings_button(self):
        self.app.current_view.settings_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['settings'])

    def test_history_button(self):
        self.app.current_view.history_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['history'])

    @classmethod
    def tearDownClass(cls):
        print('MainViewTest tearDownClass')
        rpc_server_teardown(cls.rpc_server)
        cls.rpc_server = None
        cls.app.quit()
        cls.app.destroy()
        cls.app._app = None
        RPCClient._instance = None