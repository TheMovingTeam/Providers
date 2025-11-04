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
        lineId = int(line["route_id"])
        print("Fetching line: " + str(lineId))
        lineStops: list[int] = []
        for i in range(0, 10):
            try:
                r = requests.get(
                    API_URL + "routes/" + str(lineId) + "/stops?direction=" + str(i)
                )
                stops = json.loads(r.text)["stops"]
                lineStops: list[int] = [int(stop["stop_id"]) for stop in stops]
            except KeyError:
                break

        lines.append(
            c.LineObject(
                lineId,
                line["route_long_name"],
                line["route_short_name"],
                "#" + line["route_color"],
                lineStops,
            )
        )

    return lines


def fetchStops() -> list[c.StopObject]:
    stops: list[c.StopObject] = []
    r = requests.get(API_URL + "old/stops")
    response = '{ "stops": ' + r.content.decode("utf-8") + "}"
    fetchedStops = json.loads(response)["stops"]
    for stop in fetchedStops:
        print("Fetching stop: " + str(stop['stop_id']))
        r = requests.get(API_URL + "stops/code/" + stop['stop_code'] + "/routes")
        response = '{ "lines": ' + r.content.decode("utf-8") + "}"
        fetchedLines = json.loads(response)["lines"]
        stopLines = [line['route_id'] for line in fetchedLines]
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
        print("-- Starting: Metrobus Valencia")
        run()
    except KeyboardInterrupt:
        print("Interrupted!")
