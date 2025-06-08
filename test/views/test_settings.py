import unittest
import json
from src.clients.rpc import RPCClient
from gui import App
from config import subscriptions
from test.utils.rpc_server_helper import RPCServerContextManager
from test.utils.config import config_mock
from test.factories.subscription import SubscriptionFactory

class SettingsTest(unittest.TestCase):
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

    def test_buttons(self):
        with config_mock() as mock_cfg:
            self.app.current_view.settings_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['settings'])
            #Testing Node Selection Button
            self.app.current_view.node_selection_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['node_selection'])
            self.app.current_view._back_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['settings'])

            #Testing Set Currency Button
            self.app.current_view.set_currency_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['set_currency'])
            self.app.current_view._back_button._canvas.event_generate('<Button-1>')
            self.app.update()
            self.assertEqual(self.app.current_view, self.app.views['settings'])

            mock_cfg.add_subscription(SubscriptionFactory.create())

            #Testing Export Subscriptions
            with unittest.mock.patch('tkinter.filedialog.asksaveasfilename', return_value='test_subscriptions.json'):
                self.app.current_view.export_subscriptions_file._canvas.event_generate('<Button-1>')
                self.app.update()
                with open('test_subscriptions.json', 'r') as f:
                    self.assertEqual(json.load(f), json.loads(subscriptions()))

            sub = SubscriptionFactory.create(custom_label='Test')
            import_subs = [sub.json_friendly()]

            with open('test_subscriptions.json', 'w') as f:
                json.dump(import_subs, f)

            #Testing Import Subscriptions
            with unittest.mock.patch('tkinter.filedialog.askopenfilename', return_value='test_subscriptions.json'):
                self.app.current_view.import_subscriptions_file._canvas.event_generate('<Button-1>')
                self.app.update()
                self.assertEqual(json.loads(subscriptions()), import_subs)

            mock_cfg.remove_subscription(sub)

    @classmethod
    def tearDownClass(cls):
        cls.context.server_teardown()
        cls.app.shutdown_steps()
        cls.app._app = None
        RPCClient._instance = None