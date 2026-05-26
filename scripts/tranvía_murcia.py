import requests
import json
import modules.common as c

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
            None,
            stop['nombre'],
            [1],
            [],
            stop['lat'],
            stop['lng']
        ))
    return fetchedStops


def run():
    line = c.LineObject(
        1,
        "Tranvía de Murcia",
        "TdM",
        "#ccd622",
        [],
    )
    stops = fetchStops(line)
    c.exportLines(PROVIDER, [line])
    c.exportStops(PROVIDER, stops)
    c.updateProvider(PROVIDER)


if __name__ == "__main__":
    try:
        print("-- Starting: Tranvía de Murcia")
        run()
    except KeyboardInterrupt:
        print("Interrupted!")
