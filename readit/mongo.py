import flask
import pymongo
import readit


@readit.app.before_request
def initialize_mongo_connection():
    flask.g.db = None

@readit.app.after_request
def teardown_mongo_connection(response):
    if flask.g.db:
        readit.app.logger.debug('closing connection %s', str(flask.g.db))
        flask.g.db.connection.close()
    return response


def connect_to_db():
    if flask.g.db is None:
        url = readit.app.config['MONGO_URL']
        readit.app.logger.debug('connecting to %s', url)
        conn = pymongo.connection.Connection(host=url)
        flask.g.db = conn.readit

def get_db():
    connect_to_db()
    return flask.g.db


@readit.app.route('/readings')
def fetch_reading_list():
    db = get_db()
    readings = db.readings.find({'user_id': flask.g.user['_id']})
    return flask.render_template('list.html', read_list=readings)

