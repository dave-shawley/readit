"""
User related Functions & Classes
================================

The main export from this module is the :py:class:`.User` class.  The user is
the core abstraction in this system.  It provides CRUD access to the list
of read items as well as class methods to locate and :py:class:`.User`
instances in the first place.

"""
import uuid


class User(object):
    """I represent a user that is registered in the system.
    
    I am identified by a unique ID value that is assigned by the underlying
    system when the user is created.  I have a few attributes of my own
    as well.  The unique ID is stored in :py:attr:`user_id` but is also
    available as :py:attr:`object_id`, more on that shortly.
    
    >>> u = User()
    >>> u.session_key, u.open_id, u.display_name, u.user_id, u.email
    (None, None, None, None, None)
    
    I also keep track of whether the user has been logged in to the system
    or not.  In this abstraction, the instance is considered to be *logged
    in* when a unique session key has been established and the :py:meth:`login`
    method has been called.  The user is logged in until the :py:meth:`logout`
    method is invoked.
    
    >>> u.logged_in
    False
    >>> class Details:
    ...    identity_url = 'http://open.id.identity/url'
    ...    fullname = "User's full name"
    ...    email = 'email@somewhere.com'
    ...
    >>> u.login(Details)
    >>> u.session_key is not None
    True
    >>> u.logged_in
    True
    >>> u.logout()
    >>> u.logged_in
    False
    
    The persistence aspects of a user are handled by implementing the expected
    StorableItem protocol using the :py:attr:`user_id` attribute as the unique
    identifier for a user.  This is why it is aliased as :py:attr:`object_id`.
    
    >>> u = User.from_persistence({'email': 'dave@example.com',
    ...   'display_name': 'Dave Shawley',
    ...   'openid': 'http://openid.net/me'})
    >>> persist = u.to_persistence()
    >>> persist['email'] == u.email
    True
    >>> persist['display_name'] == u.display_name
    True
    """

    def __init__(self, session_key=None):
        super(User, self).__init__()
        self.display_name = None
        self.email = None
        self.user_id = None
        self._session_key = session_key
        self._open_id = None
        self._readings = set()

    def login(self, details):
        """Update fields based on a successful login event.
        The user information is read from the fields of the ``details``
        instance.  The ``details`` object is required to define the
        following attributes:
        
          #. *identity_url*: this is used as the Open ID identity that is
             available from the :py:attr:`open_id` property.
          #. *email*: this is the email address associated with the
             Open ID
          #. *fullname*: this is the preferred display name
          #. *nickname*: if fullname is not set, then this is used as the
             display name
        
        The only attribute that is absolutely required to have a value is
        ``identity_url``.  The other attributes can be safely set to
        ``None``.
        
        >>> class SampleDetails:
        ...    identity_url = 'http://open.id.identity/url'
        ...    fullname, nickname, email = None, None, None
        ...
        >>> u = User()
        >>> u.login(SampleDetails)
        >>> u.open_id
        'http://open.id.identity/url'
        >>> u.display_name
        'http://open.id.identity/url'
        >>> u.email is None
        True
        
        The :py:attr:`display_name` attribute is derived from the three
        remaining fields in the order specified above.  The first one that
        is not ``None`` wins.
        
        >>> SampleDetails.email = 'daveshawley@gmail.com'
        >>> u.login(SampleDetails)
        >>> u.display_name
        'daveshawley@gmail.com'
        >>> SampleDetails.nickname = 'dave.shawley'
        >>> u.login(SampleDetails)
        >>> u.display_name
        'dave.shawley'
        >>> SampleDetails.fullname = 'Dave Shawley'
        >>> u.login(SampleDetails)
        >>> u.display_name
        'Dave Shawley'
        """
        if self._session_key is None:
            self._session_key = str(uuid.uuid4())
        self._open_id = details.identity_url
        self.display_name = (details.fullname or details.nickname or
                details.email or details.identity_url)
        self.email = details.email

    def logout(self):
        """Reset my fields and ensure that future reads of the
        :py:attr:`logged_in` property return ``False``.
        """
        self.display_name = None
        self.email = None
        self._open_id = None
        self._session_key = None

    @property
    def readings(self):
        """Answers the list of things that this user has read in
        chronological order starting with the most recently read item."""
        return sorted(self._readings, key=lambda r: r.when, reverse=True)

    def add_reading(self, reading):
        """Appends an item to the list of things that this user has read."""
        self._readings.add(reading)

    def remove_reading(self, reading):
        """Removes a reading from the user's list."""
        self._readings.remove(reading)

    @property
    def open_id(self):
        """The URL that is my identifying property.  This value is ``None``
        unless the user is logged in."""
        return self._open_id

    @property
    def session_key(self):
        return self._session_key

    @property
    def logged_in(self):
        """Is the user currently logged in?"""
        return self._session_key is not None

    def to_persistence(self):
        """Return a dictionary of attributes to persist."""
        return {'email': self.email, 'display_name': self.display_name}

    @classmethod
    def from_persistence(clazz, value_dict):
        instance = clazz()
        instance.email = value_dict['email']
        instance.display_name = value_dict.get('display_name', instance.email)
        return instance

    @property
    def object_id(self):
        return self.user_id

    @object_id.setter
    def object_id(self, value):
        self.user_id = str(value)

    def __str__(self):
        return (r'user <{0.user_id}, email={0.email}, '
                r'open_id={0.open_id}>').format(self)

