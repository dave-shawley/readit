"""
OpenID Implementation
======================

This module implements Flask handlers and other related hooks that add
OpenID support to the application.

Flask Usage
-----------

.. py:data:: flask.g.user

The :py:class:`~readit.User` instance for the currently active (e.g., *logged
in*) identity or ``None``.  This is managed by :py:func:`lookup_user`,
:py:func:`openid_validated`, and :py:func:`openid_logout`.

.. py:data:: flask.session['user_id']

The internal (DB) ID for the currently active identity.  This is managed by
:py:func:`lookup_user`, :py:func:`openid_validated`, and
:py:func:`openid_logout`.

OpenID Functions
-----------------

"""
import flask
import flaskext.openid
import readit


oid = flaskext.openid.OpenID(readit.app)
_SESSION_KEY = 'user_id'


@readit.app.before_request
def lookup_user():
    """Called before a request to establish :py:data:`flask.g.user`
    based on the ``user_id`` session attribute."""
    flask.g.user = None
    if _SESSION_KEY in flask.session:
        flask.g.user = readit.User.find(user_id=flask.session[_SESSION_KEY])
        readit.app.logger.debug('found %s for %s', flask.g.user,
                flask.session[_SESSION_KEY])
        if flask.g.user is None:
            flask.session.pop(_SESSION_KEY, None)

@readit.app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def openid_login():
    """Handler for OpenID logins.
    
    :registered as: :py:meth:`flaskext.openid.OpenID.loginhandler`
    :exposed as: :http:get:`/login`, :http:post:`/login`
    
    Processes a login request by checking if an identity is active and
    redirecting to the next page if one is.  Otherwise, a :http:method:`GET`
    request is answered by a login form and a :http:method:`POST` request
    is processed by the OpenID layer.
    
    In the :http:method:`POST` case, the *openid* field of the form is
    expected to contain the OpenID URL that is processed.
    """
    if flask.g.user is not None: # user already logged in
        readit.app.logger.debug('user %s is logged in', flask.g.user)
        return flask.redirect(oid.get_next_url(), code=303)
    if flask.request.method == 'POST':
        openid = flask.request.form.get('openid')
        if openid:
            readit.app.logger.debug('processing login for %s', openid)
            requested_attributes = [ 'email', 'fullname',
                    'nickname', 'image' ]
            return oid.try_login(openid, ask_for=requested_attributes)
    return flask.render_template('openid-login.html',
            next=oid.get_next_url(), error=oid.fetch_error())

@oid.after_login
def openid_validated(response):
    """Called when the OpenID is considered complete & valid.
    
    :param flaskext.openid.OpenIDResponse response:
        the OpenID response to process
    :registered as: :py:meth:`flaskext.openid.OpenID.after_login`
    
    Accepts the OpenID response and looks up the :py:class:`.User` instance
    associated with :py:data:`response.identity_url`.  If the user is not
    found, then a new user is created and persisted.  In any case, the
    ``User`` instance is stored in :py:data:`flask.g.user`, the internal user
    ID is stashed in :py:data:`flask.session` as ``user_id``, and
    :http:statuscode:`303` is returned.
    """
    open_id = response.identity_url
    readit.app.logger.debug('validated OpenID %s, looking up user', open_id)
    user = readit.User.find(open_id=open_id)
    if user is None:
        user = readit.User()
        user.open_id = open_id
        user.name = response.fullname or response.nickname
        user.email = response.email
        user.update()
        readit.app.logger.debug('created user %s', user)
        flask.flash(u'New account created for ' + user.open_id)
    flask.g.user = user
    flask.session[_SESSION_KEY] = user.id
    return flask.redirect('/readings', code=303)

@readit.app.route('/logout')
def openid_logout():
    """Logs the user out of the system.

    :exposed as: :http:get:`/logout`

    Logs out of the system by removing the *user_id* session attribute and
    clearing :py:data:`flask.g.user`.
    """
    flask.session.pop(_SESSION_KEY, None)
    flask.g.user = None
    flask.flash(u'You were signed out')
    return flask.redirect('/login')

