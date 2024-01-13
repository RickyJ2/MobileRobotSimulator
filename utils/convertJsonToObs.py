from obstacle import Obstacle

def convertJsonToObs(object):
    obs = []
    for obj in object:
        rect = Obstacle(obj["position"][0], obj["position"][1], obj["size"][0], obj["size"][1])
        obs.append(rect)
    return obs  