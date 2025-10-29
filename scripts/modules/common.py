import json
import time
import os


class LineObject:
    def __init__(self, id, name, emblem, color, stops):
        self.id = id
        self.name = name
        self.emblem = emblem
        self.color = color
        self.stops = stops
        pass

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'emblem': self.emblem,
            'color': self.color,
            'stops': self.stops
        }
        pass
    pass


class StopObject:
    def __init__(self, id, comId, name, lines, notifications, geoX, geoY):
        self.id = id
        self.comId = comId
        self.name = name
        self.lines = lines
        self.notifications = notifications
        self.geoX = geoX
        self.geoY = geoY
        pass

    def to_dict(self):
        return {
            'id': self.id,
            'comId': self.comId,
            'name': self.name,
            'geoX': self.geoX,
            'geoY': self.geoY,
            'notifications': self.notifications,
            'lines': self.lines,
        }
        pass
    pass


def exportLines(provider, lines):
    linesDict = {'lines': [line.to_dict() for line in lines]}
    linesJson = json.dumps(linesDict)
    with open('../' + provider + '/lines.json', 'w') as outfile:
        outfile.write(linesJson)


def exportStops(provider, stops):
    stopsDict = {'stops': [stop.to_dict() for stop in stops]}
    stopsJson = json.dumps(stopsDict)
    with open('../' + provider + '/stops.json', 'w') as outfile:
        outfile.write(stopsJson)


def updateProvider(provider):
    filename = '../' + provider + '/metadata.json'
    with open(filename, 'r') as file:
        metadata = json.load(file)
        metadata['lastUpdated'] = int(time.time())
    os.remove(filename)
    with open(filename, 'w') as file:
        json.dump(metadata, file, indent=4)
