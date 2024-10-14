"""
A class for each individual Subscription object
"""

import time
import logging
import logging.config
from datetime import datetime, timedelta
import monerorequest
from sched import scheduler
from crontab import CronTab
from src.clients.rpc import RPCClient
from src.logging import config as logging_config
from config import send_payments, stagenet, config_file
from src.exchange import Exchange

class Subscription:
    schedul = scheduler(timefunc=time.time)

    def __init__(self, custom_label, sellers_wallet, currency, amount,  payment_id, start_date, schedule, number_of_payments, change_indicator_url=''):
        self.custom_label = custom_label if monerorequest.Check.name(custom_label) else ''
        self.sellers_wallet = sellers_wallet if monerorequest.Check.wallet(wallet_address=sellers_wallet, allow_standard=True, allow_integrated_address=True, allow_subaddress=False, allow_stagenet=stagenet()) else ''
        self.currency = currency if monerorequest.Check.currency(currency) else ''
        self.amount = amount if monerorequest.Check.amount(amount) else ''
        self.payment_id = payment_id if monerorequest.Check.payment_id(payment_id) else monerorequest.make_random_payment_id()
        if monerorequest.Check.start_date(start_date):
            start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%fZ')
        else:
            start_date = datetime.now()
        self.start_date = start_date
        self.schedule = schedule if monerorequest.Check.schedule(schedule) else '0 0 1 * *'
        self.number_of_payments = number_of_payments if monerorequest.Check.number_of_payments(number_of_payments) else 1
        self.change_indicator_url = change_indicator_url if monerorequest.Check.change_indicator_url(change_indicator_url) else ''
        logging.config.dictConfig(logging_config)
        self.logger = logging.getLogger(self.__module__)

    def json_friendly(self):
        json_data = {
            "custom_label": self.custom_label,
            "sellers_wallet": self.sellers_wallet,
            "currency": self.currency,
            "amount": self.amount,
            "payment_id": self.payment_id,
            "start_date":  monerorequest.convert_datetime_object_to_truncated_RFC3339_timestamp_format(self.start_date),
            "schedule": self.schedule,
            "number_of_payments": self.number_of_payments,
            "change_indicator_url": self.change_indicator_url
        }

        attributes = json_data

        return attributes

    def encode(self):
        monero_request = monerorequest.make_monero_payment_request(custom_label=self.custom_label,
                                sellers_wallet=self.sellers_wallet,
                                currency=self.currency,
                                amount=self.amount,
                                payment_id=self.payment_id,
                                start_date=monerorequest.convert_datetime_object_to_truncated_RFC3339_timestamp_format(self.start_date),
                                schedule=self.schedule,
                                number_of_payments=self.number_of_payments,
                                change_indicator_url=self.change_indicator_url,
                                allow_stagenet=stagenet())

        return monero_request

    def relative_payment_time(self):
        if self.start_date < datetime.now():
            relative_time = CronTab(self.schedule).next()
        else:
            delta = self.start_date - datetime.now()
            relative_time = delta.total_seconds()
        self.logger.info('Relative Payment Time %s', relative_time)
        return round(relative_time)

    def next_payment_time(self):
        days = self.relative_payment_time() / 24 / 60 / 60
        remainder_seconds = self.relative_payment_time() % 60
        delta = timedelta(days=days, seconds=remainder_seconds)
        return datetime.now() + delta

    @classmethod
    def decode(cls, code):
        subscription_data_as_json = monerorequest.Decode.monero_payment_request_from_code(monero_payment_request=code)

        return subscription_data_as_json

    def make_payment(self):
        result = False
        self.logger.debug('Entered make_payment function')
        if self.payable():
            if send_payments():
                client = RPCClient.get()
                integrated_address = client.make_integrated_address(self.sellers_wallet, self.payment_id)['integrated_address']
                transfer_result = client.transfer(integrated_address, self.amount)
                client.set_tx_notes([transfer_result['tx_hash']], [self.custom_label])
                self.logger.info('Sent %s XMR', self.amount)
                Exchange.refresh_prices()
                if self.number_of_payments == 1:
                    self.number_of_payments = -1
                elif self.number_of_payments > 1:
                    self.number_of_payments -= 1
                self.logger.debug('Number of Payments Remaining %s', self.number_of_payments)
                config_file.update_subscription(self)
                config_file.write()
                result = transfer_result['amount'] == int(self.amount)
            else:
                self.logger.info('Sending Funds Disabled')
        else:
            self.logger.error('Insuffient Funds Balance: %s', Exchange.XMR_UNLOCKED)

        self.queue()
        return result

    def payable(self):
        if self.number_of_payments > -1:
            Exchange.refresh_prices()
            xmr_to_send = Exchange.to_atomic_units(self.currency, float(self.amount))
            self.logger.info('Able to send funds %s XMR', xmr_to_send)
            return Exchange.to_atomic_units('XMR', Exchange.XMR_UNLOCKED) > xmr_to_send
        else:
            return False

    def queue(self):
        self.schedul.enter(delay=self.relative_payment_time(), priority=1, action=self.make_payment)

    def deschedule(self):
        for event in self.schedul.queue:
            if self.json_friendly() == event.action.__self__.json_friendly():
                self.schedul.cancel(event)
