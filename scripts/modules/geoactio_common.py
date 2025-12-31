import requests
import jsonpath_ng
import json
import modules.common as c


API_BASE_URL = "https://@city.geoactio.com/index.php/api/"
stopQuery = jsonpath_ng.parse("$.lineas[*].id")


def fetchLines(city: str) -> list[c.LineObject]:
    lines: list[c.LineObject] = []
    r: requests.Request = requests.get(
        API_BASE_URL.replace("@city", city) + "lineas",
    )
    response: list[dict] = json.loads(r.content.decode("utf-8"))["message"]
    for line in response:
        fetchedLine = c.LineObject(
            int(line["id"]), line["name"], line["id"], line["color"], []
        )
        lines.append(fetchedLine)
        pass
    return lines


def fetchStops(city: str, geoX: str, geoY: str) -> list[c.StopObject]:
    stops: list[c.StopObject] = []
    r = requests.get(
        API_BASE_URL.replace("@city", city) + "paradas",
    )
    response: list[dict] = json.loads(r.content.decode("utf-8"))["message"]
    for stop in response:
        lines = [int(match.value) for match in stopQuery.find(stop)]
        try:
            fetchedStop = c.StopObject(
                int(stop["id"]),
                stop["id"],
                stop["name"],
                lines,
                [],
                stop[geoX],
                stop[geoY],
            )
        except KeyError:
            fetchedStop = c.StopObject(
                int(stop["id"]),
                stop["id"],
                stop["name"],
                lines,
                [],
                None,
                None,
            )
        stops.append(fetchedStop)
        pass
    return stops


# TODO
def fetchAssociations(lines: list[c.LineObject], stops: list[c.StopObject]):
    for stop in stops:
        [line.stops.append(stop.id) for line in lines if line.id in stop.lines]
        pass
    # Remove empty lines
    [lines.remove(line) for line in lines if not line.stops]
    pass
