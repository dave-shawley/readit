import flask
import pymongo
import readit


@readit.app.route('/readings')
def fetch_reading_list():
    return flask.render_template('list.html',
            read_list=flask.g.user.get_readings())

@readit.app.before_request
def _initialize_mongo_connection():
    flask.g.db = None

@readit.app.after_request
def _teardown_mongo_connection(response):
    if flask.g.db:
        readit.app.logger.debug('closing connection %s', str(flask.g.db))
        flask.g.db.connection.close()
    return response


def _connect_to_db():
    if flask.g.db is None:
        url = readit.app.config['MONGO_URL']
        readit.app.logger.debug('connecting to %s', url)
        conn = pymongo.connection.Connection(host=url)
        flask.g.db = conn.readit

def _get_db():
    _connect_to_db()
    return flask.g.db


class ParameterError(Exception):
    """An incorrect parameter was specified."""
    pass

class User(object):
    """I represent a user that is registered in the system.
    """
    def __init__(self):
        self._user_dict = {}

    @property
    def id(self):
        """The unique identifier assigned to me by the persistence layer.
        In the case of Mongo, this the ObjectId."""
        return self._user_dict.get('_id')

    def get_open_id(self):
        return self._user_dict.get('open_id')
    def set_open_id(self, open_id):
        self._user_dict['open_id'] = open_id
    open_id = property(get_open_id, set_open_id,
            doc="""My Open ID as a string.""")

    def get_name(self):
        return self._user_dict.get('name')
    def set_name(self, name):
        self._user_dict['name'] = name
    name = property(get_name, set_name,
            doc="""My display name.  This is either the full name from
                   the Open ID layer or the nickname.""")

    def get_email(self):
        return self.email
    def set_email(self, email):
        self._user_dict['email'] = email
    email = property(get_email, set_email,
            doc="""My email address or ``None``""")

    def update(self):
        """Persist myself.
        
        Once I am persistent, you can retrieve me by calling :py:meth:`.find`
        with either my :py:attr:`.id` or :py:attr:`.open_id`.  If this is the
        first time that I am stored, then a new :py:attr:`id` attribute will
        be assigned."""
        _get_db().save(self._user_dict)

    def get_readings(self):
        """Find my readings.
        
        :rtype: list of readings
        """
        return _get_db().readings.find({'user_id': self.id})

    @staticmethod
    def find(open_id=None, user_id=None):
        """Lookup a user by either Open ID or user ID.
        
        :param str open_id: Open ID.
        :param str user_id: Internal user identifier.
        :rtype: :py:class:`.User`
        :raises: :py:class:`ParameterError` if neither parameter is provided
        """
        query = {}
        if open_id is not None:
            query['open_id'] = open_id
        if user_id is not None:
            query['_id'] = user_id
        if len(query) == 0:
            raise ParameterError('either open_id or user_id must be supplied')
        user = None
        db = _get_db()
        user_dict = db.users.find_one(query)
        if user_dict is None:
            readit.app.logger.debug('user not found for %s', str(query))
        else:
            user = User()
            user._user_dict = user_dict.copy()
        return user
    def __str__(self):
        return '<{0}.{1} id={2} openid={3}>'.format(self.__module__,
                self.__class__.__name__, self.id, self.open_id)


