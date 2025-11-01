import requests
import modules.common as c

PROVIDER = "Metrovalencia"
API_URL = "https://www.fgv.es/ap18/api/public/es/api/v1/V"


def fetchLines() -> list[c.LineObject]:
    lines: list[c.LineObject] = []
    r = requests.get(API_URL + "/lineas")
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


def fetchStops() -> list[c.StopObject]:
    stops: list[c.StopObject] = []
    r = requests.get(API_URL + "/estaciones")
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
        except KeyError as e:
            print("KeyError found:")
            print(e)
            pass
        pass
    return stops


def stopLines(lines, stops):
    for stop in stops:
        lineIds = [line.id for line in lines if str(stop.id) in line.stops]
        stop.lines = list(lineIds)


def run():
    fetchedLines = fetchLines()
    fetchedStops = fetchStops()
    stopLines(fetchedLines, fetchedStops)
    c.exportLines(PROVIDER, fetchedLines)
    c.exportStops(PROVIDER, fetchedStops)
    c.updateProvider(PROVIDER)
    pass


if __name__ == "__main__":
    try:
        print("-- Starting: Metrovalencia")
        run()
    except KeyboardInterrupt:
        print("Interrupted!")
