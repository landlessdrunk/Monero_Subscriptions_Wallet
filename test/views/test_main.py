import unittest
from gui import App
from test.utils.rpc_server_helper import rpc_server_test

class MainViewTest(unittest.TestCase):
    def test_build(self):
        for _ in rpc_server_test():
            #Don't start a second rpc server
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