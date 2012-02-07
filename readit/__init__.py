import flask

from flaskapp import app

#from reading import Reading
#from persistence import Persistence
#from user import User
#import openid # forces registrations


class ParameterError(Exception):
    """An incorrect parameter was specified."""
    pass

class NotFoundError(Exception):
    """The target was not found."""
    def __init__(self, target):
        self.target = target


def run():
    app.run()

