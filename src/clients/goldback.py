import requests
from decimal import Decimal

def scrape():
    url = 'https://gbcapi.gbdomainapi.xyz/GBCalculatorSettingsAPICSharpProdV1/CurrencyRates'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Ocp-Apim-Subscription-Key': '14b8cd90c80149a888d9986e22dbfb95'
    }
    api_json = requests.get(url, headers=headers).json()
    # Find the gb_average_exchange_rate constant's value
    usd_cost_for_one_goldback = api_json.get('quotes', {}).get('USDUSD')
    dollar_value_in_goldbacks = Decimal(1) / Decimal(usd_cost_for_one_goldback)
    return dollar_value_in_goldbacks
