import jsonpath_ng
import modules.common as c
import requests
import xmltodict
from modules.common import LineObject, StopObject

PROVIDER = "Transporte de Murcia"
API_URL = "http://95.63.53.45:8045/SIRI.IIS/SiriWS.asmx"

REQUEST = """<?xml version='1.0' encoding='utf-8'?><soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:xsd='http://www.w3.org/2001/XMLSchema'><soap:Body><LinesDiscovery xmlns='http://tempuri.org/'><request><Request xmlns=''><RequestTimestamp xmlns='http://www.siri.org.uk/siri'>2025-11-05T12:44:21.1920000+01:00</RequestTimestamp><AccountId xmlns='http://www.siri.org.uk/siri'>wshuesca</AccountId><AccountKey xmlns='http://www.siri.org.uk/siri'>WS.huesca</AccountKey><LinesDetailLevel xmlns='http://www.siri.org.uk/siri'>normal</LinesDetailLevel></Request></request></LinesDiscovery></soap:Body></soap:Envelope>"""


def fetchInfo() -> tuple[list[LineObject], list[StopObject]]:
    lines: list[c.LineObject] = []
    stops: list[c.StopObject] = []
    r = requests.post(API_URL, REQUEST, headers={"Content-Type": "text/xml"})
    responseJson = xmltodict.parse(r.text.replace(":", ""))
    query = jsonpath_ng.parse(
        "$.soapEnvelope.soapBody.LinesDiscoveryResponse.LinesDiscoveryResult.Answer.AnnotatedLineRef[*]"
    )
    for line in [match.value for match in query.find(responseJson)]:
        lineStops = line["Directions"]["Direction"][0]["Stops"]["StopPointInPattern"]
        lineId = int(line["LineRef"].replace("C", "").replace("R", ""))
        match lineId:
            case 1:
                color = "#ee1c25"
                pass
            case 2:
                color = "#f12536"
                pass
            case 3:
                color = "#000000"
                pass
            case 4:
                color = "#ffffff"
                pass
            case 5:
                color = "#0000cd"
                pass
            case 12:
                color = "#333333"
                pass
            case 14:
                color = "#64bc45"
                pass
            case 17:
                color = "#c47eb6"
                pass
            case 20:
                color = "#6acff6"
                pass
            case 80:
                color = "#ffd402"
                pass
            case _:
                color = "#334466"
        lines.append(
            c.LineObject(
                lineId,  # Properly hash emblem for IDs
                line["LineName"],
                line["LineRef"],
                color,
                [int(stop["StopPointRef"]) for stop in lineStops],
            )
        )
        for stop in lineStops:
            for presentStop in stops:
                if presentStop.id == int(stop["StopPointRef"]):
                    presentStop.lines.append(lineId)
                    break
                pass
            stops.append(
                c.StopObject(
                    int(stop["StopPointRef"]),
                    int(stop["StopPointRef"]),
                    stop["StopName"],
                    [lineId],
                    [],
                    stop["Location"]["Latitude"],
                    stop["Location"]["Longitude"],
                )
            )
            pass
        pass
    return (lines, list(set(stops)))


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
