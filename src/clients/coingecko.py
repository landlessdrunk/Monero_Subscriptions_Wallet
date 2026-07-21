from pycoingecko import CoinGeckoAPI

def get_price(currency):
    cg = CoinGeckoAPI()
    return cg.get_price(ids='monero', vs_currencies=currency.lower()).get('monero', {}).get(currency.lower(), 0)