import tornado.ioloop

from .handlers.web import MainHandler


def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
    ], debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(6543)
    tornado.ioloop.IOLoop.current().start()
