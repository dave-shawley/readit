import os
import StringIO
import flask



application = flask.Flask(__name__)

class Configuration(object):
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = 5000
        self.debug = False
        self.mongo_url = 'mongodb://localhost/'
        self.enable_config = False

class Response(StringIO.StringIO):
    def add_table(self, name, data):
        self.write('<table><caption><h2>' + name + '</h2></caption>')
        for (k, v) in data.iteritems():
            self.write('<tr><th>')
            self.write(k)
            self.write('</th><td>')
            self.write(v)
            self.write('</td></tr>')
        self.write('</table>')


@application.route('/config')
def fetch_read_list():
    response = Response()
    response.write('<html><head><title>Settings</title></head><body>')
    response.add_table('application.config', application.config)
    response.add_table('os.environ', os.environ)
    response.write('</body></html>')
    return response.getvalue()


def run(config):
    application.run(host=config.host, port=config.port, debug=config.debug)

