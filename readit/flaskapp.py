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

The :py:class:`~readit.User` instance for the currently active (e.g., *logged
in*) identity or ``None``.  This is managed by
:py:func:`initialize_current_user`, :py:func:`openid_validated`,
and :py:func:`logout`.

.. py:data:: flask.session['user_id']

The internal (DB) ID for the currently active identity.  This is managed by
:py:func:`initialize_current_user`, :py:func:`openid_validated`, and
:py:func:`logout`.

Application API
---------------
"""

import binascii
import logging
import os

import flask
import flaskext.openid

import readit.persistence
import readit.user


class Application(flask.Flask):
    """
    I am the core Flask application.
    
    I don't provide much beyond what is already provided by
    :py:class:`flask.Flask`.  Just some simple configuration niceties.
    """
    def __init__(self, config_envvar='APP_CONFIG'):
        super(Application, self).__init__(__package__)
        self.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
        self.config['HOST'] = os.environ.get('HOST', '0.0.0.0')
        self.config['PORT'] = int(os.environ.get('PORT', '5000'))
        self.config['SECRET_KEY'] = os.urandom(24)
        self.config['MONGO_URL'] = os.environ.get('MONGOURL',
                'mongodb://localhost/readit')
        self.config.from_envvar(config_envvar, silent=True)
    def run(self, **kwds):
        args = kwds.copy()
        args.setdefault('host', self.config['HOST'])
        args.setdefault('port', self.config['PORT'])
        args.setdefault('debug', self.config['DEBUG'])
        if args['debug']:
            self.logger.setLevel(logging.DEBUG)
        super(Application, self).run(**args)

app = Application()
open_id = flaskext.openid.OpenID(app)

@app.before_request
def initialize_current_user():
    """Called before a request to establish :py:data:`flask.g.user`
    based on the ``user_id`` session attribute and set up the persistence
    layer."""
    flask.g.db = readit.persistence.Persistence()
    flask.g.user = None
    if 'user_id' in flask.session:
        flask.g.user = readit.user.find(user_id=flask.session['user_id'])
        if flask.g.user is None:
            flask.session.pop('user_id', None)

@app.after_request
def teardown_persistence(response):
    """Called after a request to teardown the persistence layer."""
    if flask.g.db is not None:
        flask.g.db.close()
        flask.g.db = None
    return response

@app.route('/', methods=['GET', 'POST'])
@open_id.loginhandler
def login():
    """Perform the Open ID login"""
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
    """Process a successful Open ID login"""
    oid = response.identity_url
    app.logger.debug('validated Open ID %s, looking up user', oid)
    user = readit.user.find(open_id=oid)
    if user is None:
        app.logger.info('no user found for %s, creating a new one', oid)
        user = readit.user.User()
        user.open_id = oid
        user.name = response.nickname or response.fullname or response.email
        user.email = response.email
        user.update()
    flask.g.user = user
    flask.session['user_id'] = user.id
    flask.flash(u'You have been logged in')
    return flask.redirect(flask.url_for('fetch_reading_list'), code=303)

@app.route('/readings')
def fetch_reading_list():
    """Retrieve a list of readings for display."""
    if flask.g.user is None:
        return flask.redirect(flask.url_for('login'))
    return flask.render_template('list.html',
            read_list=flask.g.user.get_readings())

@app.route('/readings', methods=['POST'])
def add_reading():
    """Add a new reading, returns the JSON representation of the reading."""
    if flask.g.user is None:
        return flask.redirect(flask.url_for('login'))
    data = flask.request.json or flask.request.data or flask.request.form
    if not data:
        return flask.Response(status=400)
    doc = flask.g.user.add_reading(data['title'], data['link'])
    doc['when'] = doc['when'].isoformat() + 'Z'
    return flask.Response(response=flask.json.dumps(doc), mimetype='text/json')

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
    """Clear out the Open ID session attributes."""
    flask.session.pop('user_id', None)
    flask.g.user = None
    flask.flash(u'You have been logged out.')
    return flask.redirect(flask.url_for('login'))

