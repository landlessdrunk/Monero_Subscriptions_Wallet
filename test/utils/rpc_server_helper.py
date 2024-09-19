from unittest.mock import patch
from src.rpc_server import RPCServer
from src.wallet import Wallet

def rpc_server_test(wallet_name='test_wallet'):
    with patch('config.stagenet', return_value=True):
        wallet = Wallet('test_wallet')
        rpc_server = RPCServer(wallet)
        rpc_server.start()
        rpc_server.ready()
        yield
        rpc_server.kill()

'''
What is this for?
This only needs to be used when we want to re-record or record new VCR tests that invlove the RPC server.
This is just a helper function to be able to set up the environment for those kinds of tests a bit easier.
Once they are recorded, the code involving this function can be safely removed and it will help speed up
tests a bit since they won't load up the rpc server on every test.

To use:
Re-add to test
from test.utils.rpc_server_helper import rpc_server_test
for _ in rpc_server_test:
    write test code here
    any vcr.use_cassette should go here too as there are some requests made to the rpc server in order
    to check for readiness. If this helper function is removed, those requests will no longer happen.

By default it will look for a 'test_wallet' in the 'wallets' directory. It doesn't need to be the same one
but the project does have a wallet already set up with funds in it. Access will be gated, but as it is a
stagenet wallet, it is more of an inconvenience if someone drains funds from it just to grief the project.
'''
