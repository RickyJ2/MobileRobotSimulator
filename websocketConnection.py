import asyncio
import logging
import threading
from client import Client
from config import IP, PORT
from tornado import httpclient
from tornado.ioloop import IOLoop, PeriodicCallback

class WebsocketConnection:
    def __init__(self, id, clientOnMsg, sendAGVState):
        header = {
            'id': f'{id}'
        }
        self.id = id
        self.req = httpclient.HTTPRequest(f"ws://{IP}:{PORT}/agv", headers=header)
        self.client: Client = Client(self.req, 5)
        self.clientOnMsg = clientOnMsg
        self.sendAGVState = sendAGVState
        self.runThread = False
        self.thread = None
        self.ioloop = None
    
    def run(self):
        self.runThread = True
        self.thread = threading.Thread(target=self._start, name=f"AGV-{self.id}", daemon=True)
        self.thread.start()
    
    def _start(self):
        logging.info(f"AGV-{self.id} started")
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.ioloop = IOLoop.current()
        asyncio.ensure_future(self.client.connect(self.clientOnMsg))
        PeriodicCallback(self.sendAGVState, 1000).start()
        self.ioloop.start()
    
    def send(self, msg):
        self.client.send(msg)
    
    def close(self):
        self.client.closeConnection()
        self.runThread = False
        self.ioloop.stop()
        if not (self.thread is None):
            self.thread.join()