import unittest
import vcr
from src.clients.rpc import RPCClient
import requests
from test.utils.config import config_mock
from test.utils.rpc_server_helper import rpc_server_test

class testRPCClient(unittest.TestCase):
    def test_version(self):
        with vcr.use_cassette('test/fixtures/cassettes/version.yaml'):
            client = RPCClient()
            version = client.get_version()
        self.assertEqual(version, 65563)

    def test_get_address(self):
        with vcr.use_cassette('test/fixtures/cassettes/address.yaml'):
            client = RPCClient()
            address = client.get_address()
        self.assertEqual(address, '54NGcidS2BnhEMDdZEBdPdKQQRfh1QXHra7HQzXCwrwgWfxkCmSXfWi5tQ8qc2nFTPVNBsfc7cRwWL59xYiN8S5jMX6g9Tq')

    def test_get_balance(self):
        with vcr.use_cassette('test/fixtures/cassettes/get_balance.yaml'):
            client = RPCClient()
            balance = client.get_balance()
        self.assertEqual(balance, 52561416412713)

    def test_make_integrated_address(self):
        with vcr.use_cassette('test/fixtures/cassettes/integrated_address.yaml'):
            client = RPCClient()
            address = '54NGcidS2BnhEMDdZEBdPdKQQRfh1QXHra7HQzXCwrwgWfxkCmSXfWi5tQ8qc2nFTPVNBsfc7cRwWL59xYiN8S5jMX6g9Tq'
            payment_id = '075eed614ebea072'
            integrated_address = client.make_integrated_address(address, payment_id)
        self.assertEqual(integrated_address['integrated_address'], '5KNNQBWjwWU3zP16ZAPaeHXsPoNczVaGo245CgDSW9WpiMxvP1N7WdxX1RA4vob6ABGGBxUgjcCN2LjeSGPiH8AEUmgrwoxBZLKDt8PcKB')

    def test_transfer(self):
        with vcr.use_cassette('test/fixtures/cassettes/transfer.yaml'):
            client = RPCClient()
            address = '54NGcidS2BnhEMDdZEBdPdKQQRfh1QXHra7HQzXCwrwgWfxkCmSXfWi5tQ8qc2nFTPVNBsfc7cRwWL59xYiN8S5jMX6g9Tq'
            result = client.transfer(address, 1000)
        self.assertEqual(result['amount'], 1000)

    def test_create_wallet(self):
        with vcr.use_cassette('test/fixtures/cassettes/create_wallet.yaml'):
            client = RPCClient()
            result = client.create_wallet('test_wallet_2')
        self.assertEqual(result, {})

    def test_set_tx_notes(self):
        with vcr.use_cassette('test/fixtures/cassettes/set_tx_notes.yaml'):
            client = RPCClient()
            transfers = client.get_transfers()
            client.set_tx_notes([transfers['out'][0]['txid']], ['test_note'])
            tx_notes_get_result = client.get_tx_notes([transfers['out'][0]['txid']])
            self.assertEqual(tx_notes_get_result, ['test_note'])

    def test_open_wallet(self):
        with vcr.use_cassette('test/fixtures/cassettes/open_wallet.yaml'):
            client = RPCClient()
            result = client.open_wallet('test_wallet_2')
        self.assertEqual(result, True)

    def test_open_wallet_error(self):
        with unittest.mock.patch('src.clients.rpc.RPCClient.post', return_value={'error': {'message': 'error'}}):
            client = RPCClient()
            self.assertEqual(client.open_wallet('test_wallet_2'), False)

    def test_post_error_message(self):
        response = requests.models.Response()
        response.status_code = 500
        response._content = b'{"error": {"message": "error"}}'
        with unittest.mock.patch('requests.post', return_value=response):
            client = RPCClient()
            self.assertEqual(client.get_address(), {'error': {'message': 'error'}})

    def test_post_exception(self):
        with unittest.mock.patch('requests.post', side_effect=requests.exceptions.ConnectionError('error')):
            client = RPCClient()
            self.assertEqual(client.get_address(), {'exception': 'error'})

    def test_daemon_post_error_message(self):
        response = requests.models.Response()
        response.status_code = 500
        response._content = b'{"error": {"message": "error"}}'
        with unittest.mock.patch('requests.post', return_value=response):
            client = RPCClient()
            self.assertEqual(client.current_block_height(), {'error': {'message': 'error'}})

    def test_daemon_post_exception(self):
        with unittest.mock.patch('requests.post', side_effect=requests.exceptions.ConnectionError('error')):
            client = RPCClient()
            self.assertEqual(client.current_block_height(), {'exception': 'error'})

'''
To create a new test with the wallet rpc server started use
for _ in rpc_server_test():
    with vcr.use_cassette(filename):

The rpc_server_test line can be removed once the cassette is created.
'''
if __name__ == '__main__':
    unittest.main()