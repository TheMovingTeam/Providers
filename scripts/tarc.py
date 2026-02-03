import requests
import json
import jsonpath_ng
import modules.common as c

PROVIDER = "TARC"
API_BASE_URL = "https://tarc.rideralerts.com/"
KML_QUERY = '$.kml.Document.Folder.Placemark[?LineString].LineString.coordinates'


def fetchLines() -> list[c.LineObject]:
    lines = []
    
    r= requests.get(API_BASE_URL + "InfoPoint/rest/Routes/GetVisibleRoutes")
    responseLines = json.loads("{\"lines\":" + r.content.decode('utf-8') + "}")
    for line in responseLines["lines"]:
        print("Fetching route " + line["ShortName"])

        path = fetchPath(line["RouteTraceFilename"])
        stops = fetchLineStops(line["RouteId"])
        fetchedLine = c.LineObject(
                line["RouteId"],
                line["LongName"],
                line["ShortName"],
                "#" + line["Color"],
                stops,
                path
                )
        lines.append(fetchedLine)
    return lines

def fetchPath(filename: str) -> str:
    r = requests.get(API_BASE_URL + "/InfoPoint/Resources/Traces/" + filename)
    kml = c.parseKML(r.content.decode('utf-8'), KML_QUERY)
    return c.makeGeoJson(kml, True)


def fetchLineStops(id: int) -> list[int]:
    r = requests.get(API_BASE_URL + "InfoPoint/rest/RouteDetails/Get/" + str(id))
    lineStopQuery = jsonpath_ng.parse("$.RouteStops.[*].StopId")
    return [match.value for match in lineStopQuery.find(r.json())]


def fetchStops() -> list[c.StopObject]:
    stops = []
    
    r = requests.get(API_BASE_URL + "/InfoPoint/rest/Stops/GetAllStops")
    responseStops = json.loads("{\"stops\":" + r.content.decode('utf-8') + "}")
    for stop in responseStops["stops"]:
        print("Fetching stop " + str(stop["StopId"]))
        fetchedStop = c.StopObject(
                stop["StopId"],
                stop["StopRecordId"],
                stop["Name"],
                [],
                [],
                stop["Latitude"],
                stop["Longitude"]
                )
        stops.append(fetchedStop)
    return stops


def fetchAssociations(lines: list[c.LineObject], stops: list[c.StopObject]):
    for line in lines:
        [stop.lines.append(line.id) for stop in stops if stop.id in line.stops]
        pass
    pass


def run():
    lines = fetchLines()
    stops = fetchStops()
    fetchAssociations(lines, stops)
    c.exportLines(PROVIDER, lines)
    c.exportStops(PROVIDER, stops)
    c.updateProvider(PROVIDER)
    pass


if __name__ == "__main__":
    try:
        print("-- Starting: " + PROVIDER)
        run()
    except KeyboardInterrupt:
        print("Interrupted!")
