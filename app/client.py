from __future__ import absolute_import, division, print_function, unicode_literals

import requests


class OrderBookClient(object):
    """
    Fetches all the bids and asks right from coinbase.

    """
    ORDER_BOOK_URL = "https://api.gdax.com/products/{}/book?level=2"

    def __init__(self, currency_pair):
        self.currency_pair = currency_pair
        self.response = self.make_request()

    def make_request(self):
        response = requests.get(self._get_request_url())
        self.validate_response(response)
        return response.json()

    def validate_response(self, response):
        if response.status_code == 404:
            raise ValueError("Invalid currency pair provided")
        if response.status_code != 200:
            raise Exception("Service unavailable")

    def _get_request_url(self):
        return self.ORDER_BOOK_URL.format(self.currency_pair)

    def refresh(self):
        self.make_request()

    def get_asks(self):
        for ask in self.response['asks']:
            yield ask

    def get_bids(self):
        for bid in self.response['bids']:
            yield bid

