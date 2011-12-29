import os
import flask


application = flask.Flask(__name__)

@application.route('/')
def fetch_read_list():
    return "You ain't read nothin!"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)

