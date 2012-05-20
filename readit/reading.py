import datetime
import uuid

from .storage import StorableItem


class Reading(StorableItem):
    """I represent something that a :py:class:`~readit.User` has read.
    
    A reading is little more than a display name, a link, and a timestamp.
    Equality is based on the name and link and the properties are all simple
    properties with full read+write access.
    
    >>> r = Reading('<Title>', '<Link>')
    >>> r.title, r.link
    ('<Title>', '<Link>')
    >>> r == Reading('<Title>', '<Link>')
    True
    
    The other interesting property of an item that the user has read is
    when it was read.  This is tracked by my ``when`` attribute which is
    a :py:class:`~datetime.datetime` instance but can specified as a
    ISO-8601 encoded string as well.
    
    >>> when = '2012-03-24T11:56:48Z'
    >>> r = Reading('<Title>', '<Link>', when)
    >>> r.when
    datetime.datetime(2012, 3, 24, 11, 56, 48)
    >>> when = datetime.datetime.utcnow()
    >>> r = Reading('<Title>', '<Link>', when)
    >>> r.when == when
    True
    
    I also act as a simple value type that is comparable for equality and
    hashable.  This property allows me to be safely inserted into lists and
    sets.
    
    >>> r1 = Reading('<Title>', '<Link>')
    >>> a_set = set()
    >>> a_set.add(r1)
    >>> len(a_set)
    1
    >>> a_set.add(r1)
    >>> len(a_set)
    1
    >>> a_set.remove(Reading('<Title>', '<Link>'))
    >>> len(a_set)
    0
    
    The final interesting attribute is that I have a unique identifying
    string that you can access with the :py:attr:`~readit.Reading.id`
    attribute.  If you do not assign one, I will gladly create a GUID-based
    identifier.  You can overwrite the identifier freely and it does not
    factor into my view of equality.
    
    >>> r2 = Reading('<Title>', '<Link>')
    >>> r1 == r2 and r1._id != r2._id
    True
    >>> r1._id = r2._id
    >>> r1 == r2 and r1._id == r2._id
    True
    """

    _PERSIST = ['_id', 'title', 'link', 'when']

    def __init__(self, title=None, link=None, when=None):
        super(Reading, self).__init__()
        self.title = title
        self.link = link
        self.when = when or datetime.datetime.utcnow()
        self._id = str(uuid.uuid4())

    @property
    def when(self):
        return self._when

    @when.setter
    def when(self, value):
        if isinstance(value, (str, unicode)):
            dt_string, rest = value[0:19], value[19:]
            value = datetime.datetime.strptime(dt_string, '%Y-%m-%dT%H:%M:%S')
        self._when = value

    def __eq__(self, other):
        return self is other or (self.title == other.title and
                                 self.link == other.link)

    def __str__(self):
        return ('<Reading [id={0._id} title={0.title}, '
                'link={0.link}]>'.format(self))

    def __hash__(self):
        return 3 + (hash(self.title) * 5) + (hash(self.link) * 7)

