from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Flask, jsonify, request
from decimal import Decimal

from .lib import create_order_book, find_product
from .order_book import QuoteGenerator, NotEnoughBookOrders

app = Flask(__name__)


@app.route('/quote', methods=['POST'])
def quote():
    """
    Quoting enpoint.

    This enpoint accepts only json request body with the following format:
    {
        "action": [buy|sell],
        "base_currency: string,
        "quote_currency": string,
        "amount": numeric
    }

    """
    params = request.get_json()
    error_response = validate_input_params(params)
    if error_response:
        return error_response

    try:
        product, inversed = get_product_from_params(params)
        order_book = create_order_book(str(product), inversed=inversed)
    except Exception as e:
        return response_error(400, str(e))

    quoter = QuoteGenerator(order_book)
    try:
        price, amount = quoter.quote(Decimal(params['amount']), params['action'])
    except NotEnoughBookOrders:
        return response_error(500, 'not enough orders to complete quote')

    return jsonify({
        'price': "{:.8f}".format(price / amount),
        'total': "{:.8f}".format(price),
        'currency': params['quote_currency'].upper()
    })

def validate_input_params(request_body):
    required_params = ('action', 'base_currency', 'quote_currency', 'amount')
    errors = []
    for required_param in required_params:
        if not request_body.get(required_param):
            errors.append({'field': required_param, 'error': 'required'})
    if request_body.get('action') not in ['buy', 'sell']:
        errors.append({'field': 'action', 'error': 'invalid'})
    if errors:
        return response_error(400, 'invalid parameters', {'invalid_parameters': errors})
    return None

def get_product_from_params(params):
    product, inversed = find_product(params['base_currency'].upper(), params['quote_currency'].upper())
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
