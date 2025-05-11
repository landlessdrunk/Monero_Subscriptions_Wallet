import unittest
from datetime import date, timedelta
from test.utils.rpc_server_helper import rpc_server_setup, rpc_server_teardown
from src.clients.rpc import RPCClient
from gui import App

class TestCreatePaymentRequest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rpc_server = rpc_server_setup()
        with unittest.mock.patch('gui.rpc', return_value='False'):
            with unittest.mock.patch('gui.cfg.subscriptions', return_value='[]'):
                cls.app = App()
                cls.app.update()
                cls.rpc_server.ready()

    def setUp(self):
        self.app.switch_view('main')
        #Navigate to the create_payment_request view
        self.app.views['main'].receive_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['recieve'])
        self.app.views['recieve'].create_payment_request_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['create_payment_request'])

    def test_payment_request_creation(self):
        custom_label = 'Test'
        amount = '1'
        currency = 'USD'
        number_of_payments = 1
        schedule = 'Daily'
        start_date = date.today()+timedelta(days=1)
        sellers_wallet = '59fhPNhFLEx3zP16ZAPaeHXsPoNczVaGo245CgDSW9WpiMxvP1N7WdxX1RA4vob6ABGGBxUgjcCN2LjeSGPiH8AEKpAMFKC'
        #Fill out the payment request creation form.
        self.app.current_view.custom_label_input.insert(0, custom_label)
        self.app.current_view.amount_input.insert(0, amount)
        #The currency input is an option menu, doesn't really seem necessary to test customTkinter
        #by trying to test the clicking of an element itself.
        self.app.current_view.currency_input.set(currency)
        self.app.current_view.number_of_payments_input.insert(0, number_of_payments)
        #Might want to try to figure out how to test the triggering of the custom schedule.
        self.app.current_view.schedule.set(schedule)
        self.app.current_view.start_date_input.selection_set(start_date)
        #Setting to the staging wallet
        self.app.current_view.sellers_wallet_input.insert(0, sellers_wallet)
        self.app.update()
        self.app.current_view.create_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['copy_payment_request'])
        payment_request = self.app.current_view.payment_request
        self.assertEqual(payment_request['custom_label'], custom_label)
        self.assertEqual(payment_request['amount'], amount)
        self.assertEqual(payment_request['currency'], currency)
        self.assertEqual(payment_request['number_of_payments'], number_of_payments)
        self.assertEqual(payment_request['schedule'], '0 0 * * *')
        self.assertEqual(payment_request['start_date'], start_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'Z')
        self.assertEqual(payment_request['sellers_wallet'], sellers_wallet)
        #This kind of testing may be sufficient, but we could also potentially take the payment request
        #and navigate to the pay view and add it to the subscriptions.
        self.app.current_view.next_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['main'])

    @classmethod
    def tearDownClass(cls):
        rpc_server_teardown(cls.rpc_server)
        cls.app.destroy()
        cls.app._app = None
        cls.rpc_server = None
        RPCClient._instance = None