import logging

from . import lib

logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.INFO)
lib.PRODUCTS = lib.fetch_all_products()
logging.info("Fetched all products")
