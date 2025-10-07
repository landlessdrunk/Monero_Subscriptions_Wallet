import requests
import json
import logging
import logging.config
from config import local_rpc_url, daemon_url, wallet_name
from src.logging import config as logging_config
from src.interfaces.observer import Observer
from src.interfaces.notifier import Notifier

class RPCClient(Notifier):
    _instance = None
    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._headers = None
        logging.config.dictConfig(logging_config)
        self.logger = logging.getLogger(self.__module__)
        self._observers = []
        self._balance = ''

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def detach(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)

    def current_block_height(self):
        result = self.daemon_post(self._current_block_height())
        return result.get("result", {}).get("height", False) or result

    def _current_block_height(self):
        return {
            "jsonrpc": "2.0",
            "id": "0",
            "method": "get_info"
        }

    def get_version(self):
        result = self.post(self._get_version())
        return result.get("result", {}).get("version", False) or result

    def _get_version(self):
        return {
            "jsonrpc": "2.0",
            "id": "0",
            "method": "get_version"
        }

    def local_healthcheck(self):
        return isinstance(self.get_version(), int)

    def refresh(self):
        #No-Op
        return self.post(self._refresh())

    def _refresh(self):
        return {
            "jsonrpc": "2.0",
            "id": "0",
            "method": "refresh"
        }

    def create_wallet(self, filename=wallet_name()):
        return self.post(self._create_wallet(filename))['result']


    def _create_wallet(self, filename=wallet_name()):
        return {
            "jsonrpc": "2.0",
            "id": "0",
            "method": 'create_wallet',
            "params": {
                "filename": filename,
                "language": "English"
            }
        }

    def open_wallet(self, filename=wallet_name()):
        request_result = self.post(self._open_wallet(filename))
        if request_result.get('error'):
            self.logger.debug(request_result['error'])
            return False
        else:
            return True


    def _open_wallet(self, filename=wallet_name()):
        return {
            "jsonrpc": "2.0",
            "id": "0",
            "method": 'open_wallet',
            "params": {
                "filename": filename
            }
        }

    def get_address(self):
        address_request = self.post(self._get_address())
        return address_request.get('result', {}).get('address') or address_request

    def _get_address(self):
        return {
            "jsonrpc": "2.0",
            "id": "0",
            "method": "get_address",
        }

    def get_balance(self, which='balance'):
        request = self.post(self._get_balance())
        self._balance = request.get('result', {}).get(which, '0')
        self.notify()
        return self._balance

    def _get_balance(self):
        return {
            "jsonrpc": "2.0",
            "id": "0",
            "method": "get_balance"
        }

    def make_integrated_address(self, wallet, payment_id):
        return self.post(self._make_integrated_address(wallet, payment_id))['result']

    def _make_integrated_address(self, wallet, payment_id):
        return {
            "jsonrpc": "2.0",
            "id": "0",
            "method": "make_integrated_address",
            "params": {
                "standard_address": wallet,
                "payment_id": payment_id
            }
        }

    def transfer(self, destination, amount):
        return self.post(self._transfer(destination, amount)).get('result')

    def _transfer(self, destination, amount):
        return {
            "jsonrpc": "2.0",
            "id": "0",
            "method": "transfer",
            "params": {
                "destinations": [{
                    'address': destination,
                    'amount': amount
                 }]
            }
        }

    def get_transfers(self):
        self._transfers = self.post(self._get_transfers())
        return self._transfers.get('result', [])

    def _get_transfers(self):
        return {
            'jsonrpc': '2.0',
            'id': '0',
            'method': 'get_transfers',
            'params': {
                'in': True,
                'out': True,
                'pending': True,
                'failed': False,
                'all_accounts': True
            }
        }

    def set_tx_notes(self, tx_ids: list, notes: list):
        return self.post(self._set_tx_notes(tx_ids, notes))


    def _set_tx_notes(self, tx_ids: list[str], notes: list[str]):
        return {
            'jsonrpc': '2.0',
            'id': '0',
            'method': 'set_tx_notes',
            'params': {
                'notes': notes,
                'txids': tx_ids
            }
        }

    def get_tx_notes(self, tx_ids: list):
        return self.post(self._get_tx_notes(tx_ids)).get('result', {}).get('notes')


    def _get_tx_notes(self, tx_ids:list[str]):
        return {
            'jsonrpc': '2.0',
            'id': '0',
            'method': 'get_tx_notes',
            'params': {
                'txids': tx_ids
            }
        }

    @property
    def headers(self):
        if not self._headers:
            self._headers = {'Content-Type': 'application/json'}
        return self._headers

    def post(self, data):
        try:
            response = requests.post(local_rpc_url(), headers=self.headers, data=json.dumps(data))
            result = response.json()
            if 'error' in result:
                self.logger.error('Error: %s', result['error']['message'])
            return result
        except requests.exceptions.ConnectionError as e:
            self.logger.debug(str(e))
            return {'exception': str(e)}

    def daemon_post(self, data):
        try:
            response = requests.post(daemon_url(), headers=self.headers, data=json.dumps(data))
            result = response.json()
            if 'error' in result:
                self.logger.error('Error: %s', result['error']['message'])
            return result
        except requests.exceptions.ConnectionError as e:
            self.logger.debug(str(e))
            return {'exception': str(e)}
