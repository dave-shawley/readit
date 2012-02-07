"""
Flask Application Hooks
=======================

This module contains most of the Flask application.  This is where you will
find the various view functions and other flasky hooks.

Flask Usage
-----------

.. py:data:: flask.g.db

This is set to an instance of :py:class:`~readit.persistence.Persistence`
It is populated using a :py:meth:`flask.Flask.before_request` hook.  The
connection to the backend is lazily created in the implementation.  Another
hook registered with :py:meth:`flask.Flask.after_request` will tear down the
connection if one was created.

.. py:data:: flask.g.user

This is set to an instance of :py:class:`~readit.user.User` when the user is
validated by the Open ID backend.

Application API
---------------
"""

import binascii
import os

import flask
import flaskext.openid

import readit.persistence
import readit.user


class Application(flask.Flask):
    def __init__(self, config_envvar='APP_CONFIG'):
        super(Application, self).__init__(__package__)
        self.DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
        self.HOST = os.environ.get('HOST', '0.0.0.0')
        self.PORT = int(os.environ.get('PORT', '5000'))
        self.SECRET_KEY = os.urandom(24)
        self.MONGO_URL = os.environ.get('MONGOURL', 'mongodb://localhost/readit')
        self.config.from_object(self)
        self.config.from_envvar(config_envvar, silent=True)
    def run(self, **kwds):
        args = kwds.copy()
        args.setdefault('host', self.HOST)
        args.setdefault('port', self.PORT)
        super(Application, self).run(**args)

app = Application()
open_id = flaskext.openid.OpenID(app)

@app.before_request
def initialize_current_user():
    """Called before a request to establish :py:data:`flask.g.user`
    based on the ``user_id`` session attribute."""
    flask.g.db = readit.persistence.Persistence()
    flask.g.user = None
    if 'user_id' in flask.session:
        flask.g.user = readit.user.find(user_id=flask.session['user_id'])
        if flask.g.user is None:
            flask.session.pop('user_id', None)
        else:
            flask.flash(u'Logged in as ' + flask.g.user.open_id)

@app.after_request
def teardown_persistence(response):
    if flask.g.db is not None:
        flask.g.db.close()
        flask.g.db = None
    return response

@app.route('/', methods=['GET', 'POST'])
@open_id.loginhandler
def login():
    if flask.g.user is not None:
        app.logger.debug('user %s is logged in', flask.g.user)
        return flask.redirect(flask.url_for('fetch_reading_list'), code=303)
    if flask.request.method == 'POST':
        oid = flask.request.form.get('openid')
        if oid:
            app.logger.debug('processing login for %s', oid)
            requested = [ 'email', 'fullname', 'nickname' ]
            return open_id.try_login(oid, ask_for=requested)
    return flask.render_template('openid-login.html',
            next=open_id.get_next_url(), error=open_id.fetch_error())

@open_id.after_login
def openid_validated(response):
    oid = response.identity_url
    app.logger.debug('validated Open ID %s, looking up user', oid)
    user = readit.user.find(open_id=oid)
    if user is None:
        app.logger.error('no user found for ' + oid)
        return flask.abort(404)
    flask.g.user = user
    flask.session['user_id'] = user.id
    return flask.redirect(flask.url_for('fetch_reading_list'), code=303)

@app.route('/readings')
def fetch_reading_list():
    if flask.g.user is None:
        return flask.redirect(flask.url_for('openid_login'))
    return flask.render_template('list.html',
            read_list=flask.g.user.get_readings())

@app.route('/config')
def dump_configuration():
    if not app.config['DEBUG']:
        flask.abort(403)
    cfg = os.environ.copy()
    if 'SECRET_KEY' in cfg:
        cfg['SECRET_KEY'] = binascii.hexlify(cfg['SECRET_KEY'])
    return flask.render_template('config.html', environ=os.environ, config=cfg)

@app.route('/logout')
def logout():
    flask.session.pop('user_id', None)
    flask.g.user = None
    flask.flash(u'You have been logged out.')
    return flask.redirect(flask.url_for('login'))

