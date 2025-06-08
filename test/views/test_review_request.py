import unittest
import customtkinter as ctk
from monerorequest import make_random_payment_id, decode_monero_payment_request
from datetime import datetime
from src.clients.rpc import RPCClient
from gui import App
from test.utils.rpc_server_helper import RPCServerContextManager
from test.utils.config import config_mock
from test.factories.subscription import SubscriptionFactory

class ReviewRequestTest(unittest.TestCase):
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

    def test_reactivation(self):
        with config_mock():
            #Set Up First Activation
            self.app.current_view.pay_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['pay'])
            #Clear out input from other tests
            self.app.current_view.input_box_for_wallet_or_request.delete(0, ctk.END)
            monero_request = 'monero-request:2:H4sIAAAAAAAC/y1O246CMBD9FdPHjW5aBBTeEBUTlZBFF+NLU0q5GKCkFBc1++/bms1MMjm3zHkB0vChlcAFCEwBLUlbMFy1WUWJ5AIPolaSVgYhWEsfCp3j9ZvoJW9wTVKmLSfWS8W2Q5MygXmOO/JoWCt74KIp+Ae4ypTVntPlwoHURKYDzTxXsZ6WLBtqplQ4gZMPPZpmdc1Ej3+Iurqj5eRlFJbbw2acPyNkX72IsN2lj3hIn98k4IZp+cU6Tpykq47jPULhIsnGC/ryzDtPbW8VBKvxXNyoHxqHG4uDqNotvc2+847bva9fSiIkzojUXQxoWDNozRA6Qei+9xNCeAW/f49op5Q4AQAA'
            self.app.current_view.input_box_for_wallet_or_request.insert(0, monero_request)
            self.app.update()
            self.app.current_view.next_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['review_request'])
            decoded_request = decode_monero_payment_request(monero_request)
            review_view = self.app.current_view
            self.assertEqual(review_view.custom_label.cget('text'), f"{decoded_request['custom_label']}:")
            amount_label = f"{decoded_request['amount']} {decoded_request['currency']} worth of XMR billed at 12:00 am"
            self.assertEqual(review_view.amount_label.cget('text'), amount_label)
            start_text = "First payment due: May 11, 2025"
            self.assertEqual(review_view.starting_on.cget('text'), start_text)
            seller_text = f"Paying To: {decoded_request["sellers_wallet"][:5]}...{decoded_request["sellers_wallet"][-5:]}"
            self.assertEqual(review_view.sellers_wallet_label.cget('text'), seller_text)

            #Reactivation
            self.app.current_view._back_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['pay'])
            #Clear out input from other tests
            self.app.current_view.input_box_for_wallet_or_request.delete(0, ctk.END)
            new_subscription = SubscriptionFactory(custom_label='Subscription Test', currency='XMR',
                                amount='15', payment_id=make_random_payment_id(), start_date=datetime(2025,5,15).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
                                sellers_wallet='5B9PgE8kH6GPTamHY9WdXEbNr66PtiJfuU8nMvR2b7bsPLtUtjbwfNPBuFxNgCwAyg299LGt9xdZUizZ4whTHA7K614k9va')
            monero_request = new_subscription.encode()
            self.app.current_view.input_box_for_wallet_or_request.insert(0, monero_request)
            self.app.update()
            self.app.current_view.next_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['review_request'])
            decoded_request = new_subscription.json_friendly()
            review_view = self.app.current_view
            self.assertEqual(review_view.custom_label.cget('text'), f"{decoded_request['custom_label']}:")
            amount_label = f"{decoded_request['amount']} {decoded_request['currency']} billed at 12:00 am, on day 1 of the month"
            self.assertEqual(review_view.amount_label.cget('text'), amount_label)
            start_text = "First payment due: May 15, 2025"
            self.assertEqual(review_view.starting_on.cget('text'), start_text)
            seller_text = f"Paying To: {decoded_request["sellers_wallet"][:5]}...{decoded_request["sellers_wallet"][-5:]}"
            self.assertEqual(review_view.sellers_wallet_label.cget('text'), seller_text)

    def test_cancel(self):
        with config_mock():
            self.app.current_view.pay_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['pay'])
            #Clear out input from other tests
            self.app.current_view.input_box_for_wallet_or_request.delete(0, ctk.END)
            monero_request = 'monero-request:2:H4sIAAAAAAAC/y1O246CMBD9FdPHjW5aBBTeEBUTlZBFF+NLU0q5GKCkFBc1++/bms1MMjm3zHkB0vChlcAFCEwBLUlbMFy1WUWJ5AIPolaSVgYhWEsfCp3j9ZvoJW9wTVKmLSfWS8W2Q5MygXmOO/JoWCt74KIp+Ae4ypTVntPlwoHURKYDzTxXsZ6WLBtqplQ4gZMPPZpmdc1Ej3+Iurqj5eRlFJbbw2acPyNkX72IsN2lj3hIn98k4IZp+cU6Tpykq47jPULhIsnGC/ryzDtPbW8VBKvxXNyoHxqHG4uDqNotvc2+847bva9fSiIkzojUXQxoWDNozRA6Qei+9xNCeAW/f49op5Q4AQAA'
            self.app.current_view.input_box_for_wallet_or_request.insert(0, monero_request)
            self.app.update()
            self.app.current_view.next_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['review_request'])
            self.app.current_view.cancel_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['main'])

    @classmethod
    def tearDownClass(cls):
        cls.context.server_teardown()
        cls.app.shutdown_steps()
        cls.app._app = None
        RPCClient._instance = None