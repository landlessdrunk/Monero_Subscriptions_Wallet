import unittest
from gui import App
from src.clients.rpc import RPCClient
from test.utils.rpc_server_helper import RPCServerContextManager
from src.views.node_selection import get_random_node, check_if_node_works
import vcr
from test.utils.config import config_mock

class TestNodeSelection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with unittest.mock.patch('gui.rpc', return_value='False'):
            with unittest.mock.patch('gui.cfg.subscriptions', return_value='[]'):
                cls.app = App()
                cls.app.update()
                cls.context = RPCServerContextManager()
                cls.context.server_setup()
                cls.context.server_ready()

    def test_set_node(self):
        with config_mock():
            with unittest.mock.patch('src.views.node_selection.RPCServer.check_readiness', return_value=True):
                self.app.switch_view('node_selection')
                node_selection = self.app.current_view
                self.assertEqual(node_selection.node_selection.get(), 'http://127.0.0.1:38081')
                node_selection.node.set('localhost:38081')
                self.app.update()
                self.assertEqual(node_selection.node.get(), "localhost:38081")
                node_selection.submit_button._canvas.event_generate("<Button-1>")
                self.app.update()
                self.assertEqual(self.app.current_view, self.app.views['main'])
                self.context.server_ready()
                self.assertEqual(self.context.rpc_server._daemon_address(), 'localhost:38081')

    def test_set_random_node(self):
        with unittest.mock.patch('src.views.node_selection.RPCServer.check_readiness', return_value=True):
            with vcr.use_cassette('test/fixtures/cassettes/test_set_random_node.yaml'):
                with unittest.mock.patch('src.views.node_selection.get_random_node', return_value='ldn1.derp.anstee.dev:18081'):
                    with unittest.mock.patch('src.views.history.TransactionsScrollableFrame.update_txs', return_value=True):
                        self.app.switch_view('node_selection')
                        self.app.update()
                        node_selection = self.app.current_view
                        node_selection.random_node._canvas.event_generate("<Button-1>")
                        self.app.update()
                        self.assertEqual(node_selection.node_selection.get(), 'ldn1.derp.anstee.dev:18081')
                        node_selection.submit_button._canvas.event_generate("<Button-1>")
                        self.context.server_ready()
                        self.app.update()
                        self.assertEqual(self.app.current_view, self.app.views['main'])
                        self.assertEqual(self.context.rpc_server._daemon_address(), 'ldn1.derp.anstee.dev:18081')
    
    @classmethod
    def tearDownClass(cls):
        cls.context.server_teardown()
        cls.app.shutdown_steps()
        cls.app._app = None
        RPCClient._instance = None

class TestNodeSelectionMethods(unittest.TestCase):
    def test_get_random_node(self):
        with vcr.use_cassette('test/fixtures/cassettes/test_get_random_node.yaml'):
            with unittest.mock.patch('lxml.html.HtmlElement.xpath', return_value=['invalid', 'http://invalid_with:port', 'https://xmr-de.boldsuck.org:18081']):
                self.assertEqual(get_random_node(), 'xmr-de.boldsuck.org:18081')

    def test_check_if_node_works(self):
        with vcr.use_cassette('test/fixtures/cassettes/test_check_if_node_works.yaml'):
            self.assertTrue(check_if_node_works('xmr-de.boldsuck.org:18081'))

        with vcr.use_cassette('test/fixtures/cassettes/test_check_if_node_works_invalid_url.yaml'):
            self.assertFalse(check_if_node_works('invalid'))

        with unittest.mock.patch('requests.models.Response.json') as response_json:
            response_json.return_value = {
                'result': {
                    'status': 'ERROR'
                } 
            }
            with vcr.use_cassette('test/fixtures/cassettes/test_check_if_node_works_invalid_response.yaml'):
                self.assertFalse(check_if_node_works('76.121.87.19:18081'))
