from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal

from .client import OrderBookClient
from .order_book import OrderBook, OrderBookEntry


def create_order_book(currency_pair):
    client = OrderBookClient(currency_pair)
    return create_order_book_from_client(client)

def create_order_book_from_client(client):
    order_book = OrderBook()
    for ask in client.get_asks():
        order_book.add_ask(parse_to_order_book_entry(ask))
    for bid in client.get_bids():
        order_book.add_bid(parse_to_order_book_entry(bid))
    return order_book

def parse_to_order_book_entry(position):
    return OrderBookEntry(
        price=Decimal(position[0]),
        size=Decimal(position[1]),
        num_orders=position[2],
    )
