import unittest
from test.utils.rpc_server_helper import RPCServerContextManager
from test.utils.config import config_mock
from gui import App
import clipman
from src.clients.rpc import RPCClient
from test.factories.subscription import SubscriptionFactory
import time

class TestSubscriptionView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = RPCServerContextManager()
        cls.context.server_setup()
        with unittest.mock.patch('gui.rpc', return_value='False'):
            with unittest.mock.patch('src.views.history.RPCClient.get_transfers', return_value=[]):
                cls.app = App()
                cls.app.update()
                cls.context.server_ready()

    def setUp(self):
        self.app.switch_view('main')
        self.app.update()

    def test_subscriptions(self):
        self.app.current_view.subscriptions_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['subscriptions'])
        self.assertEqual(len(self.app.current_view.sub_frame.sub_frames), 0)
        clipman.init()
        monero_request = 'monero-request:2:H4sIAAAAAAAC/y1O246CMBD9FdPHjW5aBBTeEBUTlZBFF+NLU0q5GKCkFBc1++/bms1MMjm3zHkB0vChlcAFCEwBLUlbMFy1WUWJ5AIPolaSVgYhWEsfCp3j9ZvoJW9wTVKmLSfWS8W2Q5MygXmOO/JoWCt74KIp+Ae4ypTVntPlwoHURKYDzTxXsZ6WLBtqplQ4gZMPPZpmdc1Ej3+Iurqj5eRlFJbbw2acPyNkX72IsN2lj3hIn98k4IZp+cU6Tpykq47jPULhIsnGC/ryzDtPbW8VBKvxXNyoHxqHG4uDqNotvc2+847bva9fSiIkzojUXQxoWDNozRA6Qei+9xNCeAW/f49op5Q4AQAA'
        clipman.copy(monero_request)
        # add subscription
        self.app.current_view.add_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['pay'])
        self.app.current_view.next_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['review_request'])
        self.app.current_view.confirm_button._canvas.event_generate('<Button-1>')
        #Need to give the app time to update the subscription list
        time.sleep(.1)
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['subscriptions'])
        self.assertEqual(len(self.app.current_view.sub_frame.sub_frames), 1)
        # cancel subscription, without canceling it
        self.app.current_view.sub_frame.sub_frames[0].subscription_cancel_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['review_delete'])
        self.app.current_view.no_button._canvas.event_generate('<Button-1>')
        self.assertEqual(self.app.current_view, self.app.views['subscriptions'])
        # cancel subscription for real this time
        self.app.current_view.sub_frame.sub_frames[0].subscription_cancel_button._canvas.event_generate('<Button-1>')
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['review_delete'])
        self.app.current_view.yes_button._canvas.event_generate('<Button-1>')
        #Need to give the app time to update the subscription list
        time.sleep(.2)
        self.app.update()
        time.sleep(.2)
        self.app.update()
        self.assertEqual(self.app.current_view, self.app.views['subscriptions'])
        self.assertEqual(len(self.app.current_view.sub_frame.sub_frames), 0)

    @classmethod
    def tearDownClass(cls):
        cls.context.server_teardown()
        cls.app.shutdown_steps()
        cls.app._app = None
        RPCClient._instance = None

class TestExistingSubscriptionView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = RPCServerContextManager()
        cls.context.server_setup()
        cls.sub = SubscriptionFactory()
        with unittest.mock.patch('gui.rpc', return_value='False'):
            with config_mock() as cfg:
                cfg.add_subscription(cls.sub)
                cls.app = App()
                cls.app.update()
                cls.context.server_ready()

    def setUp(self):
        self.app.switch_view('main')
        self.app.update()

    def test_existing_subscriptions(self):
        with config_mock():
            self.app.current_view.subscriptions_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['subscriptions'])
            self.assertEqual(len(self.app.current_view.sub_frame.sub_frames), 1)

    @classmethod
    def tearDownClass(cls):
        cls.context.server_teardown()
        cls.app.shutdown_steps()
        cls.app._app = None
        RPCClient._instance = None
        with config_mock() as cfg:
            cfg.remove_subscription(cls.sub)