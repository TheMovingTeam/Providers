import requests
import xmltodict
import jsonpath_ng
import common as c

API_BASE_URL = "http://atu@city.cuatroochenta.com/webservice.php/sync.php?compression=false"
POST_STRING = "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><data appVersion=\"1.15.1\" deviceId=\"9999\" culture=\"es\" platform=\"android\" />"
stopIds = []


def fetchLines(city):
    lines = []
    r = requests.post(
        API_BASE_URL.replace("@city", city),
        POST_STRING
    )
    query = jsonpath_ng.parse('$.data.line[*]')
    itineraries = [match.value for match in query.find(
        xmltodict.parse(r.text))]
    for i in itineraries:
        line = c.LineObject(
            i['id'],
            i['name'],
            i['alias'],
            i['color'],
            []
        )
        lines.append(line)
        pass
    return lines


def fetchStops(city):
    stops = []
    r = requests.post(
        API_BASE_URL.replace("@city", city),
        POST_STRING
    )
    query = jsonpath_ng.parse('$.data.line_stop[*]')
    line_stops = [match.value for match in query.find(xmltodict.parse(r.text))]
    for i in line_stops:
        stop = c.StopObject(
            i['id'],
            i['importation_id'],
            i['name'],
            [],  # Lines
            [],  # Incidences
            i['location_latitude'],
            i['location_longitude'],
        )
        stops.append(stop)
        pass
    return stops


def fetchAssociations(lines, stops, city):
    r = requests.post(
        API_BASE_URL.replace("@city", city),
        POST_STRING
    )
    query = jsonpath_ng.parse('$.data.linestopline[*]')
    line_stop_associations = [
        match.value for match in query.find(xmltodict.parse(r.text))]
    for association in line_stop_associations:
        try:
            line_id = association['line_id']
            line_stop_id = association['line_stop_id']
            for stop in stops:
                if stop.id == line_stop_id:
                    stop.lines.append(line_id)
                    pass
                pass
            for line in lines:
                if line.id == line_id:
                    line.stops.append(line_stop_id)
                    pass
                pass
            pass
        except KeyError:
            continue
