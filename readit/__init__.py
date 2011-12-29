import os
import StringIO
import flask



application = flask.Flask(__name__)

class Configuration(object):
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = 5000
        self.debug = True
        self.mongo_url = 'mongodb://localhost/'



@application.route('/config')
def fetch_read_list():
    response = StringIO.StringIO()
    response.write('<html><head><title>Settings</title></head><body>')
    response.write('<table>')
    for (k, v) in os.environ.iteritems():
        response.write('<tr><th>')
        response.write(k)
        response.write('</th><td>')
        response.write(v)
        response.write('</td></tr>')
    response.write('</table></body></html>')
    return response.getvalue()


def run(config):
    application.run(host=config.host, port=config.port, debug=config.debug)

