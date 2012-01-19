import flask

from application import app, Configuration
from reading import Reading
from persistence import Persistence
from user import User
import openid # forces registrations


class ParameterError(Exception):
    """An incorrect parameter was specified."""
    pass

class NotFoundError(Exception):
    """The target was not found."""
    def __init__(self, target):
        self.target = target


def run(config=None):
    if config is None:
        config = Configuration()
    app.config.update(config.values())
    app.run(host=config.host, port=config.port, debug=config.debug)

