import requests
import common as c

PROVIDER = "Tram Alacant"
API_URL = "https://www.fgv.es/ap18/api/public/es/api/v1/"


def fetchLines():
    lines = []
    r = requests.get(API_URL + "/A/lineas")
    response = r.json()
    for line in response:
        try:
            fetchedLine = c.LineObject(
                    line['linea_id_FGV'],
                    "Línea " + line['nombre_largo'].replace('L', ''),
                    line['nombre_corto'],
                    line['color'],
                    line['stops'].split(',')
            )
            lines.append(fetchedLine)
        except KeyError:
            print("KeyError found")
            pass
        pass
    return lines


def fetchStops():
    stops = []
    r = requests.get(API_URL + "/A/estaciones")
    response = r.json()
    for stop in response:
        try:
            fetchedStop = c.StopObject(
                    stop['estacion_id_FGV'],
                    None,
                    stop['nombre'],
                    [],
                    [],
                    stop['latitud'],
                    stop['longitud'],
            )
            stops.append(fetchedStop)
        except KeyError:
            print("KeyError found")
            pass
        pass
    return stops


def stopLines(lines, stops):
    for stop in stops:
        presentLines = filter(lambda line: stop.id in line.stops, lines)
        lineIds = map(lambda line: line.id, presentLines)
        stop.lines = lineIds


if __name__ == "__main__":
    fetchedLines = fetchLines()
    fetchedStops = fetchStops()
    c.exportLines(PROVIDER, fetchedLines)
    c.exportStops(PROVIDER, fetchedStops)
    c.updateProvider(PROVIDER)
