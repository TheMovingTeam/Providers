import requests
import jsonpath_ng
import modules.common as c


PROVIDER = "EMT Madrid"
API_URL = "https://openapi.emtmadrid.es/"
CLIENT_ID = "428b01e6-693c-4f7f-a11e-3bb923420587"
TOKEN_CONTENT = {
    "passKey": "504fea88211f2f90633f964189b7696037d65cc3a5f47b8fa1d5ea5e34db0239ad2e068851e72be0cec125779224749e3bc236c1b7af39d8a3d398e99223f058",
    "X-ClientId": CLIENT_ID
}
STOP_CONTENT = {
    "statistics": "",
    "cultureInfo": "",
    "Text_StopRequired_YN": "Y",
    "Text_EstimationsRequired_YN": "Y",
    "Text_IncidencesRequired_YN": "Y",
    "DateTime_Referenced_Incidencies_YYYYMMDD": "20180823"
}


def fetchToken():
    r = requests.post(
        "https://api.mpass.mobi/v1/core/identity/login/integrator",
        json=TOKEN_CONTENT,
        headers={"X-ClientId": CLIENT_ID,
                 "Content-Type": "application/json",
                 "debug": "1"}
    )
    query = jsonpath_ng.parse("$.data[*].idUser")
    token = query.find(r.json())[0].value
    return token


def fetchLines(token: str) -> list[c.LineObject]:
    lines = []
    r = requests.get(
        API_URL + "v2/transport/busemtmad/lines/info/",
        headers={"accessToken": token}
    )
    for line in r.json()['data']:
        print("Fetching line " + line['line'])
        # Fetch stops both ways
        r1 = requests.get(
            API_URL + "/v1/transport/busemtmad/lines/" +
            str(line['line']) + "/stops/1/",
            headers={"accessToken": token}
        ).json()
        r2 = requests.get(
            API_URL + "/v1/transport/busemtmad/lines/" +
            str(line['line']) + "/stops/2/",
            headers={"accessToken": token}
        ).json()
        lineStops1 = [int(stop['stop']) for stop in r1['data'][0]['stops']]
        lineStops2 = [int(stop['stop']) for stop in r2['data'][0]['stops']]
        if line['nameA'] == line['nameB']:
            lineName = [line['nameA']]
        else:
            lineName = line['nameA'] + " - " + line['nameB'],
        print(lineName[0])
        # Create line object
        fetchedLine = c.LineObject(
            int(line['line']),
            lineName[0],
            line['label'],
            "#" + line['color'],
            list(set(lineStops1 + lineStops2))
        )
        fetchPath(fetchedLine, token)
        lines.append(fetchedLine)
        pass
    return lines


def fetchStops(token: str) -> list[c.StopObject]:
    fetchedStops = []
    
    r = requests.post(
        API_URL + "/v1/transport/busemtmad/stops/list/",
        headers={"accessToken": token}
    )
    query = jsonpath_ng.parse("$.data[*]")

    stops = [match.value for match in query.find(r.json())]
    for stop in stops:
        fetchedStop = c.StopObject(
            int(stop['node']),
            None,
            stop['name'],
            [int(line.split('/')[0]) for line in stop['lines']],
            [],
            stop['geometry']['coordinates'][1],
            stop['geometry']['coordinates'][0],
        )
        fetchedStops.append(fetchedStop)
    return fetchedStops


def fetchPath(line: c.LineObject, token: str):
    r = requests.get(
            API_URL
                + "v1/transport/busemtmad/lines/"
                + str(line.id)
                + "/route",
                headers= {"accessToken": token}
            )
    query1 = jsonpath_ng.parse("$.data.itinerary.toA.features[*].geometry.coordinates[*]")
    query2 = jsonpath_ng.parse("$.data.itinerary.toB.features[*].geometry.coordinates[*]")

    segments1: list[list[list[float]]] = [match.value for match in query1.find(r.json())]
    segments2: list[list[list[float]]] = [match.value for match in query2.find(r.json())]

    path = c.makeGeoJson(segments1 + segments2, True)

    line.path = path
    pass


def run():
    token = fetchToken()
    lines = fetchLines(token)
    stops = fetchStops(token)
    c.exportLines(PROVIDER, lines)
    c.exportStops(PROVIDER, stops)
    c.updateProvider(PROVIDER)


if __name__ == "__main__":
    try:
        print("-- Starting: EMT Madrid")
        run()
    except KeyboardInterrupt:
        print("Interrupted!")
