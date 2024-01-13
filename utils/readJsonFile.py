import json

def readJsonFile(FileName):
    f = open(FileName)
    jsonData = json.load(f)
    f.close
    return jsonData