import requests
import json
import common as c

PROVIDER = "Tranvía de Murcia"
API_URL = "https://tranviademurcia.es/"


def fetchStops(line):
    fetchedStops = []
    r = requests.get(
        API_URL + "api-horarios/get_paradas",
        headers={"Accept": "*/*", "User-Agent": "curl/8.16.0"}
    )
    input = '{"stops": ' + r.text + '}'
    stops = json.loads(input)
    for stop in stops['stops']:
        line.stops.append(int(stop['id']))
        fetchedStops.append(c.StopObject(
            int(stop['id']),
            None,  # ComId
            stop['nombre'],
            [1],  # Line is constant
            [],  # Notifications
            stop['lat'],
            stop['lng']
        ))
        pass
    return fetchedStops


def run():
    line = c.LineObject(
        1,
        "Tranvía de Murcia",
        "TdM",
        "#ccd622",
        [],  # Stops
    )
    stops = fetchStops(line)
    c.exportLines(PROVIDER, [line])
    c.exportStops(PROVIDER, stops)
    c.updateProvider(PROVIDER)
    pass


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("Interrupted!")
