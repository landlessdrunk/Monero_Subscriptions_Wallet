"""
Configuration File for Monero Subscriptions Wallet
Contains global settings and variables used across the application.

Using this for fiat currencies (other than the hard-coded ones): https://github.com/datasets/currency-codes

Exchange rates scraped from XE.com
"""

import os
import platform

import monerorequest
import requests
from io import StringIO
import csv
import monero_usd_price
from lxml import html
from decimal import Decimal, ROUND_HALF_UP
from configparser import ConfigParser
import re
import json

SHOULD_CENTER_WINDOW = True

NODE_URL = 'xmr-node.cakewallet.com:18081'

# This sets the defaults for config.ini when initially created. It does NOT overwrite an existing config.ini
config_options = {
    'rpc': {
        'rpc_bind_port': 18088,
        'rpc_username': 'monero',
        'rpc_password': 'monero',
        'rpc': True,
        'local_rpc_url': 'http://127.0.0.1:18088/json_rpc',
        'node_url': NODE_URL,
        'daemon_url': f'{NODE_URL}/json_rpc',
        'wallet_dir': 'wallets',
        'stagenet': False
    },
    'subscriptions': {
        'subscriptions': [],
        'default_currency': 'USD',
        'secondary_currency': 'XMR'
    },
    'other': {
        'is_first_launch': True,
        'send_payments': True
    }

}

class ConfigFile():
    def __init__(self, path='./config.ini'):
        self._config = ConfigParser()
        self._path = path
        self._observers = []

        if self.exists():
            self.read()
        else:
            self.create()

    def read(self):
        options = {}
        if self.exists():
            options = self._config.read(self._path)
        return options

    def write(self):
        with open(self._path, 'w') as conf:
            self._config.write(conf)

    def exists(self):
        return os.path.isfile(self._path)

    def set_defaults(self):
        for section, options in config_options.items():
            for option, value in options.items():
                self._config['DEFAULT'][option] = str(value)

    def set(self, section, option, value):
        self._config[section][option] = value

    def get(self, section, option):
        return self._config.get(section, option)

    def create(self):
        self.set_defaults()
        for section in config_options.keys():
            self._config[section] = {}
        self.write()

    def add_subscription(self, subscription):
        subs = json.loads(self.get('subscriptions', 'subscriptions'))
        subs.append(subscription.json_friendly())
        self.set('subscriptions', 'subscriptions', json.dumps(subs))
        self.write()
        return True

    def remove_subscription(self, subscription):
        subs = [sub for sub in json.loads(self.get('subscriptions', 'subscriptions')) if sub != subscription.json_friendly()]
        self.set('subscriptions', 'subscriptions', json.dumps(subs))
        self.write()
        return True

    def update_subscription(self, subscription):
        update_subs = [
            sub for sub in json.loads(self.get('subscriptions', 'subscriptions'))
                if sub.get('payment_id') == subscription.payment_id and
                   sub.get('sellers_wallet') == subscription.sellers_wallet
        ]
        same_subs = [
            sub for sub in json.loads(self.get('subscriptions', 'subscriptions'))
                if sub.get('payment_id') != subscription.payment_id or
                   sub.get('sellers_wallet') != subscription.sellers_wallet
        ]
        updated_subs = []
        for sub in update_subs:
            updated_subs.append(subscription.json_friendly())
        self.set('subscriptions', 'subscriptions', json.dumps(same_subs + updated_subs))
        return True

config_file = ConfigFile('./config.ini')

def variable_value(section, option):
    value = None
    # Get From Config File
    if value is None:
        value = config_file.get(section, option)

    # Get From Environment
    if value is None:
        value = os.environ.get(option.upper())

    # Get Default Value
    if value is None:
        value = config_options[section][option]

    return value


# Set CLI Options as importable variables
for section, options in config_options.items():
    for option in options.keys():
        exec(f'{option} = lambda: variable_value("{section}", "{option}")')


def get_platform(os=platform.system()):
    os = os.lower()
    if os == 'darwin':
        return 'Mac'
    if os == 'windows':
        return 'Windows'
    else:
        return 'Linux'


platform = get_platform()


# TODO: Adjust the sorting of these at some point.

SHOW_DEFAULT_CURRENCY = True

monero_orange = '#ff6600'
ui_overall_background = '#1D1D1D'

CURRENT_PAYMENT_REQUEST = ''
CURRENT_SEND_AMOUNT = ''
CURRENT_SEND_CURRENCY = ''
SELECTED_SUBSCRIPTION = ''

CURRENT_CREATE_PAYMENT_REQUEST_CURRENCY = ''

