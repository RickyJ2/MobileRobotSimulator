import logging
from tornado.websocket import websocket_connect, WebSocketClosedError, WebSocketClientConnection

class Client(object):
    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout
        self.ws: WebSocketClientConnection = None
        self.tryingConnecting : bool = False

    async def connect(self, onMsg = None):
        if not (onMsg is None):
            self.onMsg = onMsg
        if(self.tryingConnecting):
            return
        logging.info("Trying to connect to server...")
        try:
            self.tryingConnecting = True
            self.ws = await websocket_connect(self.url, on_message_callback=self.onMsg)
        except Exception as e:
            self.tryingConnecting = False
            logging.error(f"connection error: {e}")
        else:
            self.tryingConnecting = False
            logging.info("Connected to Server")

    def send(self, msg):
        if self.ws is None:
            self.connect()
        else:
            try:
                self.ws.write_message(msg)
            except WebSocketClosedError:
                self.connect()
            except Exception as e:
                logging.error(f"Websocket Error: {e}")
                logging.error(f"error msg: {msg}")

    def closeConnection(self):
        if self.ws is None:
            return
        self.ws.close()
