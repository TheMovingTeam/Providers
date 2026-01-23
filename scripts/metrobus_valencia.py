import requests
import json
import modules.common as c

PROVIDER = "Metrobus Valencia"
API_URL = "https://api.softoursistemas.com/metrobus/"


def fetchLines() -> list[c.LineObject]:
    lines: list[c.LineObject] = []

    r = requests.get(API_URL + "old/routes")
    response = '{ "lines": ' + r.content.decode("utf-8") + "}"
    fetchedLines = json.loads(response)["lines"]

    for line in fetchedLines:
        lineStops: list[int] = []

        lineId = line["route_id"]
        print("Fetching line: " + str(lineId))

        for i in range(0, 10):
            try:
                url = API_URL + "routes/" + str(lineId) + "/stops?direction=" + str(i)

                r = requests.get(url)
                stops = json.loads(r.text)["stops"]
                lineStops: list[int] = [int(stop["stop_id"]) for stop in stops]
            except KeyError:
                missingResponse = {"message":"No se encontraron paradas para esa ruta y dirección"}
                if r.json() != missingResponse:
                    print("Error parsing lineStops for line " + lineId)
                    print("Response: " + r.content.decode("utf-8"))
                    print("URL: " + url)
                break

            try:
                url = API_URL + "routes/" + str(lineId) + "/shapes/?direction=" + str(i)

                r = requests.get(url)
                path = r.content.decode("utf-8")
            except KeyError:
                missingResponse = {"message":"No se encontraron paradas para esa ruta y dirección"}
                if r.json() != missingResponse:
                    print("Error parsing shape for line " + lineId)
                    print("Response: " + r.content.decode("utf-8"))
                    print("URL: " + url)
                break

        id = int(bytes(lineId, encoding="utf-8"), 16)

        lines.append(
            c.LineObject(
                id,
                line["route_long_name"],
                line["route_short_name"],
                "#" + line["route_color"],
                lineStops,
                path,
            )
        )

    return lines


def fetchStops() -> list[c.StopObject]:
    stops: list[c.StopObject] = []

    r = requests.get(API_URL + "old/stops")
    response = '{ "stops": ' + r.content.decode("utf-8") + "}"

    fetchedStops = json.loads(response)["stops"]

    for stop in fetchedStops:
        print("Fetching stop: " + str(stop["stop_id"]))

        r = requests.get(API_URL + "stops/code/" + stop["stop_code"] + "/routes")
        response = '{ "lines": ' + r.content.decode("utf-8") + "}"

        fetchedLines = json.loads(response)["lines"]

        stopLines = [int(bytes(line["route_id"], "utf-8"), 16) for line in fetchedLines]

        stops.append(
            c.StopObject(
                int(stop["stop_id"]),
                stop["stop_code"],
                stop["stop_name"],
                stopLines,
                [],
                stop["stop_lat"],
                stop["stop_lon"],
            )
        )

    return stops


def run():
    lines = fetchLines()
    stops = fetchStops()
    c.exportLines(PROVIDER, lines)
    c.exportStops(PROVIDER, stops)
    c.updateProvider(PROVIDER)


if __name__ == "__main__":
    try:
        print("-- Starting: " + PROVIDER)
        run()
    except KeyboardInterrupt:
        print("Interrupted!")