has_seen_welcome = False

transactions = []

tx1 = {"direction": "out",
       "amount": "4.12",
       "date": "2017-08-27",
       "payment_id": "Mullvad VPN",  #monerorequest.make_random_payment_id(),  # Use this to get subscription name if available
       "paid_to": "4sakjhgfhjkkhgfdsghjkgfdhjkhgfdhjkgfdsghjkhgfdhjkjhgfdghjkhgfdhjkhgfdghjgfdhjgfdhjgfd"
       #"selected_currency_value_at_time"  # not sure how we would keep this data??? would be cool to have though.
       }

tx2 = {"direction": "in",
       "amount": "0.121212121212",
       "date": "2018-08-25",
       "payment_id": "This Is A Reasonable Long Title That Gets Cut Off This Is A Reasonable Title This Is A Reasonable Title This Is A Reasonable Title", #monerorequest.make_random_payment_id(),  # Use this to get subscription name if available
       "paid_to": "4sakjhgfhjkkhgfdsghjkgfdhjkhgfdhjkgfdsghjkhgfdhjkjhgfdghjkhgfadffffgfdhjgfdhjgfd"
       #"selected_currency_value_at_time": # not sure how we would keep this data??? would be cool to have though.
       }

tx3 = {"direction": "in",
       "amount": "0.12",
       "date": "2019-08-21",
       "payment_id": "My Phone Bill", #"#monerorequest.make_random_payment_id(),  # Use this to get subscription name if available
       "paid_to": "4sakjhgfhjkkhgfdsghjkgfdhjkhgfdhjkgfdsghjkhgfdhjkjhgfdghjkhgfdhdfhjgfdhjgfdhjgfd"
       #"selected_currency_value_at_time"  # not sure how we would keep this data??? would be cool to have though.
       }

tx4 = {"direction": "out",
       "amount": "44",
       "date": "2020-08-18",
       "payment_id": "Other stuff", #"#monerorequest.make_random_payment_id(),  # Use this to get subscription name if available
       "paid_to": "4sakjhgfhjkkhgfdsghjkgfdhjkhgfdhjkgfdsghjkhgfdhjkjhgfdghjkhgfdhdfhjgfdhjgfdhjgfd"
       #"selected_currency_value_at_time"  # not sure how we would keep this data??? would be cool to have though.
       }

tx5 = {"direction": "out",
       "amount": "0.121212121212",
       "date": "2020-08-10",
       "payment_id": "Calming Dog Beds Cat Cave Bed with - Hooded Cover, Anti-Anxiety SoftFEFEFEFEFEFEFEFFEFEFEFEFEFFEFEFEF", #"#monerorequest.make_random_payment_id(),  # Use this to get subscription name if available
       "paid_to": "4sakjhgfhjkkhgfdsghjkgfdhjkhgfdhjkgfdsghjkhgfdhjkjhgfdghjkhgfdhdfhjgfdhjgfdhjgfd"
       #"selected_currency_value_at_time"  # not sure how we would keep this data??? would be cool to have though.
       }

tx6 = {"direction": "in",
       "amount": "15.1212",
       "date": "2021-08-03",
       "payment_id": "Calming Dog Beds Cat Cave Bed with - Hooded Cover, Anti-Anxiety Soft Plush Faux!", #"#monerorequest.make_random_payment_id(),  # Use this to get subscription name if available
       "paid_to": "4sakjhgfhjkkhgfdsghjkgfdhjkhgfdhjkgfdsghjkhgfdhjkjhgfdghjkhgfdhdfhjgfdhjgfdhjgfd"
       #"selected_currency_value_at_time"  # not sure how we would keep this data??? would be cool to have though.
       }

tx7 = {"direction": "in",
       "amount": "4444.121212121212",
       "date": "2022-05-21",
       "payment_id": "Other stuff 4 sdfgjksdfgjksdfgjkdfsgjkhdfkjhdfgkjhdfgskjhdfgkjhdfsjkhdfkhjdfskjhdfskjhsdfkjhskjfhsdfgkj", #"#monerorequest.make_random_payment_id(),  # Use this to get subscription name if available
       "paid_to": "4sakjhgfhjkkhgfdsghjkgfdhjkhgfdhjkgfdsghjkhgfdhjkjhgfdghjkhgfdhdfhjgfdhjgfdhjgfd"
       #"selected_currency_value_at_time"  # not sure how we would keep this data??? would be cool to have though.
       }

transactions.append(tx1)
transactions.append(tx2)
transactions.append(tx3)
transactions.append(tx4)
transactions.append(tx5)
transactions.append(tx6)
transactions.append(tx7)
