import os
import os.path

import flask

import readit.flaskapp

if __name__ == '__main__':
    root = os.path.dirname(os.path.abspath(__file__))
    javascript_dir = os.path.join(root, 'javascript')
    if os.path.isdir(javascript_dir):
        @readit.flaskapp.app.route('/js/<path:filename>')
        def send_javascript(filename):
            return flask.send_from_directory(javascript_dir, filename)

        readit.flaskapp.app.run(debug=True, host='0.0.0.0')

