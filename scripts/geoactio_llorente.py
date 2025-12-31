import modules.geoactio_common as gc
import modules.common as c

PROVIDER = "Llorente Bus"
CITY = "llorentebus"


def run():
    lines = gc.fetchLines(CITY)
    stops = gc.fetchStops(CITY, "latitude", "longitude")
    gc.fetchAssociations(lines, stops)
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
