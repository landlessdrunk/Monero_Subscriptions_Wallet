import unittest
import clipboard
import vcr
from test.utils.rpc_server_helper import RPCServerContextManager
from test.utils.config import config_mock, clear_test_config
from src.clients.rpc import RPCClient
from gui import App
from monerorequest import decode_monero_payment_request
from datetime import datetime

class TestPay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with config_mock():
            cls.context = RPCServerContextManager()
            cls.context.server_setup()
            with unittest.mock.patch('gui.rpc', return_value='False'):
                with unittest.mock.patch('gui.cfg.subscriptions', return_value='[]'):
                    cls.app = App()
                    cls.app.update()
                    cls.context.server_ready()

    def test_pay_monero_request_no_clip(self):
        with config_mock():
            self.app.switch_view('main')
            self.app.update()
            self.app.current_view.pay_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['pay'])
            monero_request = 'monero-request:2:H4sIAAAAAAAC/y1O246CMBD9FdPHjW5aBBTeEBUTlZBFF+NLU0q5GKCkFBc1++/bms1MMjm3zHkB0vChlcAFCEwBLUlbMFy1WUWJ5AIPolaSVgYhWEsfCp3j9ZvoJW9wTVKmLSfWS8W2Q5MygXmOO/JoWCt74KIp+Ae4ypTVntPlwoHURKYDzTxXsZ6WLBtqplQ4gZMPPZpmdc1Ej3+Iurqj5eRlFJbbw2acPyNkX72IsN2lj3hIn98k4IZp+cU6Tpykq47jPULhIsnGC/ryzDtPbW8VBKvxXNyoHxqHG4uDqNotvc2+847bva9fSiIkzojUXQxoWDNozRA6Qei+9xNCeAW/f49op5Q4AQAA'
            self.app.current_view.payment_input.set(monero_request)
            self.app.update()
            self.app.current_view.next_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['review_request'])
            decoded_request = decode_monero_payment_request(monero_request)
            review_view = self.app.current_view
            self.assertEqual(review_view.custom_label.cget('text'), f"{decoded_request['custom_label']}:")
            amount_label = f"{decoded_request['amount']} {decoded_request['currency']} worth of XMR billed at 12:00 am"
            self.assertEqual(review_view.amount_label.cget('text'), amount_label)
            start_text = f"First payment due: {datetime.strptime(decoded_request['start_date'].split("T")[0], "%Y-%m-%d").strftime("%B %-d, %Y")}"
            self.assertEqual(review_view.starting_on.cget('text'), start_text)
            seller_text = f"Paying To: {decoded_request["sellers_wallet"][:5]}...{decoded_request["sellers_wallet"][-5:]}"
            self.assertEqual(review_view.sellers_wallet_label.cget('text'), seller_text)
            review_view.confirm_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['subscriptions'])
            self.assertEqual(len(self.app.current_view.sub_frame.sub_frames), 1)

    def test_pay_monero_request_clip(self):
        with config_mock():
            monero_request = 'monero-request:2:H4sIAAAAAAAC/y1O246CMBD9FdPHjW5aBBTeEBUTlZBFF+NLU0q5GKCkFBc1++/bms1MMjm3zHkB0vChlcAFCEwBLUlbMFy1WUWJ5AIPolaSVgYhWEsfCp3j9ZvoJW9wTVKmLSfWS8W2Q5MygXmOO/JoWCt74KIp+Ae4ypTVntPlwoHURKYDzTxXsZ6WLBtqplQ4gZMPPZpmdc1Ej3+Iurqj5eRlFJbbw2acPyNkX72IsN2lj3hIn98k4IZp+cU6Tpykq47jPULhIsnGC/ryzDtPbW8VBKvxXNyoHxqHG4uDqNotvc2+847bva9fSiIkzojUXQxoWDNozRA6Qei+9xNCeAW/f49op5Q4AQAA'
            clipboard.copy(monero_request)
            self.app.switch_view('main')
            self.app.update()
            self.app.current_view.pay_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['pay'])
            self.assertEqual(self.app.current_view.input_box_for_wallet_or_request.get(), monero_request)
            self.app.current_view.next_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['review_request'])
            decoded_request = decode_monero_payment_request(monero_request)
            review_view = self.app.current_view
            self.assertEqual(review_view.custom_label.cget('text'), f"{decoded_request['custom_label']}:")
            amount_label = f"{decoded_request['amount']} {decoded_request['currency']} worth of XMR billed at 12:00 am"
            self.assertEqual(review_view.amount_label.cget('text'), amount_label)
            start_text = f"First payment due: {datetime.strptime(decoded_request['start_date'].split("T")[0], "%Y-%m-%d").strftime("%B %-d, %Y")}"
            self.assertEqual(review_view.starting_on.cget('text'), start_text)
            seller_text = f"Paying To: {decoded_request["sellers_wallet"][:5]}...{decoded_request["sellers_wallet"][-5:]}"
            self.assertEqual(review_view.sellers_wallet_label.cget('text'), seller_text)
            review_view.confirm_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['subscriptions'])
            self.assertEqual(len(self.app.current_view.sub_frame.sub_frames), 1)

    def test_pay_monero_address_no_clip(self):
        with config_mock():
            self.app.switch_view('main')
            self.app.update()
            self.app.current_view.pay_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['pay'])
            monero_address = '59fhPNhFLEx3zP16ZAPaeHXsPoNczVaGo245CgDSW9WpiMxvP1N7WdxX1RA4vob6ABGGBxUgjcCN2LjeSGPiH8AEKpAMFKC'
            self.app.current_view.payment_input.set(monero_address)
            self.app.update()
            self.app.current_view.next_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['amount'])
            self.app.current_view.input_box_for_amount.insert(0, '1')
            self.assertEqual(self.app.current_view.wallet.cget('text'), 'To Wallet: 59fhP...AMFKC')
            self.app.update()
            self.app.current_view.send_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['review_send'])
            self.assertEqual(self.app.current_view.label.cget('text'), 'Send Payment?')
            self.assertEqual(self.app.current_view.sending_to.cget('text'), '1 USD worth of XMR to: 59fhP...AMFKC')
            with vcr.use_cassette('test/fixtures/cassettes/pay_address_no_clip.yaml'):
                self.app.current_view.confirm_button._canvas.event_generate('<Button-1>')
                self.app.update()
                self.assertEqual(self.app.current_view, self.app.views['main'])
            #TODO: Check that the payment request happened/went through. Not sure the best way to do that.
            #Probably should be a VCR request.

    def tearDown(self):
        clipboard.copy('')
        clear_test_config()

    @classmethod
    def tearDownClass(cls):
        cls.context.server_teardown()
        cls.app.destroy()
        cls.app._app = None
        RPCClient._instance = None