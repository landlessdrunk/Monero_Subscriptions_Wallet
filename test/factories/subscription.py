import factory
from monerorequest import make_random_payment_id
from datetime import datetime
from src.subscription import Subscription

class SubscriptionFactory(factory.Factory):
    class Meta:
        model = Subscription

    custom_label = factory.Sequence(lambda n: 'Subscription %s' % n)
    sellers_wallet = '4At3X5rvVypTofgmueN9s9QtrzdRe5BueFrskAZi17BoYbhzysozzoMFB6zWnTKdGC6AxEAbEE5czFR3hbEEJbsm4hCeX2S'
    currency = 'USD'
    amount = '10'
    payment_id = make_random_payment_id()
    start_date = factory.LazyAttribute(lambda _: datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z')
    schedule = '0 0 1 * *'
    number_of_payments = 10