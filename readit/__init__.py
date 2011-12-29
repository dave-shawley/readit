import os
import StringIO
import flask


application = flask.Flask(__name__)
application.HOST = '0.0.0.0'
application.PORT = 5000


@application.route('/')
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


