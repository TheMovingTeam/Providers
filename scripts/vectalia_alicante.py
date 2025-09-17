import requests
import time
import common as c

PROVIDER = "Vectalia Alicante"
API_URL = "https://appalicante-api-rvpro.vectalia.es/es/api/public/"
stopIds = []


def fetchLines():
    lines = []
    for i in range(166, 1001):  # I hate this but I can't find a clear list
        print("Testing " + str(i))
        r = requests.get(API_URL + "itinerary/" + str(i))
        response = r.json()
        try:
            if response['code'] == 200:
                data = response['data']
                lineStopsResponse = data['line_stops']
                lineStops = []
                if lineStopsResponse == []:
                    print("No stops found, skipping")
                    continue  # Skip line if it has no stops
                for lineStop in lineStopsResponse:
                    stopIds.append(lineStop['line_stop_id'])
                    lineStops.append(lineStop['line_stop_id'])
                line = c.LineObject(
                    data['id'],
                    data['name'],
                    data['line_alias'],
                    data['color'],
                    lineStops
                )
                lines.append(line)
                print("Pass")
                pass
        except KeyError:
            print("KeyError found")
            pass
        time.sleep(1)
        pass
    return lines


def fetchStops(ids):
    stops = []
    uniqueStopIds = set(ids)
    for id in uniqueStopIds:
        r = requests.get(API_URL + "linestop/" + str(id))
        response = r.json()
        try:
            if response['code'] == 200:
                data = response['data']
                itinerariesResponse = data['itineraries']
                linesInStop = []
                if itinerariesResponse == []:
                    print("No lines found, skipping")
                    continue  # Skip stop if it has no lines
                for itinerary in itinerariesResponse:
                    linesInStop.append(itinerary['lineItineraryId'])
                stop = c.StopObject(
                    data['id'],
                    int(data['nameCommercial']),
                    data['name'],
                    linesInStop,
                    data['incidences'],
                    data['locationLatitude'],
                    data['locationLongitude'],
                )
                stops.append(stop)
                print("ID " + str(id) + ": Pass")
                pass
        except KeyError:
            print("KeyError found")
            pass
        time.sleep(1)
        pass
    return stops


if __name__ == "__main__":
    try:
        fetchedLines = fetchLines()
        fetchedStops = fetchStops(stopIds)
        c.exportLines(PROVIDER, fetchedLines)
        c.exportStops(PROVIDER, fetchedStops)
    except KeyboardInterrupt:
        print("Interrupted!")
