from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Flask, jsonify, request
from decimal import Decimal

from .lib import create_order_book
from .order_book import QuoteGenerator

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify({
        'service': 'Coinbase Quote Service'
    })

@app.route('/quote', methods=['POST'])
def quote():
    params = request.get_json()
    errors = validate_input_params(params)
    if errors:
        return error(400, 'invalid parameters', {'invalid_parameters': errors}), 400

    try:
        order_book = create_order_book(create_currency_pair(params))
    except Exception as e:
        return error(400, str(e)), 400

    quote = QuoteGenerator(order_book)
    price, amount = quote.quote_inverse(Decimal(params['amount']), params['action'])

    return jsonify({
        'price': str(price / amount),
        'amount': str(amount),
        'currency': params['quote_currency']
    })

def validate_input_params(request_body):
    required_params = ('action', 'base_currency', 'quote_currency', 'amount')
    errors = []
    for required_param in required_params:
        if required_param not in request_body:
            errors.append({'field': required_param, 'error': 'required'})
    if 'action' not in errors:
        if request_body['action'] not in ['buy', 'sell']:
            errors.append({'field': 'action', 'error': 'invalid'})
    return errors

def create_currency_pair(request_body):
    return "{}-{}".format(request_body['base_currency'], request_body['quote_currency'])

@app.errorhandler(404)
def page_not_found(error):
    return error(404, 'method not found'), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return error(405, 'method not allowed'), 405

def error(code, message, extra=None):
    return jsonify({
        'code': code,
        'message': message,
        'extra': extra
    })
