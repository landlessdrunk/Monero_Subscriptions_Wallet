import unittest
from gui import App
from test.utils.rpc_server_helper import rpc_server_setup, rpc_server_teardown

class MainViewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rpc_server = rpc_server_setup()

    def test_amount_switch(self):
        with unittest.mock.patch('gui.rpc', return_value='False'):
            #Don't process subscriptions
            with unittest.mock.patch('gui.cfg.subscriptions', return_value='[]'):
                app = App()
                app.update()
                app.switch_view('main')
                app.update()
                amount_text = app.current_view.amount.cget('text')
                self.assertIn('USD', amount_text)
                app.current_view.amount._canvas.event_generate('<Button-1>')
                app.update()
                amount_text = app.current_view.amount.cget('text')
                self.assertIn('XMR', amount_text)
                app.destroy()

    def test_receive_button(self):
        with unittest.mock.patch('gui.rpc', return_value='False'):
            #Don't process subscriptions
            with unittest.mock.patch('gui.cfg.subscriptions', return_value='[]'):
                app = App()
                app.update()
                app.switch_view('main')
                app.update()
                app.current_view.receive_button._canvas.event_generate('<Button-1>')
                app.update()
                self.assertEqual(app.current_view, app.views['recieve'])
                app.destroy()

    def test_pay_button(self):
        with unittest.mock.patch('gui.rpc', return_value='False'):
            #Don't process subscriptions
            with unittest.mock.patch('gui.cfg.subscriptions', return_value='[]'):
                app = App()
                app.update()
                app.switch_view('main')
                app.update()
                app.current_view.pay_button._canvas.event_generate('<Button-1>')
                app.update()
                self.assertEqual(app.current_view, app.views['pay'])
                app.destroy()

    def test_subscriptions_button(self):
        with unittest.mock.patch('gui.rpc', return_value='False'):
            #Don't process subscriptions
            with unittest.mock.patch('gui.cfg.subscriptions', return_value='[]'):
                app = App()
                app.update()
                app.switch_view('main')
                app.update()
                app.current_view.subscriptions_button._canvas.event_generate('<Button-1>')
                app.update()
                self.assertEqual(app.current_view, app.views['subscriptions'])
                app.destroy()

    def test_settings_button(self):
        with unittest.mock.patch('gui.rpc', return_value='False'):
            #Don't process subscriptions
            with unittest.mock.patch('gui.cfg.subscriptions', return_value='[]'):
                app = App()
                app.update()
                app.switch_view('main')
                app.update()
                app.current_view.settings_button._canvas.event_generate('<Button-1>')
                app.update()
                self.assertEqual(app.current_view, app.views['settings'])
                app.destroy()

    def test_history_button(self):
        with unittest.mock.patch('gui.rpc', return_value='False'):
            #Don't process subscriptions
            with unittest.mock.patch('gui.cfg.subscriptions', return_value='[]'):
                app = App()
                app.update()
                app.switch_view('main')
                app.update()
                app.current_view.history_button._canvas.event_generate('<Button-1>')
                app.update()
                self.assertEqual(app.current_view, app.views['history'])
                app.destroy()

    @classmethod
    def tearDownClass(cls):
        rpc_server_teardown(cls.rpc_server)