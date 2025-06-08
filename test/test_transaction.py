import unittest
from test.factories.transaction import TransactionFactory
from test.factories.subscription import SubscriptionFactory
from test.utils.config import config_mock

class TestTransaction(unittest.TestCase):
    def test_transaction(self):
        with config_mock() as cfg:
            transaction = TransactionFactory()
            subscription = SubscriptionFactory(payment_id=transaction.payment_id)
            cfg.add_subscription(subscription)
            self.assertEqual(transaction.subscription(), subscription.json_friendly())