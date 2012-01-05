import datetime

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
    >>> r.title, r.link, r.when
    (None, None, None)
    
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
    """
    def __init__(self):
        self._title = StringAttribute()
        self._link = StringAttribute()
        self._when = DateTimeAttribute()
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()

