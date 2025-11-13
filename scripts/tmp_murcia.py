import requests
import json
import modules.common as c

PROVIDER = "TMP Murcia"
API_URL = "https://api.latbus.com/"


def fetchInfo():
    fetchedLines = []
    fetchedStops = []

    r = requests.get(
        API_URL + "latbusapp/rest/line",
    )
    input = '{"lines": ' + r.text + '}'
    lines = json.loads(input)
    for line in lines['lines']:

        lineId = line['route']

        existingLine = next(
            (existingLine for existingLine in fetchedLines
             if existingLine.id == lineId),
            None
        )

        if existingLine is None:
            fetchedLine = c.LineObject(
                lineId,
                line['name'],
                str(line['route']),
                "#FF0000",
                []  # Stops
            )
            fetchedLines.append(fetchedLine)
            pass
        else:
            fetchedLine = existingLine
            pass

        for stop in line['stops']:

            fetchedLine.stops.append(stop['id'])

            existingStop = next(
                (existingStop for existingStop in fetchedStops
                 if existingStop.id == stop['id']),
                None
            )

            if existingStop is None:
                fetchedStop = c.StopObject(
                    stop['id'],
                    None,  # ComId
                    stop['name'],
                    [lineId],  # Lines
                    [],  # Notifications,
                    stop['latitude'],
                    stop['longitude']
                )
                fetchedStops.append(fetchedStop)
            else:
                existingStop.lines.append(lineId)
                pass

            pass
        pass
    return fetchedLines, fetchedStops


def run():
    lines, stops = fetchInfo()
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
