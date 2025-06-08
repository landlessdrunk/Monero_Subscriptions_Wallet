import config
from config import ConfigFile, config_file
import unittest
from contextlib import contextmanager

@contextmanager
def config_mock():
    config.config_options['rpc']['node_url'] = 'http://127.0.0.1:38081'
    config.config_options['rpc']['daemon_url'] = 'http://127.0.0.1:38081/json_rpc'
    config.config_options['rpc']['wallet_name'] = 'test_wallet'
    config.config_options['rpc']['stagenet'] = True
    cfg = ConfigFile('config-test.ini')
    with unittest.mock.patch.object(config_file, '_config', cfg._config):
        with unittest.mock.patch.object(config_file, '_path', cfg._path):
            yield(cfg)

def clear_test_config():
    ConfigFile('config-test.ini').clear()