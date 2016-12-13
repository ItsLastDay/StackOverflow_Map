from gevent.wsgi import WSGIServer
from tile_server import app

http_server = WSGIServer(('', 8000), app)
http_server.serve_forever()
