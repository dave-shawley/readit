import flask


application = flask.Flask(__name__)
DEFAULT_CONFIG = {
        'host': '0.0.0.0',
        'port': 5000,
        'debug': False,
        }

@application.route('/')
def fetch_read_list():
    return "You ain't read nothin!"


def get_defaults():
    return DEFAULT_CONFIG.copy()

def run(config):
    application.run(host=config['host'], port=config['port'],
            debug=config['debug'])

