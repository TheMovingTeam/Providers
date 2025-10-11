import vectalia_common as vc
import common as c

PROVIDER = "Vectalia Elda"
CITY = "elda"


def fetch():
    lines = vc.fetchLines(CITY)
    stops = vc.fetchStops(CITY)
    vc.fetchAssociations(lines, stops, CITY)
    c.exportLines(PROVIDER, lines)
    c.exportStops(PROVIDER, stops)
    c.updateProvider(PROVIDER)
    pass


if __name__ == "__main__":
    fetch()
