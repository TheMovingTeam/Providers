import requests
from jsonpath_ng import parse
import modules.common as c
import modules.vectalia_common as vc

PROVIDER = "Vectalia Alicante"
API_URL = "https://appalicante-api-rvpro.vectalia.es/es/api/public/"

ITINERARY_QUERY = "$.data.transport_nets[*].lines[*].itineraries[*].id"
stopIds = []

KML_QUERY = "$.kml.Document.Folder.Placemark.LineString.coordinates"


def fetchLines():
    lines = []
    # Get itinerary list
    rq = requests.get(API_URL + "city/4")
    query = parse(ITINERARY_QUERY)
    itineraries = [match.value for match in query.find(rq.json())]
    # Download itineraries
    for i in itineraries:
        print("Fetching line " + str(i))

        r = requests.get(API_URL + "itinerary/" + str(i))
        response = r.json()

        try:
            if response["code"] == 200:
                data = response["data"]

                lineStopsResponse = data["line_stops"]

                if lineStopsResponse == []:
                    print("No stops found, skipping")
                    continue  # Skip line if it has no stops

                lineStops = []

                for lineStop in lineStopsResponse:
                    stopIds.append(lineStop["line_stop_id"])
                    lineStops.append(lineStop["line_stop_id"])

                line = c.LineObject(
                    data["id"],
                    data["name"],
                    data["line_alias"],
                    data["color"],
                    lineStops,
                )
                lines.append(line)

                vc.fetchPath(line, data["kml"], KML_QUERY)

                # Exclude broken routes, but don't null them so they don't try generating
                # Literally how does this even happen
                if (line.emblem == "TURI") or (line.emblem == "C-53"):
                    line.path = None

        except KeyError:
            print("KeyError found")

    return lines


def fetchStops(ids):
    stops = []

    uniqueStopIds = set(ids)

    for id in uniqueStopIds:
        r = requests.get(API_URL + "linestop/" + str(id))
        response = r.json()

        try:
            if response["code"] == 200:
                data = response["data"]

                # TODO: Generate images from Street View link
                if data["image"] is not None:
                    fetchImage(data["image"], id)

                itinerariesResponse = data["itineraries"]
                linesInStop = []

                if itinerariesResponse == []:
                    print("No lines found, skipping")
                    continue  # Skip stop if it has no lines

                for itinerary in itinerariesResponse:
                    linesInStop.append(itinerary["lineItineraryId"])

                incidence_msgs = []
                try:
                    incidences = data["incidences"]
                    if incidences != []:
                        incidence_msgs = list(map(lambda i: i["message"], incidences))
                except KeyError:
                    print("Incidences empty")
                    incidence_msgs: list[str] = []

                stop = c.StopObject(
                    data["id"],
                    int(data["nameCommercial"]),
                    data["name"],
                    linesInStop,
                    incidence_msgs,
                    data["locationLatitude"],
                    data["locationLongitude"],
                )
                stops.append(stop)
        except KeyError:
            print("KeyError found")

    return stops


def fetchImage(url: str, stopId: int):
    r = requests.get(url)

    # Check for success
    if 200 <= r.status_code < 300:
        try:
            img = r.content
            c.saveImage(img, stopId, PROVIDER)
        except Exception as e:
            print(e)


def run():
    fetchedLines = fetchLines()
    fetchedStops = fetchStops(stopIds)
    c.exportLines(PROVIDER, fetchedLines)
    c.exportStops(PROVIDER, fetchedStops)
    c.updateProvider(PROVIDER)


if __name__ == "__main__":
    try:
        print("-- Starting: Vectalia Alicante")
        run()
    except KeyboardInterrupt:
        print("Interrupted!")
