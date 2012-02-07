"""
User related Functions & Classes
================================

This module contains a handful of functions that are hooked into Flask
and a single class (:py:class:`.User`) that acts as the programmatic
interface.  A ``User`` object is a pretty simple CRUD wrapper over the
persistence layer with *business logic* methods that manipulate the
read item list associated with the user.

Examples
--------

A :py:class:`.User` instance is created without parameters so all of
its properties are initially empty.

>>> u = User()
>>> u.id, u.open_id, u.name, u.email
(None, None, None, None)

All of the properties are simple read/write properties except for
:py:attr:`.User.id` which is read-only (for obvious reasons).

>>> u.id = 'something'
Traceback (most recent call last):
...
AttributeError: can't set attribute
>>> u.open_id = 'foo'
>>> u.name = u'Dave Shawley'
>>> u.email = 42
>>> u.id, u.open_id, u.name, u.email
(None, 'foo', u'Dave Shawley', 42)

It might be a little surprising that there is really no enforcement of
type here, but `it is easier to ask for forgiveness than it is to get
permission <http://en.wikipedia.org/wiki/Grace_Hopper#Anecdotes>`_.

User API
--------

"""
import flask
import readit



class User(object):
    """I represent a user that is registered in the system.
    
    I am identified by a unique OpenID, have a few attributes like my
    email address and name, and have a list of things that I have read.
    The list of articles that I have read are available as
    :py:class:`~readit.Reading` instances from my :py:meth:`get_readings`
    method.
    """
    def __init__(self):
        self._user_dict = {}

    @property
    def id(self):
        """The unique identifier assigned to me by the persistence layer."""
        return self._user_dict.get('_id')

    def get_open_id(self):
        return self._user_dict.get('open_id')
    def set_open_id(self, open_id):
        self._user_dict['open_id'] = open_id
    open_id = property(get_open_id, set_open_id,
            doc="""My OpenID as a string.""")

    def get_name(self):
        return self._user_dict.get('name')
    def set_name(self, name):
        self._user_dict['name'] = name
    name = property(get_name, set_name,
            doc="""My display name.  This is either the full name from
                   the OpenID layer or the nickname.""")

    def get_email(self):
        return self._user_dict.get('email')
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
        flask.g.db.save_user(self._user_dict)

    def get_readings(self):
        """Find my readings.
        
        :rtype: list of :py:class:`~readit.Reading` instances
        """
        readings = []
        for doc in flask.g.db.find_readings(user_id=self.id):
            readit.app.logger.debug('found %s', str(doc))
            readings.append(readit.Reading.from_dict(doc))
        return readings

    def remove_reading(self, reading_id):
        """Remove a specific reading.
        
        :param str reading_id: the object ID of the reading
        """
        flask.g.db.remove_reading(self.id, reading_id)

    def add_reading(self, title, link):
        return flask.g.db.add_reading(self.id, title, link)

    @staticmethod
    def find(open_id=None, user_id=None):
        """Lookup a user by either OpenID or user ID.
        
        :param str open_id: OpenID.
        :param str user_id: Internal user identifier.
        :rtype: :py:class:`.User`
        :raises: :py:class:`readit.ParameterError` if neither parameter is
                 provided
        """
        user = None
        user_dict = flask.g.db.find_user(open_id, user_id)
        if user_dict is None:
            readit.app.logger.debug('user not found for %s',
                    str((open_id, user_id)))
        else:
            user = User()
            user._user_dict = user_dict.copy()
        return user

    def __str__(self):
        return '<{0}.{1} id={2} openid={3}>'.format(self.__module__,
                self.__class__.__name__, self.id, self.open_id)


def find(**kwds):
    return User.find(**kwds)

