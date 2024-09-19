import unittest
import time_machine
import vcr
from unittest.mock import patch
from datetime import datetime
from src.subscription import Subscription
from src.exchange import Exchange
from test.factories.subscription import SubscriptionFactory
from test.utils.rpc_server_helper import rpc_server_test
class TestSubscription(unittest.TestCase):
    @time_machine.travel('2024-05-16 12:00:00')
    def test_relative_payment_time(self):
        date_format = '%Y-%m-%d %H:%M:%S'
        subscription = SubscriptionFactory(start_date=datetime.strptime('2024-05-9 12:00:00', date_format).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z')
        self.assertEqual(subscription.relative_payment_time(), 15*24*60*60 + 12*60*60)
        subscription = SubscriptionFactory(start_date=datetime.strptime('2024-06-10 12:00:00', date_format).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z')
        self.assertEqual(subscription.relative_payment_time(), 25*24*60*60)

    def test_json_friendly(self):
        subscription = SubscriptionFactory()
        self.assertEqual(subscription.json_friendly(), {
            'custom_label': subscription.custom_label,
            'sellers_wallet': subscription.sellers_wallet,
            'currency': subscription.currency,
            'amount': subscription.amount,
            'payment_id': subscription.payment_id,
            'start_date': subscription.start_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'Z',
            'schedule': subscription.schedule,
            'number_of_payments': subscription.number_of_payments,
            'change_indicator_url': subscription.change_indicator_url
        })

    def test_encode(self):
        with patch('src.subscription.stagenet', return_value=False):
            subscription = SubscriptionFactory(
                custom_label='test_label',
                sellers_wallet='4At3X5rvVypTofgmueN9s9QtrzdRe5BueFrskAZi17BoYbhzysozzoMFB6zWnTKdGC6AxEAbEE5czFR3hbEEJbsm4hCeX2S',
                currency='USD',
                amount='10',
                payment_id='abcdef1234567890',
                start_date=datetime.strptime('2024-05-10 12:00:00', '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                schedule='0 0 0 * MON',
                number_of_payments=10,
                change_indicator_url=''
            )
            self.assertEqual(subscription.encode(), 'monero-request:2:H4sIAAAAAAACAy1OXU+DQBD8K+Qem9bcUaDCG61gotHEtmrty+XglkKEu+Y+VDD9796ZJpvszsxOZn4RG6QVBmWIYDRHdcvECWgneFczIxW1qneaV6xSIOrRodfd3T+hjRxozyrwLwa0uYI5EnaoQFHZ0DMbBxBGo4zgOboi2nHnYFXNoSHhMoqT1W3q43XdArc9OBUHOCDBLJh5GvoelKbfzG3fNcrN8hCrr7fxvJfNabDwnOr0xaiJbyFeWyiV/syPHVmt5UfVTqOW0ySfynUyvYv9I7/fJPlPkVdFEddTuV227nqo9BC1GziEOx9pmDKUM+O7hDiMFjheELwnYYaxmxuM8RFd/gDIow3zQAEAAA==')

    def test_decode(self):
        with patch('src.subscription.stagenet', return_value=False):
            subscription = SubscriptionFactory()
            sub_copy = Subscription(**Subscription.decode(subscription.encode()))
        self.assertEqual(subscription.custom_label, sub_copy.custom_label)
        self.assertEqual(subscription.sellers_wallet, sub_copy.sellers_wallet)
        self.assertEqual(subscription.currency, sub_copy.currency)
        self.assertEqual(subscription.amount, sub_copy.amount)
        self.assertEqual(subscription.payment_id, sub_copy.payment_id)
        self.assertEqual(subscription.start_date, sub_copy.start_date)
        self.assertEqual(subscription.schedule, sub_copy.schedule)
        self.assertEqual(subscription.number_of_payments, sub_copy.number_of_payments)
        self.assertEqual(subscription.change_indicator_url, sub_copy.change_indicator_url)

    def test_make_payment(self):
        with vcr.use_cassette('test/fixtures/cassettes/make_payment.yaml'):
            with patch('src.subscription.send_payments', return_value=True):
                subscription = SubscriptionFactory(payment_id='c2c9f284c33a4903', sellers_wallet='59fhPNhFLEx3zP16ZAPaeHXsPoNczVaGo245CgDSW9WpiMxvP1N7WdxX1RA4vob6ABGGBxUgjcCN2LjeSGPiH8AEKpAMFKC')
                nop = subscription.number_of_payments
                self.assertEqual(subscription.make_payment(), True)
                self.assertEqual(subscription.number_of_payments, nop - 1)

    def test_payable(self):
        with vcr.use_cassette('test/fixtures/cassettes/payable.yaml'):
            with patch('src.exchange.Exchange.refresh_prices', return_value=True):
                Exchange.XMR_TOTAL = 1000
                subscription = SubscriptionFactory(number_of_payments=1)
                self.assertEqual(subscription.payable(), True)
                invalid_subscription = SubscriptionFactory(number_of_payments=-1)
                self.assertEqual(invalid_subscription.payable(), False)

if __name__ == '__main__':
    unittest.main()
