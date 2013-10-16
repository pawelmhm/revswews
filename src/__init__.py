"""
Initialize Flask app

"""
from flask import Flask
import os
import logging

app = Flask('src')

if os.getenv('FLASK_CONF') == 'DEV':
    app.config.from_object('src.config.DevelopmentConfig')
    #app.logger.info('<Development Configuration>')
    #from flask_debugtoolbar import DebugToolbarExtension
    #toolbar = DebugToolbarExtension(app)
    #logging.debug('hello')

elif os.getenv('FLASK_CONF') == 'TEST':
    app.config.from_object('src.config.TestConfig')
    app.logger.info('<Testing Configuration>')

else:
    app.config.from_object('src.config.ProductionConfig')
    app.logger.info('<Production Configuration>')


import flaskr
