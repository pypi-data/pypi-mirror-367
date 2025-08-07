"""
Price API
"""

from decimal import Decimal

import requests

from binance.client import API_URL, PRICE_PATH
from binance.exception import SymbolException


def get_symbol_price(symbol: str) -> Decimal:
    """
    推荐使用 get_coin_price
    :param symbol: symbol
    :param process_error: 是否需要处理错误
    :return: price(decimal.Decimal)
    """
    resp = requests.get(f'{API_URL}{PRICE_PATH}?symbol={symbol}')
    result_json = resp.json()
    if not resp.ok:
        result_json['symbol'] = symbol
        raise SymbolException(result_json)
    return Decimal(result_json['price'])


def get_coin_price(coin: str) -> Decimal:
    """
    USDT USD 价格为 1
    :param coin: coin
    :return: price(decimal.Decimal)
    """
    if coin in ('USDT', 'USD'):
        return Decimal(1)
    return get_symbol_price(f'{coin}USDT')


def batch_get_symbol_price(symbols: list[str]) -> dict:
    """
    :param symbols: symbol list
    :return: symbol -> price dict
    """
    return dict(zip(symbols, [get_symbol_price(symbol) for symbol in symbols]))


def batch_get_coin_price(coins: list[str]) -> dict:
    """
    :param coins: coin list
    :return: coin -> pice dict
    """
    return dict(zip(coins, [get_coin_price(coin) for coin in coins]))


def get_coin_price_with_default(coin: str, default: Decimal = Decimal(1)) -> Decimal:
    """
    get coin price with default value
    :param coin: target crypto
    :param default: default price，1
    :return:
    """
    try:
        return get_coin_price(coin)
    except SymbolException as sex:
        print(f'get {coin} price error:', sex)
        return default


if __name__ == '__main__':
    print(get_symbol_price('BTCUSDT'))
    print(get_coin_price('BTC'))
    print(batch_get_symbol_price(['BTCUSDT', 'ETHUSD']))
    print(batch_get_coin_price(['BTC', 'ETH']))
    print(get_coin_price_with_default('JUP'))
