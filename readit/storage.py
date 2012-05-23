import functools

from .helpers import deprecated


class MoreThanOneResultError(LookupError):
    """Raised by :py:meth:`Storage.retrieve_one` when more than one object
    is found."""
    pass


class StorableItem(object):
    """Helpful base class for items that :py:class:`Storage` can store
    and retrieve.  :py:class:`Storage` instances work solely on dictionary
    instances under the hood.  This class provides the under-pinnings to
    easily serialize and deserialize object instances to and from simple
    dictionaries.
    
    It is easy to create storable classes based on this class.  Simply
    use it as a base class and add a :py:attr:`_PERSIST` class attribute
    that is a list of the instance attributes to store.  The ``Storage``
    instance will use the :py:meth:`to_persistence` and
    :py:meth:`from_persistence` methods which will, in turn, use the
    :py:attr:`_PERSIST` attribute.
    
    >>> class Point(StorableItem):
    ...   _PERSIST = ['x', 'y']
    ...   def __init__(self, x, y):
    ...     super(Point, self).__init__()
    ...     self.x = x
    ...     self.y = y
    ...
    >>> a_point = Point(3, 4)
    >>> a_point.to_persistence() == {'x': 3, 'y': 4}
    True
    
    You can also take advantage of the variable argument list of my
    constructor and skip the ``_PERSIST`` attribute altogether.
    
    >>> class Point(StorableItem):
    ...   def __init__(self, x, y):
    ...     super(Point, self).__init__('x', 'y')
    ...     self.x, self.y = x, y
    ...
    >>> a_point = Point(3, 4)
    >>> a_point.to_persistence() == {'x': 3, 'y': 4}
    True
    """

    def __init__(self, *persist):
        super(StorableItem, self).__init__()
        self._PERSIST = getattr(self.__class__, '_PERSIST',
                list(persist))[:]

    def __get_persistable_properties(self):
        return set(self._PERSIST or
                   filter(lambda x: not x.startswith('_'),
                          self.__dict__.keys()))

    def to_persistence(self):
        """Return a dictionary of persistable attributes."""
        value_dict = {}
        for name in self.__get_persistable_properties():
            value_dict[name] = getattr(self, name, None)
        return value_dict

    def from_persistence(self, value_dict):
        """Update :py:obj:`self` based on the persistence dictionary."""
        valid_props = self.__get_persistable_properties()
        for name in set(value_dict.keys()) and valid_props:
            setattr(self, name, value_dict[name])

    def __eq__(self, other):
        """Storable instances only care about their persistent
        representation, so that defines equality."""
        return self.to_persistence() == other.to_persistence()


#
#    """I save object states as simple :py:class:`dict` instances.
#
#    Instances are stored in sets that are identified by a *bin*
#    A item is stored using the :py:meth:`save` method to
#    store the item's state in the named bin.  Once it has been stored,
#    it can be retrieved with either the :py:meth:`retrieve` method or the
#    :py:meth:`retrieve_one` method.  You can always call :py:meth:`retrieve`
#    since it returns the contents of a bin as an iterable.
#    If you are expecting (or require) that the result of retrieving an
#    item from a *bin* identifies
#    a singular item, then you can call :py:meth:`retrieve_one` which will
#    raise an exception if more than one such item exists.
#
#    It is important to note that the object instances themselves are not
#    stored.  Instead, the instance's *state* is stored.  The state is a
#    simple ``dict`` instance that is passed into :py:meth:`save` as:
#
#    1. the keyword argument list or
#    2. a ``dict`` instance or
#    3. an instance that implements the :py:class:`StorableItem` protocol
#
#    In any case, the ``dict`` instance is what is saved off.  This is also
#    what is returned from :py:meth:`retrieve` and :py:meth:`retrieve_one`.
#    """
