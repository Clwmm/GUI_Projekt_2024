from datetime import datetime, timedelta
import pandas as pd
import time as time
from pycoingecko import CoinGeckoAPI

print("Starting CoinGeckoAPI instance...")
cg = CoinGeckoAPI()
print("\tSuccessfully created CoinGeckoAPI instance!")

try:
    print("Connecting to CoinGeckoAPI...")
    cg.ping()
    print("\tSuccessfully connected to CoinGeckoAPI!")
except Exception as e:
    print("Connetction Error: ", e)

def getPrice(coin_id, vs_currency):
    from_ = coin_id
    if from_ == "btc":
        from_ = "bitcoin"
    if from_ == "eth":
        from_ = "ethereum"
    price = cg.get_price(ids=from_, vs_currencies=vs_currency)
    price = next(iter(next(iter(price.values())).values()))

    return price

def getPairPriceChart(coin_id, vs_currency):
    current_date = datetime.now()

    from_ = coin_id
    if from_ == "btc":
        from_ = "bitcoin"
    if from_ == "eth":
        from_ = "ethereum"

    date_one_year_ago = current_date - timedelta(days=363)

    current_date_str = current_date.strftime("%Y-%m-%d")
    date_one_year_ago_str = date_one_year_ago.strftime("%Y-%m-%d")

    from_timestamp = int(time.mktime(time.strptime(date_one_year_ago_str, "%Y-%m-%d")))
    to_timestamp = int(time.mktime(time.strptime(current_date_str, "%Y-%m-%d")))

    try:
        data = cg.get_coin_market_chart_range_by_id(
            id=from_,
            vs_currency=vs_currency,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
        )
    except Exception as e:
        print(e)

    chart_data = data['prices']
    transformed_data = [
        {"time": datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d'), "value": value}
        for timestamp, value in chart_data
    ]
    return transformed_data


def getBtcUsdtPriceChart():
    coin_id = 'bitcoin'
    vs_currency = 'usd' # usd = usdt
    current_date = datetime.now()

    date_one_year_ago = current_date - timedelta(days=363)

    current_date_str = current_date.strftime("%Y-%m-%d")
    date_one_year_ago_str = date_one_year_ago.strftime("%Y-%m-%d")

    from_timestamp = int(time.mktime(time.strptime(date_one_year_ago_str, "%Y-%m-%d")))
    to_timestamp = int(time.mktime(time.strptime(current_date_str, "%Y-%m-%d")))

    try:
        data = cg.get_coin_market_chart_range_by_id(
            id=coin_id,
            vs_currency=vs_currency,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
        )
    except Exception as e:
        print(e)

    chart_data = data['prices']
    transformed_data = [
        {"time": datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d'), "value": value}
        for timestamp, value in chart_data
    ]
    return transformed_data
