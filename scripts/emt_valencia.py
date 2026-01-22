import requests
import xmltodict
import jsonpath_ng
import xml.parsers.expat as e
import logging
import time
import modules.common as c

PROVIDER = "EMT Valencia"
API_URL = "https://www.emtvalencia.es/ciudadano/servicios/"


def fetchLines() -> list[c.LineObject]:
    fetchedLines = []
    r = requests.get(API_URL + "info_lineas_v2.xml")
    data = xmltodict.parse(r.content.decode('utf-8'))
    query = jsonpath_ng.parse("$.lineas.linea[*]")
    lines = [match.value for match in query.find(data)]
    for line in lines:
        for id in line['id_publico'].split("-"):
            fetchedLine = c.LineObject(
                id,
                line['nombre_linea'],
                line['id_publico'],
                "#FF0000",
                []  # Stops
            )
        fetchedLines.append(fetchedLine)
        pass
    return fetchedLines


def fetchStops(lines) -> list[c.StopObject]:
    fetchedStops = []
    
    url = "https://www.emtvalencia.es/EMT/mapfunctions/MapUtilsPetitions.php?sec=findParadas&sCoordenadas=4326"
    r = requests.get(url)
    geoJson = xmltodict.parse(r.content.decode('utf-8'))
    
    for line in lines:
        print("Fetching stops for line " + line.id)
        match line.id:
            case "C1":
                id = 5
                line.id = 5
                pass
            case "C2":
                id = 80
                line.id = 80
                pass
            case "C3":
                id = 90
                line.id = 90
                pass
            case _:
                id = int(line.id)
                pass
        routesURL = API_URL + "sentidos_ruta_linea.php" + \
            "?usuario=7gH8m45w7A" + \
            "&linea=" + str(id) + \
            "&lang=es"
        r = requests.get(routesURL)
        
        try:
            data = xmltodict.parse(r.content.decode('utf-8'))
        except e.ExpatError:
            # Wait and try again to ensure rate limit isn't hit
            time.sleep(5)
            r = requests.get(routesURL)
            try:
                data = xmltodict.parse(r.content.decode('utf-8'))
            except e.ExpatError:
                logging.warning("Error found fetching routes for line: " + line.id)
                print("Input:")
                print(r.content.decode('utf-8'))
                print("URL: " + routesURL)
        
        query = jsonpath_ng.parse("$.linea.sentidos_ruta.sentido_ruta[*]")
        routes = [match.value for match in query.find(data)]
        for route in routes:
            r = requests.get(API_URL + "paradas_linea.php" +
                             "?usuario=7gH8m45w7A&"
                             "&linea=" + str(id) +
                             "&ruta=" + route['ruta'] +
                             "&sentido=" + route['sentido']
                             )
            try:
                data = xmltodict.parse(r.content.decode('utf-8'))
            except e.ExpatError:
                logging.warning(
                    "Error found fetching stops on line: " + line.id)
                print("Input:")
                print(r.content.decode('utf-8'))
                continue
            
            query = jsonpath_ng.parse("$.linea.paradas.parada[*]")
            stops = [match.value for match in query.find(data)]

            stopIdQuery = jsonpath_ng.parse("$.linea.paradas.parada[*].id_parada")
            
            stopIds = [int(match.value) for match in stopIdQuery.find(data)]
            line.stops = stopIds

            for stop in stops:
                print("\tFetching stop " + stop['id_parada'])
                lineQuery = jsonpath_ng.parse("$.lineas_parada.linea_parada[*]")
                
                stopLineEmblems = [
                    match.value
                    for match in lineQuery.find(stop)
                    ]
                
                stopLines = [
                        line.id
                        for line in lines
                        if line.emblem in stopLineEmblems
                        ]
                
                fetchedStop = c.StopObject(
                    int(stop['id_parada']),
                    None,
                    stop['nombre_parada'],
                    stopLines,
                    [],
                    None,
                    None,
                )
                
                if fetchedStop not in fetchedStops:
                    fetchStopPoints(fetchedStop, geoJson)
                    fetchedStops.append(fetchedStop)
                pass
            # Rate limit
            time.sleep(2.5)
            pass
        time.sleep(2.5)
    return list(set(fetchedStops))


def fetchStopPoints(stop: c.StopObject, data: dict):
    for point in data["findBusStopes"]["list"]["paradaInfo"]:
        id = int(point["id"])
        if stop.id == id:
            coords: dict = point["mappoint"]
            # Coordinates are inverted
            stop.geoX = float(coords["@y"])
            stop.geoY = float(coords["@x"])


def run():
    lines = fetchLines()
    stops = fetchStops(lines)
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
