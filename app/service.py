from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Flask, jsonify, request
from decimal import Decimal

from .lib import create_order_book, find_product
from .order_book import QuoteGenerator, NotEnoughBookOrders

app = Flask(__name__)


@app.route('/quote', methods=['POST'])
def quote():
    params = request.get_json()
    response = validate_input_params(params)
    if response:
        return response

    try:
        product, inversed = get_product_from_params(params)
        order_book = create_order_book(str(product))
    except Exception as e:
        return response_error(400, str(e))

    quote = QuoteGenerator(order_book)
    quote_method = quote.quote if not inversed else quote.quote_inverse
    try:
        price, amount = quote_method(Decimal(params['amount']), params['action'])
    except NotEnoughBookOrders:
        return response_error(500, 'not enough orders to complete quote')

    return jsonify({
        'price': "{:.8f}".format(price / amount),
        'total': "{:.8f}".format(price),
        'currency': params['quote_currency']
    })

def validate_input_params(request_body):
    required_params = ('action', 'base_currency', 'quote_currency', 'amount')
    errors = []
    for required_param in required_params:
        if required_param not in request_body:
            errors.append({'field': required_param, 'error': 'required'})
    if 'action' not in errors and 'action' in request_body:
        if request_body['action'] not in ['buy', 'sell']:
            errors.append({'field': 'action', 'error': 'invalid'})
    if errors:
        return response_error(400, 'invalid parameters', {'invalid_parameters': errors})
    return None

def get_product_from_params(request_body):
    product, inversed = find_product(request_body['base_currency'], request_body['quote_currency'])
    if not product:
        raise Exception("invalid currency pair provided")
    return (product, inversed,)

@app.errorhandler(404)
def page_not_found(error):
    return response_error(404, 'method not found')

@app.errorhandler(405)
def method_not_allowed(error):
    return error(405, 'method not allowed')

def response_error(code, message, extra=None):
    return jsonify({
        'code': code,
        'message': message,
        'extra': extra
    }), code
