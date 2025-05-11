from config import ConfigFile, config_file
import unittest
from contextlib import contextmanager

@contextmanager
def config_mock():
    cfg = ConfigFile('config-test.ini')
    with unittest.mock.patch.object(config_file, '_config', cfg._config):
        with unittest.mock.patch.object(config_file, '_path', cfg._path):
            yield

def clear_test_config():
    ConfigFile('config-test.ini').clear()