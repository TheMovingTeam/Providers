import requests
import xmltodict
import jsonpath_ng
import modules.common as c

API_BASE_URL = (
    "http://atu@city.cuatroochenta.com/webservice.php/sync.php?compression=false"
)
POST_STRING = '<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'yes\' ?><data appVersion="1.15.1" deviceId="9999" culture="es" platform="android" />'

KML_QUERY = '$.kml.Document.Folder.Placemark[?LineString].LineString.coordinates'

stopIds = []

def fetchLines(city: str, pairs: dict = {}) -> list[c.LineObject]:
    lines = []
    r = requests.post(API_BASE_URL.replace("@city", city), POST_STRING)
    query = jsonpath_ng.parse("$.data.line[*]")
    itineraries = [match.value for match in query.find(xmltodict.parse(r.text))]
    for i in itineraries:
        emblem: str = i["alias"]
        if city == "alcoy":
            emblem = "L" + emblem[0]
            pass

        line = c.LineObject(
            i["id"],
            i["name"],
            emblem,
            "#" + i["color"].replace("H", "D").replace("J", "E").replace("K", "F"),
            [],  # Stops
        )

        fetchPath(line, i["kml"])

        lines.append(line)
        pass
    return lines


def fetchStops(city, provider) -> list[c.StopObject]:
    stops = []
    r = requests.post(API_BASE_URL.replace("@city", city), POST_STRING)
    query = jsonpath_ng.parse("$.data.line_stop[*]")
    line_stops = [match.value for match in query.find(xmltodict.parse(r.text))]
    for i in line_stops:
        stops.append(
            c.StopObject(
                i["id"],
                i["importation_id"],
                i["name"],
                [],  # Lines
                [],  # Incidences
                i["location_latitude"],
                i["location_longitude"],
            )
        )
        fetchImage(i["importation_id"], i["id"], city, provider)
        pass
    return stops


def fetchAssociations(lines, stops, city):
    r = requests.post(API_BASE_URL.replace("@city", city), POST_STRING)
    query = jsonpath_ng.parse("$.data.linestopline[*]")
    line_stop_associations = [
        match.value for match in query.find(xmltodict.parse(r.text))
    ]
    for association in line_stop_associations:
        try:
            line_id = association["line_id"]
            line_stop_id = association["line_stop_id"]

            [
                stop.lines.append(int(line_id))
                for stop in stops
                if stop.id == line_stop_id
            ]
            [
                line.stops.append(int(line_stop_id))
                for line in lines
                if line.id == line_id
            ]
        except KeyError:
            continue


def fetchImage(comId: int, stopId: int, city: str, provider: str):
    url = API_BASE_URL.replace("@city", city).replace(
        "webservice.php/sync.php?compression=false",
        "mdf-uploads/line_stop/street_view_local_stop_" + str(comId) + ".png",
    )
    r = requests.get(url)

    # Check for success
    if 200 <= r.status_code < 300:
        try:
            image = r.content
            c.saveImage(image, stopId, provider)
        except Exception as e:
            print(e)
            pass
        pass
    pass


# URL location
def fetchPath(line: c.LineObject, url: str, kmlQuery: str = KML_QUERY):
    r = requests.get(url)

    # Try both itineraries, wtf Vectalia
    if 200 <= r.status_code < 300:
        try:
            path = c.makeGeoJson(c.parseKML(r.text, kmlQuery))
            line.path = path
        except Exception as e:
            print(
                "KML exception in line "
                + str(line.emblem)
                + " (ID: "
                + str(line.id)
                + "): "
                + str(e)
            )
            pass
    pass
