import unittest
import readit


class PersistenceTest(unittest.TestCase):
    def test_initialization(self):
        readit.app.config['MONGO_URL'] = 'some url'
        db = readit.Persistence()
        self.assertEqual('some url', db._url)

