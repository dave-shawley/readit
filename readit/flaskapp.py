"""
This module contains the Flask-specific portion of the application.  This
isn't meant to be a replaceable interface.  Instead, it is a convenient way
to isolate the Flasky stuff into one place.

Flask Global Usage
------------------

.. py:data:: flask.g.user

   A new instance of :py:class:`~readit.User` is stored in ``flask.g.user``
   when a new request comes in.  If the session contains our data, then the
   user is automagically logged in.  Otherwise, ``flask.g.user`` will be in
   the *logged out* state.

.. py:data:: flask.session

   A generated session key is placed into ``flask.session["session_key"]``
   when the user logs in.  The session key is used as a URL path parameter
   to refer to manipulate the user through the session.

Read It Flask Application
-------------------------

"""
import datetime
import functools
import os

import flask
import flask.ext.openid
import flask.ext.heroku_runner
import werkzeug.exceptions

import readit
import readit.json_support


class Application(flask.ext.heroku_runner.HerokuApp, readit.LinkMap):
    """I extend :py:class:`flask.Flask` to add Open ID tracking and use
    :py:class:`LinkMap` to provide a list of actions.
    
    The original goal of this class was to implement all of the user
    management and other *business logic* outside of the Flask view
    functions.
    """

    JAVASCRIPT_DEBUG_FILE_LIFETIME = 60

    def __init__(self):
        super(Application, self).__init__(__package__)
        readit.LinkMap.__init__(self)
        self.config['SECRET_KEY'] = os.urandom(24)
        self.load_configuration()
        self.oid = flask.ext.openid.OpenID(self)
        self.oid.after_login(self._login_succeeded)
        self.oid.errorhandler(self._report_openid_error)

    def load_configuration(self):
        self.config['SESSION_LIFETIME'] = 5 * 60
        self.config['HOST'] = os.environ.get('HOST', '127.0.0.1')
        self.config['PORT'] = os.environ.get('PORT', '5000')
        self.config['STORAGE_URL'] = os.environ.get('MONGOURL', None)
        flag = os.environ.get('DEBUG', None)
        if flag is not None:
            self.config['DEBUG'] = flag.lower() in ['true', 't', 'yes', '1']

    @property
    def openid(self):
        """The :py:class:`flask.ext.openid.OpenID` instance that is bound to
        the application.  Use this to establish Open ID login handlers."""
        return self.oid

    # @openid.after_login
    def _login_succeeded(self, response):
        result = flask.g.db.retrieve_one('users', email=response.email,
                clazz=readit.User)
        if result:
            flask.g.user = result
            flask.g.user.login(response)
            flask.session['session_key'] = flask.g.user.session_key
            flask.session['user_id'] = flask.g.user.user_id
            self.logger.debug('login succeeded for %s => %s',
                    flask.session['session_key'], flask.g.user)
            next = flask.request.args.get('next') or self.oid.get_next_url()
            self.logger.debug('redirecting to %s', next)
            return flask.redirect(next)
        self.logger.error('failed to find user for identity %s',
                response.identity_url)
        return flask.Response(status=404)

    # @openid.errorhandler
    def _report_openid_error(self, message):
        self.logger.error('Open ID Error [%s]', message, exc_info=1)
        raise werkzeug.exceptions.InternalServerError('Open ID Failure')

    def logout(self):
        """Log the current user out of the application.  Calling this method
        will invokes the :py:meth:`~readit.User.logout` method on
        :py:data:`flask.g.user` and removing data that was stored in
        :py:data:`flask.session`."""
        flask.session.pop('user_id', None)
        flask.session.pop('session_key', None)
        flask.g.user.logout()

    # This requires Flask >= 0.9
    def get_send_file_max_age(self, filename):
        if self.debug:
            if filename.lower().endswith('.js'):
                return self.JAVASCRIPT_DEBUG_FILE_LIFETIME
        return super(Application, self).get_send_file_max_age(filename)

    def jsonify(self, obj):
        """JSONify an object using the
        :py:class:`readit.json_support.JSONEncoder` class.
        """
        encoder = readit.json_support.JSONEncoder()
        return self.response_class(encoder.encode(obj),
                mimetype='application/json')

    def process_response(self, response):
        """Slight customization of response processing.
        
        :param response: :py:class:`flask.Response` instance
        :returns: either ``response`` or a new :py:class:`flask.Response`
            instance containing a JSON redirect.
        
        If :py:class:`flask.request` is an AJAX request and ``response`` is a
        HTTP redirect response, then the response is rewritten as a HTTP OK
        containing a JSON object with a single attribute named ``redirect_to``
        and the value of the ``Location`` header from the response::
            
            HTTP/1.1 303 See Other
            Location: http://other.server.com/location
        
        becomes::
            
            HTTP/1.1 200 OK
            Content-Type: application/json
            Content-Length: 52
            
            {"redirect_to":"http://other.server.com/location"}
        
        This hack is necessary to work around a deficiency in the way that
        XMLHTTPRequest processes redirect responses.
        """
        if flask.request.is_xhr and readit.helpers.is_redirect(response):
            location = response.headers['location']
            app.logger.debug('transforming redirect "%s" into JSON', location)
            response = self.jsonify({'redirect_to': location})
        return super(Application, self).process_response(response)

