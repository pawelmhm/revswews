"""
Initialize Flask app

"""
from flask import Flask
import os
import logging
app = Flask(__name__)

logging.basicConfig(filename="/var/www/app/flask_app.log",level=logging.DEBUG,
        format="%(asctime)s %(filename)s %(message)s", datefmt='%m/%d/%Y %I:%M:%S %p')

if os.getenv('FLASK_CONF') == 'DEV':
    app.config.from_object('src.config.DevelopmentConfig')
    logging.info("app starts, conf Development")
elif os.getenv('FLASK_CONF') == 'TEST':
    app.config.from_object('src.config.TestConfig')
    logging.info("app starts conf test")
else:
    app.config.from_object('src.config.ProductionConfig')
    logging.info("app starts conf production")

import flaskr
