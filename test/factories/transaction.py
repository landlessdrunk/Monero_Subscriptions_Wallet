import factory
import random
from monerorequest import make_random_payment_id
from datetime import datetime
from src.transaction import Transaction

def generate_address(allow_standard=True, allow_stagenet=True, allow_subaddress=True):
    allowed_types = []
    standard = 1
    stagenet = 2
    standard_subaddress = 3
    stagenet_subaddress = 4
    if allow_standard:
        allowed_types.append(standard)
        if allow_subaddress:
            allowed_types.append(standard_subaddress)
    if allow_stagenet:
        allowed_types.append(stagenet)
        if allow_subaddress:
            allowed_types.append(stagenet_subaddress)

    picked_type = random.choice(allowed_types)

    valid_characters = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    match picked_type:
        case 1:
            first_character = '4'
        case 2:
            first_character = '8'
        case 3:
            first_character = '5'
        case 4:
            first_character = '7'

    match picked_type:
        case 1 | 2:
            length = 106
        case 3 | 4:
            length = 95

    address = first_character
    for i in range(length-1):
        address += random.choice(valid_characters)

    return address

#8855d1401047668d8cf1892d0e7e56f98ccfced58ff9370098178f6f19d12ec5
def generate_txid():
    valid_characters = '123456789abcdefghijkmnopqrstuvwxyz'
    length = 75
    txid = ''
    for i in range(length):
        txid += random.choice(valid_characters)
    return txid

def now_timestamp():
    return datetime.now().timestamp()

class TransactionFactory(factory.Factory):
    class Meta:
        model = Transaction

    address = factory.LazyFunction(generate_address)
    amount = 10
    double_spend_seen = False
    fee = 1
    height = 1000
    locked = False
    note = ''
    payment_id = factory.LazyFunction(make_random_payment_id)
    timestamp = factory.LazyFunction(now_timestamp)
    txid = factory.LazyFunction(generate_txid)
    type = 'in'
    unlock_time = 12345
    direction = 'in'
    subaddr_index = {'major': 0, 'minor': 0}
    subaddr_indices = [{'major': 0, 'minor': 0}]
    suggested_confirmations_threshold = 0
    amounts = [1]
    destinations = [{'address': '', 'amount': 0}]
    confirmations = 0