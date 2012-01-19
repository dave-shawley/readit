"""
Persistence Layer
=================

This module provides a somewhat pluggable persistence abstraction.  The
chosen implementation class is exported as the :py:class:`.Persistence`
class.

Mongo Persistence API
---------------------

"""
import datetime
import pymongo, pymongo.objectid
import readit


class MongoPersistence(object):
    """
    I am a connection to the MongoDB persistence layer.
    """
    def __init__(self):
        self._url = readit.app.config['MONGO_URL']
        self._mongo = None
        self._logger = readit.app.logger
    def find_user(self, open_id=None, user_id=None):
        """Lookup a user by either OpenID or user ID.
        
        :param str open_id: OpenID.
        :param str user_id: Internal user identifier.
        :rtype: :py:class:`dict`
        :raises: :py:class:`readit.ParameterError` if neither parameter is
                 provided
        """
        query = {}
        if open_id is not None:
            query['open_id'] = open_id
        if user_id is not None:
            query['_id'] = user_id
        if len(query) == 0:
            raise readit.ParameterError('either open_id or user_id must '
                    'be supplied to find_user')
        return self.mongo.users.find_one(query)
    def save_user(self, user_dict):
        """Write a user document."""
        self.mongo.users.save(user_dict)
    def find_readings(self, user_id):
        return self.mongo.readings.find({'user_id': user_id})
    def add_reading(self, user_id, title, link):
        """Add a reading for a user.
        
        :param str user_id:
        :param str title:
        :param str link:
        :rtype: the document that was inserted as a dict
        """
        doc = { 'title': title, 'link': link,
                'user_id': pymongo.objectid.ObjectId(user_id),
                'when': datetime.datetime.utcnow() }
        self.mongo.readings.insert(doc, safe=True)
        doc['_id'] = str(doc['_id'])
        doc['user_id'] = str(doc['user_id'])
        return doc
    def remove_reading(self, user_id, reading_id):
        """Remove a specific reading.
        
        :param str user_id: the Mongo ObjectId of the user
        :param str reading_id: the Mongo ObjectId of the reading to remove
        """
        key = { 'user_id': pymongo.objectid.ObjectId(user_id),
                '_id': pymongo.objectid.ObjectId(reading_id) }
        response = self.mongo.readings.remove(key, safe=True)
        if response['n'] == 0:
            raise readit.NotFoundError(key)
        readit.app.logger.debug(response)
    @property
    def mongo(self):
        """Retrieve the MongoDB connection instance."""
        if self._mongo is None:
            self._logger.debug('connecting to %s', self._url)
            self._mongo = pymongo.connection.Connection(host=self._url)
            if self._mongo:
                self._mongo = self._mongo.readit
        return self._mongo
    def close(self):
        """Close the MongoDB connection instance."""
        if self._mongo is not None:
            self._logger.debug('closing connection %s', self._mongo)
            self._mongo.connection.close()
            self._mongo = None

# export the interface
Persistence = MongoPersistence

