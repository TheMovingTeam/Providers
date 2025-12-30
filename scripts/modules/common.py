import json
import time
import os


class LineObject:
    def __init__(self, id: int, name: str, emblem: str, color: str, stops: list[int]):
        self.id: int = id
        self.name: str = name
        self.emblem: str = emblem
        self.color: str = color
        self.stops: list[int] = stops
        pass

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "emblem": self.emblem,
            "color": self.color,
            "stops": self.stops,
        }
        pass

    pass


class StopObject:
    def __init__(
        self,
        id: int,
        comId: int | None,
        name: str,
        lines: list[int],
        notifications: list[str],
        geoX: float | None,
        geoY: float | None,
    ):
        self.id: int = id
        self.comId: int | None = comId
        self.name: str = name
        self.lines: list[int] = lines
        self.notifications: list[str] = notifications
        self.geoX: float | None = geoX
        self.geoY: float | None = geoY
        pass

    def to_dict(self):
        return {
            "id": self.id,
            "comId": self.comId,
            "name": self.name,
            "geoX": self.geoX,
            "geoY": self.geoY,
            "notifications": self.notifications,
            "lines": self.lines,
        }
        pass

    pass


def exportLines(provider: str, lines: list[LineObject]):
    linesDict = {"lines": [line.to_dict() for line in lines]}
    linesJson = json.dumps(linesDict)
    with open("../" + provider + "/lines.json", "w") as outfile:
        outfile.write(linesJson)


def exportStops(provider: str, stops: list[StopObject]):
    stopsDict = {"stops": [stop.to_dict() for stop in stops]}
    stopsJson = json.dumps(stopsDict)
    with open("../" + provider + "/stops.json", "w") as outfile:
        outfile.write(stopsJson)
        pass
    pass


def updateProvider(provider: str):
    filename = "../" + provider + "/metadata.json"
    with open(filename, "r") as file:
        metadata = json.load(file)
        metadata["lastUpdated"] = int(time.time())
    os.remove(filename)
    with open(filename, "w") as file:
        json.dump(metadata, file, indent=4)
        pass
    pass


def saveImage(img: bytes, stopId: int, provider: str):
    filename = "../" + provider + "/res/stop/" + str(stopId) + ".png"
    with open(filename, "wb") as file:
        file.write(img)
        file.close()
        pass
    pass
