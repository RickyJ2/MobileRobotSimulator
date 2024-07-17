import json
import logging
import math
import pandas as pd
import os
from datetime import datetime
import uuid
from point import Point, dictToPoint
from pose import Pose
from robot import Robot
from util import distance, findOrientation
from websocketConnection import WebsocketConnection

IDLE = 0
FOLLOW_PATH = 1
WAIT_PATH = 2
FILENAME = "data.xlsx"

class AGV:
    def __init__(self, id, samplingTime):
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
        self.sampleTime = samplingTime
        self.previousTime = 0
        self.vLyapunov = 0
        self.omegaLyapunov = 0
        self.clearData()
    
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

    def writeToExcel(self):
        if len(self.data["time"]) == 0:
            logging.info("No data to write")
            return
        df = pd.DataFrame(self.data)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_uuid = uuid.uuid4().hex[:6]
        sheet_name = f"AGV{self.id}_{timestamp}_{unique_uuid}"
        if not os.path.exists(FILENAME):
            with pd.ExcelWriter(FILENAME, mode='w', engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            logging.info(f"Data has been written to {FILENAME} sheet {sheet_name}")
        else:
            with pd.ExcelWriter(FILENAME, mode='a', engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            logging.info(f"Data has been written to {FILENAME} sheet {sheet_name}")
        #clear self.data
        self.clearData()

    def clearData(self):
        self.data = {
            "time": [],
            "cur_x": [],
            "cur_y": [],
            "cur_orien": [],
            "goal_x": [],
            "goal_y": [],
            "goal_orien": [],
            "power": [],
            "v_lyapunov": [],
            "omega_lyapunov": [],
            "v_left": [],
            "v_right": [],
        }
    
    def insertData(self, time):
        currentPos = self.robot.getPos()
        goal = self.currentTargetPose
        v = self.vLyapunov
        omega = self.omegaLyapunov
        self.data["time"].append(time)
        self.data["cur_x"].append(currentPos.point.x)
        self.data["cur_y"].append(currentPos.point.y)
        self.data["cur_orien"].append(currentPos.orientation)
        self.data["goal_x"].append(goal.point.x)
        self.data["goal_y"].append(goal.point.y)
        self.data["goal_orien"].append(goal.orientation)
        self.data["power"].append(round(self.power))
        self.data["v_lyapunov"].append(v)
        self.data["omega_lyapunov"].append(omega)
        self.data["v_left"].append(self.robot.vLeft)
        self.data["v_right"].append(self.robot.vRight)

    def run(self, milis):
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
                    self.writeToExcel()
                    if self.isReachGoal():
                        self.clearFollowPathParams()
                        self.updateState(IDLE)
                    return
                elif self.isCurrentTargetPointNone():
                    self.updateTargetPoint()
                    return
                else:
                    self.steerToTargetPoint()
                if milis - self.previousTime > self.sampleTime:
                    self.previousTime = milis
                    self.insertData(datetime.now().strftime("%H:%M:%S.%f"))
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
        self.vLyapunov = v
        self.omageLyapunov = omega
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