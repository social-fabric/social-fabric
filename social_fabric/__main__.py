from gevent.pywsgi import WSGIServer
from ors_blockchain.app import app

def main():
    host = app.config['HOST']
    port = app.config['PORT']
    http_server = WSGIServer((host, port), app)
    http_server.serve_forever()

if __name__ == '__main__':
    main()