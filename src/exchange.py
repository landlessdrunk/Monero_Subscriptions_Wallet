import csv
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from src.clients.goldback import scrape as goldback_scrape
from src.clients.xe import scrape as xe_scrape
from src.clients.rpc import RPCClient
from monero_usd_price import median_price, calculate_atomic_units_from_monero, calculate_monero_from_atomic_units

class Exchange():
    _options = None
    ROUNDING = {
        "BTC": 8,
        "LTC": 8,
        "BCH": 8,
        "ADA": 6,
        "DOGE": 8,
        "DOT": 8,  # 10, but rounded to fit well
        "ETH": 8,  # 18, but that does not fit on the window
        "LINK": 8,  # 18, but that does not fit on the window
        "UNI": 8  # 18, but that does not fit on the window
    }

    SYMBOLS = {
        "USD": "$",
        "BTC": "₿",
        "CYN": "¥",
        "EUR": "€",
        "JPY": "¥",
        "GBP": "£",
        "KRW": "₩",
        "INR": "₹",
        "CAD": "$",
        "HKD": "$",
        "AUD": "$"
    }

    US_EXCHANGE = 0
    XMR_TOTAL = 0
    XMR_UNLOCKED = 0
    LAST_REFRESHED = None

    @classmethod
    def convert(cls, to_sym: str, amount: Decimal):
        if to_sym != 'XMR':
            if to_sym == 'XGB':
                sym_value = goldback_scrape()
            else:
                sym_value = xe_scrape(to_sym)
            converted = Decimal(cls.convert_usd(Decimal(amount))) * Decimal(sym_value)
        else:
            converted = Decimal(amount)
        return str(cls._round(converted, to_sym))

    '''
    This function gets the atomic units from the monero exchange.
    We want to be able to convert from one currency to another.
    We do not need to convert to USD if it is already USD, or if it is already XMR.
    '''
    @classmethod
    def to_atomic_units(cls, from_sym: str, amount: Decimal):
        if from_sym != 'XMR':
            if from_sym == 'XGB':
                sym_value = goldback_scrape()
            else:
                sym_value = xe_scrape(from_sym)
            usd_value = Decimal(sym_value) * Decimal(amount)
            xmr_value = usd_value / Decimal(cls.US_EXCHANGE)
        #We don't need to convert to USD if it is already USD
        elif from_sym == 'USD':
            xmr_value = usd_value / Decimal(cls.US_EXCHANGE)
        #We don't need to convert to XMR if it is already XMR
        elif from_sym == 'XMR':
            xmr_value = Decimal(amount)
        return calculate_atomic_units_from_monero(Decimal(xmr_value))

    @classmethod
    def _round(cls, value: Decimal, to_sym: str):
        if to_sym not in cls.ROUNDING.keys():
            final_rounded = format(value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), ",.2f")
        else:
            rounding_spec = Decimal('1.' + ('0' * cls.ROUNDING[to_sym]))
            final_rounded = value.quantize(rounding_spec, rounding=ROUND_HALF_UP)
            final_rounded = format(final_rounded, f",.{str(cls.ROUNDING[to_sym])}f")
        return final_rounded

    @classmethod
    def display(cls, to_sym: str):
        symbol = cls.SYMBOLS.get(to_sym, '')
        return f'{symbol}{cls.convert(to_sym, cls.XMR_UNLOCKED)} ({cls.convert(to_sym, cls.XMR_TOTAL)}) {to_sym.upper()}'

    @classmethod
    def options(cls):
        if cls._options is None:
            options = ["XMR", "BTC", "XGB", "XAU", "XAG", "USD", "EUR", "GBP", "CAD", "AUD", "CNY", "JPY", "KRW", "INR", "HKD", "BRL", "TWD", "CHF", "LTC", "BCH", "ADA", "DOGE", "DOT", "ETH", "LINK", "UNI"]
            with open('data/currency_codes.csv') as codes:
                reader = csv.DictReader(codes)
                for ticker in reader:
                    options.append(ticker['AlphabeticCode'])
                cls._options = options
        return cls._options

    @classmethod
    def convert_usd(cls, xmr_amount: Decimal):
        return round(cls.US_EXCHANGE * xmr_amount, 2)

    @classmethod
    def refresh_prices(cls):
        if not cls.LAST_REFRESHED or cls.LAST_REFRESHED <= (datetime.now() - timedelta(seconds=5*60)):
            cls.US_EXCHANGE = Decimal(median_price())
            cls.XMR_TOTAL = Decimal(calculate_monero_from_atomic_units(RPCClient.get().get_balance()))
            cls.XMR_UNLOCKED = Decimal(calculate_monero_from_atomic_units(RPCClient.get().get_balance('unlocked_balance')))
            cls.LAST_REFRESHED = datetime.now()