"""
Reading related Classes
=======================

"""
import datetime
import flask
import readit


class StringAttribute(object):
    """Attribute that coerces everything into a unicode value.
    
    >>> s = StringAttribute()
    >>> s.value is None
    True
    >>> s.value = 1
    >>> s.value
    u'1'
    >>> s.value = 'one'
    >>> s.value
    u'one'
    >>> str(s)
    'one'
    """
    def __init__(self, value=None):
        self._value = None
        self.set_value(value)
    def get_value(self):
        return self._value
    def set_value(self, value):
        if value is None:
            self._value = None
        else:
            self._value = unicode(value)
    value = property(get_value, set_value)
    def __str__(self):
        return str(self._value)
    def __unicode__(self):
        return unicode(self._value)

class DateTimeAttribute(object):
    """An attribute that requires a datetime value.
    
    >>> d = DateTimeAttribute()
    >>> d.value is None
    True
    >>> d.value = datetime.datetime(2012, 1, 1, 0, 0, 0)
    >>> str(d)
    '2012-01-01T00:00:00'
    >>> unicode(d)
    u'2012-01-01T00:00:00'
    >>> d.value
    datetime.datetime(2012, 1, 1, 0, 0)
    >>> d.value = '2012-01-01'
    Traceback (most recent call last):
    ...
    TypeError: value is required to be a datetime instance
    """
    def __init__(self, value=None):
        self._value = None
        self.set_value(value)
    def get_value(self):
        return self._value
    def set_value(self, value):
        if value is None:
            self._value = None
        elif isinstance(value, DateTimeAttribute):
            self._value = value._value
        elif isinstance(value, datetime.datetime):
            self._value = value
        else:
            raise TypeError('value is required to be a datetime instance')
    value = property(get_value, set_value)
    @staticmethod
    def now():
        return DateTimeAttribute(datetime.datetime.now())
    def __str__(self):
        if self._value is None:
            return str(None)
        return self._value.isoformat()
    def __unicode__(self):
        return unicode(str(self))


class Reading(object):
    """I represent something that has been read.
    
    The Read It application tracks blog posts, articles, or web pages that
    have been read and when they were read.  This isn't really the same as
    a bookmarking service since bookmarks are usually something *to be read*
    or reference material.
    
    A ``Reading`` instance includes little more than the minimal information
    needed for the application.  By default, all of the attributes are set
    to ``None``.
    
    >>> r = Reading()
    >>> r.id, r.title, r.link, r.when
    (None, None, None, None)
    
    The attributes are simple data attributes.  The :py:attr:`title` and
    :py:attr:`link` attributes are strings and the :py:attr:`when` attribute
    is a :py:class:`~datetime.datetime` instance.
    
    >>> r.title = 1
    >>> r.title
    u'1'
    >>> r.link = u'some link'
    >>> r.link
    u'some link'
    >>> r.when = '11/11/2011'
    Traceback (most recent call last):
    ...
    TypeError: value is required to be a datetime instance
    >>> r.when = datetime.datetime(2011, 11, 11, 0, 0, 0)
    >>> r.when
    datetime.datetime(2011, 11, 11, 0, 0)
    >>> str(r.when)
    '2011-11-11 00:00:00'
    
    The :py:attr:`id` attribute is the unique identifier from the persistence
    layer.  It should only be created by the persistence layer and should be
    undefined if this object has never been persisted.
    
    Reading instances can also be initialized by passing keyword arguments
    into the initializer.
    
    >>> r = Reading(title='a title', link='http://foo.com')
    >>> r.title, r.link, r.when
    (u'a title', u'http://foo.com', None)
    """
    def __init__(self, title=None, link=None, when=None):
        self._id = None
        self._title = StringAttribute(title)
        self._link = StringAttribute(link)
        self._when = DateTimeAttribute(when)
    @classmethod
    def from_dict(cls, a_dict):
        """Creates a new instance from a dictionary.
        
        The dictionary is required to contain entries for the :py:attr:`title`,
        :py:attr:`link`, and :py:attr:`when` attributes.  If it does not, then
        a :py:class:`KeyError` will be raised.

        >>> inst = Reading.from_dict({})
        Traceback (most recent call last):
        ...
        KeyError: 'title'
        """
        an_instance = cls()
        an_instance._id = a_dict.get('_id')
        an_instance.title = a_dict['title']
        an_instance.link = a_dict['link']
        an_instance.when = a_dict['when']
        return an_instance
    @property
    def id(self):
        return self._id
    def _get_title(self):
        return self._title.value
    def _set_title(self, value):
        self._title.value = value
    def _get_link(self):
        return self._link.value
    def _set_link(self, value):
        self._link.value = value
    def _get_when(self):
        return self._when.value
    def _set_when(self, value):
        self._when.value = value
    title = property(_get_title, _set_title)
    link = property(_get_link, _set_link)
    when = property(_get_when, _set_when)

