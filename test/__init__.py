import unittest

from app.order_book import OrderBook, OrderBookEntry, QuoteGenerator


class QuoteGeneratorTestCase(unittest.TestCase):
    def setUp(self):
        self.books = {}

    def _create_order_book(self, currency_pair):
        self.books[currency_pair] = OrderBook()
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
        book = self._create_order_book('BTC-USD')
        book.add_ask(OrderBookEntry(price=100, size=1, num_orders=1))
        book.add_ask(OrderBookEntry(price=200, size=1, num_orders=1))
        book.add_ask(OrderBookEntry(price=300, size=1, num_orders=1))

        quoter = QuoteGenerator(book)
        amount, price = quoter.quote_inverse(100, QuoteGenerator.SIDE_BUY)
        self.assertEquals(amount, 1)
        self.assertEquals(price, 100)
        amount, price = quoter.quote_inverse(150, QuoteGenerator.SIDE_BUY)
        self.assertEquals(amount, 1.25)
        amount, price = quoter.quote_inverse(200, QuoteGenerator.SIDE_BUY)
        self.assertEquals(amount, 1.5)
        amount, price = quoter.quote_inverse(350, QuoteGenerator.SIDE_BUY)
        self.assertEquals("{:.2f}".format(amount), '2.17')

    def test_buy_btc_to_usd_inverse_when_multiple_num_orders(self):
        book = self._create_order_book('BTC-USD')
        book.add_ask(OrderBookEntry(price=100, size=1, num_orders=2))
        book.add_ask(OrderBookEntry(price=200, size=1, num_orders=1))
        book.add_ask(OrderBookEntry(price=300, size=1, num_orders=1))

        quoter = QuoteGenerator(book)
        amount, price = quoter.quote_inverse(200, QuoteGenerator.SIDE_BUY)
        self.assertEquals(amount, 2)
        amount, price = quoter.quote_inverse(300, QuoteGenerator.SIDE_BUY)
        self.assertEquals(amount, 2.5)


suite = unittest.TestSuite()
test_cases = [QuoteGeneratorTestCase]
for test in test_cases:
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(test))
unittest.TextTestRunner().run(suite)
