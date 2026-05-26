import modules.vectalia_common as vc
import modules.common as c

PROVIDER = "Vectalia Alcoi"
CITY = "alcoy"


def filterUnusedLines(lines: list[c.LineObject]):
    return [line for line in lines if line.path is not None]


def run():
    lines = vc.fetchLines(CITY)
    stops = vc.fetchStops(CITY, PROVIDER)
    filteredLines = filterUnusedLines(lines)
    vc.fetchAssociations(filteredLines, stops, CITY)
    c.exportLines(PROVIDER, filteredLines)
    c.exportStops(PROVIDER, stops)
    c.updateProvider(PROVIDER)


if __name__ == "__main__":
    try:
        print("-- Starting: " + PROVIDER)
        run()
    except KeyboardInterrupt:
        print("Interrupted!")
