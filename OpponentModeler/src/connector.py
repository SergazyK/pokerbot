import tornado.ioloop
import tornado.web
import os
import socket
from contextlib import closing
import subprocess

from subprocess import Popen
def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class PortHandler(tornado.web.RequestHandler):
    def get(self):
        port = find_free_port()
        p = Popen(['pypokergui','serve','/Users/home/PycharmProjects/pokerbot/OpponentModeler/src/config.yaml','--port',str(port)])
        self.write(str(port))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/get_port", PortHandler)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()