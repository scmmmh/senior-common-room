from tornado.websocket import WebSocketHandler


class ClientAPIHandler(WebSocketHandler):
    def open(self):
        # print("WebSocket opened")
        pass

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        # print("WebSocket closed")
        pass
