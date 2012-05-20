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


class Storage(object):
    """I save object states as simple :py:class:`dict` instances.
    
    Instances are stored in lists that are identified by a *bin* and a unique
    identifier (or *slot*).  The *bin* and *slot* form a coordinate system
    for stored items.  A item is stored using the :py:meth:`save` method to
    store the item's state in a named bin and slot.  Once it has been stored,
    it can be retrieved with either the :py:meth:`retrieve` method or the
    :py:meth:`retrieve_one` method.  You can always call :py:meth:`retrieve`
    since it returns the contents of a specific slot within the bin as a
    list.  If you are expecting (or require) that the slot and bin identifies
    a singular item, then you can call :py:meth:`retrieve_one` which will
    raise an exception if more than one item exists.
    
    It is important to note that the object instances themselves are not
    stored.  Instead, the instance's *state* is stored.  The state is a
    simple ``dict`` instance that is passed into :py:meth:`save` as:
    
    1. the keyword argument list or
    2. a ``dict`` instance or
    3. an instance that implements the :py:class:`StorableItem` protocol
    
    In any case, the ``dict`` instance is what is saved off.  This is also
    what is returned from :py:meth:`retrieve` and :py:meth:`retrieve_one`.
    """

    def __init__(self):
        self.bins = {}

    def save(self, storage_bin, storage_id, storable=None, **persist_values):
        """Add a single item to a slot in a bin.
        
        :param str storage_bin: the name of the bin to store the item into
        :param str storage_id: the slot id to store the item into
        :param storable: either a ``dict`` instance to store or something
            that implements the :py:class:`StorableItem` protocol
        :param persist_values: the state to store as keyword arguments
        
        This method accomodates a number of different usage patterns with
        different calling conventions.  You can pass either a ``dict`` or
        something that implements the :py:class:`StorableItem` protocol as
        the ``storable`` named parameter.  You can also pass the instance
        state to store as keyword parameters.
        
        >>> s = Storage()
        >>> s.save('bin', 'id', storable={'one': 1, 'two': 2})
        >>> s.retrieve_one('bin', 'id') == {'one': 1, 'two': 2}
        True
        >>> s.save('bin', 'another-id', one=1, two=2)
        >>> s.retrieve_one('bin', 'another-id') == {'one': 1, 'two': 2}
        True
        """
        if storable is not None:
            if not isinstance(storable, dict):
                storable = storable.to_persistence()
                print storable
        else:
            storable = persist_values
        self._add_to_bin(storage_bin, storage_id, storable)

    def retrieve(self, storage_bin, storage_id, factory=None, **constraint):
        """Retrieve zero or more matching elements from ``storage_bin``
        and ``storage_id``.
        
        :param str storage_bin: name of the storage bin to retrieve from
        :param str storage_id: identifier of the object to retrieve
        :param callable factory: callable to create new instances with.
            If this is not ``None``, then it will be called with zero
            arguments and should return an instance that implements the
            :py:class:`StorableItem` protocol.
        :param constraint: optional keyword arguments used to further
            constrain the result set
        :returns: the object from storage or ``default``
        
        If one ore more constraint keywords are included, then only
        instances that match *all* of the constraints are returned.
        """
        values = self.bins.get(storage_bin, {}).get(storage_id, [])
        if constraint:
            def matcher(obj):
                return all(obj[n] == v for n, v in constraint.iteritems())
            values = filter(matcher, values)
        if factory and values:
            create = functools.partial(self._create_from_factory, factory)
            values = map(create, values)
        return values

    def retrieve_one(self, storage_bin, storage_id, default=None,
            factory=None, **constraint):
        """Retrieve zero or one element from ``storage_bin`` matching
        ``storage_id``.  If no element is found, then ``default`` is
        returned.
        
        :param str storage_bin: name of the storage bin to retrieve from
        :param str storage_id: identifier of the object to retrieve
        :param callable factory: callable to create new instances with.
            If this is not ``None``, then it will be called with zero
            arguments and should return an instance that implements the
            :py:class:`StorableItem` protocol.
        :param constraint: optional keyword arguments used to further
            constrain the result set
        :returns: the object from storage or ``default``
        
        :raises MoreThanOneResultError: when more than one result exists"""
        inst = default
        values = self.retrieve(storage_bin, storage_id, **constraint)
        if values:
            if len(values) > 1:
                raise MoreThanOneResultError()
            inst = self._create_from_factory(factory, values[0])
        return inst

    def remove_all(self, storage_bin, storage_id):
        """Removes all elements matching ``storage_id`` from ``storage_bin``"""
        self.bins.get(storage_bin, {}).pop(storage_id, None)

    def remove(self, storage_bin, storage_id, value=None, **constraint):
        if value is not None:
            def matcher(obj):
                return obj == value
        elif constraint:
            def matcher(obj):
                return all(obj[n] == v for n, v in constraint.iteritems())
        else:
            def matcher(obj):
                return True
        values = self.bins.get(storage_bin, {}).get(storage_id, [])
        for value in filter(matcher, values):
            values.remove(value)
        self.bins[storage_bin][storage_id] = values

    @deprecated
    def remove_one(self, storage_bin, storage_id, value):
        self.remove(storage_bin, storage_id, value)

    def _add_to_bin(self, storage_bin, storage_id, persist_value):
        """Subclass method that stores a dictionary under the slot identified
        by ``storage_id`` in ``storage_bin``.
        """
        bin = self.bins.get(storage_bin, {})
        values = bin.get(storage_id, [])
        values.append(persist_value)
        bin[storage_id] = values
        self.bins[storage_bin] = bin

    def _create_from_factory(self, factory, value_dict):
        if factory:
            inst = factory()
            inst.from_persistence(value_dict)
            return inst
        return value_dict

