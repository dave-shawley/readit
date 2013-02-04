import datetime


class Reading(object):
    """I represent something that a :py:class:`~readit.User` has read.
    
    A reading is little more than a display name, a link, and a timestamp.
    Equality is based on the name and link and the properties are all simple
    properties with full read+write access.
    
    >>> r = Reading('<Title>', '<Link>')
    >>> r.title, r.link
    ('<Title>', '<Link>')
    >>> r == Reading('<Title>', '<Link>')
    True

    My ``user_id`` attribute is used to tie this reading instance with a
    specific user.  After all, my primary purpose is to associated a user
    with something that was read.  Since this is persisted, I need to
    guarantee that the value is round-trippable through the persistence
    layer so I coerce it to a string before passing it along.  You shouldn't
    need to concern yourself with this implementation detail unless you
    plan on comparing my ``user_id`` attribute to something.

    >>> r = Reading('<Title>', '<Link>')
    >>> any_instance = object()
    >>> r.user_id = any_instance
    >>> r.user_id != any_instance
    True
    >>> r.user_id == str(any_instance)
    True

    The other interesting property of an item that the user has read is
    when it was read.  This is tracked by my ``when`` attribute which is
    a :py:class:`~datetime.datetime` instance but can specified as a
    ISO-8601 encoded string as well.  However, ``datetime`` instances
    have the sub-second portion dropped.
    
    >>> when = '2012-03-24T11:56:48Z'
    >>> r = Reading('<Title>', '<Link>', when)
    >>> r.when
    datetime.datetime(2012, 3, 24, 11, 56, 48)
    >>> now = datetime.datetime.utcnow()
    >>> r = Reading(title='<Title>', link='<Link>', when=now)
    >>> r.when == (now - datetime.timedelta(microseconds=now.microsecond))
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
    """

    def __init__(self, title=None, link=None, when=None, user=None):
        super(Reading, self).__init__()
        self.object_id = None
        self._user_id = None
        self.title = title
        self.link = link
        self.when = when or datetime.datetime.utcnow()
        if user is not None:
            self.user_id = user.object_id

    @property
    def when(self):
        return self._when

    @when.setter
    def when(self, value):
        if isinstance(value, (str, unicode)):
            dt_string, rest = value[0:19], value[19:]
            value = datetime.datetime.strptime(dt_string, '%Y-%m-%dT%H:%M:%S')
        self._when = value - datetime.timedelta(microseconds=value.microsecond)

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        if value is None:
            self._user_id = None
        else:
            self._user_id = str(value)

    def to_persistence(self):
        return {'title': self.title, 'link': self.link, 'when': self.when,
                'user_id': self._user_id}
    
    @classmethod
    def from_persistence(cls, persist_dict):
        # requires all attributes
        instance = cls()
        instance.title = persist_dict['title']
        instance.link = persist_dict['link']
        instance.when = persist_dict['when']
        instance._user_id = persist_dict['user_id']
        return instance

    def __eq__(self, other):
        if self is other:
            return True
        if other is None:
            return False
        return self.title == other.title and self.link == other.link

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return ('<Reading [id={0.object_id} title={0.title}, '
                'link={0.link}]>'.format(self))

    def __hash__(self):
        return (3 + hash(self.title)) + (5 * hash(self.link))

