from __future__ import absolute_import, division, print_function, unicode_literals

from collections import namedtuple


OrderBookEntry = namedtuple('OrderBookEntry', ['price', 'size', 'num_orders'])


class Product(object):
    """
    A product represents a currency pair in the coinbase
    order book API.
    """
    def __init__(self, base_currency, quote_currency):
        self.base_currency = base_currency
        self.quote_currency = quote_currency

    def matches_currencies(self, cur1, cur2):
        return self.base_currency == cur1 and self.quote_currency == cur2

    def matches_currencies_inversed(self, cur1, cur2):
        return self.base_currency == cur2 and self.quote_currency == cur1

    def __str__(self):
        return "{}-{}".format(self.base_currency, self.quote_currency)


class OrderBook(object):
    """
    OrderBook represents a collection of bids and
    asks for a given currency pair.
    OrderBook is agnostic to the actual currency pair
    that is being used, that logic must be placed in the
    implementing code.

    """
    def __init__(self, inversed=False):
        # Offers to buy - Highest price first.
        self.bids = []
        # Offers to sell - Lowest price first.
        self.asks = []
        self.inversed = inversed

    def add_bid(self, entry):
        self.bids.append(entry)

    def add_ask(self, entry):
        self.asks.append(entry)

    def get_bids_iter(self):
        self._sort_bids()
        for bid in self.bids:
            yield bid

    def get_asks_iter(self):
        self._sort_asks()
        for ask in self.asks:
            yield ask

    def _sort_bids(self):
        self.bids = sorted(self.bids, key=lambda x: x.price, reverse=True)

    def _sort_asks(self):
        self.asks = sorted(self.asks, key=lambda x: x.price)

    def reset(self):
        self.bids = []
        self.asks = []


class NotEnoughBookOrders(Exception):
    pass


class QuoteGenerator(object):
    """
    A quote generator will be linked to a specific
    OrderBook and will traverse positions in order
    to make quotes.
    This implementation is also currency-pair agnostic.

    """
    SIDE_BUY = 'buy'
    SIDE_SELL = 'sell'

    def __init__(self, order_book):
        self.order_book = order_book

    def quote_sell(self, amount):
        return self.quote(amount, self.SIDE_SELL)

    def quote_buy(self, amount):
        return self.quote(amount, self.SIDE_BUY)

    def quote(self, amount, side):
        if self.order_book.inversed:
            return self._quote_inverse(amount, side)
        return self._quote(amount, side)

    def _quote(self, amount, side):
        entries_iter = self._get_order_book_entries_iter(side)
        price = 0
        total_size = 0
        for entry in entries_iter():
            current_size = self._get_entry_total_size(entry)
            if (total_size + current_size) > amount:
                current_size = (amount - total_size)
            total_size += current_size
            price += (current_size * entry.price)
            if total_size >= amount:
                break
        if total_size < amount:
            raise NotEnoughBookOrders("Unable to complete quote")
        return (price, total_size,)

    def _get_entry_total_size(self, entry):
        return entry.size * entry.num_orders

    def _quote_inverse(self, price, side):
        entries_iter = self._get_order_book_entries_iter(side)
        amount = 0
        total_price = 0
        for entry in entries_iter():
            current_price = self._get_entry_total_price(entry)
            current_amount = self._get_entry_total_size(entry)
            if (total_price + current_price) > price:
                price_remaining = price - total_price
                current_amount = (price_remaining * current_amount) / current_price
            else:
                price_remaining = 0
            amount += current_amount
            total_price += (price_remaining if price_remaining else current_price)
            if total_price >= price:
                break
        if total_price < price:
            raise NotEnoughBookOrders("Unable to complete quote")
        return (amount, price,)

    def _get_entry_total_price(self, entry):
        return entry.price * entry.size * entry.num_orders

    def _get_order_book_entries_iter(self, side):
        if side == self.SIDE_BUY:
            return self.order_book.get_asks_iter
        return self.order_book.get_bids_iter
