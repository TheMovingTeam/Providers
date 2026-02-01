import modules.vectalia_common as vc
import modules.common as c

PROVIDER = "Vectalia Cáceres"
CITY = "caceres"


def run():
    lines = vc.fetchLines(CITY)
    stops = vc.fetchStops(CITY, PROVIDER)
    vc.fetchAssociations(lines, stops, CITY)
    c.exportLines(PROVIDER, lines)
    c.exportStops(PROVIDER, stops)
    c.updateProvider(PROVIDER)
    pass


if __name__ == "__main__":
    try:
        print("-- Starting: Vectalia Cáceres")
        run()
    except KeyboardInterrupt:
        print("Interrupted!")
