"""
Core Application Hooks
======================

This module contains the connection and session related hooks into Flask
as well as the core :py:class:`flask.Flask` application instance.

Flask Usage
-----------

.. py:data:: flask.g.db

This is set to an instance of :py:class:`~readit.persistence.Persistence`
It is populated using a :py:meth:`flask.Flask.before_request` hook.  The
connection to the backend is lazily created in the implementation.  Another
hook registered with :py:meth:`flask.Flask.after_request` will tear down the
connection if one was created.

Top-level Application
---------------------

"""
import datetime
import os

import flask

import persistence
import readit


app = flask.Flask('readit')
app.secret_key = 'My really secure secret key'

class Configuration(object):
    def __init__(self):
        self.host = os.environ.get('HOST', '0.0.0.0')
        self.port = int(os.environ.get('PORT', '5000'))
        value = os.environ.get('DEBUG', 'False').lower()
        self.debug = value == 'true' or value == '1'
        self.mongo_url = os.environ.get('MONGOURL', 'mongodb://localhost/readit')
    def values(self):
        return {'HOST': self.host, 'PORT': self.port, 'DEBUG': self.debug,
                'MONGO_URL': self.mongo_url}




@app.route('/config')
def dump_configuration():
    if not app.config['DEBUG']:
        flask.abort(403)
    return flask.render_template('config.html', environ=os.environ)

@app.before_request
def initialize_persistence():
    flask.g.db = persistence.Persistence()

@app.after_request
def teardown_persistence(response):
    if flask.g.db is not None:
        flask.g.db.close()
        flask.g.db = None
    return response

@app.route('/readings')
def fetch_reading_list():
    if flask.g.user is None:
        return flask.redirect(flask.url_for('openid_login'))
    return flask.render_template('list.html',
            read_list=flask.g.user.get_readings())

@app.route('/readings', methods=['POST'])
def add_reading():
    if flask.g.user is None:
        return flask.redirect(flask.url_for('openid_login'))
    data = flask.request.json or flask.request.data or flask.request.form
    if not data:
        return flask.Response(status=400)
    doc = flask.g.user.add_reading(data['title'], data['link'])
    doc['when'] = doc['when'].isoformat() + 'Z'
    return flask.Response(
            response=flask.json.dumps(doc),
            mimetype='text/json')

@app.route('/readings/<reading_id>', methods=['DELETE'])
def delete_reading(reading_id):
    if flask.g.user is None:
        return flask.redirect(flask.url_for('openid_login'))
    try:
        app.logger.debug('removing ' + str(reading_id))
        flask.g.user.remove_reading(reading_id)
        return flask.Response(status=204)
    except readit.NotFoundError, err:
        return flask.Response(status=404)

