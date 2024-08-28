from unittest.mock import patch
from src.rpc_server import RPCServer
from src.wallet import Wallet

def rpc_server_test(wallet_name='test_wallet'):
    with patch('config.stagenet', return_value=True):
        wallet = Wallet('test_wallet')
        rpc_server = RPCServer(wallet)
        rpc_server.start()
        yield
        rpc_server.ready()
        rpc_server.kill()
