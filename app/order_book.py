from __future__ import absolute_import, division, print_function, unicode_literals

from collections import namedtuple


OrderBookEntry = namedtuple('OrderBookEntry', ['price', 'size', 'num_orders'])


class OrderBook(object):
    """
    OrderBook represents a collection of bids and
    asks for a given currency pair.
    OrderBook is agnostic to the actual currency pair
    that is being used, that logic must be placed in the
    implementing code.

    """
    def __init__(self):
        # Offers to buy
        self.bids = []
        # Offers to sell
        self.asks = []

    def add_bid(self, entry):
        self.bids.append(entry)

    def add_ask(self, entry):
        self.asks.append(entry)

    def reset(self):
        self.bids = []
        self.asks = []


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
        positions = self._get_order_book_positions(side)
        price = 0
        total_size = 0
        for position in positions:
            current_size = position.size
            if (total_size + current_size) > amount:
                current_size = (amount - total_size)
            total_size += current_size
            price += (current_size * position.price)
            if total_size >= amount:
                break
        return (price, total_size,)

    def quote_inverse(self, price, side):
        positions = self._get_order_book_positions(side)
        amount = 0
        total_price = 0
        for position in positions:
            current_price = position.price
            if (total_price + current_price) > price:
                current_price = (price - total_price)
            total_size += current_size
            if total_price >= price:
                break
        return (total_size, price, )

    def _get_order_book_positions(self, side):
        if side == self.SIDE_BUY:
            return self.order_book.asks
        return self.order_book.bids
