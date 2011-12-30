import flask
import flaskext.openid
import readit


oid = flaskext.openid.OpenID(readit.app)

@readit.app.before_request
def lookup_user():
    flask.g.user = None
    if 'user_id' in flask.session:
        db = readit.get_db()
        flask.g.user = db.users.find_one({'_id': flask.session['user_id']})
        readit.app.logger.debug('found %s for %s', flask.g.user,
                flask.session['user_id'])
        if flask.g.user is None:
            flask.session.pop('user_id', None)

@readit.app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def openid_login():
    if flask.g.user is not None: # user already logged in
        readit.app.logger.debug('user %s is logged in', flask.g.user)
        return flask.redirect(oid.get_next_url())
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
    open_id = response.identity_url
    readit.app.logger.debug('validated OpenID %s, looking up user', open_id)
    db = readit.get_db()
    user = db.users.find_one({'open_id': open_id})
    if user is None:
        user = { 'open_id': open_id,
                'name': response.fullname or response.nickname,
                'email': response.email,
                'image': response.image }
        db.users.insert(user, safe=True)
        readit.app.logger.debug('created user %s', str(user))
        flask.flash(u'New account created for ' + user['open_id'])
    flask.g.user = user
    flask.session['user_id'] = user['_id']
    return flask.redirect('/readings')

@readit.app.route('/logout')
def openid_logout():
    flask.session.pop('user_id', None)
    flask.g.user = None
    flask.flash(u'You were signed out')
    return flask.redirect('/login')

