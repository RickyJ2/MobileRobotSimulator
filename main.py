import asyncio
import json
import logging
from simulation import Simulation
from client import Client
from config import IP, PORT, ID
from tornado import httpclient
from tornado.ioloop import IOLoop, PeriodicCallback
import threading
from point import dictToPoint

#CONSTANTS
IDLE = 0
FOLLOW_PATH = 1
WAIT_PATH = 2

header = {
    'id': f'{ID}'
}
request = httpclient.HTTPRequest(f"ws://{IP}:{PORT}/agv", headers=header)
client = Client(request, 5)

runMainThread = False
mainThread = None

def clientOnMsg(msg):
    if msg is None:
        return
    msg = json.loads(msg)
    logging.info(msg)
    type = msg["type"]
    data = msg["data"]
    if type == "position":
        pass
        # agv.setStartCoordinate(dictToPoint(data))
    elif type == "path":
        path = map(dictToPoint, data["path"])
        # agv.insertGoal(dictToPoint(data["goal"]))
        # agv.insertPath(list(path))

def sendAGVState():
    msg = {
        "type": "state",
        # "data": agv.getRobotState()
    }
    client.send(json.dumps(msg))

def sendNotifReachPoint():
    msg = {
        "type": "notif",
    }
    # ioloop.add_callback(client.send, json.dumps(msg)) #For calling in Thread

def websocket():
    asyncio.set_event_loop(asyncio.new_event_loop())
    ioloop = IOLoop.current()
    asyncio.ensure_future(client.connect(clientOnMsg))
    #call sendAGVState every 1 second
    PeriodicCallback(sendAGVState, 1000).start()
    ioloop.start()

def main():
    global runMainThread, mainThread
    runMainThread = True
    mainThread = threading.Thread(target=websocket, name="Websocket", daemon=True)
    mainThread.start()
    simulation = Simulation()
    simulation.run()
    client.closeConnection()
    mainThread.join()

if __name__ == '__main__':
    main()