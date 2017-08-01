from __future__ import absolute_import, division, print_function, unicode_literals

import requests


class ClientBase(object):
    """
    A base client for all the other clients.

    """
    def validate_response(self, response):
        if response.status_code == 404:
            raise ValueError("Invalid currency pair provided")
        if response.status_code != 200:
            raise Exception("Service unavailable")

    def make_request(self):
        response = requests.get(self.get_request_url())
        self.validate_response(response)
        return response.json()

    def refresh(self):
        self.make_request()


class OrderBookClient(ClientBase):
    """
    Fetches all the bids and asks right from coinbase.

    """
    ORDER_BOOK_URL = "https://api.gdax.com/products/{}/book?level=2"

    def __init__(self, currency_pair):
        self.currency_pair = currency_pair
        self.response = self.make_request()

    def get_request_url(self):
        return self.ORDER_BOOK_URL.format(self.currency_pair)

    def get_asks(self):
        for ask in self.response['asks']:
            yield ask

    def get_bids(self):
        for bid in self.response['bids']:
            yield bid


class ProductsClient(ClientBase):
    PRODUCTS_URL = "https://api.gdax.com/products/"

    def __init__(self):
        self.response = self.make_request()

    def get_request_url(self):
        return self.PRODUCTS_URL

    def get_products(self):
        for product in self.response:
            yield (product['base_currency'], product['quote_currency'],)
