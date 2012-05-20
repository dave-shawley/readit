import functools
import inspect
import warnings

import flask


def is_redirect(response):
    return (300 <= response.status_code < 400 and
            response.status_code != 304 and
            'location' in response.headers)


def wants_json(request):
    product_types = ['application/json', 'text/html', 'application/xhtml']
    requested = request.accept_mimetypes.best_match(product_types,
            'text/html')
    return any(requested.endswith(x) for x in ['/json', '+json'])


def deprecated(func):
    @functools.wraps(func)
    def decorated(*any, **args):
        warnings.warn('Call to deprecated function ' +
                func.__module__ + '.' + func.__name__,
                category=DeprecationWarning)
        return func(*any, **args)
    return decorated


class LinkMap(object):
    """I maintain a map of hypermedia actions.
    
    You can append to the list of actions using the :py:func:`advertise`
    decorator on a Flask view function.
    """
    def __init__(self):
        super(LinkMap, self).__init__()
        self._links = {}

    def advertise(self, *advertisement_info):
        """Decorate a function as an advertised link.
        
        :param advertisement_info: a list of (link-name, method) tuples to
            advertise the route as or a single (link-name, method) pair
        
        If ``advertisement_info`` contains two string instances, then a single
        advertisement is added.  Otherwise, the argument is a list of tuples.
        
        >>> link_map = LinkMap()
        >>> @link_map.advertise('foo', 'GET')
        ... def foo(): pass
        ...
        >>> link_map._links['foo']['function']
        'foo'
        >>> link_map._links['foo']['args']
        []
        >>> link_map._links['foo']['method']
        'GET'
        >>> @link_map.advertise(('get-foo', 'GET'), ('put-foo', 'PUT'))
        ... def foo(): pass
        ...
        >>> link_map._links['get-foo']['function']
        'foo'
        >>> link_map._links['get-foo']['method']
        'GET'
        >>> link_map._links['put-foo']['function']
        'foo'
        >>> link_map._links['put-foo']['method']
        'PUT'
        """
        def decorator(func):
            if (len(advertisement_info) == 2 and
                    isinstance(advertisement_info[0], str) and
                    isinstance(advertisement_info[1], str)):
                name, method = advertisement_info
                self._links[name] = {'method': method,
                        'function': func.__name__,
                        'args': inspect.getargspec(func).args}
            else:
                for (name, method) in advertisement_info:
                    self._links[name] = {'method': method,
                            'function': func.__name__,
                            'args': inspect.getargspec(func).args}
            return func
        return decorator

    def build_link(self, link_name, **args):
        """Create a link object for ``link_name`` based on the current flask
        environment.
        
        :param link_name: the name of the link as registered with
            :py:meth:`advertise`
        :param args: any arguments required by the flask endpoint that was
            advertised
        
        :exception RuntimeError: if this is run outside of a Flask request
            context
        :exception KeyError: if ``link_name`` is not a registered link
        """
        link_obj = self._links[link_name]
        return {'method': link_obj['method'],
                'url': flask.url_for(link_obj['function'], **args)}

    @property
    def links(self):
        """A dict mapping link names to link objects.  A *link object* is
        nothing more than a dictionary containing the method and URL to
        apply it to."""
        links = {}
        for (link_name, link_dict) in self._links.iteritems():
            args = dict()
            for arg in link_dict['args']:
                if arg == 'session_key':
                    if flask.g.user.logged_in:
                        args['session_key'] = flask.g.user.session_key
                else:  # pragma: no cover
                    self.logger.warn('unhandled argument %s in link %s',
                            arg, link_name)
            if len(args) == len(link_dict['args']):
                links[link_name] = self.build_link(link_name, **args)
        return links

