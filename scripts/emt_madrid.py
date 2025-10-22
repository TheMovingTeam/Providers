import requests
import jsonpath_ng
import common as c
import time


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


def fetchLines(token):
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
        # Create line object
        fetchedLine = c.LineObject(
            int(line['line']),
            line['nameA'] + " - " + line['nameB'],
            line['label'],
            "#" + line['color'],
            list(set(lineStops1 + lineStops2))  # Stops
        )
        lines.append(fetchedLine)
        pass
    return lines


def fetchStops(token):
    fetchedStops = []
    r = requests.post(
        API_URL + "/v1/transport/busemtmad/stops/list/",
        headers={"accessToken": token}
    )
    query = jsonpath_ng.parse("$.data[*]")
    stops = [match.value for match in query.find(r.json())]
    for stop in stops:
        fetchedStop = c.StopObject(
            stop['node'],
            None,  # ComId
            stop['name'],
            [line.split('/')[0] for line in stop['lines']],  # Lines
            [],  # Notifications
            stop['geometry']['coordinates'][0],
            stop['geometry']['coordinates'][1],
        )
        fetchedStops.append(fetchedStop)
    return fetchedStops


def run():
    token = fetchToken()
    lines = fetchLines(token)
    print([line.to_dict() for line in lines])
    stops = fetchStops(token)
    print([stop.to_dict() for stop in stops])
    c.exportLines(PROVIDER, lines)
    c.exportStops(PROVIDER, stops)
    c.updateProvider(PROVIDER)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("Interrupted!")
