import json
import logging
import math
from point import Point, dictToPoint
from pose import Pose
from robot import Robot
from util import distance, findOrientation
from websocketConnection import WebsocketConnection

IDLE = 0
FOLLOW_PATH = 1
WAIT_PATH = 2

class AGV:
    def __init__(self, id):
        self.id = id
        self.state = IDLE

        self.errorTolerance = 5

        self.power = 100
        self.container = False
        self.websocket = WebsocketConnection(id, self.clientOnMsg, self.sendAGVState)
        
        self.robot: Robot = None
        self.startCoordinate: Point = Point(0,0)
        self.goalPointList: list[Point] = []
        self.pathList: list[list[Point]] = []
        self.currentGoal: Point = None
        self.currentPath: list[Point] = []
        self.currentTargetPose: Pose = None
    
    def reducePower(self):
        self.power -= self.robot.getVelocity() * 0.001

    def init(self, robot):
        self.robot = robot
    
    def connectWebsocket(self):
        self.websocket.run()

    def disconnectWebsocket(self):
        self.websocket.close()

    def clientOnMsg(self, msg):
        if msg is None:
            return
        msg = json.loads(msg)
        logging.info(msg)
        type = msg["type"]
        data = msg["data"]
        if type == "position":
            self.setStartCoordinate(dictToPoint(data))
        elif type == "path":
            path = map(dictToPoint, data["path"])
            self.insertGoal(dictToPoint(data["goal"]))
            self.insertPath(list(path))
    
    def sendAGVState(self):
        msg = {
            "type": "state",
            "data": self.getRobotState()
        }
        self.websocket.send(json.dumps(msg))
    
    def sendNotifReachPoint(self):
        msg = {
            "type": "notif",
        }
        self.websocket.send(json.dumps(msg))

    def run(self):
        try:
            if self.stateIs(IDLE):
                if self.noGoal():
                    if self.robot.getVelocity() > 0:
                        self.stopMoving()
                else:
                    self.updateNewGoal()
                    self.updateState(FOLLOW_PATH)
            elif self.stateIs(FOLLOW_PATH):
                if self.isReachTargetPoint():
                    self.stopMoving()
                    self.updateTargetPoint()
                    self.sendNotifReachPoint()
                    if self.isReachGoal():
                        self.clearFollowPathParams()
                        self.updateState(IDLE)
                elif self.isCurrentTargetPointNone():
                    self.updateTargetPoint()
                else:
                    self.steerToTargetPoint()
        except Exception as e:
            logging.error(e)

    def clearFollowPathParams(self):
        self.currentTargetPose = None
        self.currentGoal = None
        self.currentPath = []
    
    def noGoal(self) -> bool:
        return len(self.goalPointList) == 0   
    
    def updateNewGoal(self):
        self.currentGoal = self.goalPointList.pop(0)
        self.currentPath = self.pathList.pop(0)

    def changeCurrentPath(self, path: list[Point]):
        self.currentPath = path
        self.updateTargetPoint()

    def updateTargetPoint(self):
        if len(self.currentPath) == 0:
            return
        self.currentTargetPose = Pose(self.currentPath.pop(0), 0)
        if len(self.currentPath) == 0:
            self.currentTargetPose.orientation = math.pi
        else:
            self.currentTargetPose.orientation = findOrientation(self.currentPath[0], self.currentTargetPose)
        logging.info(f"current Target point: {self.currentTargetPose.point.toDict()}")

    def isReachGoal(self) -> bool:
        currentPos: Pose = self.robot.getPos()
        return distance(currentPos, self.currentGoal) < self.errorTolerance
    
    def isReachTargetPoint(self) -> bool:
        if self.currentTargetPose is None:
            return False
        currentPos:Pose = self.robot.getPos()
        return distance(currentPos, self.currentTargetPose) < self.errorTolerance

    def isCurrentPathEmpty(self) -> bool:
        return len(self.currentPath) == 0

    def isCurrentTargetPointNone(self) -> bool:
        return self.currentTargetPose is None

    def stateIs(self, state) -> bool:
        return self.state == state

    def updateState(self, state):
        logging.info(f"State changed from {self.state} to {state}")
        self.state = state
    
    def setStartCoordinate(self, point: Point):
        self.startCoordinate = point
    
    def insertGoal(self, goal: Point):
        self.goalPointList.append(goal)

    def insertPath(self, path: list[Point]):
        self.pathList.append(path)

    def getRobotState(self) -> dict:
        pos: Pose = self.robot.getPos()
        return {
            "container": self.container,
            "power": round(self.power),
            "orientation": math.degrees(pos.orientation),
            "velocity": self.robot.getVelocity(),
            "position": pos.point.toDict(),
        }
    
    def stopMoving(self):
        logging.info("Stop moving")
        self.robot.stop()
    
    def steerToTargetPoint(self):
        currentPos = self.robot.getPos()
        self.currentTargetPose.orientation = findOrientation(self.currentTargetPose.point, currentPos)
        v, omega = self.LyapunovControl(currentPos, self.currentTargetPose)
        self.robot.setSpeed(v, omega)

    def LyapunovControl(self, startPoint: Pose, targetPoint: Pose) -> tuple[float, float]:
        errorX = targetPoint.point.x - startPoint.point.x
        errorY = targetPoint.point.y - startPoint.point.y
        errorTheta = targetPoint.orientation - startPoint.orientation
        k1 = 1
        k2 = 0.8
        if errorTheta > math.pi:
            errorTheta -= 2 * math.pi
        elif errorTheta < -math.pi:
            errorTheta += 2 * math.pi
        if errorTheta > math.pi/6 or errorTheta < -math.pi/6:
            return 0, k2 * errorTheta
        v = k1 * (errorX * math.cos(startPoint.orientation) + errorY * math.sin(startPoint.orientation))
        omega = k2 * errorTheta

        return v, omega