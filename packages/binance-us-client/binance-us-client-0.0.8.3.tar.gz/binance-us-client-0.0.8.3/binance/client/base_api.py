"""
Binance.US API
https://docs.binance.us/?python#request-for-quote
"""

import hashlib
import hmac
import urllib.parse

import requests

API_URL = "https://api.binance.us"
ACCOUNT_PATH = "/api/v3/account"
PRICE_PATH= '/api/v3/ticker/price'
QUOTE_PATH = "/sapi/v1/otc/quotes"
PLACE_ORDER_PATH = "/sapi/v1/otc/orders"
ORDER_PATH = "/sapi/v1/otc/orders"
HISTORICAL_TRADES = "/api/v3/historicalTrades"


# get binanceus signature
def get_binanceus_signature(data, secret):
    """
    gen signature
    """
    postdata = urllib.parse.urlencode(data)
    message = postdata.encode()
    byte_key = bytes(secret, 'UTF-8')
    mac = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
    return mac


def binanceus_get(uri_path, data, api_key, api_sec):
    """
    binance get request
    """
    headers = {}
    headers['X-MBX-APIKEY'] = api_key
    signature = get_binanceus_signature(data, api_sec)
    params={
        **data,
        "signature": signature,
    }
    resp = requests.get((API_URL + uri_path), params=params, headers=headers)
    return resp.json()


def binanceus_get_without_signature(uri_path, data, api_key):
    """
    binance get request
    """
    headers = {}
    headers['X-MBX-APIKEY'] = api_key
    params={
        **data,
    }
    resp = requests.get((API_URL + uri_path), params=params, headers=headers)
    return resp.json()


# Attaches auth headers and returns results of a POST request
def binanceus_post(uri_path, data, api_key, api_sec):
    """
    binance post request
    """
    headers = {}
    headers['X-MBX-APIKEY'] = api_key
    signature = get_binanceus_signature(data, api_sec)
    payload = {
        **data,
        "signature": signature,
    }
    resp = requests.post((API_URL + uri_path), headers=headers, data=payload)
    return resp.json()
