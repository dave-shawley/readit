import os
import flask


app = flask.Flask('readit')
app.secret_key = 'My really secure secret key'

class Configuration(object):
    def __init__(self):
        self.host = os.environ.get('HOST', '0.0.0.0')
        self.port = int(os.environ.get('PORT', '5000'))
        value = os.environ.get('DEBUG', 'False').lower()
        self.debug = value == 'true' or value == '1'
        self.mongo_url = os.environ.get('MONGOURL', 'mongodb://localhost/readit')
    def values(self):
        return {'HOST': self.host, 'PORT': self.port, 'DEBUG': self.debug,
                'MONGO_URL': self.mongo_url}




@app.route('/config')
def dump_configuration():
    if not app.config['DEBUG']:
        flask.abort(403)
    return flask.render_template('config.html', environ=os.environ)