app = Application()
 

def verify_session(func):
    """Decorator that verifies the authenticity of the session key.
    
    Use this to decorate a flask view function that takes the session key
    as its only argument.  If the session key doesn't match the key that
    is stored in the signed session or it doesn't match the user's session
    key, then a 409 is raised.  If there is no key in the session, then we
    obviously are not logged in, so a redirect to the login page is
    returned.
    """
    @functools.wraps(func)
    def wrapper(session_key):
        if 'session_key' not in flask.session:
            #  303 is required since we may be wrapping a non-GET request
            return flask.redirect(flask.url_for('login'), code=303)
        if session_key != flask.session['session_key']:
            raise werkzeug.exceptions.Conflict('session key mismatch')
        return func(session_key)
    return wrapper


@app.before_request
def initialize_user():
    """Make sure that ``flask.g.user`` is initialized to an instance
    of :py:class:`readit.User`."""
    flask.g.user = readit.User(flask.session.get('session_key', None))
    flask.g.user.user_id = flask.session.get('user_id', None)


@app.before_request
def setup_storage():
    if not hasattr(flask.g, 'db'):
        import readit.mongo
        flask.g.db = readit.mongo.Storage(
            storage_url=app.config['STORAGE_URL'])


@app.route('/')
def root():
    """Application entry point.  This will redirect to either a login page
    or the list of readings for the currently logged in user."""
    if not flask.g.user.logged_in:
        return flask.redirect(flask.url_for('login'))
    return flask.redirect(flask.url_for('reading_list',
        session_key=flask.g.user.session_key))


@app.route('/login', methods=['GET', 'POST'])
@app.advertise('start-login', 'GET')
@app.openid.loginhandler
def login():
    """Root of the login process.  A :http:method:`GET` will return the
    login page.  However, if the user is already logged in, then this will
    simply redirect to the reading list."""
    next_arg = flask.request.args.get('next')
    if flask.g.user.logged_in:
        next_arg = next_arg or app.openid.get_next_url()
        app.logger.debug('redirecting to %s', next_arg)
        return flask.redirect(next_arg)
    if flask.request.method == 'POST':
        openid = flask.request.form.get('openid')
        if openid:
            app.logger.debug('trying openid %s', openid)
            return app.openid.try_login(openid,
                    ask_for=['email', 'fullname', 'nickname'])
        raise werkzeug.exceptions.InternalServerError(
            'POST missing openid parameter')
    next_arg = next_arg or flask.url_for('root')
    return flask.render_template('login.html', next=next_arg)


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/<session_key>', methods=['DELETE'])
@app.advertise('logout', 'DELETE')
@verify_session
def logout(session_key):
    """Log a session out of the system."""
    app.logout()
    return app.jsonify(app.links)


@app.route('/<session_key>/links')
@app.advertise('get-links', 'GET')
@verify_session
def get_links(session_key):
    """Return a list of links for this session."""
    return app.jsonify(app.links)


@app.route('/<session_key>/readings')
@app.advertise('get-readings', 'GET')
@verify_session
def reading_list(session_key):
    """Return the list of readings for this session."""
    if readit.helpers.wants_json(flask.request):
        app.logger.debug('retrieving data from %s for %s',
                flask.g.db, flask.g.user.user_id)
        data = flask.g.db.retrieve('readings',
                user_id=flask.g.user.user_id,
                clazz=readit.Reading)
        return app.jsonify({'actions': app.links, 'readings': data})
    return flask.render_template('list.html', actions=app.links)


@app.route('/<session_key>/readings', methods=['POST'])
@app.advertise('add-reading', 'POST')
@verify_session
def add_reading(session_key):
    data = flask.request.json or flask.request.form
    try:
        app.logger.debug('saving reading to %s for %s',
                flask.g.db, flask.g.user)
        reading = readit.Reading(title=data['title'], link=data['link'],
                when=data.get('when', datetime.datetime.utcnow()),
                user=flask.g.user)
        flask.g.db.save('readings', reading)
        return app.jsonify({'actions': app.links, 'new_reading': reading})
    except KeyError, exc:
        raise werkzeug.exceptions.BadRequest(
            '{0} is a required field'.format(exc))


@app.route('/<session_key>/readings/<reading_id>', methods=['DELETE'])
def remove_reading(session_key, reading_id):
    flask.g.db.remove('readings', flask.g.user.user_id, _id=reading_id)
    return flask.Response(status=204)


