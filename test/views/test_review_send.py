import unittest
from gui import App
from test.utils.rpc_server_helper import RPCServerContextManager
from src.clients.rpc import RPCClient
import customtkinter as ctk

class ReviewSendTest(unittest.TestCase):
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

    def test_receive_cancel(self):
        self.app.current_view.pay_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['pay'])
        self.app.current_view.input_box_for_wallet_or_request.delete(0, ctk.END)
        self.app.update()
        monero_address = '5B9PgE8kH6GPTamHY9WdXEbNr66PtiJfuU8nMvR2b7bsPLtUtjbwfNPBuFxNgCwAyg299LGt9xdZUizZ4whTHA7K614k9va'
        self.app.current_view.input_box_for_wallet_or_request.insert(0, monero_address)
        self.app.update()
        self.app.current_view.next_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['amount'])
        self.app.current_view.input_box_for_amount.delete(0, ctk.END)
        self.app.update()
        self.app.current_view.input_box_for_amount.insert(0, '100')
        self.app.update()
        self.app.current_view.send_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['review_send'])
        self.app.current_view.cancel_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['main'])

    def test_confirm_failure(self):
        self.app.current_view.pay_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['pay'])
        self.app.current_view.input_box_for_wallet_or_request.delete(0, ctk.END)
        self.app.update()
        monero_address = '5B9PgE8kH6GPTamHY9WdXEbNr66PtiJfuU8nMvR2b7bsPLtUtjbwfNPBuFxNgCwAyg299LGt9xdZUizZ4whTHA7K614k9va'
        self.app.current_view.input_box_for_wallet_or_request.insert(0, monero_address)
        self.app.update()
        self.app.current_view.next_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['amount'])
        self.app.current_view.input_box_for_amount.delete(0, ctk.END)
        self.app.update()
        self.app.current_view.input_box_for_amount.insert(0, '100')
        self.app.update()
        with unittest.mock.patch('src.views.review_send.RPCClient.transfer', return_value=False):
            self.app.current_view.send_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['review_send'])
            self.app.current_view.confirm_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['amount'])

    @classmethod
    def tearDownClass(cls):
        cls.context.server_teardown()
        cls.app.shutdown_steps()
        cls.app._app = None
        RPCClient._instance = None