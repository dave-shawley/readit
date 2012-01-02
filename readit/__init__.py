import flask

from application import app, Configuration
from user import ParameterError, User
import openid # forces registrations



def run(config=None):
    if config is None:
        config = Configuration()
    app.config.update(config.values())
    app.run(host=config.host, port=config.port, debug=config.debug)

