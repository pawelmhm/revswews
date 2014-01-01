"""
Initialize Flask app

"""
from flask import Flask
import os

app = Flask(__name__)

if os.getenv('FLASK_CONF') == 'DEV':
    app.config.from_object('src.config.DevelopmentConfig')

elif os.getenv('FLASK_CONF') == 'TEST':
    app.config.from_object('src.config.TestConfig')

else:
    app.config.from_object('src.config.ProductionConfig')

import flaskr
