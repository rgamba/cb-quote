from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal

from .client import OrderBookClient, ProductsClient
from .order_book import OrderBook, OrderBookEntry, Product


# Cache for the fetched products.
PRODUCTS = []

def create_order_book(currency_pair, **kwargs):
    """
    Create a new OrderBook from the ground up
    for the given currency pair.
    We'll try to fetch the orderbook using the OrderBookClient.
    """
    client = OrderBookClient(currency_pair)
    return create_order_book_from_client(client, **kwargs)

def create_order_book_from_client(client, inversed=False):
    order_book = OrderBook(inversed=inversed)
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

def fetch_all_products():
    """
    Fetch all products using the ProductsClient
    and return a list of Product.
    """
    products = []
    client = ProductsClient()
    for product in client.get_products():
        products.append(Product(
            base_currency=product[0],
            quote_currency=product[1],
        ))
    return products

def find_product(base_currency, quote_currency):
    """
    Try to find a product that matches the base and quoting currencies.

    The response format will be a tuple of:
        (product, is_inversed)
    Where is_inversed will be True if the given currencies don't exactly match
    the product, but they are inversed.
    For example: if the product is BTC-USD and the given currencies are inverted
    like USD-BTC, then is_inversed will return True.
    """
    for product in PRODUCTS:
        if product.matches_currencies(base_currency, quote_currency):
            return (product, False,)
        if product.matches_currencies_inversed(base_currency, quote_currency):
            return (product, True,)
    return (None, None,)

