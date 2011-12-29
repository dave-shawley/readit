import os
import StringIO

import flask
import pymongo



application = flask.Flask(__name__)

class Configuration(object):
    def __init__(self):
        self.host = os.environ.get('HOST', '0.0.0.0')
        self.port = int(os.environ.get('PORT', '5000'))
        value = os.environ.get('DEBUG', 'False').lower()
        self.debug = value == 'true' or value == '1'
        self.mongo_url = os.environ.get('MONGOURL', 'mongodb://localhost/')
    def values(self):
        return {'HOST': self.host, 'PORT': self.port, 'DEBUG': self.debug,
                'MONGO_URL': self.mongo_url}


@application.before_request
def initialize_mongo_connection():
    flask.g.db = None

@application.after_request
def teardown_mongo_connection(response):
    if flask.g.db:
        application.logger.debug('closing connection %s', str(flask.g.db))
        flask.g.db.connection.close()
    return response

def connect_to_db():
    if flask.g.db is None:
        application.logger.debug('connecting to %s',
                application.config['MONGO_URL'])
        conn = pymongo.connection.Connection(
                host=application.config['MONGO_URL'])
        flask.g.db = conn.readit


@application.route('/config')
def fetch_read_list():
    if not application.config['DEBUG']:
        flask.abort(403)
    return flask.render_template('config.html', environ=os.environ)


def run(config=None):
    if config is None:
        config = Configuration()
    application.config.update(config.values())
    application.run(host=config.host, port=config.port, debug=config.debug)

