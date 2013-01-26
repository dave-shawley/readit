import os
import random

import mock
import flask

import readit

from .testing import ReaditTestCase


class HerokuTests(ReaditTestCase):
    """Tests related to the heroku python environment.
    
    The Heroku python stack communicates the run time parameters via
    environment variables.  This test makes sure that our application is
    honoring the environment settings so that we do not get any undue surprises
    at deployment time.
    """
    def setUp(self):
        super(HerokuTests, self).setUp()
        self.saved_env = os.environ.copy()
        self.saved_app = readit.app

    def tearDown(self):
        super(HerokuTests, self).tearDown()
        os.environ = self.saved_env
        readit.app = self.saved_app

    def test_host_env(self):
        os.environ['HOST'] = 'server.example.com'
        readit.app = readit.app.__class__()
        with readit.app.test_request_context('/'):
            self.assertEquals('server.example.com',
                    flask.current_app.config['HOST'])

    def test_port_env(self):
        os.environ['PORT'] = '6543'
        readit.app = readit.app.__class__()
        with readit.app.test_request_context('/'):
            self.assertEquals('6543', flask.current_app.config['PORT'])

    def test_debug_env(self):
        for truthy in ['True', 'T', '1', 'yes']:
            os.environ['DEBUG'] = truthy
            readit.app = readit.app.__class__()
            with readit.app.test_request_context('/'):
                self.assertEquals(True, flask.current_app.config['DEBUG'])
        for falsy in ['False', 'F', '0', 'no']:
            os.environ['DEBUG'] = falsy
            readit.app = readit.app.__class__()
            with readit.app.test_request_context('/'):
                self.assertEquals(False, flask.current_app.config['DEBUG'])

    @mock.patch('flask.Flask.run')
    def test_running(self, flask_run):
        os.environ['HOST'] = 'server.example.com'
        os.environ['PORT'] = str(random.randint(5000, 8000))
        os.environ['DEBUG'] = 'Yes'
        readit.app = readit.app.__class__()
        readit.app.run()
        flask_run.assert_called_once_with(
            host='server.example.com', port=int(os.environ['PORT']),
            debug=True)

    @mock.patch('flask.Flask.run')
    def test_keyword_args(self, flask_run):
        readit.app = readit.app.__class__()
        readit.app.run(host='my.host', port=6543, debug='SENTINEL')
        flask_run.assert_called_once_with(
            host='my.host', port=6543, debug='SENTINEL')

    @mock.patch('flask.Flask.run')
    def test_keyword_args_override_env_vars(self, flask_run):
        os.environ['HOST'] = 'server.example.com'
        os.environ['PORT'] = '8080'
        os.environ['DEBUG'] = 'No'
        readit.app = readit.app.__class__()
        readit.app.run(host='my.host', port=6543, debug='SENTINEL')
        flask_run.assert_called_once_with(
            host='my.host', port=6543, debug='SENTINEL')

