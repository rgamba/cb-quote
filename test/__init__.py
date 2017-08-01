import unittest

from app.order_book import OrderBook, OrderBookEntry, QuoteGenerator, Product
from app import lib


class QuoteGeneratorTestCase(unittest.TestCase):
    def setUp(self):
        self.books = {}

    def _create_order_book(self, currency_pair, inversed=False):
        self.books[currency_pair] = OrderBook(inversed=inversed)
        return self.books[currency_pair]

    def test_buy_btc_to_usd(self):
        book = self._create_order_book('BTC-USD')
        book.add_ask(OrderBookEntry(price=100, size=1, num_orders=1))
        book.add_ask(OrderBookEntry(price=200, size=1, num_orders=1))
        book.add_ask(OrderBookEntry(price=300, size=1, num_orders=1))

        quoter = QuoteGenerator(book)

        price, amount = quoter.quote_buy(1)
        self.assertEquals(price, 100)
        self.assertEquals(amount, 1)
        price, amount = quoter.quote_buy(1.5)
        self.assertEquals(price, 200)
        price, amount = quoter.quote_buy(1.7)
        self.assertEquals(price, 240)

    def test_buy_btc_to_usd_with_multiple_num_orders(self):
        book = self._create_order_book('BTC-USD')
        book.add_ask(OrderBookEntry(price=100, size=1, num_orders=2))
        book.add_ask(OrderBookEntry(price=200, size=1, num_orders=2))
        book.add_ask(OrderBookEntry(price=300, size=1, num_orders=2))

        quoter = QuoteGenerator(book)

        price, amount = quoter.quote_buy(1)
        self.assertEquals(price, 100)
        self.assertEquals(amount, 1)
        price, amount = quoter.quote_buy(1.5)
        self.assertEquals(price, 150)
        price, amount = quoter.quote_buy(2)
        self.assertEquals(price, 200)
        price, amount = quoter.quote_buy(4)
        self.assertEquals(price, 600)

    def test_sell_btc_to_usd(self):
        book = self._create_order_book('BTC-USD')
        book.add_bid(OrderBookEntry(price=300, size=1, num_orders=1))
        book.add_bid(OrderBookEntry(price=200, size=1, num_orders=1))
        book.add_bid(OrderBookEntry(price=100, size=1, num_orders=1))

        quoter = QuoteGenerator(book)

        price, amount = quoter.quote_sell(1)
        self.assertEquals(price, 300)
        self.assertEquals(amount, 1)
        price, amount = quoter.quote_sell(1.5)
        self.assertEquals(price, 400)
        price, amount = quoter.quote_sell(1.7)
        self.assertEquals(price, 440)

    def test_buy_btc_to_usd_when_book_can_not_fullfill(self):
        book = self._create_order_book('BTC-USD')
        book.add_bid(OrderBookEntry(price=300, size=1, num_orders=1))
        quoter = QuoteGenerator(book)

        with self.assertRaises(Exception):
            quoter.quote_buy(2)

    def test_buy_btc_to_usd_inverse(self):
        book = self._create_order_book('BTC-USD', True)
        book.add_ask(OrderBookEntry(price=100, size=1, num_orders=1))
        book.add_ask(OrderBookEntry(price=200, size=1, num_orders=1))
        book.add_ask(OrderBookEntry(price=300, size=1, num_orders=1))

        quoter = QuoteGenerator(book)
        amount, price = quoter.quote_buy(100)
        self.assertEquals(amount, 1)
        self.assertEquals(price, 100)
        amount, price = quoter.quote_buy(150)
        self.assertEquals(amount, 1.25)
        amount, price = quoter.quote_buy(200)
        self.assertEquals(amount, 1.5)
        amount, price = quoter.quote_buy(350)
        self.assertEquals("{:.2f}".format(amount), '2.17')

    def test_buy_btc_to_usd_inverse_half_orders(self):
        book = self._create_order_book('BTC-USD', True)
        book.add_ask(OrderBookEntry(price=100, size=.5, num_orders=1))
        book.add_ask(OrderBookEntry(price=200, size=.5, num_orders=1))
        book.add_ask(OrderBookEntry(price=300, size=.5, num_orders=1))

        quoter = QuoteGenerator(book)
        amount, price = quoter.quote_buy(100)
        self.assertEquals(amount, .75)
        self.assertEquals(price, 100)
        amount, price = quoter.quote_buy(300)
        self.assertEquals(amount, 1.5)

    def test_buy_btc_to_usd_inverse_half_orders_multi_number(self):
        book = self._create_order_book('BTC-USD', True)
        book.add_ask(OrderBookEntry(price=100, size=.5, num_orders=2))
        book.add_ask(OrderBookEntry(price=200, size=.5, num_orders=2))

        quoter = QuoteGenerator(book)
        amount, price = quoter.quote_buy(100)
        self.assertEquals(amount, 1)
        amount, price = quoter.quote_buy(300)
        self.assertEquals(amount, 2)

    def test_buy_btc_to_usd_inverse_when_multiple_num_orders(self):
        book = self._create_order_book('BTC-USD', True)
        book.add_ask(OrderBookEntry(price=100, size=1, num_orders=2))
        book.add_ask(OrderBookEntry(price=200, size=1, num_orders=1))
        book.add_ask(OrderBookEntry(price=300, size=1, num_orders=1))

        quoter = QuoteGenerator(book)
        amount, price = quoter.quote_buy(200)
        self.assertEquals(amount, 2)
        amount, price = quoter.quote_buy(300)
        self.assertEquals(amount, 2.5)


class ProductsTestCase(unittest.TestCase):
    def test_matches_currencies_ok(self):
        p1 = Product(base_currency='USD', quote_currency='BTC')
        self.assertTrue(p1.matches_currencies('USD', 'BTC'))
        self.assertFalse(p1.matches_currencies('BTC', 'USD'))

    def test_matches_currencies_inversed(self):
        p1 = Product(base_currency='USD', quote_currency='BTC')
        self.assertFalse(p1.matches_currencies('BTC', 'USD'))
        self.assertTrue(p1.matches_currencies_inversed('BTC', 'USD'))


class LibFunctionsTestCase(unittest.TestCase):
    def setUp(self):
        lib.PRODUCTS = [
            Product(base_currency='BTC', quote_currency='USD'),
            Product(base_currency='LTC', quote_currency='USD'),
        ]

    def tearDown(self):
        lib.PRODUCTS = []

    def test_find_product_regular(self):
        product, inversed = lib.find_product('BTC', 'USD')
        self.assertIsNotNone(product)
        self.assertEquals(str(product), 'BTC-USD')
        self.assertEquals(inversed, False)

    def test_find_product_inversed(self):
        product, inversed = lib.find_product('USD', 'BTC')
        self.assertIsNotNone(product)
        self.assertEquals(str(product), 'BTC-USD')
        self.assertEquals(inversed, True)

    def test_find_product_when_doesnt_exist(self):
        product, inversed = lib.find_product('invalid', 'USD')
        self.assertIsNone(product)


suite = unittest.TestSuite()
test_cases = [
    QuoteGeneratorTestCase,
    ProductsTestCase,
    LibFunctionsTestCase,
]
for test in test_cases:
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(test))
unittest.TextTestRunner().run(suite)
