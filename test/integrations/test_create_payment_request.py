import unittest
from datetime import date, timedelta
from test.utils.rpc_server_helper import RPCServerContextManager
from src.clients.rpc import RPCClient
from gui import App
import clipman
import customtkinter as ctk

class TestCreatePaymentRequest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = RPCServerContextManager()
        cls.context.server_setup()
        with unittest.mock.patch('gui.rpc', return_value='False'):
            with unittest.mock.patch('gui.cfg.subscriptions', return_value='[]'):
                with unittest.mock.patch('src.views.history.RPCClient.get_transfers', return_value=[]):
                    cls.app = App()
                    cls.app.update()
                    cls.context.server_ready()

    def setUp(self):
        with unittest.mock.patch('src.views.history.RPCClient.get_transfers', return_value=[]):
            self.app.switch_view('main')
            #Navigate to the create_payment_request view
            self.app.update()
            self.app.views['main'].receive_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['receive'])
            self.app.views['receive'].create_payment_request_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['create_payment_request'])

    def test_payment_request_creation(self):
        with unittest.mock.patch('src.views.history.RPCClient.get_transfers', return_value=[]):
            custom_label = 'Test'
            amount = '1'
            currency = 'USD'
            number_of_payments = 1
            schedule = 'Daily'
            start_date = date.today()+timedelta(days=1)
            sellers_wallet = '54NGcidS2BnhEMDdZEBdPdKQQRfh1QXHra7HQzXCwrwgWfxkCmSXfWi5tQ8qc2nFTPVNBsfc7cRwWL59xYiN8S5jMX6g9Tq'
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
            self.app.current_view.copy_request_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(clipman.paste(), str(payment_request))
            self.app.current_view.copy_payment_id_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(clipman.paste(), payment_request['payment_id'])
            #This kind of testing may be sufficient, but we could also potentially take the payment request
            #and navigate to the pay view and add it to the subscriptions.
            self.app.current_view.next_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['main'])

    def test_payment_request_creation_invalid_custom_schedule(self):
        with unittest.mock.patch('src.views.history.RPCClient.get_transfers', return_value=[]):
            custom_label = 'Test'
            amount = '1'
            currency = 'USD'
            number_of_payments = 1
            start_date = date.today()+timedelta(days=1)
            sellers_wallet = '54NGcidS2BnhEMDdZEBdPdKQQRfh1QXHra7HQzXCwrwgWfxkCmSXfWi5tQ8qc2nFTPVNBsfc7cRwWL59xYiN8S5jMX6g9Tq'
            custom_schedule = 'invalid'
            #Fill out the payment request creation form.
            self.app.current_view.custom_label_input.insert(0, custom_label)
            self.app.current_view.amount_input.insert(0, amount)
            #The currency input is an option menu, doesn't really seem necessary to test customTkinter
            #by trying to test the clicking of an element itself.
            self.app.current_view.currency_input.set(currency)
            self.app.current_view.number_of_payments_input.insert(0, number_of_payments)
            #Might want to try to figure out how to test the triggering of the custom schedule.
            self.app.current_view.start_date_input.selection_set(start_date)
            self.assertEqual(hasattr(self.app.current_view, 'custom_schedule'), False)
            self.app.current_view.schedule._dropdown_menu.invoke(3)
            self.app.update()
            self.app.current_view.custom_schedule.insert(0, custom_schedule)
            #Setting to the staging wallet
            # self.app.current_view.sellers_wallet_input.insert(0, sellers_wallet) still exists from previous run
            self.app.update()
            self.app.current_view.create_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view.error_label_element.cget('text'), 'Schedule is not a valid cron syntax.')

    def test_billing_frequency_callback(self):
        self.assertEqual(hasattr(self.app.current_view, 'custom_schedule'), False)
        self.app.current_view.schedule._dropdown_menu.invoke(3)
        self.app.update()
        #Check for existence of the custom schedule
        self.assertIsInstance(self.app.current_view.custom_schedule, ctk.CTkEntry)
        self.app.current_view.schedule._dropdown_menu.invoke(0)
        self.app.update()
        #Check it gets removed after the default is selected
        self.assertEqual(hasattr(self.app.current_view, 'custom_schedule'), False)

    def test_schedule_mapping(self):
        self.assertEqual(self.app.current_view.schedule_mapping('Monthly', date(2020, 1, 15)), '0 0 15 * *')
        self.assertEqual(self.app.current_view.schedule_mapping('Weekly', date(2020, 1, 15)), '0 0 * * WED')
        self.assertEqual(self.app.current_view.schedule_mapping('Daily', date(2020, 1, 15)), '0 0 * * *')

    @classmethod
    def tearDownClass(cls):
        cls.context.server_teardown()
        cls.app.shutdown_steps()
        cls.app._app = None
        RPCClient._instance = None